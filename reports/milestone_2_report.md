# Milestone 2 ML Evaluation and Implementation Report

## Scope and assumptions

This implementation uses 5,000 hourly synthetic observations across four fields, four crops, and four growth stages. Irrigation need is defined as soil moisture below a crop-adjusted threshold when effective rainfall is below 2 mm. Water quantity is a positive continuous recommendation in liters. A field is treated as over-watered when soil moisture is at least 75% or forecast rainfall is at least 5 mm.

## Phase 1

The generator creates realistic correlated temperature, humidity, radiation, rainfall, soil moisture, crop, stage, and irrigation-history variables. It intentionally inserts missing humidity values and one duplicate to exercise quality controls. Preparation removes duplicates, clips impossible bounded values, fills numeric gaps with medians, and applies chronological ordering. Features include six-hour soil moisture rolling mean, deficit from optimal moisture, ET0 proxy, 24-hour rainfall, seven-day cumulative irrigation, hour, day of year, one-hot crop/stage/field encodings, and days since irrigation.

The target variables are `irrigation_needed` (classification) and `water_quantity_liters` (regression). Chronological 70/15/15 train-validation-test splits avoid future leakage.

## Phase 2

Mean/majority baselines, Random Forest, and Gradient Boosting models are evaluated with accuracy, precision, recall, F1, ROC-AUC, RMSE, MAE, and R2. Randomized two-fold tuning selects the production Random Forest classifier and regressor, retrained on train plus validation. Artifacts are saved under `models/`; metrics are under `reports/metrics.json`; MLflow runs are stored under `mlruns/` when MLflow is installed.

TensorFlow is optional because the environment may not support it. `src/models/lstm.py` provides the explicit integration hook and reports a skipped status when TensorFlow is unavailable. The primary engine remains fully reproducible without it.

## API and deployment

FastAPI loads artifacts at import/startup. `/health` reports model readiness, `/predict` returns an immediate decision, and `/schedule` adds a time slot and persists JSONL schedule records. Inputs include forecast rainfall, crop type, growth stage, and previous irrigation quantity. Guardrails suppress events for substantial forecast rain or near-saturated soil and cap event volume.

## Limitations

Synthetic relationships are not a substitute for agronomist-reviewed field data. ET0 is a proxy rather than a reference evapotranspiration calculation. The schedule is a recommendation, not an automated valve command. Before production, calibrate thresholds and units by field, add sensor freshness checks, monitor drift, validate against yield and water-use outcomes, and require operational approval for actuation.
