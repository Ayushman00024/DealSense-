import io
import json
import os

import imagehash
import numpy as np
from PIL import Image

DB_FILE = "image_db.json"   # remembers photos we have seen before
SOFTWARE_TAGS = ["photoshop", "canva", "snapseed", "picsart", "gimp", "lightroom"]


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return []


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)


def analyze_image(data: bytes, seller_id: str = "unknown", save: bool = True) -> dict:
    img = Image.open(io.BytesIO(data))
    reasons, notes = [], []
    score = 0

    # 1. Reused photo detection (perceptual hash)
    h = imagehash.phash(img)
    db = load_db()
    other_sellers = set()
    for entry in db:
        if entry["seller_id"] != seller_id:
            if h - imagehash.hex_to_hash(entry["hash"]) <= 6:
                other_sellers.add(entry["seller_id"])
    if other_sellers:
        n = len(other_sellers)
        score += min(25 + 8 * n, 50)
        reasons.append(f"This photo was already used by {n} other seller(s)")

    # 2. Metadata checks
    exif = img.getexif()
    camera = " ".join(str(exif.get(t, "")) for t in (271, 272)).strip()
    software = str(exif.get(305, "")).lower()
    if not exif:
        score += 10
        reasons.append("No camera metadata (common for screenshots, downloaded or edited images)")
    elif camera:
        notes.append(f"Camera metadata found: {camera}")
    if any(s in software for s in SOFTWARE_TAGS):
        score += 15
        reasons.append(f"Image was edited with software ({software})")

    # 3. Quality checks
    w, ht = img.size
    if w < 400 or ht < 400:
        score += 10
        reasons.append(f"Very low resolution ({w}x{ht})")

    gray = np.asarray(img.convert("L").resize((512, 512)), dtype=float)
    lap = (-4 * gray[1:-1, 1:-1] + gray[:-2, 1:-1] + gray[2:, 1:-1]
           + gray[1:-1, :-2] + gray[1:-1, 2:])
    if lap.var() < 40:
        score += 5
        reasons.append("Image is very blurry")

    if save:
        db.append({"hash": str(h), "seller_id": seller_id})
        save_db(db)

    score = min(score, 100)
    level = "High" if score >= 50 else "Medium" if score >= 25 else "Low"
    return {"image_score": score, "level": level, "reasons": reasons,
            "notes": notes, "hash": str(h), "size": [w, ht]}