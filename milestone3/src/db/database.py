from pathlib import Path
from datetime import datetime, date, timedelta
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.db.models import Base, Farmer, Field, SensorReading, IrrigationSchedule, IrrigationRecord, Alert, NotificationPreference

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "irrigation.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

# Ensure SQLite handles multi-threaded access in FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables and seed initial data if database is empty."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Check if farmer exists
        farmer = db.query(Farmer).first()
        if not farmer:
            farmer = Farmer(
                id=1,
                name="Ramesh Patel",
                phone="+91 9876543210",
                email="ramesh.patel@smartirrigation.local",
                location="Dharwad, Karnataka, India",
                preferred_language="en"
            )
            db.add(farmer)
            db.commit()
            db.refresh(farmer)

            # Default preferences
            prefs = NotificationPreference(
                farmer_id=farmer.id,
                enable_push=True,
                enable_sms=True,
                enable_email=True,
                enable_weather_alerts=True,
                enable_moisture_alerts=True,
                enable_reminders=True,
                quiet_hours_start="22:00",
                quiet_hours_end="06:00",
                low_moisture_threshold=30.0,
                high_rain_threshold=15.0
            )
            db.add(prefs)
            db.commit()

        # Seed standard fields from Milestone 2
        existing_fields = {f.id for f in db.query(Field).all()}
        default_fields = [
            Field(
                id="north",
                farmer_id=1,
                name="North Plot - Tomato",
                crop_type="tomato",
                growth_stage="vegetative",
                soil_type="loam",
                area_acres=2.5,
                location="North Sector, Block A",
                target_moisture_min=40.0,
                target_moisture_max=75.0,
                is_active=True
            ),
            Field(
                id="west",
                farmer_id=1,
                name="West Plot - Lettuce",
                crop_type="lettuce",
                growth_stage="flowering",
                soil_type="sandy loam",
                area_acres=1.8,
                location="West Valley Terrace",
                target_moisture_min=50.0,
                target_moisture_max=80.0,
                is_active=True
            ),
            Field(
                id="east",
                farmer_id=1,
                name="East Plot - Cotton",
                crop_type="cotton",
                growth_stage="vegetative",
                soil_type="black cotton soil",
                area_acres=4.0,
                location="East Plateau",
                target_moisture_min=30.0,
                target_moisture_max=65.0,
                is_active=True
            ),
            Field(
                id="south",
                farmer_id=1,
                name="South Plot - Maize",
                crop_type="maize",
                growth_stage="maturity",
                soil_type="clay loam",
                area_acres=3.2,
                location="South Basin",
                target_moisture_min=35.0,
                target_moisture_max=70.0,
                is_active=True
            )
        ]

        for f in default_fields:
            if f.id not in existing_fields:
                db.add(f)
        db.commit()

        # Seed sensor readings from raw_irrigation.csv if sensor_readings table is empty
        sensor_count = db.query(SensorReading).count()
        raw_csv = DATA_DIR / "raw_irrigation.csv"
        if sensor_count == 0 and raw_csv.exists():
            df = pd.read_csv(raw_csv)
            # Fill numeric NaNs with medians or defaults
            for col, default_val in [
                ("soil_moisture_pct", 40.0),
                ("temperature_c", 25.0),
                ("humidity_pct", 60.0),
                ("rainfall_mm", 0.0),
                ("wind_speed_mps", 1.5),
                ("solar_radiation_wm2", 450.0)
            ]:
                if col in df.columns:
                    med = df[col].median()
                    df[col] = df[col].fillna(med if pd.notna(med) else default_val)

            readings = []
            for field_id in ["north", "west", "east", "south"]:
                field_df = df[df["field_id"] == field_id].tail(96)  # last 4 days of hourly data
                for _, row in field_df.iterrows():
                    ts = pd.to_datetime(row["timestamp"])
                    readings.append(SensorReading(
                        field_id=field_id,
                        timestamp=ts.to_pydatetime() if hasattr(ts, 'to_pydatetime') else datetime.fromisoformat(str(ts)),
                        soil_moisture_pct=float(row["soil_moisture_pct"]) if pd.notna(row["soil_moisture_pct"]) else 40.0,
                        temperature_c=float(row["temperature_c"]) if pd.notna(row["temperature_c"]) else 25.0,
                        humidity_pct=float(row["humidity_pct"]) if pd.notna(row["humidity_pct"]) else 60.0,
                        rainfall_mm=float(row["rainfall_mm"]) if pd.notna(row["rainfall_mm"]) else 0.0,
                        wind_speed_mps=float(row["wind_speed_mps"]) if pd.notna(row["wind_speed_mps"]) else 1.5,
                        solar_radiation_wm2=float(row["solar_radiation_wm2"]) if pd.notna(row["solar_radiation_wm2"]) else 450.0,
                        is_simulated=False
                    ))
            db.bulk_save_objects(readings)
            db.commit()

        # Seed initial Today's Schedule if none exist
        today = date.today()
        sched_count = db.query(IrrigationSchedule).filter(IrrigationSchedule.schedule_date == today).count()
        if sched_count == 0:
            schedules = [
                IrrigationSchedule(
                    field_id="north",
                    schedule_date=today,
                    recommended_start=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=0),
                    duration_minutes=15.0,
                    water_quantity_liters=30.0,
                    status="scheduled",
                    reason="Soil moisture (28%) is below optimal threshold (40%) for vegetative tomato",
                    ml_recommendation_needed=True
                ),
                IrrigationSchedule(
                    field_id="west",
                    schedule_date=today,
                    recommended_start=datetime.now().replace(hour=8, minute=30, second=0, microsecond=0),
                    duration_minutes=10.0,
                    water_quantity_liters=20.0,
                    status="scheduled",
                    reason="High evapotranspiration predicted; flowering stage water demand",
                    ml_recommendation_needed=True
                ),
                IrrigationSchedule(
                    field_id="east",
                    schedule_date=today,
                    recommended_start=datetime.now().replace(hour=17, minute=0, second=0, microsecond=0),
                    duration_minutes=0.0,
                    water_quantity_liters=0.0,
                    status="skipped",
                    reason="Rain forecast >= 5mm and adequate deep soil moisture (58%)",
                    ml_recommendation_needed=False
                )
            ]
            for s in schedules:
                db.add(s)
            db.commit()

        # Seed realistic past irrigation records if none exist
        records_count = db.query(IrrigationRecord).count()
        if records_count == 0:
            past_records = [
                IrrigationRecord(
                    field_id="north",
                    timestamp=datetime.now() - timedelta(days=2, hours=3),
                    duration_minutes=15.0,
                    water_quantity_liters=30.0,
                    status="completed",
                    notes="Automated drip cycle completed successfully"
                ),
                IrrigationRecord(
                    field_id="west",
                    timestamp=datetime.now() - timedelta(days=1, hours=5),
                    duration_minutes=12.0,
                    water_quantity_liters=24.0,
                    status="completed",
                    notes="Sprinkler irrigation executed"
                ),
                IrrigationRecord(
                    field_id="south",
                    timestamp=datetime.now() - timedelta(days=3, hours=8),
                    duration_minutes=20.0,
                    water_quantity_liters=40.0,
                    status="completed",
                    notes="Basin soak prior to maturity grain filling"
                )
            ]
            for r in past_records:
                db.add(r)
            db.commit()

        # Seed initial active alerts if none exist
        alert_count = db.query(Alert).count()
        if alert_count == 0:
            initial_alerts = [
                Alert(
                    field_id="north",
                    alert_type="low_moisture",
                    severity="critical",
                    title="Critical Soil Moisture Deficit",
                    message="Soil moisture in North Plot (Tomato) has dropped to 26.5%, below minimum threshold of 40%.",
                    suggested_action="Execute scheduled 15-minute drip irrigation cycle immediately.",
                    status="unread",
                    created_at=datetime.utcnow() - timedelta(hours=2)
                ),
                Alert(
                    field_id="west",
                    alert_type="ml_deficit",
                    severity="warning",
                    title="ML Predicted Water Demand",
                    message="ML model predicts moderate moisture deficit for flowering lettuce under current solar radiation.",
                    suggested_action="Review Today's Irrigation Schedule for 20 Liters watering window.",
                    status="unread",
                    created_at=datetime.utcnow() - timedelta(hours=5)
                )
            ]
            for a in initial_alerts:
                db.add(a)
            db.commit()

    finally:
        db.close()
