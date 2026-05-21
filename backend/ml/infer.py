import os
import joblib
import numpy as np
import pandas as pd

from .config import INPUT_FEATURES

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH = os.path.join(ARTIFACT_DIR, "model.joblib")
DATASET_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "maize_yield.csv"))


def _get_model_feature_names(model):
    if hasattr(model, "feature_names_in_"):
        return tuple(getattr(model, "feature_names_in_"))

    if hasattr(model, "named_steps"):
        prep = model.named_steps.get("prep")
        if prep is not None and hasattr(prep, "feature_names_in_"):
            return tuple(getattr(prep, "feature_names_in_"))

    return None


def _validate_dataset_schema():
    if not os.path.exists(DATASET_PATH):
        return

    try:
        df = pd.read_csv(DATASET_PATH, nrows=0)
    except Exception as exc:
        raise ValueError(
            f"Unable to read training dataset at {DATASET_PATH}. "
            "Ensure the file is a valid CSV."
        ) from exc

    missing_columns = [c for c in INPUT_FEATURES +
                       ["yield"] if c not in df.columns]
    if missing_columns:
        raise ValueError(
            "Training dataset schema does not match expected app inputs. "
            f"Missing columns: {', '.join(missing_columns)}. "
            f"Dataset file: {DATASET_PATH}. "
            "Update the CSV to include the expected columns from backend/ml/config.py."
        )


def predict_yield(payload: dict) -> float:
    """payload must include keys in INPUT_FEATURES."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model artifacts not found. Run training first.")

    _validate_dataset_schema()

    model = joblib.load(MODEL_PATH)

    trained_features = _get_model_feature_names(model)
    if trained_features is not None and tuple(INPUT_FEATURES) != trained_features:
        raise ValueError(
            "Saved model input features do not match current app config. "
            f"Expected: {tuple(INPUT_FEATURES)}. "
            f"Found: {trained_features}. "
            "Retrain the model with a dataset that includes the expected columns."
        )

    row = {k: payload.get(k) for k in INPUT_FEATURES}
    # Ensure correct column order and numeric types
    X = pd.DataFrame([[row[k] for k in INPUT_FEATURES]],
                     columns=INPUT_FEATURES)

    pred = model.predict(X)[0]

    # Standardize output type
    if isinstance(pred, (np.floating, float, int)):
        return float(pred)
    return float(np.asarray(pred).ravel()[0])
