"""Add directly verified coordinates and DDproperty/Hipflat listings for Elephant Tower."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 6415
PROJECT_NAME = "Elephant Tower"
CHECKED = "2026-10-18"
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/elephant-tower-gpsyvn"
DD_SALE_PROJECT = "https://www.ddproperty.com/en/condo-for-sale/at-elephant-tower-1425"
DD_RENT_PROJECT = "https://www.ddproperty.com/en/condo-for-rent/at-elephant-tower-1425"
COORDINATE_SOURCE = "https://thinkofliving.com/project/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/1425/"

SALE_SAMPLES = [
    {
        "id": "500633541", "price": 7_900_000, "area": 89, "priceSqm": 88_764,
        "beds": 2, "roomType": "2BR",
        "title": "Elephant Tower 2BR, 89 sqm — DDproperty 500633541",
        "url": "https://www.ddproperty.com/en/property/elephant-tower-bangkok-for-sale-500633541",
        "sourceName": "DDproperty", "projectName": PROJECT_NAME,
        "updated": "2026-10-09", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_active_DDproperty_project_listing",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "11157290", "price": 22_000_000, "area": 345, "priceSqm": 63_768,
        "beds": 3, "roomType": "3BR+maid",
        "title": "Elephant Tower 3BR+maid, 345 sqm — DDproperty 11157290",
        "url": "https://www.ddproperty.com/en/property/elephant-tower-bangkok-for-sale-11157290",
        "sourceName": "DDproperty", "projectName": PROJECT_NAME,
        "updated": "2026-09-22", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_active_DDproperty_project_listing",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "11510086", "price": 28_500_000, "area": 440, "priceSqm": 64_773,
        "beds": 6, "roomType": "6BR",
        "title": "Elephant Tower 6BR, 440 sqm — DDproperty 11510086",
        "url": "https://www.ddproperty.com/en/property/elephant-tower-bangkok-for-sale-11510086",
        "sourceName": "DDproperty", "projectName": PROJECT_NAME,
        "updated": "2026-09-18", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_active_DDproperty_project_listing",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "11157294", "price": 31_000_000, "area": 480, "priceSqm": 64_583,
        "beds": 5, "roomType": "5BR+maid",
        "title": "Elephant Tower 5BR+maid, 480 sqm — DDproperty 11157294",
        "url": "https://www.ddproperty.com/en/property/elephant-tower-bangkok-for-sale-11157294",
        "sourceName": "DDproperty", "projectName": PROJECT_NAME,
        "updated": "2026-09-22", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_active_DDproperty_project_listing",
        "listingStatus": "active_as_listed",
    },
]

RENT_SAMPLES = [
    {
        "id": "U1758442", "price": 19_000, "area": 67, "priceSqm": round(19_000 / 67),
        "beds": 2, "roomType": "2BR",
        "title": "Elephant Tower 2BR, 67 sqm — ฿19,000/month",
        "url": "https://www.hipflat.co.th/ads/n27a4h8h80uh2u742h9h3uc13u0h19hl",
        "sourceName": "Hipflat", "projectName": PROJECT_NAME,
        "updated": CHECKED, "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_direct_listing_unit_U1758442",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "10279919", "price": 33_000, "area": 118, "priceSqm": round(33_000 / 118),
        "beds": 2, "roomType": "2BR",
        "title": "Elephant Tower Duplex 2BR, 118 sqm — DDproperty 10279919",
        "url": "https://www.ddproperty.com/en/property/elephant-tower-bangkok-for-rent-10279919",
        "sourceName": "DDproperty", "projectName": PROJECT_NAME,
        "updated": "2026-10-15", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_active_DDproperty_project_listing",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "500516442", "price": 60_000, "area": 116, "priceSqm": round(60_000 / 116),
        "beds": 3, "roomType": "3BR",
        "title": "Elephant Tower 3BR, 116 sqm — DDproperty 500516442",
        "url": "https://www.ddproperty.com/en/property/elephant-tower-bangkok-for-rent-500516442",
        "sourceName": "DDproperty", "projectName": PROJECT_NAME,
        "updated": "2026-09-30", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_active_DDproperty_project_listing",
        "listingStatus": "active_as_listed",
    },
]


def read_array(filename: str, symbol: str) -> tuple[Path, str, list[dict]]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*?\]);\s*$", text, re.S)
    if not match:
        raise RuntimeError(f"Could not parse {symbol} in {path}")
    return path, text, json.loads(match.group(1))


def write_array(path: Path, text: str, symbol: str, rows: list[dict]) -> None:
    replacement = f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};"
    updated, count = re.subn(
        rf"window\.{re.escape(symbol)}\s*=\s*\[.*?\];\s*$",
        replacement,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"Could not update {symbol}")
    path.write_text(updated, encoding="utf-8", newline="")


sale_rates = [sample["price"] / sample["area"] for sample in SALE_SAMPLES]
rent_rates = [sample["price"] / sample["area"] for sample in RENT_SAMPLES]
sale_min_total = min(SALE_SAMPLES, key=lambda sample: sample["price"])
sale_min_sqm = min(SALE_SAMPLES, key=lambda sample: sample["price"] / sample["area"])
rent_min_total = min(RENT_SAMPLES, key=lambda sample: sample["price"])
rent_min_sqm = min(RENT_SAMPLES, key=lambda sample: sample["price"] / sample["area"])

sale_by_bedroom = {}
for beds in sorted({sample["beds"] for sample in SALE_SAMPLES}):
    room_samples = [sample for sample in SALE_SAMPLES if sample["beds"] == beds]
    low_total = min(room_samples, key=lambda sample: sample["price"])
    low_sqm = min(room_samples, key=lambda sample: sample["price"] / sample["area"])
    sale_by_bedroom[str(beds)] = {
        "beds": beds,
        "count": len(room_samples),
        "minimum": low_total["price"],
        "minimumArea": low_total["area"],
        "area": low_total["area"],
        "priceSqm": round(low_sqm["price"] / low_sqm["area"]),
        "minimumSqm": low_sqm["price"] / low_sqm["area"],
        "minimumSourceUrl": low_total["url"],
        "minimumSqmSourceUrl": low_sqm["url"],
        "sourceUrl": low_total["url"],
    }

rent_by_bedroom = {}
for beds in sorted({sample["beds"] for sample in RENT_SAMPLES}):
    room_samples = [sample for sample in RENT_SAMPLES if sample["beds"] == beds]
    low_total = min(room_samples, key=lambda sample: sample["price"])
    low_sqm = min(room_samples, key=lambda sample: sample["price"] / sample["area"])
    rent_by_bedroom[str(beds)] = {
        "beds": beds,
        "count": len(room_samples),
        "minimum": low_total["price"],
        "minimumArea": low_total["area"],
        "area": low_total["area"],
        "priceSqm": round(low_sqm["price"] / low_sqm["area"]),
        "minimumSqm": low_sqm["price"] / low_sqm["area"],
        "averageSqm": sum(sample["price"] / sample["area"] for sample in room_samples) / len(room_samples),
        "minimumSourceUrl": low_total["url"],
        "minimumSqmSourceUrl": low_sqm["url"],
        "sourceUrl": low_total["url"],
    }

sale = {
    "count": 4,
    "observedCount": len(SALE_SAMPLES),
    "countKind": "manual_verified_listing",
    "average": round(sum(sample["price"] for sample in SALE_SAMPLES) / len(SALE_SAMPLES)),
    "minimum": sale_min_total["price"],
    "minimumArea": sale_min_total["area"],
    "averageSqm": round(sum(sale_rates) / len(sale_rates)),
    "minimumSqm": round(sale_min_sqm["price"] / sale_min_sqm["area"]),
    "minimumSampleUpdated": sale_min_total["updated"],
    "minimumSqmSampleUpdated": sale_min_sqm["updated"],
    "asOf": CHECKED,
    "sourceName": "DDproperty 個別出售掛牌（4 筆在架）",
    "source": DD_SALE_PROJECT,
    "minimumSourceUrl": sale_min_total["url"],
    "minimumSqmSourceUrl": sale_min_sqm["url"],
    "byBedroom": sale_by_bedroom,
    "samples": SALE_SAMPLES,
}

rent = {
    "count": len(RENT_SAMPLES),
    "observedCount": len(RENT_SAMPLES),
    "countKind": "manual_verified_listing",
    "average": round(sum(sample["price"] for sample in RENT_SAMPLES) / len(RENT_SAMPLES)),
    "minimum": rent_min_total["price"],
    "minimumArea": rent_min_total["area"],
    "averageSqm": round(sum(rent_rates) / len(rent_rates)),
    "minimumSqm": round(rent_min_sqm["price"] / rent_min_sqm["area"]),
    "minimumSampleUpdated": rent_min_total["updated"],
    "minimumSqmSampleUpdated": rent_min_sqm["updated"],
    "asOf": CHECKED,
    "sourceName": "Hipflat／DDproperty 個別出租掛牌（3 筆核對樣本）",
    "source": DD_RENT_PROJECT,
    "minimumSourceUrl": rent_min_total["url"],
    "minimumSqmSourceUrl": rent_min_sqm["url"],
    "byBedroom": rent_by_bedroom,
    "samples": RENT_SAMPLES,
}

manual_path, manual_text, manual_rows = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual = next((row for row in manual_rows if int(row["hipflatId"]) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    manual_rows.append(manual)
manual.update({"hipflatId": PROJECT_ID, "name": PROJECT_NAME, "replaceSale": True, "replaceRent": True, "asOf": CHECKED, "sale": sale, "rent": rent})
manual_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array(manual_path, manual_text, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

coord_path, coord_text, coord_rows = read_array(
    "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"
)
coordinate = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.825377,
    "lng": 100.567445,
    "locationVerified": True,
    "sourceName": "ThinkOfLiving 專案頁座標",
    "sourceUrl": COORDINATE_SOURCE,
    "verificationSourceUrl": HIPFLAT_PROJECT,
    "verificationMethod": "ThinkOfLiving 專案座標與 Hipflat Elephant Tower 名稱、Chatuchak 地址交叉核對",
}
coord_rows = [row for row in coord_rows if int(row["hipflatId"]) != PROJECT_ID]
coord_rows.append(coordinate)
coord_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array(coord_path, coord_text, "BANGKOK_VERIFIED_COORDINATES", coord_rows)

cross_path, cross_text, cross_rows = read_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": CHECKED,
    "sourceName": "DDproperty",
    "projectSourceUrl": DD_SALE_PROJECT,
    "sale": {
        "activeListingCount": 4,
        "sourceUrl": DD_SALE_PROJECT,
        "samples": [
            {"listingId": sample["id"], "bedrooms": sample["beds"], "price": sample["price"], "area": sample["area"], "priceSqm": sample["priceSqm"], "url": sample["url"], "listedAt": sample["updated"]}
            for sample in SALE_SAMPLES
        ],
    },
    "rent": {
        "activeListingCount": 3,
        "sourceUrl": DD_RENT_PROJECT,
        "samples": [
            {"listingId": sample["id"], "bedrooms": sample["beds"], "price": sample["price"], "area": sample["area"], "priceSqm": round(sample["price"] / sample["area"]), "url": sample["url"], "listedAt": sample["updated"]}
            for sample in RENT_SAMPLES if sample["sourceName"] == "DDproperty"
        ],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat", "url": HIPFLAT_PROJECT, "statusLabel": "專案頁顯示 4 筆出售、12 筆出租；個別樣本與 DDproperty 有重疊可能"},
    ],
}
cross_rows = [row for row in cross_rows if int(row["hipflatId"]) != PROJECT_ID]
cross_rows.append(crosscheck)
cross_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array(cross_path, cross_text, "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

index_path = DIST / "index.html"
index = index_path.read_text(encoding="utf-8")
for old, new in [
    ("bangkok-verified-coordinates.js?v=20261018aa-chateau-pinklao-crosscheck", "bangkok-verified-coordinates.js?v=20261018ab-elephant-tower"),
    ("bangkok-manual-market-samples.js?v=20261018ac-belle-grand-two-bedroom-listings", "bangkok-manual-market-samples.js?v=20261018ad-elephant-tower-market"),
    ("bangkok-market-crosschecks.js?v=20261018w-belle-grand-two-bedroom", "bangkok-market-crosschecks.js?v=20261018x-elephant-tower"),
]:
    if old not in index:
        raise RuntimeError(f"Expected cache tag not found: {old}")
    index = index.replace(old, new, 1)
index_path.write_text(index, encoding="utf-8", newline="")

monthly_rent_estimate = rent_by_bedroom["2"]["minimumSqm"] * sale_by_bedroom["2"]["minimumArea"]
gross_roi = monthly_rent_estimate * 12 / sale_by_bedroom["2"]["minimum"] * 100
report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": CHECKED,
    "coordinate": coordinate,
    "sale": sale,
    "rent": rent,
    "roi": {
        "status": "estimated_from_lowest_two_bedroom_sale_and_lowest_two_bedroom_rent_rate",
        "purchasePriceThb": sale_by_bedroom["2"]["minimum"],
        "purchaseAreaSqm": sale_by_bedroom["2"]["minimumArea"],
        "rentRateThbPerSqmMonth": rent_by_bedroom["2"]["minimumSqm"],
        "estimatedMonthlyRentThb": round(monthly_rent_estimate),
        "grossAnnualYieldPercent": round(gross_roi, 2),
        "managementFeeDeducted": False,
        "note": "Project management fee was not publicly verified. Rent rate and sale price come from two-bedroom, directly linked listings; rental rate is applied to the selected sale listing's area.",
    },
    "sources": {
        "hipflatProject": HIPFLAT_PROJECT,
        "ddSaleProject": DD_SALE_PROJECT,
        "ddRentProject": DD_RENT_PROJECT,
        "coordinateSource": COORDINATE_SOURCE,
    },
}
(ROOT / "reports" / "elephant-tower-enrichment-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [coordinate["lat"], coordinate["lng"]], "saleSamples": len(SALE_SAMPLES), "saleTwoBedroomMinimum": sale_by_bedroom["2"], "rentSamples": len(RENT_SAMPLES), "twoBedroomRentRateThbSqm": rent_by_bedroom["2"]["minimumSqm"], "grossYieldPercent": round(gross_roi, 2)}, ensure_ascii=False))
