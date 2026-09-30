from pathlib import Path
import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.dummy import DummyClassifier, DummyRegressor

ROOT = Path(__file__).resolve().parents[2]


def log_mlflow(metrics: dict, params: dict) -> None:
    try:
        import mlflow
        mlflow.set_tracking_uri(f"file:///{(ROOT / 'mlruns').as_posix()}")
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics({k: float(v) for k, v in metrics.items() if isinstance(v, (int, float)) and np.isfinite(v)})
    except Exception:
        pass


def train() -> dict:
    frame = pd.read_csv(ROOT / "data" / "processed_irrigation.csv")
    class_target, reg_target = "irrigation_needed", "water_quantity_liters"
    features = [c for c in frame.columns if c not in [class_target, reg_target]]
    split1, split2 = int(len(frame) * .70), int(len(frame) * .85)
    train, valid, test = frame.iloc[:split1], frame.iloc[split1:split2], frame.iloc[split2:]
    x_train, x_valid, x_test = train[features], valid[features], test[features]
    yct, ycv, ycs = train[class_target], valid[class_target], test[class_target]
    yrt, yrv, yrs = train[reg_target], valid[reg_target], test[reg_target]
    models = {
        "rf_classifier": RandomForestClassifier(n_estimators=180, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1),
        "gb_classifier": GradientBoostingClassifier(n_estimators=120, max_depth=3, random_state=42),
        "rf_regressor": RandomForestRegressor(n_estimators=180, max_depth=14, random_state=42, n_jobs=-1),
        "gb_regressor": GradientBoostingRegressor(n_estimators=120, max_depth=3, random_state=42),
    }
    baseline_c, baseline_r = DummyClassifier(strategy="most_frequent"), DummyRegressor(strategy="mean")
    baseline_c.fit(x_train, yct); baseline_r.fit(x_train, yrt)
    models["baseline_classifier"], models["baseline_regressor"] = baseline_c, baseline_r
    metrics = {}
    for name, model in models.items():
        if "classifier" in name:
            model.fit(x_train, yct)
            pred = model.predict(x_test)
            probability = model.predict_proba(x_test)[:, 1] if hasattr(model, "predict_proba") else pred
            metrics[name] = {"accuracy": accuracy_score(ycs, pred), "precision": precision_score(ycs, pred, zero_division=0), "recall": recall_score(ycs, pred, zero_division=0), "f1": f1_score(ycs, pred, zero_division=0), "roc_auc": roc_auc_score(ycs, probability)}
        else:
            model.fit(x_train, yrt)
            pred = np.maximum(0, model.predict(x_test))
            metrics[name] = {"rmse": mean_squared_error(yrs, pred) ** .5, "mae": mean_absolute_error(yrs, pred), "r2": r2_score(yrs, pred)}
    # Small time-respecting search on the strongest model families.
    search_c = RandomizedSearchCV(RandomForestClassifier(random_state=42, class_weight="balanced", n_jobs=-1), {"n_estimators": [120, 180], "max_depth": [8, 12, None]}, n_iter=3, cv=2, scoring="f1", random_state=42, n_jobs=-1)
    search_r = RandomizedSearchCV(RandomForestRegressor(random_state=42, n_jobs=-1), {"n_estimators": [120, 180], "max_depth": [10, 14, None]}, n_iter=3, cv=2, scoring="neg_mean_absolute_error", random_state=42, n_jobs=-1)
    search_c.fit(pd.concat([x_train, x_valid]), pd.concat([yct, ycv])); search_r.fit(pd.concat([x_train, x_valid]), pd.concat([yrt, yrv]))
    selected = {"classifier": search_c.best_estimator_, "regressor": search_r.best_estimator_}
    for key, model in selected.items(): joblib.dump(model, ROOT / "models" / f"{key}_v1.joblib")
    (ROOT / "models" / "feature_columns.json").write_text(json.dumps(features, indent=2))
    (ROOT / "models" / "model_metadata.json").write_text(json.dumps({"version": "v1", "best_params": {"classifier": search_c.best_params_, "regressor": search_r.best_params_}, "lstm": "optional/skipped unless TensorFlow installed"}, indent=2, default=str))
    (ROOT / "reports" / "metrics.json").write_text(json.dumps(metrics, indent=2, default=float))
    for name, values in metrics.items(): log_mlflow(values, {"model": name})
    print(json.dumps({"selected_classifier": search_c.best_params_, "selected_regressor": search_r.best_params_, "test_metrics": metrics}, indent=2, default=float))
    return metrics


if __name__ == "__main__":
    train()
