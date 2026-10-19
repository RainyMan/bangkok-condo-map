"""Verify Murraya Place Ladprao 27 (I-SHAPE) location and direct listings."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ID = 3498
NAME = "Murraya Place Condominium - I-SHAPE"
AS_OF = "2026-10-20"
HIPFLAT = "https://www.hipflat.co.th/en/projects/murraya-place-condominium-ishape-evvpij"
TOOKTEE = "https://www.tooktee.com/en/project/2359/murraya-place-ladprao-27"
PH_PROJECT = "https://propertyhub.in.th/en/projects/murraya-place-ladprao-27"
PH_SALE = "https://propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B9%80%E0%B8%A1%E0%B8%AD%E0%B8%A3%E0%B9%8C%E0%B8%A3%E0%B8%B2%E0%B8%8D%E0%B8%B2-%E0%B9%80%E0%B8%9E%E0%B8%A5%E0%B8%AA-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-27-murraya-place-ladprao-27-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-mrt-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7---6312448"
PH_RENT = "https://propertyhub.in.th/listings/r8629-050169-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-murraya%E2%80%8B-place-ladproa27-condo---5689038"
LAT, LNG = 13.8042, 100.5781


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
    "locationVerified": True, "sourceName": "Tooktee 專案地圖座標",
    "sourceUrl": TOOKTEE, "verificationSourceUrl": HIPFLAT,
    "verificationMethod": "exact_project_name_alias_and_address; published_project_coordinates",
    "mapUrl": f"https://www.google.com/maps/search/?api=1&query={LAT}%2C{LNG}",
    "note": "Tooktee project page publishes coordinates 13.8042,100.5781 and Google Maps coordinates; Hipflat I-SHAPE name/address aligns with PropertyHub's Murraya Place Ladprao 27 (I-SHAPE) alias, 79 units, 8 floors, completed 2009.",
})
coords.sort(key=lambda row: int(row["hipflatId"]))
write_rows("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coords, suffix)

sale = {
    "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
    "average": 1700000, "minimum": 1700000, "minimumArea": 34.18,
    "minimumSampleUpdated": "2026-10-18", "averageSqm": 49737,
    "minimumSqm": 49737, "minimumSqmSampleUpdated": "2026-10-18",
    "asOf": AS_OF, "sourceName": "PropertyHub 單筆出售掛牌",
    "source": PH_PROJECT, "minimumSourceUrl": PH_SALE, "minimumSqmSourceUrl": PH_SALE,
    "samples": [{
        "id": "6312448", "price": 1700000, "area": 34.18, "priceSqm": 49737,
        "beds": 1, "roomType": "1BR", "title": "Murraya Place Ladprao 27，1 房，34.18 ㎡，฿1,700,000",
        "url": PH_SALE, "sourceName": "PropertyHub", "projectName": NAME,
        "updated": "2026-10-18", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_propertyhub_i_shape_alias",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }],
    "byBedroom": {"1": {
        "count": 1, "minimum": 1700000, "area": 34.18, "minimumArea": 34.18,
        "minimumSqm": 49737, "sourceUrl": PH_SALE,
        "minimumSourceUrl": PH_SALE, "minimumSqmSourceUrl": PH_SALE,
    }},
}
rent = {
    "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
    "average": 19000, "minimum": 19000, "minimumArea": 60,
    "minimumSampleUpdated": "2026-10-17", "averageSqm": 317,
    "minimumSqm": 317, "minimumSqmSampleUpdated": "2026-10-17",
    "asOf": AS_OF, "sourceName": "PropertyHub 單筆出租掛牌",
    "source": "https://propertyhub.in.th/en/condo-for-rent/project-murraya-place-ladprao-27",
    "minimumSourceUrl": PH_RENT, "minimumSqmSourceUrl": PH_RENT,
    "samples": [{
        "id": "5689038", "price": 19000, "area": 60, "priceSqm": 317,
        "beds": 2, "roomType": "2BR", "title": "Murraya Place Ladprao 27，2 房，60 ㎡，฿19,000/月",
        "url": PH_RENT, "sourceName": "PropertyHub", "projectName": NAME,
        "updated": "2026-10-17", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_propertyhub_i_shape_alias",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }],
    "byBedroom": {"2": {
        "count": 1, "minimum": 19000, "area": 60, "minimumArea": 60,
        "minimumSqm": 317, "sourceUrl": PH_RENT,
        "minimumSourceUrl": PH_RENT, "minimumSqmSourceUrl": PH_RENT,
    }},
}
manual, suffix = read_rows("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", -1)) != ID]
manual.append({"hipflatId": ID, "name": NAME, "sale": sale, "rent": rent})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_rows("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual, suffix)

crosschecks, suffix = read_rows("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != ID]
crosschecks.append({
    "hipflatId": ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "Hipflat／Tooktee／PropertyHub",
    "projectSourceUrl": HIPFLAT,
    "location": {"lat": LAT, "lng": LNG, "sourceUrl": TOOKTEE,
                 "verificationMethod": "exact project name/address and published project coordinates"},
    "sale": {"activeListingCount": 1, "sourceUrl": PH_PROJECT,
             "listings": [{"id": "6312448", "bedrooms": 1, "price": 1700000,
                           "area": 34.18, "priceSqm": 49737, "updatedAt": "2026-10-18",
                           "url": PH_SALE}],
             "note": "PropertyHub project search showed this exact Murraya Place listing refreshed 2026-10-18: 1 bedroom, 34.18 sqm, ฿1,700,000."},
    "rent": {"activeListingCount": 1,
             "sourceUrl": "https://propertyhub.in.th/en/condo-for-rent/project-murraya-place-ladprao-27",
             "listings": [{"id": "5689038", "bedrooms": 2, "price": 19000,
                           "area": 60, "priceSqm": 317, "updatedAt": "2026-10-17",
                           "url": PH_RENT}],
             "note": "PropertyHub project search showed this exact Murraya Place listing refreshed 2026-10-17: 2 bedrooms, 60 sqm, ฿19,000/month."},
    "availabilitySources": [
        {"sourceName": "Hipflat exact project", "url": HIPFLAT,
         "statusLabel": "Murraya Place Condominium - I-SHAPE, Soi Lat Phrao 27."},
        {"sourceName": "Tooktee project map", "url": TOOKTEE,
         "statusLabel": "Exact Murraya Place Ladprao 27 project page publishes coordinates 13.8042, 100.5781 and a Google Maps link."},
        {"sourceName": "PropertyHub project details", "url": PH_PROJECT,
         "statusLabel": "Project alias includes Murraya Place Ladprao 27 (I-SHAPE), 79 units, 8 floors, completed 2009; project-page listings refreshed Oct 18 (sale) and Oct 17 (rent)."},
    ],
    "yieldStatus": "not_calculated_no_same_bedroom_sale_and_rent_pair",
    "yieldNote": "Verified current sample is 1BR sale and 2BR rent. No matching-room current sale/rent pair was verified; do not calculate ROI by mixing different room types.",
})
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
write_rows("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks, suffix)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
for old, new in [
    ("bangkok-verified-coordinates.js?v=20261020-grand-park-town-c-gps", "bangkok-verified-coordinates.js?v=20261020-murraya-place-ladprao-27-gps"),
    ("bangkok-manual-market-samples.js?v=20261020-grand-park-town-c-sale", "bangkok-manual-market-samples.js?v=20261020-murraya-place-sale-rent"),
    ("bangkok-market-crosschecks.js?v=20261020-grand-park-town-c-market", "bangkok-market-crosschecks.js?v=20261020-murraya-place-market"),
]:
    if old not in html:
        raise ValueError(f"Cache reference not found: {old}")
    html = html.replace(old, new, 1)
index_path.write_text(html, encoding="utf-8")

report_path = ROOT / "reports" / "murraya-place-ladprao-27-2026-10-20.json"
report_path.write_text(json.dumps({
    "hipflatId": ID, "coordinates": [LAT, LNG], "coordinateSource": TOOKTEE,
    "saleSource": PH_SALE, "sale": {"price": 1700000, "areaSqm": 34.18, "beds": 1, "updatedAt": "2026-10-18"},
    "rentSource": PH_RENT, "rent": {"pricePerMonth": 19000, "areaSqm": 60, "beds": 2, "updatedAt": "2026-10-17"},
    "yield": "Not calculated: sale and rent samples are different room types.", "checkedAt": AS_OF,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Enriched {NAME}: verified location, one direct sale and one direct rent sample; no mixed-room ROI.")
