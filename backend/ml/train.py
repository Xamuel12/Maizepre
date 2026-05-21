import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

from .config import INPUT_FEATURES


ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH = os.path.join(ARTIFACT_DIR, "model.joblib")
METRICS_PATH = os.path.join(ARTIFACT_DIR, "metrics.joblib")


def load_dataset(csv_path: str):
    df = pd.read_csv(csv_path)
    missing = [c for c in INPUT_FEATURES + ["yield"] if c not in df.columns]
    if missing:
        raise ValueError(
            "Dataset missing required columns: " + ", ".join(missing)
        )
    df = df.dropna(subset=INPUT_FEATURES + ["yield"])
    X = df[INPUT_FEATURES]
    y = df["yield"].astype(float)
    return X, y


def build_model(feature_names):
    # All features are treated as numeric.
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[("num", numeric_transformer, feature_names)],
        remainder="drop",
    )

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2,
    )

    pipe = Pipeline(steps=[("prep", preprocessor), ("model", model)])
    return pipe


def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(project_root, "data", "maize_yield.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. Place your CSV in data/maize_yield.csv"
        )

    X, y = load_dataset(csv_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe = build_model(INPUT_FEATURES)
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    metrics = {
        "r2": float(r2_score(y_test, preds)),
        "mae": float(mean_absolute_error(y_test, preds)),
    }

    joblib.dump(pipe, MODEL_PATH)
    joblib.dump(metrics, METRICS_PATH)

    print("Training complete.")
    print("Artifacts saved to:", ARTIFACT_DIR)
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()
