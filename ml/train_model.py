"""
train_model.py
--------------
Train a RandomForestClassifier on the synthetic dataset, evaluate, and
persist the model to ml/models/maintenance_model.pkl via joblib.
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "synthetic_assets.csv")
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "maintenance_model.pkl")

FEATURES = [
    "battery_health", "operating_hours", "mission_count",
    "temperature", "humidity", "vibration_level", "pressure",
]
TARGET = "failure_risk"


def train():
    # --- Load data ---
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Dataset not found at {DATA_PATH}")
        print("        Run  python generate_dataset.py  first.")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"[INFO] Loaded {len(df)} rows from {DATA_PATH}")

    X = df[FEATURES]
    y = df[TARGET]

    # --- Split 80 / 20 ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[INFO] Train: {len(X_train)}  |  Test: {len(X_test)}")

    # --- Train ---
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # --- Evaluate ---
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n{'='*50}")
    print(f"  Accuracy: {acc:.4f}")
    print(f"{'='*50}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # --- Feature importance ---
    print("\nFeature Importances:")
    for feat, imp in sorted(zip(FEATURES, model.feature_importances_),
                            key=lambda x: x[1], reverse=True):
        print(f"  {feat:20s} {imp:.4f}")

    # --- Save ---
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n[OK] Model saved → {MODEL_PATH}")

    return model


if __name__ == "__main__":
    train()