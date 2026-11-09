<div align="center">

# ◆ DealSense AI

### Know the real price. Spot the scam before you pay.

Intelligent second-hand product pricing and fraud detection, starting with smartphones.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-quantile%20regression-2E8B57)
![Status](https://img.shields.io/badge/status-prototype-orange)

</div>

---

## Why DealSense?

Buying or selling a used phone means two questions: **"Is this price fair?"** and **"Can I trust this listing?"** Most people guess. DealSense answers both with numbers and reasons you can check.

| For sellers | For buyers |
|---|---|
| Enter your product details and get a quick-sale, expected and suggested listing price | Paste a listing and see if the asking price is fair |
| Check that your photos look trustworthy | See a fraud risk score with the reasons behind it |

## Features

- **Price range, not a single number.** Three LightGBM quantile models (10th, 50th and 90th percentile) give a low, median and high estimate.
- **Deal verdict.** Every asking price is labeled *Great deal*, *Fair price* or *Overpriced*.
- **Seller price estimate.** `/estimate` returns a quick-sale price, an expected price and a suggested listing price.
- **Explainable fraud score (0 to 100).** Rules check price bait, scam phrases, off-platform contact, new accounts, bulk listings and reused photos. Every point comes with a plain-language reason.
- **Image checks.** Perceptual hashing finds photos reused across sellers, and metadata and quality checks flag edited, low-resolution or blurry images.
- **Marketplace-style search UI.** Search, filter and sort listings, each checked live, with a detail panel and a "before you pay" checklist.
- **Demo mode.** If the API is offline, the page falls back to a built-in estimator so it still works.

## How it works

```
 Browser (index.html)
        │  JSON / image upload
        ▼
 FastAPI (main.py)
   ├── /analyze         price range + deal verdict + fraud score
   ├── /estimate        seller-side price estimate
   └── /analyze-image   duplicate, metadata and quality checks
        │
        ├── predict.py       LightGBM quantile models (price_model.joblib)
        ├── fraud.py         rule-based fraud scoring with reasons
        └── image_check.py   pHash duplicate detection + image checks
```

## Quick start

```bash
# 1. Clone
git clone https://github.com/Ayushman00024/DealSense-.git
cd DealSense-

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate data and train the model
python make_data.py
python train.py

# 5. Start the API
uvicorn main:app --reload
```

Then open **`index.html`** in your browser. A green **Live model** pill means the page is talking to your API. Interactive API docs are at <http://127.0.0.1:8000/docs>.

## API example

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "iPhone 13 128GB good condition, battery 88%, with box",
    "asking_price": 32000,
    "brand": "Apple", "model": "iPhone 13",
    "storage_gb": 128, "ram_gb": 4,
    "condition": "good", "age_months": 30, "battery_health": 88,
    "seller_account_age_days": 400, "seller_num_listings": 2, "duplicate_photos": 0
  }'
```

```json
{
  "price": { "low": 25776, "median": 29291, "high": 32806, "verdict": "Fair price" },
  "fraud": { "score": 0, "level": "Low", "reasons": [] }
}
```

## Project structure

```
DealSense-/
├── data/                 generated training data (phones.csv)
├── make_data.py          builds the synthetic dataset
├── train.py              trains and saves the price models
├── predict.py            price range, estimate and deal verdict
├── fraud.py              rule-based fraud scoring
├── image_check.py        image duplicate and quality checks
├── main.py               FastAPI app
├── index.html            marketplace-style search UI
├── requirements.txt
└── README.md
```

## Current results

Trained on 600 synthetic listings:

| Metric | Result | Target |
|---|---|---|
| Median price error (MAPE) | 9.0% | under 15% |
| Real prices inside the low-to-high range | 60.8% | about 80% |

The range is narrower than it should be, so `predict.py` widens it to at least ±12% around the median.

## Honest limitations

- **The training data is synthetic.** The model learns the depreciation rules used to generate it, not real market prices. It proves the pipeline works, nothing more.
- **Six phone models are supported:** iPhone 12, iPhone 13, Galaxy S21, Galaxy S22, OnePlus 9 and Redmi Note 11.
- **Images give risk signals, not proof.** A photo alone can't show that a phone is counterfeit, and many apps strip metadata, so a missing tag is a weak signal.
- **Fraud scores are signals, not verdicts.** Always inspect the phone and avoid paying in advance.

## Roadmap

- [x] Price range model with quantile regression
- [x] Rule-based fraud scoring with reasons
- [x] FastAPI backend
- [x] Marketplace-style search UI
- [x] Image duplicate and quality checks
- [ ] Seller page with product form and photo upload
- [ ] Train on real listings (fixes the narrow price range)
- [ ] Vision model check for product match and damage
- [ ] Fraud classifier trained on user-reported scams
- [ ] More categories (laptops, bikes, furniture)
- [ ] Flutter mobile app

## Tech stack

Python · FastAPI · LightGBM · pandas · scikit-learn · Pillow · imagehash · HTML, CSS and JavaScript

## Contributing

Ideas and pull requests are welcome. Open an issue to discuss a larger change first.

## Author

Built by [Ayushman](https://github.com/Ayushman00024).

---

<div align="center">
<sub>Prototype for learning and demonstration. Not financial advice.</sub>
</div>
