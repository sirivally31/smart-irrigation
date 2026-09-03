from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FarmerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str | None = None


class FarmerResponse(FarmerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class FieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    farmer_id: int = Field(gt=0)
    location: str | None = Field(default=None, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    size_hectares: float | None = Field(default=None, gt=0)


class FieldResponse(FieldCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class CropCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    planting_date: date | None = None
    growth_stage: str | None = Field(default=None, max_length=120)


class CropResponse(CropCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    field_id: int


class SensorCreate(BaseModel):
    serial_number: str = Field(min_length=1, max_length=120)
    name: str | None = Field(default=None, max_length=120)
    sensor_type: str = Field(default="soil_moisture", max_length=80)
    status: str = Field(default="active", max_length=40)
    installed_at: datetime | None = None


class SensorResponse(SensorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    field_id: int
    created_at: datetime