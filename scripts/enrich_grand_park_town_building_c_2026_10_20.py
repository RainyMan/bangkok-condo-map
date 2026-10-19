"""Add verified GPS and a current, exact Building C sale sample."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ID = 3495
NAME = "Grand Park Town Building C"
AS_OF = "2026-10-20"
HIPFLAT = "https://www.hipflat.co.th/en/projects/grand-park-town-building-c-ispeze"
TP = "https://www.thailand-property.com/condo/4056/grand-park-town-building-c"
PH_PROJECT = "https://propertyhub.in.th/en/projects/grand-park-town"
PH_SALE = "https://propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B9%81%E0%B8%81%E0%B8%A3%E0%B8%99%E0%B8%94%E0%B9%8C-%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%84-%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C-%E0%B8%AD%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3-c-%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99-2-1-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-%E0%B8%82%E0%B8%99%E0%B8%B2%E0%B8%94-33-%E0%B8%95%E0%B8%A3%E0%B8%A1-%E0%B9%83%E0%B8%81%E0%B9%89-%E0%B9%82%E0%B8%A3%E0%B8%87%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99-%E0%B8%93-%E0%B8%94%E0%B8%A3%E0%B8%B8%E0%B8%93--a3950931---6267709"
LAT, LNG = 13.772468, 100.593594


def read_rows(filename: str, symbol: str) -> tuple[list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise ValueError(f"Unexpected {symbol} format")
    return json.loads(match.group(1)), match.group(2)


def write_rows(filename: str, symbol: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


coords, suffix = read_rows("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coords = [row for row in coords if int(row.get("hipflatId", -1)) != ID]
coords.append({
    "hipflatId": ID, "name": NAME, "lat": LAT, "lng": LNG,
    "locationVerified": True, "sourceName": "Thailand-Property 專案 GPS",
    "sourceUrl": TP, "verificationSourceUrl": HIPFLAT,
    "verificationMethod": "exact_project_name_and_address; embedded_schema_gps",
    "mapUrl": f"https://www.google.com/maps/search/?api=1&query={LAT}%2C{LNG}",
    "note": "Thailand-Property exact Building C page publishes gps_lat/gps_lon and schema.org GeoCoordinates; Hipflat exact project name and 584/20 Soi Aminsen address match.",
})
coords.sort(key=lambda row: int(row["hipflatId"]))
write_rows("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coords, suffix)

sale = {
    "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
    "average": 1690000, "minimum": 1690000, "minimumArea": 33.0,
    "minimumSampleUpdated": "2026-10-13", "averageSqm": 51212,
    "minimumSqm": 51212, "minimumSqmSampleUpdated": "2026-10-13",
    "asOf": AS_OF, "sourceName": "PropertyHub Building C 單筆掛牌",
    "source": PH_PROJECT, "minimumSourceUrl": PH_SALE, "minimumSqmSourceUrl": PH_SALE,
    "samples": [{
        "id": "6267709", "price": 1690000, "area": 33.0, "priceSqm": 51212,
        "beds": 1, "roomType": "1BR", "title": "Grand Park Town Building C，1 房，33 ㎡，฿1,690,000",
        "url": PH_SALE, "sourceName": "PropertyHub",
        "projectName": NAME, "updated": "2026-10-13", "checkedAt": AS_OF,
        "matchedBy": "exact_building_name_on_project_listing_and_direct_listing_id",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }],
    "byBedroom": {"1": {
        "count": 1, "minimum": 1690000, "area": 33.0, "minimumArea": 33.0,
        "minimumSqm": 51212, "sourceUrl": PH_SALE,
        "minimumSourceUrl": PH_SALE, "minimumSqmSourceUrl": PH_SALE,
    }},
}
manual, suffix = read_rows("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", -1)) != ID]
manual.append({"hipflatId": ID, "name": NAME, "sale": sale})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_rows("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual, suffix)

crosschecks, suffix = read_rows("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != ID]
crosschecks.append({
    "hipflatId": ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "PropertyHub／Thailand-Property／Hipflat",
    "projectSourceUrl": HIPFLAT,
    "location": {"lat": LAT, "lng": LNG, "sourceUrl": TP,
                 "verificationMethod": "exact project name/address and embedded GPS"},
    "sale": {"activeListingCount": 1, "sourceUrl": PH_PROJECT,
             "listings": [{"id": "6267709", "bedrooms": 1, "price": 1690000,
                           "area": 33.0, "priceSqm": 51212, "updatedAt": "2026-10-13",
                           "url": PH_SALE}],
             "note": "PropertyHub project listings refreshed 2026-10-13 include this exact Building C one-bedroom unit; listed total ฿1,690,000 / 33 sqm."},
    "rent": {"activeListingCount": 0, "sourceUrl": "https://propertyhub.in.th/en/condo-for-rent/project-grand-park-town",
             "note": "No current rental listing explicitly matches Building C in the checked PropertyHub project results. Hipflat's ฿18,500 figure is a project summary without a verifiable individual unit link; Propso Building C rentals are over 30 days old. Neither is used as a current rent sample or for yield."},
    "availabilitySources": [
        {"sourceName": "Hipflat exact project", "url": HIPFLAT,
         "statusLabel": "Exact project name and address 584/20 Soi Aminsen; Hipflat has price summaries but no directly verifiable individual rent sample."},
        {"sourceName": "Thailand-Property exact Building C page", "url": TP,
         "statusLabel": "Exact Building C page lists 8 floors, completed 2006, and embeds GPS 13.772468, 100.593594."},
        {"sourceName": "PropertyHub project listings", "url": PH_PROJECT,
         "statusLabel": "Refreshed 2026-10-13; exact Building C 1BR, 33 sqm, ฿1,690,000 listing; current displayed rent samples are other buildings or do not identify Building C."},
    ],
    "yieldStatus": "not_calculated_no_current_exact_building_rent_listing",
    "yieldNote": "A current sale sample exists, but no current Building C rental sample with an individual property link was verified. Do not calculate ROI from a project-level rent summary or stale Building C rental ads.",
})
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
write_rows("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks, suffix)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
for old, new in [
    ("bangkok-verified-coordinates.js?v=20261020-93-residence-gps", "bangkok-verified-coordinates.js?v=20261020-grand-park-town-c-gps"),
    ("bangkok-manual-market-samples.js?v=20261020-happy-condo-building-h", "bangkok-manual-market-samples.js?v=20261020-grand-park-town-c-sale"),
    ("bangkok-market-crosschecks.js?v=20261020-93-residence-availability", "bangkok-market-crosschecks.js?v=20261020-grand-park-town-c-market"),
]:
    if old not in html:
        raise ValueError(f"Cache reference not found: {old}")
    html = html.replace(old, new, 1)
index_path.write_text(html, encoding="utf-8")

report_path = ROOT / "reports" / "grand-park-town-building-c-2026-10-20.json"
report_path.write_text(json.dumps({"hipflatId": ID, "coordinates": [LAT, LNG],
                                   "coordinateSource": TP, "saleSource": PH_SALE,
                                   "sale": {"price": 1690000, "areaSqm": 33, "beds": 1,
                                            "updatedAt": "2026-10-13"},
                                   "rent": "No current exact-building direct listing found; yield not calculated.",
                                   "checkedAt": AS_OF}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Enriched {NAME}: GPS verified, one exact recent sale listing, no current exact-building rent/yield.")
