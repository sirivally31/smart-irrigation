from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SensorReadingCreate(BaseModel):
    sensor_id: int = Field(gt=0)
    field_id: int = Field(gt=0)
    soil_moisture: float = Field(ge=0, le=100)
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        normalized = value.astimezone(timezone.utc)
        if normalized > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("timestamp cannot be in the future")
        return normalized


class SensorReadingResponse(SensorReadingCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = "stored"