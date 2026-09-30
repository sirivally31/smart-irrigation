from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Field, IrrigationRecord
from src.api.schemas import IrrigationRecordCreate, IrrigationRecordResponse

router = APIRouter(prefix="/api/history", tags=["Irrigation History"])


@router.get("/irrigation", response_model=List[IrrigationRecordResponse])
def get_irrigation_history(
    field_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fetch completed irrigation records with filtering by field and date range."""
    start_time = datetime.utcnow() - timedelta(days=days)
    query = db.query(IrrigationRecord).filter(IrrigationRecord.timestamp >= start_time)

    if field_id:
        query = query.filter(IrrigationRecord.field_id == field_id)
    if status:
        query = query.filter(IrrigationRecord.status == status)

    records = query.order_by(IrrigationRecord.timestamp.desc()).all()

    enriched = []
    for r in records:
        f = db.query(Field).filter(Field.id == r.field_id).first()
        enriched.append({
            "id": r.id,
            "field_id": r.field_id,
            "field_name": f.name if f else r.field_id.capitalize(),
            "timestamp": r.timestamp,
            "duration_minutes": r.duration_minutes,
            "water_quantity_liters": r.water_quantity_liters,
            "status": r.status,
            "notes": r.notes,
            "created_at": r.created_at
        })
    return enriched


@router.post("/irrigation", response_model=IrrigationRecordResponse, status_code=201)
def log_irrigation_record(
    data: IrrigationRecordCreate,
    db: Session = Depends(get_db)
):
    """Log an ad-hoc or manual irrigation event."""
    field = db.query(Field).filter(Field.id == data.field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field '{data.field_id}' not found.")

    new_record = IrrigationRecord(
        field_id=data.field_id,
        timestamp=datetime.utcnow(),
        duration_minutes=data.duration_minutes,
        water_quantity_liters=data.water_quantity_liters,
        status=data.status,
        notes=data.notes or "Manual farmer irrigation entry"
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "id": new_record.id,
        "field_id": new_record.field_id,
        "field_name": field.name,
        "timestamp": new_record.timestamp,
        "duration_minutes": new_record.duration_minutes,
        "water_quantity_liters": new_record.water_quantity_liters,
        "status": new_record.status,
        "notes": new_record.notes,
        "created_at": new_record.created_at
    }


@router.get("/summary")
def get_irrigation_summary(
    field_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Compute aggregate water usage, cycle counts, and efficiency stats."""
    start_time = datetime.utcnow() - timedelta(days=days)
    query = db.query(IrrigationRecord).filter(IrrigationRecord.timestamp >= start_time)
    if field_id:
        query = query.filter(IrrigationRecord.field_id == field_id)

    records = query.all()
    total_liters = sum(r.water_quantity_liters for r in records)
    total_minutes = sum(r.duration_minutes for r in records)

    return {
        "period_days": days,
        "field_id": field_id or "all_fields",
        "total_events": len(records),
        "total_water_liters": round(total_liters, 1),
        "total_duration_minutes": round(total_minutes, 1),
        "avg_liters_per_event": round(total_liters / len(records), 1) if records else 0.0
    }
