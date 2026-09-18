# Milestone 2: ML Irrigation Scheduling Engine

Complete synthetic-data implementation of an irrigation decision engine. Real CSV replacement is supported by placing a compatible file at `data/raw_irrigation.csv`.

## Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.pipeline
.\.venv\Scripts\python.exe -m src.eda.eda
```

The pipeline creates raw and processed data, metrics, MLflow file tracking, versioned joblib models, and EDA output. The split is chronological: 70% train, 15% validation, 15% test. Missing numeric values use training-compatible medians; invalid bounded values are clipped; duplicates are removed.

## API

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --reload
```

```powershell
curl -X POST http://127.0.0.1:8000/schedule -H "Content-Type: application/json" -d '{"field_id":"north","crop_type":"tomato","growth_stage":"flowering","soil_moisture_pct":28,"temperature_c":31,"humidity_pct":48,"rainfall_mm":0,"wind_speed_mps":3,"solar_radiation_wm2":700,"days_since_irrigation":3,"forecast_rainfall_mm":0,"previous_irrigation_liters":12}'
```

`/predict` returns need, quantity, duration, and reason. `/schedule` additionally writes a JSONL schedule record and applies guardrails: forecast rain >= 5 mm or soil moisture >= 75% suppresses watering, quantity is capped at 30 L, and the recommendation is no more than one event per 12 hours.

## Layout

- `data/`: raw, processed, feature metadata, generated schedules
- `src/features.py`: cleaning and feature engineering
- `src/models/train.py`: baseline, RF, GB, tuning, metrics, MLflow
- `src/models/lstm.py`: optional TensorFlow integration point
- `src/api/app.py`: FastAPI prediction and schedule endpoints
- `reports/`: metrics, EDA image, implementation report
- `models/`: selected versioned artifacts
