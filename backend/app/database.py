from collections.abc import Generator
from datetime import date

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    from app.models.entities import Crop, Farmer, Field, Sensor

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        for statement in (
            "ALTER TABLE fields ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION",
            "ALTER TABLE fields ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION",
            "ALTER TABLE fields ADD COLUMN IF NOT EXISTS size_hectares DOUBLE PRECISION",
            "ALTER TABLE crops ADD COLUMN IF NOT EXISTS growth_stage VARCHAR(120)",
            "ALTER TABLE sensors ADD COLUMN IF NOT EXISTS sensor_type VARCHAR(80) NOT NULL DEFAULT 'soil_moisture'",
            "ALTER TABLE sensors ADD COLUMN IF NOT EXISTS status VARCHAR(40) NOT NULL DEFAULT 'active'",
            "ALTER TABLE sensors ADD COLUMN IF NOT EXISTS installed_at TIMESTAMPTZ",
            "ALTER TABLE weather_data ADD COLUMN IF NOT EXISTS humidity DOUBLE PRECISION",
            "ALTER TABLE weather_data ADD COLUMN IF NOT EXISTS rain_probability DOUBLE PRECISION",
            "ALTER TABLE weather_data ADD COLUMN IF NOT EXISTS forecast JSONB DEFAULT '[]'",
            "ALTER TABLE irrigation_history ADD COLUMN IF NOT EXISTS action VARCHAR(80) NOT NULL DEFAULT 'manual'",
        ):
            connection.execute(text(statement))
    with SessionLocal.begin() as db:
        farmer = db.scalar(select(Farmer).where(Farmer.email == "demo@irrigation.local"))
        if farmer is None:
            farmer = Farmer(name="Demo Farmer", email="demo@irrigation.local")
            db.add(farmer)
            db.flush()

        field = db.scalar(select(Field).where(Field.name == "Demo Field"))
        if field is None:
            field = Field(name="Demo Field", location="Demo Farm", latitude=17.3850, longitude=78.4867, size_hectares=1.0, farmer_id=farmer.id)
            db.add(field)
            db.flush()

        crop = db.scalar(select(Crop).where(Crop.name == "Demo Crop", Crop.field_id == field.id))
        if crop is None:
            db.add(Crop(name="Demo Crop", field_id=field.id, planting_date=date(2026, 8, 1)))

        sensor = db.scalar(select(Sensor).where(Sensor.serial_number == "DEMO-SENSOR-001"))
        if sensor is None:
            db.add(Sensor(serial_number="DEMO-SENSOR-001", name="Demo Soil Sensor", field_id=field.id))