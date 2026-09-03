from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Field, Sensor, SensorReading
from app.schemas.readings import SensorReadingCreate, SensorReadingResponse

router = APIRouter(prefix="/api/v1/sensors", tags=["sensor readings"])


@router.post("/readings", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
def create_reading(payload: SensorReadingCreate, db: Session = Depends(get_db)) -> SensorReading:
    sensor = db.get(Sensor, payload.sensor_id)
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    field = db.get(Field, payload.field_id)
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    if sensor.field_id != field.id:
        raise HTTPException(status_code=400, detail="Sensor does not belong to field")
    duplicate = db.scalar(
        select(SensorReading).where(
            SensorReading.sensor_id == payload.sensor_id,
            SensorReading.timestamp == payload.timestamp,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="A reading already exists for this sensor and timestamp")

    reading = SensorReading(**payload.model_dump())
    db.add(reading)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="A reading already exists for this sensor and timestamp") from error
    db.refresh(reading)
    return reading


@router.get("/readings", response_model=list[SensorReadingResponse])
def list_readings(
    limit: int = Query(default=100, ge=1, le=500), sensor_id: int | None = Query(default=None, gt=0), field_id: int | None = Query(default=None, gt=0), db: Session = Depends(get_db)
) -> list[SensorReading]:
    statement = select(SensorReading).order_by(SensorReading.timestamp.desc()).limit(limit)
    if sensor_id is not None:
        statement = statement.where(SensorReading.sensor_id == sensor_id)
    if field_id is not None:
        statement = statement.where(SensorReading.field_id == field_id)
    return list(db.scalars(statement))