"""Verify Above Sukhumvit 39 location and add its direct rental listing."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3281
PROJECT_NAME = "Above Sukhumvit 39"
RENT_URL = "https://propertyscout.co.th/en/1-br-condo-above-sukhumvit-39-near-bts-phrom-phong-2884009/"
SALE_URL = "https://propertyhub.in.th/en/listings/1-br-85-sqm-for-sale-at-above-sukhumvit-39-near-bts-phrom-phong-id-2918509---6403343"
COORD_URL = "https://www.condonayoo.com/above-sukhumvit-39/"
COORD_CHECK_URL = "https://thinkofliving.com/project/คอนโด/5411/"
PROJECT_URL = "https://verveo.co.th/projects/above-sukhumvit-39/"
RENT_PRICE, RENT_AREA = 25_000, 35
SALE_PRICE, SALE_AREA = 12_500_000, 85


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not read {symbol} in {filename}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


rent_rate = RENT_PRICE / RENT_AREA
rent_at_sale_area = rent_rate * SALE_AREA
annual_rent_after_agent = rent_at_sale_area * 11
estimated_yield = annual_rent_after_agent / SALE_PRICE * 100

# The listed Google map coordinate is cross-checked against another Thai
# project-information source; retain both links for review.
coordinate_filename = "bangkok-verified-coordinates.js"
coordinates = load_array(coordinate_filename, "BANGKOK_VERIFIED_COORDINATES")
coordinate = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.737113,
    "lng": 100.571052,
    "locationVerified": True,
    "sourceName": "CondoNayoo 公開 Google Maps 座標",
    "sourceUrl": COORD_URL,
    "verificationSourceUrl": COORD_CHECK_URL,
    "verificationMethod": "exact_project_name_and_sukhumvit_39_address_cross_checked_two_thai_project_sources",
}
coordinates = [row for row in coordinates if int(row.get("hipflatId", 0)) != PROJECT_ID]
coordinates.append(coordinate)
save_array(coordinate_filename, "BANGKOK_VERIFIED_COORDINATES", coordinates)

# Add completion year, project size, and corrected street address to the live
# PropertyHub data row while retaining its already sourced sale market data.
map_filename = "bangkok-propertyhub-map.js"
projects = load_array(map_filename, "BANGKOK_PROPERTYHUB_PROJECTS")
project = next(row for row in projects if int(row["id"]) == PROJECT_ID)
project.update({
    "address": "122 Phrom Chit Alley, Khlong Tan Nuea, Watthana District, Bangkok 10110, Thailand",
    "lat": coordinate["lat"],
    "lng": coordinate["lng"],
    "locationVerified": True,
    "locationSourceUrl": COORD_URL,
    "locationSourceName": "CondoNayoo 公開 Google Maps 座標",
    "locationVerificationSourceUrl": COORD_CHECK_URL,
    "completedYear": 2017,
    "completedYearSourceUrl": RENT_URL,
    "units": 41,
    "floors": 25,
})
save_array(map_filename, "BANGKOK_PROPERTYHUB_PROJECTS", projects)

details_filename = "bangkok-propertyhub-details.js"
details = load_array(details_filename, "BANGKOK_PROPERTYHUB_DETAILS")
detail = next(row for row in details if str(row.get("propertyHubProjectId")) == "1863")
detail.update({
    "address": project["address"],
    "lat": coordinate["lat"],
    "lng": coordinate["lng"],
    "locationVerified": True,
    "locationSourceUrl": COORD_URL,
    "locationSourceName": "CondoNayoo 公開 Google Maps 座標",
    "locationVerificationSourceUrl": COORD_CHECK_URL,
    "completedYear": 2017,
    "completedYearSourceUrl": RENT_URL,
    "units": 41,
    "floors": 25,
})
save_array(details_filename, "BANGKOK_PROPERTYHUB_DETAILS", details)

manual_filename = "bangkok-manual-market-samples.js"
manual = load_array(manual_filename, "BANGKOK_MANUAL_MARKET_SAMPLES")
entry = next((row for row in manual if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if entry is None:
    entry = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    manual.append(entry)
entry["asOf"] = "2026-10-18"
rent = entry.setdefault("rent", {})
sample = {
    "id": "2884009",
    "price": RENT_PRICE,
    "area": RENT_AREA,
    "priceSqm": round(rent_rate),
    "beds": 1,
    "roomType": "1BR",
    "title": "Above Sukhumvit 39，1 房，35 ㎡，฿25,000/月",
    "url": RENT_URL,
    "sourceName": "PropertyScout",
    "projectName": PROJECT_NAME,
    "updated": None,
    "checkedAt": "2026-10-18",
    "matchedBy": "exact_project_name_and_individual_listing_detail",
    "listingStatus": "availability_unconfirmed_date_unknown",
}
samples = [row for row in rent.get("samples", []) if row.get("url") != RENT_URL]
samples.append(sample)
rent.update({
    "count": len(samples),
    "observedCount": len(samples),
    "countKind": "manual_verified_listing",
    "average": RENT_PRICE,
    "minimum": RENT_PRICE,
    "minimumArea": RENT_AREA,
    "averageSqm": round(rent_rate),
    "minimumSqm": round(rent_rate),
    "asOf": "2026-10-18",
    "sourceName": "PropertyScout 單筆出租掛牌",
    "source": RENT_URL,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "samples": samples,
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": RENT_PRICE,
            "area": RENT_AREA,
            "minimumSqm": rent_rate,
            "averageSqm": rent_rate,
            "sourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
        }
    },
})
save_array(manual_filename, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_path.open(encoding="utf-8-sig", newline="") as stream:
    rows = list(csv.DictReader(stream))
    columns = list(rows[0]) if rows else [
        "hipflat_id", "condo", "checked_at", "market", "status",
        "verification_note", "source_1", "source_2", "source_3",
    ]
rows = [row for row in rows if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "rent")]
rows.append({
    "hipflat_id": str(PROJECT_ID),
    "condo": PROJECT_NAME,
    "checked_at": "2026-10-18",
    "market": "rent",
    "status": "direct_listing_found_availability_unconfirmed",
    "verification_note": "PropertyScout 個別頁列出 1 房、35㎡、฿25,000/月，頁面稱一個月前確認可租，現況仍未向刊登方確認；PropertyHub 與 Hipflat 有同專案的獨立 1 房出售掛牌。座標依 CondoNayoo Google Maps 公開座標，並由 ThinkOfLiving 專案頁交叉核對。管理費未核實。",
    "source_1": RENT_URL,
    "source_2": "https://www.hipflat.co.th/en/projects/above-sukhumvit-39-ffjwvm",
    "source_3": "https://propertyhub.in.th/en/condo-for-rent/project-above-sukhumvit-39",
})
with availability_path.open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": "2026-10-18",
    "location": {
        "latitude": coordinate["lat"],
        "longitude": coordinate["lng"],
        "source": COORD_URL,
        "crossCheckSource": COORD_CHECK_URL,
        "address": project["address"],
    },
    "projectDetails": {
        "completedYear": 2017,
        "units": 41,
        "floors": 25,
        "source": RENT_URL,
        "conflictingSource": "PropertyHub project overview displays Buddhist year 2559 (2016); the individual listing and two other project sources identify 2017. Displayed year follows the latter two-source agreement.",
    },
    "saleListing": {
        "priceThb": SALE_PRICE,
        "bedrooms": 1,
        "areaSqm": SALE_AREA,
        "priceThbPerSqm": round(SALE_PRICE / SALE_AREA),
        "source": SALE_URL,
        "updated": "2026-10-16",
    },
    "rentListing": {
        "monthlyRentThb": RENT_PRICE,
        "bedrooms": 1,
        "areaSqm": RENT_AREA,
        "rentThbPerSqmMonth": round(rent_rate, 2),
        "source": RENT_URL,
        "lastAvailabilityConfirmation": "PropertyScout page said confirmed available about one month before 2026-10-18; exact date and current vacancy not confirmed directly with advertiser",
    },
    "managementFee": {"rateThbPerSqmMonth": None, "status": "not verified; excluded from estimate"},
    "yieldEstimate": {
        "purchasePriceThb": SALE_PRICE,
        "purchaseAreaSqm": SALE_AREA,
        "bedrooms": 1,
        "monthlyRentRateThbPerSqm": round(rent_rate, 2),
        "monthlyRentAtSaleAreaThb": round(rent_at_sale_area),
        "agentMonthsDeducted": 1,
        "annualRentAfterAgentThb": round(annual_rent_after_agent),
        "annualCommonFeeThb": 0,
        "netYieldPercent": round(estimated_yield, 2),
        "formula": "((฿25,000 ÷ 35㎡) × 85㎡ × 11) ÷ ฿12,500,000 × 100; common fee omitted because it is unverified",
        "limitations": "The rent sample's availability was last described as confirmed about one month before the check date; the exact date and current vacancy have not been reconfirmed with the advertiser.",
    },
}
(ROOT / "reports" / "above-sukhumvit-39-rent-and-coordinate-enrichment-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({
    "hipflatId": PROJECT_ID,
    "coordinates": [coordinate["lat"], coordinate["lng"]],
    "rentThb": RENT_PRICE,
    "rentThbPerSqmMonth": round(rent_rate, 2),
    "yieldAfterOneAgentMonthPercent": round(estimated_yield, 2),
    "saleSource": SALE_URL,
    "rentSource": RENT_URL,
}, ensure_ascii=False))
