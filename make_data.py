import numpy as np
import pandas as pd
import os

rng = np.random.default_rng(42)   # fixed seed: same data every run

# (brand, model): approximate new price in INR
BASE = {
    ("Apple", "iPhone 13"): 65000,
    ("Apple", "iPhone 12"): 52000,
    ("Samsung", "Galaxy S21"): 50000,
    ("Samsung", "Galaxy S22"): 60000,
    ("OnePlus", "OnePlus 9"): 42000,
    ("Xiaomi", "Redmi Note 11"): 16000,
}
COND = {"like_new": 1.0, "good": 0.9, "fair": 0.78, "poor": 0.6}
STORAGE = {64: 0.9, 128: 1.0, 256: 1.12}

rows = []
for _ in range(600):
    (brand, model), new_price = list(BASE.items())[rng.integers(len(BASE))]
    storage = int(rng.choice(list(STORAGE)))
    cond = str(rng.choice(list(COND)))
    age = int(rng.integers(3, 48))
    battery = int(rng.integers(70, 100))
    ram = 4 if brand == "Apple" else int(rng.choice([6, 8]))

    price = (new_price * (0.985 ** age) * COND[cond] * STORAGE[storage]
             * (0.8 + 0.2 * battery / 100) * rng.lognormal(0, 0.06))
    rows.append([brand, model, storage, ram, cond, age, battery, round(price, -2)])

df = pd.DataFrame(rows, columns=["brand", "model", "storage_gb", "ram_gb",
                                 "condition", "age_months", "battery_health", "price"])

os.makedirs("data", exist_ok=True)
df.to_csv("data/phones.csv", index=False)
print(df.head())
print("Saved", len(df), "rows to data/phones.csv")