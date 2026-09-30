from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def generate_dataset(rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2024-01-01", periods=rows, freq="h")
    fields = rng.choice(["north", "south", "east", "west"], rows)
    crops = rng.choice(["tomato", "maize", "lettuce", "cotton"], rows, p=[.28, .27, .25, .20])
    stages = rng.choice(["emergence", "vegetative", "flowering", "maturity"], rows, p=[.12, .34, .32, .22])
    hour = timestamps.hour.to_numpy()
    day = timestamps.dayofyear.to_numpy()
    temperature = 24 + 8 * np.sin(2 * np.pi * (day - 80) / 365) + 4 * np.sin(2 * np.pi * (hour - 8) / 24) + rng.normal(0, 1.5, rows)
    humidity = np.clip(68 - 0.8 * (temperature - 22) + rng.normal(0, 7, rows), 20, 98)
    rainfall = np.where(rng.random(rows) < .12, rng.gamma(2, 3, rows), 0).round(2)
    wind = np.clip(rng.normal(2.4, 1.2, rows), 0, 9)
    radiation = np.clip(650 * np.maximum(0, np.sin(np.pi * (hour - 6) / 12)) + rng.normal(0, 35, rows), 0, 900)
    crop_factor = pd.Series(crops).map({"tomato": 1.0, "maize": 1.1, "lettuce": .75, "cotton": .95}).to_numpy()
    soil = np.clip(55 - .015 * np.arange(rows) - .6 * np.maximum(temperature - 24, 0) + rainfall * 1.8 + rng.normal(0, 5, rows), 8, 92)
    threshold = 38 + crop_factor * 4
    need = ((soil < threshold) & (rainfall < 2)).astype(int)
    quantity = np.clip((threshold - soil) * 1.6 + temperature * .35 + wind * 1.1 - rainfall * 2 + rng.normal(0, 1.5, rows), 0, 35) * need
    last_irrigation = np.where(need, rng.integers(1, 5, rows), rng.integers(0, 3, rows))
    frame = pd.DataFrame({"timestamp": timestamps, "field_id": fields, "crop_type": crops, "growth_stage": stages, "soil_moisture_pct": soil.round(2), "temperature_c": temperature.round(2), "humidity_pct": humidity.round(2), "rainfall_mm": rainfall, "wind_speed_mps": wind.round(2), "solar_radiation_wm2": radiation.round(2), "days_since_irrigation": last_irrigation, "irrigation_needed": need, "water_quantity_liters": quantity.round(2)})
    # Intentional dirty records exercise the cleaning pipeline.
    frame.loc[rng.choice(rows, 30, replace=False), "humidity_pct"] = np.nan
    frame = pd.concat([frame, frame.iloc[[10]]], ignore_index=True)
    frame.to_csv(ROOT / "data" / "raw_irrigation.csv", index=False)
    return frame


if __name__ == "__main__":
    print(generate_dataset().shape)
