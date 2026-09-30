from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Ramesh Patel")
    phone = Column(String(20), nullable=False, default="+91 9876543210")
    email = Column(String(100), nullable=False, default="ramesh.farmer@smartirrigation.local")
    location = Column(String(150), nullable=False, default="Dharwad, Karnataka, India")
    preferred_language = Column(String(10), nullable=False, default="en")  # 'en', 'hi', 'kn'
    created_at = Column(DateTime, default=datetime.utcnow)

    fields = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")
    preferences = relationship("NotificationPreference", back_populates="farmer", uselist=False, cascade="all, delete-orphan")
    push_subscriptions = relationship("PushSubscription", back_populates="farmer", cascade="all, delete-orphan")


class Field(Base):
    __tablename__ = "fields"

    id = Column(String(50), primary_key=True, index=True)  # 'north', 'west', 'east', 'south'
    farmer_id = Column(Integer, ForeignKey("farmers.id"), default=1)
    name = Column(String(100), nullable=False)
    crop_type = Column(String(50), nullable=False)  # 'tomato', 'lettuce', 'cotton', 'maize'
    growth_stage = Column(String(50), nullable=False, default="vegetative")  # 'emergence', 'vegetative', 'flowering', 'maturity'
    soil_type = Column(String(50), nullable=False, default="loam")
    area_acres = Column(Float, nullable=False, default=2.5)
    location = Column(String(150), default="Sector A - Main Farm")
    target_moisture_min = Column(Float, default=35.0)
    target_moisture_max = Column(Float, default=70.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="fields")
    sensor_readings = relationship("SensorReading", back_populates="field", cascade="all, delete-orphan")
    schedules = relationship("IrrigationSchedule", back_populates="field", cascade="all, delete-orphan")
    records = relationship("IrrigationRecord", back_populates="field", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="field", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey("fields.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    soil_moisture_pct = Column(Float, nullable=False, default=40.0)
    temperature_c = Column(Float, nullable=False, default=25.0)
    humidity_pct = Column(Float, nullable=False, default=60.0)
    rainfall_mm = Column(Float, nullable=False, default=0.0)
    wind_speed_mps = Column(Float, nullable=False, default=1.5)
    solar_radiation_wm2 = Column(Float, nullable=False, default=450.0)
    is_simulated = Column(Boolean, default=False)

    field = relationship("Field", back_populates="sensor_readings")


class IrrigationSchedule(Base):
    __tablename__ = "irrigation_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey("fields.id"), nullable=False, index=True)
    schedule_date = Column(Date, nullable=False, default=date.today)
    recommended_start = Column(DateTime, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    water_quantity_liters = Column(Float, nullable=False)
    status = Column(String(30), default="scheduled")  # 'scheduled', 'completed', 'skipped'
    reason = Column(String(255), default="ML model calculated soil moisture deficit")
    ml_recommendation_needed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    field = relationship("Field", back_populates="schedules")


class IrrigationRecord(Base):
    __tablename__ = "irrigation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey("fields.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    duration_minutes = Column(Float, nullable=False)
    water_quantity_liters = Column(Float, nullable=False)
    status = Column(String(30), default="completed")  # 'completed', 'manual', 'cancelled'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    field = relationship("Field", back_populates="records")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey("fields.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # 'low_moisture', 'over_watering', 'heavy_rain', 'reminder', 'sensor_failure', 'stale_data', 'ml_deficit'
    severity = Column(String(20), nullable=False, default="warning")  # 'critical', 'warning', 'info'
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=True)
    status = Column(String(20), default="unread")  # 'unread', 'read', 'dismissed'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    field = relationship("Field", back_populates="alerts")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), unique=True)
    enable_push = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=True)
    enable_email = Column(Boolean, default=True)
    enable_weather_alerts = Column(Boolean, default=True)
    enable_moisture_alerts = Column(Boolean, default=True)
    enable_reminders = Column(Boolean, default=True)
    quiet_hours_start = Column(String(10), default="22:00")
    quiet_hours_end = Column(String(10), default="06:00")
    low_moisture_threshold = Column(Float, default=30.0)
    high_rain_threshold = Column(Float, default=15.0)

    farmer = relationship("Farmer", back_populates="preferences")


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), default=1)
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="push_subscriptions")
