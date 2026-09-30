from src.generate_data import generate_dataset
from src.features import run as prepare_features
from src.models.train import train

if __name__ == "__main__":
    print("Phase 1: generating and preparing data")
    generate_dataset()
    prepare_features()
    print("Phase 2: training and evaluating models")
    train()
    print("Pipeline complete: artifacts are in data/, models/, reports/, and mlruns/.")
