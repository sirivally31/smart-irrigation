from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NUMERIC = ["soil_moisture_pct", "temperature_c", "humidity_pct", "rainfall_mm", "wind_speed_mps", "solar_radiation_wm2", "days_since_irrigation"]
CATEGORICAL = ["field_id", "crop_type", "growth_stage"]
TARGETS = ["irrigation_needed", "water_quantity_liters"]


def prepare(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    frame = raw.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    frame = frame.dropna(subset=["timestamp"]).drop_duplicates().sort_values("timestamp").reset_index(drop=True)
    frame["rainfall_mm"] = frame["rainfall_mm"].clip(lower=0)
    frame["soil_moisture_pct"] = frame["soil_moisture_pct"].clip(0, 100)
    frame["humidity_pct"] = frame["humidity_pct"].clip(0, 100)
    frame["temperature_c"] = frame["temperature_c"].clip(-20, 60)
    for column in NUMERIC:
        frame[column] = frame[column].fillna(frame[column].median())
    frame["soil_moisture_rolling_6h"] = frame.groupby("field_id")["soil_moisture_pct"].transform(lambda s: s.rolling(6, min_periods=1).mean())
    frame["soil_moisture_deficit"] = (frame["soil_moisture_rolling_6h"] - 42).clip(upper=0).abs()
    frame["et0_proxy"] = (0.0023 * (frame["temperature_c"] + 17.8) * (frame["temperature_c"] - frame["humidity_pct"] / 10).clip(lower=0) + .05 * frame["wind_speed_mps"]).clip(lower=0)
    frame["rainfall_24h"] = frame.groupby("field_id")["rainfall_mm"].transform(lambda s: s.rolling(24, min_periods=1).sum())
    frame["cumulative_irrigation_7d"] = frame.groupby("field_id")["water_quantity_liters"].transform(lambda s: s.shift(1).rolling(168, min_periods=1).sum()).fillna(0)
    frame["hour"] = frame.timestamp.dt.hour
    frame["day_of_year"] = frame.timestamp.dt.dayofyear
    frame["growth_stage_bucket"] = frame["growth_stage"].map({"emergence": "early", "vegetative": "mid", "flowering": "peak", "maturity": "late"}).fillna("mid")
    frame = pd.get_dummies(frame, columns=CATEGORICAL + ["growth_stage_bucket"], dtype=int)
    frame = frame.drop(columns=["timestamp"])
    metadata = {"numeric": NUMERIC + ["soil_moisture_rolling_6h", "soil_moisture_deficit", "et0_proxy", "rainfall_24h", "cumulative_irrigation_7d", "hour", "day_of_year"], "target_class": TARGETS[0], "target_reg": TARGETS[1]}
    return frame, metadata


def run() -> None:
    raw = pd.read_csv(ROOT / "data" / "raw_irrigation.csv")
    processed, metadata = prepare(raw)
    processed.to_csv(ROOT / "data" / "processed_irrigation.csv", index=False)
    (ROOT / "data" / "feature_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Prepared {len(processed)} rows and {len(processed.columns)} columns")


if __name__ == "__main__":
    run()
