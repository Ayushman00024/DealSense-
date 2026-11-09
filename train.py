import numpy as np
import pandas as pd
import joblib
import lightgbm as lgb
from sklearn.model_selection import train_test_split

# 1. Load data
df = pd.read_csv("data/phones.csv")
print("Loaded", len(df), "rows")

# 2. Choose features
CAT = ["brand", "model", "condition"]                         # text columns
NUM = ["storage_gb", "ram_gb", "age_months", "battery_health"]  # number columns

for c in CAT:
    df[c] = df[c].astype("category")

X = df[CAT + NUM]
y = np.log(df["price"])        # log price is easier for the model to learn

# 3. Split: 80% to learn from, 20% hidden for testing
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train three models: low (10%), median (50%), high (90%)
models = {}
for q in (0.1, 0.5, 0.9):
    m = lgb.LGBMRegressor(
        objective="quantile", alpha=q,
        n_estimators=300, learning_rate=0.05,
        num_leaves=15, min_child_samples=5, verbose=-1,
    )
    m.fit(Xtr, ytr)
    models[q] = m
    print("Trained model for quantile", q)

# 5. Test on the 20% the model has never seen
p10, p50, p90 = (np.exp(models[q].predict(Xte)) for q in (0.1, 0.5, 0.9))
actual = np.exp(yte)

mape = np.mean(np.abs(p50 - actual) / actual) * 100
inside = np.mean((actual >= p10) & (actual <= p90)) * 100
print(f"Average error (MAPE): {mape:.1f}%")
print(f"Prices inside the range: {inside:.1f}%  (aim for about 80%)")

# 6. Save the model
levels = {c: list(df[c].cat.categories) for c in CAT}
joblib.dump({"models": models, "levels": levels}, "price_model.joblib")
print("Saved price_model.joblib")