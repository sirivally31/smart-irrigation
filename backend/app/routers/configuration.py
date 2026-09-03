from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Crop, Farmer, Field, Sensor
from app.schemas.configuration import CropCreate, CropResponse, FarmerCreate, FarmerResponse, FieldCreate, FieldResponse, SensorCreate, SensorResponse

router = APIRouter(prefix="/api/v1", tags=["configuration"])


@router.post("/farmers", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db)) -> Farmer:
    farmer = Farmer(**payload.model_dump())
    db.add(farmer)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Farmer email already exists") from error
    db.refresh(farmer)
    return farmer


@router.get("/farmers", response_model=list[FarmerResponse])
def list_farmers(db: Session = Depends(get_db)) -> list[Farmer]:
    return list(db.scalars(select(Farmer).order_by(Farmer.id)))


@router.post("/fields", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(payload: FieldCreate, db: Session = Depends(get_db)) -> Field:
    if db.get(Farmer, payload.farmer_id) is None:
        raise HTTPException(status_code=404, detail="Farmer not found")
    field = Field(**payload.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


@router.get("/fields", response_model=list[FieldResponse])
def list_fields(db: Session = Depends(get_db)) -> list[Field]:
    return list(db.scalars(select(Field).order_by(Field.id)))


@router.get("/fields/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)) -> Field:
    field = db.get(Field, field_id)
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


@router.post("/fields/{field_id}/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(field_id: int, payload: CropCreate, db: Session = Depends(get_db)) -> Crop:
    if db.get(Field, field_id) is None:
        raise HTTPException(status_code=404, detail="Field not found")
    crop = Crop(field_id=field_id, **payload.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("/fields/{field_id}/crops", response_model=list[CropResponse])
def list_crops(field_id: int, db: Session = Depends(get_db)) -> list[Crop]:
    if db.get(Field, field_id) is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return list(db.scalars(select(Crop).where(Crop.field_id == field_id).order_by(Crop.id)))


@router.post("/fields/{field_id}/sensors", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def create_sensor(field_id: int, payload: SensorCreate, db: Session = Depends(get_db)) -> Sensor:
    if db.get(Field, field_id) is None:
        raise HTTPException(status_code=404, detail="Field not found")
    sensor = Sensor(field_id=field_id, **payload.model_dump())
    db.add(sensor)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Sensor serial number already exists") from error
    db.refresh(sensor)
    return sensor


@router.get("/fields/{field_id}/sensors", response_model=list[SensorResponse])
def list_sensors(field_id: int, db: Session = Depends(get_db)) -> list[Sensor]:
    if db.get(Field, field_id) is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return list(db.scalars(select(Sensor).where(Sensor.field_id == field_id).order_by(Sensor.id)))