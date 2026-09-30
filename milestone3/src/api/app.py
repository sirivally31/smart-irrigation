from pathlib import Path
from datetime import datetime, timedelta
import json
import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from src.features import prepare
from src.db.database import init_db
from src.api.routers import (
    fields, recommendations, history, alerts, notifications, ai, reports, farmer
)

app = FastAPI(
    title="Irrigation Scheduling Engine & Farmer Assistant API",
    version="2.0.0",
    description="Intelligent Smart Irrigation engine with ML inference, rule-based alerts, multilingual voice support, and farmer PWA endpoints."
)

# Configure CORS for Next.js PWA frontend
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in origins else origins + ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup hook to initialize SQLite database
@app.on_event("startup")
def on_startup():
    init_db()

# Load ML Models (Preserved from Milestone 2)
classifier = joblib.load(ROOT / "models" / "classifier_v1.joblib") if (ROOT / "models" / "classifier_v1.joblib").exists() else None
regressor = joblib.load(ROOT / "models" / "regressor_v1.joblib") if (ROOT / "models" / "regressor_v1.joblib").exists() else None
feature_columns = json.loads((ROOT / "models" / "feature_columns.json").read_text()) if (ROOT / "models" / "feature_columns.json").exists() else []

class FieldInput(BaseModel):
    field_id: str = "north"
    crop_type: str = "tomato"
    growth_stage: str = "vegetative"
    soil_moisture_pct: float = Field(..., ge=0, le=100)
    temperature_c: float = Field(25, ge=-20, le=60)
    humidity_pct: float = Field(60, ge=0, le=100)
    rainfall_mm: float = Field(0, ge=0)
    wind_speed_mps: float = Field(2, ge=0)
    solar_radiation_wm2: float = Field(500, ge=0)
    days_since_irrigation: int = Field(2, ge=0)
    forecast_rainfall_mm: float = Field(0, ge=0)
    previous_irrigation_liters: float = Field(0, ge=0)


def predict(data: FieldInput) -> dict:
    if classifier is None or regressor is None:
        raise HTTPException(503, "Models are not trained. Run python -m src.pipeline first.")
    values = data.model_dump()
    values["timestamp"] = datetime.utcnow()
    values["rainfall_mm"] += values.pop("forecast_rainfall_mm")
    values["water_quantity_liters"] = values.pop("previous_irrigation_liters")
    values["irrigation_needed"] = 0
    prepared, _ = prepare(pd.DataFrame([values]))
    x = prepared.reindex(columns=feature_columns, fill_value=0)
    needed = int(classifier.predict(x)[0])
    quantity = max(0.0, float(regressor.predict(x)[0])) if needed else 0.0
    # Business guardrail: rain and saturated soil suppress watering; cap a single event.
    if data.forecast_rainfall_mm >= 5 or data.soil_moisture_pct >= 75:
        needed, quantity = 0, 0.0
    quantity = min(quantity, 30.0)
    return {
        "field_id": data.field_id,
        "irrigation_needed": bool(needed),
        "water_quantity_liters": round(quantity, 2),
        "duration_minutes": round(quantity / 2, 1),
        "reason": "soil deficit and weather demand" if needed else "rain/saturation or adequate moisture",
        "generated_at": datetime.utcnow().isoformat()
    }

# Preserved Milestone 2 Core Endpoints
@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": classifier is not None and regressor is not None}

@app.post("/predict")
def prediction(data: FieldInput):
    return predict(data)

@app.post("/schedule")
def schedule(data: FieldInput):
    result = predict(data)
    result["recommended_start"] = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).isoformat()
    result["frequency_guardrail"] = "no more than one event per 12 hours"
    schedule_file = ROOT / "data" / "schedules.jsonl"
    with schedule_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result) + "\n")
    return result

# Mount Milestone 3 Modular Routers
app.include_router(fields.router)
app.include_router(recommendations.router)
app.include_router(history.router)
app.include_router(alerts.router)
app.include_router(notifications.router)
app.include_router(ai.router)
app.include_router(reports.router)
app.include_router(farmer.router)
