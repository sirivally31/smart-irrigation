from pathlib import Path
from datetime import datetime, timedelta
import json
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from src.features import prepare
from src.db.models import Field, SensorReading, IrrigationRecord

ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "models"

CLASSIFIER_PATH = MODELS_DIR / "classifier_v1.joblib"
REGRESSOR_PATH = MODELS_DIR / "regressor_v1.joblib"
FEATURE_COLS_PATH = MODELS_DIR / "feature_columns.json"

classifier = joblib.load(CLASSIFIER_PATH) if CLASSIFIER_PATH.exists() else None
regressor = joblib.load(REGRESSOR_PATH) if REGRESSOR_PATH.exists() else None
feature_columns = json.loads(FEATURE_COLS_PATH.read_text()) if FEATURE_COLS_PATH.exists() else []


def predict_raw(
    field_id: str,
    crop_type: str,
    growth_stage: str,
    soil_moisture_pct: float,
    temperature_c: float = 25.0,
    humidity_pct: float = 60.0,
    rainfall_mm: float = 0.0,
    wind_speed_mps: float = 2.0,
    solar_radiation_wm2: float = 500.0,
    days_since_irrigation: int = 2,
    forecast_rainfall_mm: float = 0.0,
    previous_irrigation_liters: float = 0.0
) -> dict:
    """Core prediction function preserving the exact Milestone 2 preprocessing and guardrails."""
    if classifier is None or regressor is None:
        raise RuntimeError("ML models are not loaded. Ensure classifier_v1.joblib and regressor_v1.joblib exist.")

    values = {
        "field_id": field_id,
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "soil_moisture_pct": soil_moisture_pct,
        "temperature_c": temperature_c,
        "humidity_pct": humidity_pct,
        "rainfall_mm": rainfall_mm + forecast_rainfall_mm,
        "wind_speed_mps": wind_speed_mps,
        "solar_radiation_wm2": solar_radiation_wm2,
        "days_since_irrigation": days_since_irrigation,
        "water_quantity_liters": previous_irrigation_liters,
        "irrigation_needed": 0,
        "timestamp": datetime.utcnow()
    }

    prepared, _ = prepare(pd.DataFrame([values]))
    x = prepared.reindex(columns=feature_columns, fill_value=0)
    needed = int(classifier.predict(x)[0])
    quantity = max(0.0, float(regressor.predict(x)[0])) if needed else 0.0

    # Business guardrails: rain and saturated soil suppress watering; cap a single event.
    if forecast_rainfall_mm >= 5.0 or soil_moisture_pct >= 75.0:
        needed, quantity = 0, 0.0
    quantity = min(quantity, 30.0)

    # Explanation reason
    if needed:
        reason = f"Soil moisture ({round(soil_moisture_pct, 1)}%) below target; crop demand for {crop_type} ({growth_stage})"
    else:
        if forecast_rainfall_mm >= 5.0:
            reason = f"Irrigation suppressed: Forecast rain of {forecast_rainfall_mm}mm expected"
        elif soil_moisture_pct >= 75.0:
            reason = f"Irrigation suppressed: Soil is saturated at {round(soil_moisture_pct, 1)}%"
        else:
            reason = "Adequate soil moisture and low current evapotranspiration demand"

    duration = round(quantity / 2.0, 1)
    return {
        "field_id": field_id,
        "irrigation_needed": bool(needed),
        "water_quantity_liters": round(quantity, 2),
        "duration_minutes": duration,
        "reason": reason,
        "generated_at": datetime.utcnow().isoformat()
    }


def predict_for_field(db: Session, field_id: str) -> dict:
    """Look up field metadata and the most recent sensor reading from the database, then run prediction."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ValueError(f"Field '{field_id}' not found.")

    latest_reading = db.query(SensorReading).filter(
        SensorReading.field_id == field_id
    ).order_by(SensorReading.timestamp.desc()).first()

    # Calculate days since last irrigation
    last_record = db.query(IrrigationRecord).filter(
        IrrigationRecord.field_id == field_id
    ).order_by(IrrigationRecord.timestamp.desc()).first()

    days_since = 2
    previous_liters = 0.0
    if last_record:
        delta = datetime.utcnow() - last_record.timestamp
        days_since = max(0, delta.days)
        previous_liters = last_record.water_quantity_liters

    # Fallback sensor values if no readings exist
    moisture = latest_reading.soil_moisture_pct if latest_reading else 32.0
    temp = latest_reading.temperature_c if latest_reading else 25.0
    humidity = latest_reading.humidity_pct if latest_reading else 60.0
    rain = latest_reading.rainfall_mm if latest_reading else 0.0
    wind = latest_reading.wind_speed_mps if latest_reading else 2.0
    solar = latest_reading.solar_radiation_wm2 if latest_reading else 480.0

    return predict_raw(
        field_id=field.id,
        crop_type=field.crop_type,
        growth_stage=field.growth_stage,
        soil_moisture_pct=moisture,
        temperature_c=temp,
        humidity_pct=humidity,
        rainfall_mm=rain,
        wind_speed_mps=wind,
        solar_radiation_wm2=solar,
        days_since_irrigation=days_since,
        forecast_rainfall_mm=0.0,
        previous_irrigation_liters=previous_liters
    )
