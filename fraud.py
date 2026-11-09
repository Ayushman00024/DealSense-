import re

# Phrases scammers commonly use
SCAM_PATTERNS = [
    (r"advance (payment|amount)|pay (first|in advance)", "Asks for advance payment"),
    (r"army|crpf|transfer(red)? officer|police", "Uses a transfer-officer story"),
    (r"courier|shipping agent|delivery agent", "Pushes courier or agent delivery"),
    (r"only (whatsapp|telegram)|whatsapp|telegram", "Pushes chat off-platform"),
    (r"token (amount|money)|upi.{0,12}first", "Wants a token payment up front"),
    (r"no (meet|inspection|visit)", "Refuses in-person inspection"),
    (r"urgent(ly)? sale|urgent(ly)? sell", "Creates urgency"),
]


def fraud_check(text, asking, median, account_age_days, num_listings, duplicate_photos):
    score = 0
    reasons = []
    t = text.lower()

    # 1. Price far below the market median
    drop = (median - asking) / median
    if drop > 0.40:
        score += 30
        reasons.append(f"Price is {drop:.0%} below the market median")
    elif drop > 0.25:
        score += 15
        reasons.append(f"Price is {drop:.0%} below the market median")

    # 2. Scam language (10 points each, max 40)
    hits = [label for pattern, label in SCAM_PATTERNS if re.search(pattern, t)]
    score += min(10 * len(hits), 40)
    reasons.extend(hits)

    # 3. Phone number written inside the listing text
    if re.search(r"\d[\d\s-]{8,}\d", t):
        score += 10
        reasons.append("Phone number placed inside the listing text")

    # 4. New seller account
    if account_age_days < 7:
        score += 15
        reasons.append(f"Very new seller account ({account_age_days} days)")
    elif account_age_days < 30:
        score += 7
        reasons.append(f"Young seller account ({account_age_days} days)")

    # 5. Many listings from a new account
    if num_listings > 8 and account_age_days < 30:
        score += 10
        reasons.append(f"{num_listings} listings from an account under 30 days old")

    # 6. Photos reused from other sellers
    if duplicate_photos > 0:
        score += min(10 + 5 * duplicate_photos, 30)
        reasons.append(f"Photos appear in {duplicate_photos} other seller listing(s)")

    score = min(score, 100)
    level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return {"score": score, "level": level, "reasons": reasons}


# Quick test with two example listings
if __name__ == "__main__":
    safe = fraud_check(
        "iPhone 13 128GB good condition, battery 88%, with box",
        asking=32000, median=29291, account_age_days=400,
        num_listings=2, duplicate_photos=0,
    )
    scam = fraud_check(
        "iPhone 13 like new. Urgent sale, army transfer. Advance payment by UPI first. Only WhatsApp 9812345612",
        asking=18000, median=29291, account_age_days=3,
        num_listings=12, duplicate_photos=4,
    )
    print("SAFE:", safe)
    print("SCAM:", scam)