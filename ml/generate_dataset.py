"""
generate_dataset.py
-------------------
Generate a synthetic dataset of 500 asset health records and save to
ml/data/synthetic_assets.csv.

Features:
    battery_health   (20–100)
    operating_hours  (0–500)
    mission_count    (0–60)
    temperature      (10–60  °C)
    humidity         (20–90  %)
    vibration_level  (0–10)
    pressure         (0.8–1.2 atm)

Label:
    failure_risk = 1 if (battery_health < 40 OR operating_hours > 400
                         OR mission_count > 50) else 0
    10 % random noise added (flip label).
"""

import os
import numpy as np
import pandas as pd

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
NUM_ROWS = 500
RANDOM_SEED = 42
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "synthetic_assets.csv")

np.random.seed(RANDOM_SEED)


def generate():
    # --- Features ---
    battery_health = np.random.uniform(20, 100, NUM_ROWS).round(1)
    operating_hours = np.random.randint(0, 501, NUM_ROWS)
    mission_count = np.random.randint(0, 61, NUM_ROWS)
    temperature = np.random.uniform(10, 60, NUM_ROWS).round(1)
    humidity = np.random.uniform(20, 90, NUM_ROWS).round(1)
    vibration_level = np.random.uniform(0, 10, NUM_ROWS).round(2)
    pressure = np.random.uniform(0.8, 1.2, NUM_ROWS).round(2)

    # --- Label logic ---
    failure_risk = np.where(
        (battery_health < 40) | (operating_hours > 400) | (mission_count > 50),
        1,
        0,
    )

    # --- Add 10 % noise (flip labels) ---
    noise_mask = np.random.random(NUM_ROWS) < 0.10
    failure_risk = np.where(noise_mask, 1 - failure_risk, failure_risk)

    # --- Build DataFrame ---
    df = pd.DataFrame({
        "battery_health": battery_health,
        "operating_hours": operating_hours,
        "mission_count": mission_count,
        "temperature": temperature,
        "humidity": humidity,
        "vibration_level": vibration_level,
        "pressure": pressure,
        "failure_risk": failure_risk,
    })

    # --- Save ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[OK] Generated {NUM_ROWS} rows → {OUTPUT_PATH}")
    print(f"     Label distribution:\n{df['failure_risk'].value_counts().to_string()}")
    return df


if __name__ == "__main__":
    generate()
