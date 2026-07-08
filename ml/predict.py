"""
predict.py
----------
Load the trained RandomForest model and expose a predict_failure()
function that returns a float probability (0.0–1.0).

Gracefully handles a missing model file by falling back to a heuristic.
"""

import os
import joblib
import numpy as np
import pandas as pd

feature_df = pd.DataFrame([{
    "battery_health": battery_health,
    "operating_hours": operating_hours,
    "mission_count": mission_count,
    "temperature": temperature,
    "humidity": humidity,
    "vibration_level": vibration_level,
    "pressure": pressure
}])

prob = model.predict_proba(feature_df)[0][1]

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "maintenance_model.pkl")

FEATURES = [
    "battery_health", "operating_hours", "mission_count",
    "temperature", "humidity", "vibration_level", "pressure",
]

# -------------------------------------------------------------------
# Load model (lazy)
# -------------------------------------------------------------------
_model = None
_model_loaded = False


def _load_model():
    global _model, _model_loaded
    if _model_loaded:
        return _model
    _model_loaded = True
    if os.path.exists(MODEL_PATH):
        try:
            _model = joblib.load(MODEL_PATH)
            print(f"[ML] Model loaded from {MODEL_PATH}")
        except Exception as e:
            print(f"[ML] WARNING: Could not load model: {e}")
            _model = None
    else:
        print(f"[ML] WARNING: Model file not found at {MODEL_PATH}")
        print("[ML]          Run  python train_model.py  to train the model.")
        print("[ML]          Falling back to heuristic prediction.")
    return _model


def predict_failure(asset_dict: dict) -> float:
    """
    Predict the probability of failure for a single asset.

    Parameters
    ----------
    asset_dict : dict
        Must contain (or default) the 7 features.

    Returns
    -------
    float  — probability between 0.0 and 1.0
    """
    model = _load_model()

    # Build feature vector with defaults
    feature_vector = np.array([[
        asset_dict.get("battery_health", 80),
        asset_dict.get("operating_hours", 100),
        asset_dict.get("mission_count", 10),
        asset_dict.get("temperature", 30),
        asset_dict.get("humidity", 55),
        asset_dict.get("vibration_level", 3.0),
        asset_dict.get("pressure", 1.0),
    ]])

    if model is not None:
        try:
            proba = model.predict_proba(feature_vector)[0]
            # Index 1 = failure class
            return float(proba[1]) if len(proba) > 1 else float(proba[0])
        except Exception as e:
            print(f"[ML] WARNING: Prediction failed: {e}")

    # Heuristic fallback
    prob = 0.0
    if asset_dict.get("battery_health", 80) < 40:
        prob += 0.4
    if asset_dict.get("operating_hours", 100) > 400:
        prob += 0.3
    if asset_dict.get("mission_count", 10) > 50:
        prob += 0.2
    return min(prob, 0.95)


# -------------------------------------------------------------------
# Quick CLI test
# -------------------------------------------------------------------
if __name__ == "__main__":
    test_asset = {
        "battery_health": 45,
        "operating_hours": 350,
        "mission_count": 47,
        "temperature": 35,
        "humidity": 60,
        "vibration_level": 5.5,
        "pressure": 1.0,
    }
    p = predict_failure(test_asset)
    print(f"Failure probability: {p:.4f}")
