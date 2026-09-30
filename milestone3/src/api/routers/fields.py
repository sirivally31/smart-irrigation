from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Field, SensorReading, IrrigationSchedule, Alert
from src.api.schemas import (
    FieldCreate, FieldUpdate, FieldDetailResponse,
    SensorReadingCreate, SensorReadingResponse
)

router = APIRouter(prefix="/api/fields", tags=["Fields"])


def enrich_field_detail(field: Field, db: Session) -> dict:
    latest_sensor = db.query(SensorReading).filter(
        SensorReading.field_id == field.id
    ).order_by(SensorReading.timestamp.desc()).first()

    today = datetime.utcnow().date()
    today_sched = db.query(IrrigationSchedule).filter(
        IrrigationSchedule.field_id == field.id,
        IrrigationSchedule.schedule_date == today
    ).first()

    active_alerts = db.query(Alert).filter(
        Alert.field_id == field.id,
        Alert.status == "unread"
    ).count()

    return {
        "id": field.id,
        "name": field.name,
        "crop_type": field.crop_type,
        "growth_stage": field.growth_stage,
        "soil_type": field.soil_type,
        "area_acres": field.area_acres,
        "location": field.location,
        "target_moisture_min": field.target_moisture_min,
        "target_moisture_max": field.target_moisture_max,
        "is_active": field.is_active,
        "created_at": field.created_at,
        "latest_soil_moisture": round(latest_sensor.soil_moisture_pct, 1) if latest_sensor else None,
        "latest_temperature": round(latest_sensor.temperature_c, 1) if latest_sensor else None,
        "latest_humidity": round(latest_sensor.humidity_pct, 1) if latest_sensor else None,
        "latest_rainfall": round(latest_sensor.rainfall_mm, 1) if latest_sensor else None,
        "today_schedule_status": today_sched.status if today_sched else "none",
        "today_recommended_liters": today_sched.water_quantity_liters if today_sched else None,
        "today_recommended_time": today_sched.recommended_start.strftime("%H:%M") if today_sched else None,
        "today_reason": today_sched.reason if today_sched else None,
        "active_alerts_count": active_alerts
    }


@router.get("", response_model=List[FieldDetailResponse])
def get_all_fields(db: Session = Depends(get_db)):
    """Retrieve all fields registered by the farmer with enriched status."""
    fields = db.query(Field).all()
    return [enrich_field_detail(f, db) for f in fields]


@router.post("", response_model=FieldDetailResponse, status_code=201)
def create_field(data: FieldCreate, db: Session = Depends(get_db)):
    """Register a new agricultural field."""
    existing = db.query(Field).filter(Field.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Field with ID '{data.id}' already exists.")

    new_field = Field(
        id=data.id,
        name=data.name,
        crop_type=data.crop_type.lower(),
        growth_stage=data.growth_stage.lower(),
        soil_type=data.soil_type,
        area_acres=data.area_acres,
        location=data.location,
        target_moisture_min=data.target_moisture_min,
        target_moisture_max=data.target_moisture_max,
        is_active=True
    )
    db.add(new_field)
    db.commit()
    db.refresh(new_field)

    # Add an initial baseline sensor reading
    init_sensor = SensorReading(
        field_id=new_field.id,
        timestamp=datetime.utcnow(),
        soil_moisture_pct=36.0,
        temperature_c=25.0,
        humidity_pct=60.0,
        rainfall_mm=0.0,
        wind_speed_mps=1.8,
        solar_radiation_wm2=480.0,
        is_simulated=True
    )
    db.add(init_sensor)
    db.commit()

    return enrich_field_detail(new_field, db)


@router.get("/{field_id}", response_model=FieldDetailResponse)
def get_field(field_id: str, db: Session = Depends(get_db)):
    """Retrieve single field detail."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field '{field_id}' not found.")
    return enrich_field_detail(field, db)


@router.put("/{field_id}", response_model=FieldDetailResponse)
def update_field(field_id: str, data: FieldUpdate, db: Session = Depends(get_db)):
    """Update field metadata."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field '{field_id}' not found.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(field, key, value)

    db.commit()
    db.refresh(field)
    return enrich_field_detail(field, db)


@router.delete("/{field_id}")
def delete_field(field_id: str, db: Session = Depends(get_db)):
    """Delete a field with cascading cleanup."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field '{field_id}' not found.")

    db.delete(field)
    db.commit()
    return {"status": "success", "message": f"Field '{field_id}' deleted successfully."}


@router.get("/{field_id}/sensors/current", response_model=SensorReadingResponse)
def get_current_sensors(field_id: str, db: Session = Depends(get_db)):
    """Get the latest sensor telemetry for a field."""
    reading = db.query(SensorReading).filter(
        SensorReading.field_id == field_id
    ).order_by(SensorReading.timestamp.desc()).first()

    if not reading:
        raise HTTPException(status_code=404, detail="No sensor readings found for this field.")
    return reading


@router.get("/{field_id}/sensors/history", response_model=List[SensorReadingResponse])
def get_sensor_history(
    field_id: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get historical time-series sensor data for Recharts trends."""
    start_time = datetime.utcnow() - timedelta(days=days)
    readings = db.query(SensorReading).filter(
        SensorReading.field_id == field_id,
        SensorReading.timestamp >= start_time
    ).order_by(SensorReading.timestamp.asc()).all()

    return readings


@router.post("/{field_id}/sensors/reading", response_model=SensorReadingResponse, status_code=201)
def add_sensor_reading(field_id: str, data: SensorReadingCreate, db: Session = Depends(get_db)):
    """Record a new sensor telemetry reading (IoT or simulated)."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field '{field_id}' not found.")

    new_reading = SensorReading(
        field_id=field_id,
        timestamp=datetime.utcnow(),
        soil_moisture_pct=data.soil_moisture_pct,
        temperature_c=data.temperature_c,
        humidity_pct=data.humidity_pct,
        rainfall_mm=data.rainfall_mm,
        wind_speed_mps=data.wind_speed_mps,
        solar_radiation_wm2=data.solar_radiation_wm2,
        is_simulated=data.is_simulated
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)
    return new_reading


@router.get("/{field_id}/weather")
def get_field_weather(field_id: str, db: Session = Depends(get_db)):
    """Get current weather and 24h forecast conditions for field location."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")

    latest = db.query(SensorReading).filter(
        SensorReading.field_id == field_id
    ).order_by(SensorReading.timestamp.desc()).first()

    temp = latest.temperature_c if latest else 26.5
    humidity = latest.humidity_pct if latest else 58.0
    rain = latest.rainfall_mm if latest else 0.0

    return {
        "field_id": field_id,
        "temperature_c": round(temp, 1),
        "humidity_pct": round(humidity, 1),
        "rainfall_mm": round(rain, 1),
        "condition": "Sunny" if rain == 0 and temp > 24 else ("Rainy" if rain > 0 else "Partly Cloudy"),
        "wind_speed_mps": round(latest.wind_speed_mps, 1) if latest else 2.1,
        "solar_radiation_wm2": round(latest.solar_radiation_wm2, 1) if latest else 480.0,
        "forecast_24h": {
            "expected_rain_mm": 0.0,
            "max_temp_c": round(temp + 3.0, 1),
            "min_temp_c": round(temp - 4.0, 1),
            "evapotranspiration_risk": "Moderate" if temp > 28 else "Low"
        }
    }
