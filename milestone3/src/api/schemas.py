from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

# --- Farmer Schemas ---
class FarmerProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=150)
    preferred_language: Optional[str] = Field(None, pattern="^(en|hi|kn)$")

class FarmerProfileResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    location: str
    preferred_language: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Field Schemas ---
class FieldCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    crop_type: str = Field("tomato")
    growth_stage: str = Field("vegetative")
    soil_type: str = Field("loam")
    area_acres: float = Field(2.5, ge=0.1, le=1000.0)
    location: Optional[str] = "Main Farm"
    target_moisture_min: float = Field(35.0, ge=10.0, le=90.0)
    target_moisture_max: float = Field(70.0, ge=20.0, le=95.0)

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    crop_type: Optional[str] = None
    growth_stage: Optional[str] = None
    soil_type: Optional[str] = None
    area_acres: Optional[float] = None
    location: Optional[str] = None
    target_moisture_min: Optional[float] = None
    target_moisture_max: Optional[float] = None
    is_active: Optional[bool] = None

class FieldDetailResponse(BaseModel):
    id: str
    name: str
    crop_type: str
    growth_stage: str
    soil_type: str
    area_acres: float
    location: Optional[str]
    target_moisture_min: float
    target_moisture_max: float
    is_active: bool
    created_at: datetime
    latest_soil_moisture: Optional[float] = None
    latest_temperature: Optional[float] = None
    latest_humidity: Optional[float] = None
    latest_rainfall: Optional[float] = None
    today_schedule_status: Optional[str] = None
    today_recommended_liters: Optional[float] = None
    today_recommended_time: Optional[str] = None
    today_reason: Optional[str] = None
    active_alerts_count: int = 0

    class Config:
        from_attributes = True

# --- Sensor Schemas ---
class SensorReadingCreate(BaseModel):
    field_id: str
    soil_moisture_pct: float = Field(..., ge=0.0, le=100.0)
    temperature_c: float = Field(25.0, ge=-20.0, le=60.0)
    humidity_pct: float = Field(60.0, ge=0.0, le=100.0)
    rainfall_mm: float = Field(0.0, ge=0.0)
    wind_speed_mps: float = Field(1.5, ge=0.0)
    solar_radiation_wm2: float = Field(450.0, ge=0.0)
    is_simulated: bool = False

class SensorReadingResponse(BaseModel):
    id: int
    field_id: str
    timestamp: datetime
    soil_moisture_pct: float
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float
    wind_speed_mps: float
    solar_radiation_wm2: float
    is_simulated: bool

    class Config:
        from_attributes = True

# --- Irrigation Schedule & Record Schemas ---
class ScheduleResponse(BaseModel):
    id: int
    field_id: str
    field_name: Optional[str] = None
    crop_type: Optional[str] = None
    schedule_date: date
    recommended_start: datetime
    duration_minutes: float
    water_quantity_liters: float
    status: str
    reason: str
    ml_recommendation_needed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ScheduleExecuteRequest(BaseModel):
    actual_duration_minutes: Optional[float] = Field(None, gt=0, le=1440)
    actual_water_liters: Optional[float] = Field(None, gt=0, le=100000)
    notes: Optional[str] = None

class IrrigationRecordCreate(BaseModel):
    field_id: str
    duration_minutes: float = Field(..., ge=1.0)
    water_quantity_liters: float = Field(..., ge=0.1)
    status: str = "completed"
    notes: Optional[str] = None

class IrrigationRecordResponse(BaseModel):
    id: int
    field_id: str
    field_name: Optional[str] = None
    timestamp: datetime
    duration_minutes: float
    water_quantity_liters: float
    status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Alert Schemas ---
class AlertResponse(BaseModel):
    id: int
    field_id: str
    field_name: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    suggested_action: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AlertStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(read|unread|dismissed)$")

# --- Notification Preferences Schemas ---
class NotificationPreferenceUpdate(BaseModel):
    enable_push: Optional[bool] = None
    enable_sms: Optional[bool] = None
    enable_email: Optional[bool] = None
    enable_weather_alerts: Optional[bool] = None
    enable_moisture_alerts: Optional[bool] = None
    enable_reminders: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    low_moisture_threshold: Optional[float] = None
    high_rain_threshold: Optional[float] = None

class NotificationPreferenceResponse(BaseModel):
    enable_push: bool
    enable_sms: bool
    enable_email: bool
    enable_weather_alerts: bool
    enable_moisture_alerts: bool
    enable_reminders: bool
    quiet_hours_start: str
    quiet_hours_end: str
    low_moisture_threshold: float
    high_rain_threshold: float

    class Config:
        from_attributes = True

class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # contains p256dh and auth

# --- AI & Voice Schemas ---
class AIExplainRequest(BaseModel):
    field_id: str
    language: str = Field("en", pattern="^(en|hi|kn)$")

class AIExplainResponse(BaseModel):
    field_id: str
    language: str
    headline: str
    explanation: str
    farmer_tip: str
    audio_available: bool = False
    source: str = "sarvam_ai"

class AIVoiceQueryRequest(BaseModel):
    query: str
    language: str = Field("en", pattern="^(en|hi|kn)$")
    field_id: Optional[str] = None

class AIVoiceQueryResponse(BaseModel):
    query: str
    language: str
    answer: str
    audio_base64: Optional[str] = None
    relevant_fields: List[str] = []
    source: str = "domain_agent"
