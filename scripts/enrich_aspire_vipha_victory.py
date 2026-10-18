"""Add directly linked current two-bedroom sale and rent samples for Aspire Vibha-Victory."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_PATH = ROOT / "dist" / "bangkok-manual-market-samples.js"
APP_PATH = ROOT / "dist" / "app.js"
INDEX_PATH = ROOT / "dist" / "index.html"
REPORT_PATH = ROOT / "reports" / "aspire-vibha-victory-samples-2026-10-18.json"
PROJECT_ID = 3791
PROJECT_NAME = "Aspire Vipha-Victory"
CHECKED_AT = "2026-10-18"

SALE = {
    "id": "6277901",
    "price": 7_000_000,
    "area": 60,
    "priceSqm": 116_667,
    "beds": 2,
    "roomType": "2BR",
    "title": "Aspire Vibha-Victory，2 房，60 ㎡，฿7,000,000",
    "url": "https://propertyhub.in.th/en/listings/rare-item-beautiful-condo-at-below-market-price-aspire-vibha-victory-book-now-before-its-gone---6277901",
    "sourceName": "PropertyHub",
    "projectName": "Aspire Vibha - Victory",
    "updated": "2026-10-17",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_listing_id",
    "listingStatus": "active_as_listed",
}
RENT = {
    "id": "6316910",
    "price": 28_000,
    "area": 56,
    "priceSqm": 500,
    "beds": 2,
    "roomType": "2BR",
    "title": "Aspire Vibha-Victory，2 房，56 ㎡，฿28,000/月",
    "url": "https://propertyhub.in.th/en/listings/2-br-condo-for-rent-at-aspire-vibha-victory-near-bts-sanam-pao-id-3207201---6316910",
    "sourceName": "PropertyHub",
    "projectName": "Aspire Vibha - Victory",
    "updated": CHECKED_AT,
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_listing_id",
    "listingStatus": "active_as_listed",
}


def load_rows() -> list[dict]:
    text = MANUAL_PATH.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError("Unexpected manual market sample data format")
    return json.loads(match.group(1))


rows = load_rows()
project = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    rows.append(project)

for key, sample in (("sale", SALE), ("rent", RENT)):
    market = project.setdefault(key, {})
    samples = [item for item in market.get("samples", []) if item.get("url") != sample["url"]]
    samples.append(sample)
    market["samples"] = samples

MANUAL_PATH.write_text(
    "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
    + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)

app = APP_PATH.read_text(encoding="utf-8")
app = app.replace(
    "const yieldStorageKey = 'bangkokCondoYieldInputsV61';",
    "const yieldStorageKey = 'bangkokCondoYieldInputsV62';",
    1,
)
app = app.replace(
    "const previous = JSON.parse(localStorage.getItem('bangkokCondoYieldInputsV60')",
    "const previous = JSON.parse(localStorage.getItem('bangkokCondoYieldInputsV61') || localStorage.getItem('bangkokCondoYieldInputsV60')",
    1,
)
APP_PATH.write_text(app, encoding="utf-8")
index = INDEX_PATH.read_text(encoding="utf-8")
index = index.replace(
    "bangkok-manual-market-samples.js?v=20261018y-feliz-direct-listings",
    "bangkok-manual-market-samples.js?v=20261018z-aspire-vibha-victory",
    1,
)
index = index.replace(
    "app.js?v=20261018-automatic-two-bedroom-roi-recalc-v53",
    "app.js?v=20261018-automatic-two-bedroom-roi-recalc-v54",
    1,
)
INDEX_PATH.write_text(index, encoding="utf-8")

REPORT_PATH.write_text(
    json.dumps(
        {
            "hipflatId": PROJECT_ID,
            "condo": PROJECT_NAME,
            "checkedAt": CHECKED_AT,
            "coordinate": {
                "status": "verified",
                "latitude": 13.763674107368944,
                "longitude": 100.54746122245038,
                "source": "https://propertyscout.co.th/en/bangkok/condo/aspire-vibha-victory/",
                "method": "exact_project_name_and_district",
            },
            "sale": SALE,
            "rent": RENT,
            "roi": {
                "roomType": "2BR",
                "purchasePriceTHB": SALE["price"],
                "floorAreaSqm": SALE["area"],
                "rentRateTHBPerSqmPerMonth": RENT["priceSqm"],
                "estimatedMonthlyRentTHB": 30_000,
                "agencyMonthsDeducted": 1,
                "annualNetYieldPercentBeforeCommonFee": round(30_000 * 11 / 7_000_000 * 100, 2),
                "managementFee": "not verified; not deducted",
            },
            "notes": [
                "The active PropertyHub sale project page showed one two-bedroom listing at ฿7,000,000 / 60 sqm when checked.",
                "A lower ฿5,640,000 indexed listing redirected to the project page and was excluded as not directly available.",
                "The rental listing was refreshed on 2026-10-18 at ฿28,000 / 56 sqm.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
