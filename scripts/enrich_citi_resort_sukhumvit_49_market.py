"""Add directly verified rent listings and a corroborated map pin for Citi Resort Sukhumvit 49."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
CHECKED = "2026-10-18"
PROJECT_ID = 3491
NAME = "Citi Resort Sukhumvit 49"
PROJECT_URL = "https://www.ddproperty.com/en/property-for-rent/at-citi-resort-sukhumvit-49-6467"

LOW_RATE_URL = "https://www.ddproperty.com/en/property/citi-resort-sukhumvit-49-bangkok-for-rent-500096572"
LOW_TOTAL_URL = "https://www.ddproperty.com/en/property/citi-resort-sukhumvit-49-for-rent-500446562"


def read_js_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{symbol} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript array format: {filename}")
    return json.loads(text[len(prefix):].strip().rstrip(";"))


def write_js_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


samples = [
    {
        "id": "500096572", "price": 70000, "area": 163, "priceSqm": 429.45,
        "beds": 2, "roomType": "2BR", "title": f"{NAME}，2 房，163 ㎡，฿70,000/月",
        "url": LOW_RATE_URL, "sourceName": "DDproperty", "projectName": NAME,
        "updated": "2026-10-05", "checkedAt": CHECKED,
        "matchedBy": "exact_ddproperty_project_and_listing_detail",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "500446562", "price": 45000, "area": 72, "priceSqm": 625,
        "beds": 2, "roomType": "2BR", "title": f"{NAME}，2 房，72 ㎡，฿45,000/月",
        "url": LOW_TOTAL_URL, "sourceName": "DDproperty", "projectName": NAME,
        "updated": "2026-10-14", "checkedAt": CHECKED,
        "matchedBy": "exact_ddproperty_project_and_listing_detail",
        "listingStatus": "active_as_listed",
    },
]
rent = {
    "count": 5, "observedCount": 2, "countKind": "manual_verified_listing",
    "average": 57500, "minimum": 45000, "minimumArea": 72,
    "minimumSampleUpdated": "2026-10-14", "averageSqm": 527.22,
    "minimumSqm": 429.45, "minimumSqmSampleUpdated": "2026-10-05",
    "asOf": CHECKED, "sourceName": "DDproperty 已核對單筆掛牌",
    "source": PROJECT_URL, "minimumSourceUrl": LOW_TOTAL_URL,
    "minimumSqmSourceUrl": LOW_RATE_URL, "samples": samples,
    "byBedroom": {
        "2": {
            "count": 2, "minimum": 45000, "area": 72, "priceSqm": 625,
            "minimumSqm": 429.45, "sourceUrl": LOW_TOTAL_URL,
            "minimumSqmSourceUrl": LOW_RATE_URL,
        }
    },
}
manual_path = DIST / "bangkok-manual-market-samples.js"
manual_rows = read_js_array(manual_path.name, "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": NAME}
    manual_rows.append(manual)
manual["rent"] = rent
write_js_array(manual_path.name, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

coordinate = {
    "hipflatId": PROJECT_ID, "name": NAME, "lat": 13.73113, "lng": 100.57543,
    "locationVerified": True, "sourceName": "OpenStreetMap 建築點位（Mapcarta）",
    "sourceUrl": "https://mapcarta.com/W324275320",
    "corroborationSourceUrl": "https://citiresort.com/en/sukhumvit-49-en/",
    "verificationSourceUrl": "https://www.hipflat.co.th/en/projects/citi-resort-sukhumvit-49-wukkrw",
    "verificationMethod": "exact_project_name_address_and_OSM_building_ID_corroborated_by_official_Google_Maps_pin",
}
coordinate_path = DIST / "bangkok-verified-coordinates.js"
coordinate_rows = read_js_array(coordinate_path.name, "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = [row for row in coordinate_rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
coordinate_rows.append(coordinate)
coordinate_rows.sort(key=lambda row: int(row["hipflatId"]))
write_js_array(coordinate_path.name, "BANGKOK_VERIFIED_COORDINATES", coordinate_rows)

yield_value = ((70000 / 163 * 111) * 11) / 19_900_000 * 100
evidence = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": CHECKED,
    "coordinates": coordinate,
    "rentSamples": samples,
    "saleBaseline": {
        "price": 19900000, "area": 111, "bedrooms": 2,
        "url": "https://propertyhub.in.th/en/listings/2-bedroom-2-bathroom-111-sq-m-citi-resort-sukhumvit-49---5890880",
        "availability": "PropertyHub project-index count remains visible; detail page has no update date.",
    },
    "roi": {
        "bedrooms": 2, "purchasePrice": 19900000, "purchaseAreaSqm": 111,
        "rentRatePerSqm": 429.45, "estimatedMonthlyRentAtPurchaseArea": round(70000 / 163 * 111),
        "agentMonthsDeducted": 1, "commonFee": "not found; excluded from numeric calculation",
        "netAnnualYieldBeforeUnknownCommonFeePercent": round(yield_value, 2),
    },
    "notes": [
        "DDproperty direct detail pages identify both rent units as Citi Resort Sukhumvit 49 at 39 Sukhumvit 49, and list them on 2026-10-05 and 2026-10-14; both were accessible on 2026-10-18.",
        "The two-bedroom lowest rent per sqm is 70,000 / 163 = 429.45 THB/sqm/month. Lowest total rent is a separate unit at 45,000 / 72; both source links are stored independently.",
        "PropertyHub direct sale detail identifies 2 bedrooms, 111 sqm, and THB 19,900,000, the lowest two-bedroom total in the existing project summary. Its individual update date is blank, so availability is not confirmed.",
        "The official CITI RESORT page provides the exact project name/address and a Google Maps link; Mapcarta's OSM building ID 324275320 matches the building and is used as the map centroid.",
        "Common fee could not be verified; the displayed numeric yield deducts one agent month but not an unknown common fee. Confirm the sale listing and management fee before purchase decisions.",
    ],
}
(REPORTS / "citi-resort-sukhumvit-49-market-2026-10-18.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


def append_csv(path: Path, row: dict) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not exists or path.stat().st_size == 0:
            writer.writeheader()
        writer.writerow(row)


append_csv(REPORTS / "coordinate-verification-2026-10-18.csv", {
    "hipflat_id": PROJECT_ID, "condo": NAME, "lat": coordinate["lat"], "lng": coordinate["lng"],
    "primary_source": coordinate["sourceUrl"], "corroborating_source": coordinate["corroborationSourceUrl"],
    "method": "OSM apartment building way 324275320 exact name/address; official site links to Google Maps at 13.7309631,100.5755459",
    "excluded_conflict": "",
})
append_csv(REPORTS / "listing-availability-checks-2026-10-18.csv", {
    "hipflat_id": PROJECT_ID, "condo": NAME, "checked_at": CHECKED, "market": "rent",
    "status": "two_exact_active_listings_verified",
    "verification_note": "DDproperty project filters show current listings; direct details confirm 2BR 163 sqm THB 70,000/month (listed Oct 5) and 2BR 72 sqm THB 45,000/month (listed Oct 14).",
    "source_1": LOW_RATE_URL, "source_2": LOW_TOTAL_URL, "source_3": PROJECT_URL,
})
print(json.dumps({"project": NAME, "rentSamples": len(samples), "roiBeforeUnknownFeePct": round(yield_value, 2)}, ensure_ascii=False))
