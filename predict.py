import joblib
import numpy as np
import pandas as pd

# Load the saved model
bundle = joblib.load("price_model.joblib")
models, levels = bundle["models"], bundle["levels"]


def fair_price(phone: dict, asking: float) -> dict:
    row = pd.DataFrame([phone])
    for col, lv in levels.items():
        row[col] = pd.Categorical(row[col], categories=lv)

    low, mid, high = (float(np.exp(models[q].predict(row)[0])) for q in (0.1, 0.5, 0.9))

    # Make sure the range is at least +/-12% around the median
    low = min(low, mid * 0.88)
    high = max(high, mid * 1.12)

    if asking <= low:
        verdict = "Great deal"
    elif asking <= high:
        verdict = "Fair price"
    else:
        verdict = "Overpriced"

    return {"low": round(low), "median": round(mid), "high": round(high), "verdict": verdict}


# This test code only runs when you run predict.py directly,
# not when main.py imports it
if __name__ == "__main__":
    phone = {
        "brand": "Apple", "model": "iPhone 13", "storage_gb": 128, "ram_gb": 4,
        "condition": "good", "age_months": 30, "battery_health": 88,
    }

    print(fair_price(phone, asking=32000))
    print(fair_price(phone, asking=45000))
    print(fair_price(phone, asking=22000))