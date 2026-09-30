from typing import List
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Field, IrrigationSchedule, IrrigationRecord
from src.api.schemas import ScheduleResponse, ScheduleExecuteRequest
from src.services.ml_service import predict_for_field

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations & Schedules"])


@router.get("/today", response_model=List[ScheduleResponse])
def get_today_schedules(db: Session = Depends(get_db)):
    """Fetch today's irrigation schedules and ML recommendations across all fields."""
    today = date.today()
    schedules = db.query(IrrigationSchedule).filter(
        IrrigationSchedule.schedule_date == today
    ).order_by(IrrigationSchedule.recommended_start.asc()).all()

    enriched = []
    for s in schedules:
        f = db.query(Field).filter(Field.id == s.field_id).first()
        enriched.append({
            "id": s.id,
            "field_id": s.field_id,
            "field_name": f.name if f else s.field_id.capitalize(),
            "crop_type": f.crop_type if f else "Unknown",
            "schedule_date": s.schedule_date,
            "recommended_start": s.recommended_start,
            "duration_minutes": s.duration_minutes,
            "water_quantity_liters": s.water_quantity_liters,
            "status": s.status,
            "reason": s.reason,
            "ml_recommendation_needed": s.ml_recommendation_needed,
            "created_at": s.created_at
        })
    return enriched


@router.post("/field/{field_id}", response_model=ScheduleResponse)
def generate_field_recommendation(field_id: str, db: Session = Depends(get_db)):
    """Run ML recommendation engine for a specific field and record/update today's schedule."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")

    pred = predict_for_field(db, field_id)

    today = date.today()
    existing_sched = db.query(IrrigationSchedule).filter(
        IrrigationSchedule.field_id == field_id,
        IrrigationSchedule.schedule_date == today
    ).first()

    rec_start = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    if existing_sched:
        existing_sched.recommended_start = rec_start
        existing_sched.duration_minutes = pred["duration_minutes"]
        existing_sched.water_quantity_liters = pred["water_quantity_liters"]
        existing_sched.status = "scheduled" if pred["irrigation_needed"] else "skipped"
        existing_sched.reason = pred["reason"]
        existing_sched.ml_recommendation_needed = pred["irrigation_needed"]
        sched = existing_sched
    else:
        sched = IrrigationSchedule(
            field_id=field_id,
            schedule_date=today,
            recommended_start=rec_start,
            duration_minutes=pred["duration_minutes"],
            water_quantity_liters=pred["water_quantity_liters"],
            status="scheduled" if pred["irrigation_needed"] else "skipped",
            reason=pred["reason"],
            ml_recommendation_needed=pred["irrigation_needed"]
        )
        db.add(sched)

    db.commit()
    db.refresh(sched)

    return {
        "id": sched.id,
        "field_id": sched.field_id,
        "field_name": field.name,
        "crop_type": field.crop_type,
        "schedule_date": sched.schedule_date,
        "recommended_start": sched.recommended_start,
        "duration_minutes": sched.duration_minutes,
        "water_quantity_liters": sched.water_quantity_liters,
        "status": sched.status,
        "reason": sched.reason,
        "ml_recommendation_needed": sched.ml_recommendation_needed,
        "created_at": sched.created_at
    }


@router.post("/run-all", response_model=List[ScheduleResponse])
def run_all_recommendations(db: Session = Depends(get_db)):
    """Run ML recommendation engine across all registered active fields."""
    fields = db.query(Field).filter(Field.is_active == True).all()
    results = []
    for f in fields:
        res = generate_field_recommendation(f.id, db)
        results.append(res)
    return results


@router.post("/schedule/{schedule_id}/execute")
def execute_schedule(
    schedule_id: int,
    data: ScheduleExecuteRequest,
    db: Session = Depends(get_db)
):
    """
    Mark a scheduled irrigation as executed by the farmer.
    Crucial: Clearly creates an actual IrrigationRecord and sets schedule status to 'completed'.
    """
    sched = db.query(IrrigationSchedule).filter(IrrigationSchedule.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    if sched.status == "completed":
        raise HTTPException(status_code=409, detail="This schedule has already been completed.")

    recent_cutoff = datetime.utcnow() - timedelta(hours=12)
    recent_record = db.query(IrrigationRecord).filter(
        IrrigationRecord.field_id == sched.field_id,
        IrrigationRecord.status == "completed",
        IrrigationRecord.timestamp >= recent_cutoff
    ).first()
    if recent_record:
        raise HTTPException(
            status_code=409,
            detail="Irrigation is limited to one completed event per field every 12 hours."
        )

    dur = data.actual_duration_minutes if data.actual_duration_minutes is not None else sched.duration_minutes
    liters = data.actual_water_liters if data.actual_water_liters is not None else sched.water_quantity_liters

    # Create actual irrigation record
    record = IrrigationRecord(
        field_id=sched.field_id,
        timestamp=datetime.utcnow(),
        duration_minutes=dur,
        water_quantity_liters=liters,
        status="completed",
        notes=data.notes or f"Executed from schedule #{sched.id}"
    )
    db.add(record)

    # Update schedule status
    sched.status = "completed"
    db.commit()
    db.refresh(record)

    return {
        "status": "success",
        "message": f"Irrigation marked as completed for field '{sched.field_id}'.",
        "record_id": record.id,
        "water_applied_liters": record.water_quantity_liters,
        "duration_minutes": record.duration_minutes
    }
