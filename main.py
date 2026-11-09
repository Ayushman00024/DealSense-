from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from predict import fair_price, levels
from fraud import fraud_check
from image_check import analyze_image

app = FastAPI(title="DealSense AI")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class Listing(BaseModel):
    text: str
    asking_price: float
    brand: str
    model: str
    storage_gb: int
    ram_gb: int
    condition: str
    age_months: int
    battery_health: int
    seller_account_age_days: int = 365
    seller_num_listings: int = 1
    duplicate_photos: int = 0


@app.get("/")
def home():
    return {"app": "DealSense AI", "status": "running"}


@app.post("/analyze")
def analyze(item: Listing):
    if item.model not in levels["model"]:
        raise HTTPException(status_code=400,
                            detail=f"Unknown model. Supported: {levels['model']}")
    if item.condition not in levels["condition"]:
        raise HTTPException(status_code=400,
                            detail=f"Unknown condition. Supported: {levels['condition']}")

    phone = {
        "brand": item.brand, "model": item.model,
        "storage_gb": item.storage_gb, "ram_gb": item.ram_gb,
        "condition": item.condition, "age_months": item.age_months,
        "battery_health": item.battery_health,
    }
    price = fair_price(phone, item.asking_price)
    fraud = fraud_check(item.text, item.asking_price, price["median"],
                        item.seller_account_age_days, item.seller_num_listings,
                        item.duplicate_photos)
    return {"price": price, "fraud": fraud}


@app.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...),
                                 seller_id: str = Form("unknown")):
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 8 MB)")
    try:
        return analyze_image(data, seller_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this image file")