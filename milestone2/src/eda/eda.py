from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
ROOT = Path(__file__).resolve().parents[2]

def run():
    frame = pd.read_csv(ROOT / "data" / "raw_irrigation.csv")
    output = ROOT / "reports" / "eda.png"
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    sns.histplot(frame["soil_moisture_pct"], ax=axes[0, 0]); axes[0, 0].set_title("Soil moisture")
    sns.scatterplot(data=frame.sample(min(1500, len(frame)), random_state=1), x="temperature_c", y="rainfall_mm", hue="crop_type", ax=axes[0, 1])
    sns.boxplot(data=frame, x="crop_type", y="water_quantity_liters", ax=axes[1, 0])
    sns.countplot(data=frame, x="irrigation_needed", hue="growth_stage", ax=axes[1, 1])
    fig.tight_layout(); fig.savefig(output, dpi=140); plt.close(fig)
    print(output)
if __name__ == "__main__": run()
