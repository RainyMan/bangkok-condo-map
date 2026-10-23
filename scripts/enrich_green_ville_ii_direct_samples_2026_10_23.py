"""Replace Green Ville II (2013) market summaries with current linked Hipflat units."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT = ROOT / "reports" / "green-ville-ii-condominium-direct-listings-2026-10-23.json"
SYMBOL = "BANGKOK_MANUAL_MARKET_SAMPLES"
PROJECT_ID = 5581
PROJECT_NAME = "Green Ville II Condominium"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/green-ville-ii-condominium-97u1tat01lce4leua0c1t1hl4t0thc7a"
CHECKED_AT = "2026-10-23"

sale_samples = [
    {
        "id": "U163856",
        "price": 1_490_000,
        "area": 32,
        "priceSqm": 46_563,
        "beds": 1,
        "roomType": "1BR",
        "url": "https://www.hipflat.co.th/en/ads/h2h4l7l3883a80cnh3cectau3u0h141h",
        "title": "For sale 1 bed condo in Phra Khanong, Bangkok · Green Ville II Condominium",
        "sourceName": "Hipflat",
        "projectName": PROJECT_NAME,
        "updated": CHECKED_AT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_page_unit",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "U1097514",
        "price": 2_500_000,
        "area": 58,
        "priceSqm": 43_103,
        "beds": 2,
        "roomType": "2BR",
        "url": "https://www.hipflat.co.th/en/ads/nnl1t49h8hht31e9aaclhu4t3u02u9eu",
        "title": "For sale 2 bedrooms condo in Phra Khanong, Bangkok · Green Ville II Condominium",
        "sourceName": "Hipflat",
        "projectName": PROJECT_NAME,
        "updated": CHECKED_AT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_page_unit",
        "listingStatus": "active_as_listed",
    },
]
rent_samples = [
    {
        "id": "U1636800",
        "price": 10_000,
        "area": 30,
        "priceSqm": 333,
        "beds": 1,
        "roomType": "1BR",
        "url": "https://www.hipflat.co.th/en/ads/749ct4248eullnha28t1e9t83u0h14ua",
        "title": "For rent 1 bed condo in Phra Khanong, Bangkok · Green Ville II Condominium",
        "sourceName": "Hipflat",
        "projectName": PROJECT_NAME,
        "updated": CHECKED_AT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_page_unit",
        "listingStatus": "active_as_listed",
    },
]

sale_average_sqm = round(sum(row["priceSqm"] for row in sale_samples) / len(sale_samples))
sale_min_price = min(sale_samples, key=lambda row: row["price"])
sale_min_sqm = min(sale_samples, key=lambda row: row["price"] / row["area"])
rent_min = min(rent_samples, key=lambda row: row["price"])
entry = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "replaceSale": True,
    "replaceRent": True,
    "sale": {
        "count": len(sale_samples),
        "observedCount": len(sale_samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in sale_samples) / len(sale_samples)),
        "minimum": sale_min_price["price"],
        "minimumArea": sale_min_price["area"],
        "minimumSampleUpdated": CHECKED_AT,
        "averageSqm": sale_average_sqm,
        "minimumSqm": round(sale_min_sqm["price"] / sale_min_sqm["area"]),
        "minimumSqmSampleUpdated": CHECKED_AT,
        "asOf": CHECKED_AT,
        "sourceName": "Hipflat 個別掛牌",
        "source": PROJECT_URL,
        "minimumSourceUrl": sale_min_price["url"],
        "minimumSqmSourceUrl": sale_min_sqm["url"],
        "samples": sale_samples,
    },
    "rent": {
        "count": len(rent_samples),
        "observedCount": len(rent_samples),
        "countKind": "manual_verified_listing",
        "average": rent_min["price"],
        "minimum": rent_min["price"],
        "minimumArea": rent_min["area"],
        "minimumSampleUpdated": CHECKED_AT,
        "averageSqm": round(rent_min["price"] / rent_min["area"]),
        "minimumSqm": round(rent_min["price"] / rent_min["area"]),
        "minimumSqmSampleUpdated": CHECKED_AT,
        "asOf": CHECKED_AT,
        "sourceName": "Hipflat 個別掛牌",
        "source": PROJECT_URL,
        "minimumSourceUrl": rent_min["url"],
        "minimumSqmSourceUrl": rent_min["url"],
        "samples": rent_samples,
    },
}

text = TARGET.read_text(encoding="utf-8")
match = re.search(rf"window\.{SYMBOL}\s*=\s*(\[.*\]);", text, re.S)
if not match:
    raise SystemExit(f"Cannot locate {SYMBOL} in {TARGET}")
rows = json.loads(match.group(1))
rows = [row for row in rows if int(row.get("hipflatId", 0)) != PROJECT_ID]
rows.append(entry)
TARGET.write_text(
    f"window.{SYMBOL} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)

REPORT.write_text(json.dumps({
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "projectSource": PROJECT_URL,
    "projectEvidence": [
        "Hipflat project page identifies Green Ville II Condominium, Punnawithi 28 Yaek 2, Bang Chak, Phra Khanong, 8 floors, completed January 2013.",
        "Each included listing opens from this exact Hipflat project page and its detail page repeats the project name and January 2013 completion.",
    ],
    "saleSamples": sale_samples,
    "rentSamples": rent_samples,
    "yieldBasis": {
        "bedrooms": 1,
        "salePriceTHB": sale_min_price["price"],
        "saleAreaSqm": sale_min_price["area"],
        "rentTHBPerMonth": rent_min["price"],
        "rentAreaSqm": rent_min["area"],
        "areaDifferenceSqm": abs(sale_min_price["area"] - rent_min["area"]),
        "commonFee": "not verified; not deducted",
        "notes": [
            "The 1-bedroom area difference is exactly 2 sqm, so the lowest monthly rent is used without scaling.",
            "No 2-bedroom rental listing was found on the exact Hipflat project page, so no 2-bedroom ROI is inferred.",
            "Another 1-bedroom sale listing on the project page was last updated 9 September 2026; it is older than 30 days at the check date and is excluded from current samples.",
        ],
    },
    "sourceFindings": [
        {"url": sale_samples[0]["url"], "finding": "1 bedroom, ฿1,490,000, 32 sqm; page shows updated within the last hour and project completion January 2013."},
        {"url": sale_samples[1]["url"], "finding": "2 bedrooms, ฿2,500,000, 58 sqm; page shows updated within the last two hours and project completion January 2013."},
        {"url": rent_samples[0]["url"], "finding": "1 bedroom, ฿10,000/month, 30 sqm; page shows updated within the last 9 hours and project completion January 2013."},
    ],
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "hipflatId": PROJECT_ID,
    "saleSamples": len(sale_samples),
    "rentSamples": len(rent_samples),
    "lowestOneBedroomSale": [sale_min_price["price"], sale_min_price["area"]],
    "lowestOneBedroomRent": [rent_min["price"], rent_min["area"]],
    "report": str(REPORT),
}, ensure_ascii=False))
