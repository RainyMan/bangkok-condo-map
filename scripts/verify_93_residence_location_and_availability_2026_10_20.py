"""Record 93 Residence's exact project GPS and current zero-listing checks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ID = 3502
NAME = "93 Residence"
AS_OF = "2026-10-20"
HIPFLAT = "https://www.hipflat.co.th/en/projects/93-residence-xfiznp"
THAILAND_PROPERTY = "https://www.thailand-property.com/condo/1044/93-residence"
REALTORS = "https://therealtors.net/th/project/93-residence-21"
LAT, LNG = 13.700915, 100.609726


def load_rows(filename: str, symbol: str) -> tuple[list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise ValueError(f"Unexpected {symbol} format")
    return json.loads(match.group(1)), match.group(2)


def save_rows(filename: str, symbol: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


coords, suffix = load_rows("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coords = [row for row in coords if int(row.get("hipflatId", -1)) != ID]
coords.append({
    "hipflatId": ID,
    "name": NAME,
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "Thailand-Property 專案 GPS",
    "sourceUrl": THAILAND_PROPERTY,
    "verificationSourceUrl": HIPFLAT,
    "verificationMethod": "exact_name_and_full_project_address; embedded_project_gps",
    "mapUrl": f"https://www.google.com/maps/search/?api=1&query={LAT}%2C{LNG}",
    "note": "Thailand-Property exact-project page exposes gps_lat/gps_lon and matches the Hipflat 93 Building, 237 Soi Sukhumvit 93 address.",
})
coords.sort(key=lambda row: int(row["hipflatId"]))
save_rows("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coords, suffix)

record = {
    "hipflatId": ID,
    "projectName": NAME,
    "asOf": AS_OF,
    "sourceName": "Hipflat／Thailand-Property／The Realtors",
    "projectSourceUrl": HIPFLAT,
    "location": {
        "lat": LAT,
        "lng": LNG,
        "sourceUrl": THAILAND_PROPERTY,
        "verificationMethod": "exact project name and full address match; public page GPS fields",
    },
    "sale": {
        "activeListingCount": 0,
        "sourceUrl": HIPFLAT,
        "availabilitySources": [HIPFLAT, THAILAND_PROPERTY, REALTORS],
        "note": "Hipflat says no properties are currently available; Thailand-Property reports 0 condos for sale and rent; The Realtors page reports 0 sale units. No current direct sale listing was found.",
    },
    "rent": {
        "activeListingCount": 0,
        "sourceUrl": HIPFLAT,
        "availabilitySources": [HIPFLAT, THAILAND_PROPERTY, REALTORS],
        "note": "Hipflat says no properties are currently available; Thailand-Property reports 0 condos for sale and rent; The Realtors page reports 0 rental units. No current direct rental listing was found.",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat exact project page", "url": HIPFLAT,
         "statusLabel": "Exact address 93 Building, 237 Soi Sukhumvit 93; page reports no currently available property."},
        {"sourceName": "Thailand-Property project directory", "url": THAILAND_PROPERTY,
         "statusLabel": "Exact 93 Residence page exposes GPS 13.700915, 100.609726 and reports zero sale/rent listings."},
        {"sourceName": "The Realtors project page", "url": REALTORS,
         "statusLabel": "Project page reports 0 units for sale and 0 units for rent."},
    ],
    "yieldStatus": "not_calculated_no_current_sale_or_rent_listing",
    "yieldNote": "Do not use historical sold listings or neighboring condo listings as current sale/rent inputs. No current listing pair is available, so ROI remains uncalculated.",
}
crosschecks, suffix = load_rows("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != ID]
crosschecks.append(record)
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
save_rows("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks, suffix)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html = html.replace(
    "bangkok-verified-coordinates.js?v=20261020-happy-condo-building-h",
    "bangkok-verified-coordinates.js?v=20261020-93-residence-gps",
).replace(
    "bangkok-market-crosschecks.js?v=20261020-happy-condo-building-h",
    "bangkok-market-crosschecks.js?v=20261020-93-residence-availability",
)
index_path.write_text(html, encoding="utf-8")

report = {
    "hipflatId": ID,
    "project": NAME,
    "checkedAt": AS_OF,
    "coordinates": {"lat": LAT, "lng": LNG, "source": THAILAND_PROPERTY,
                    "matchedProjectSource": HIPFLAT},
    "currentListingCheck": {
        "sale": {"count": 0, "sources": [HIPFLAT, THAILAND_PROPERTY, REALTORS]},
        "rent": {"count": 0, "sources": [HIPFLAT, THAILAND_PROPERTY, REALTORS]},
    },
    "yield": {"status": "not_calculated", "reason": "No current direct sale and rent listings."},
}
(ROOT / "reports/93-residence-location-availability-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": ID, "coordinates": [LAT, LNG],
                  "currentSaleListings": 0, "currentRentListings": 0,
                  "yield": "not calculated"}, ensure_ascii=False))
