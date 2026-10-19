"""Verify L8 Residence's map location and add a current direct rent listing."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3413
PROJECT = "L8 Residence"
CHECKED_AT = "2026-10-20"
CANONICAL_ADDRESS = "7 Soi Nai Lert, Witthayu Road, Lumphini, Pathum Wan, Bangkok 10330, THA"
COORDINATES = (13.747004, 100.549181)
HIPFLAT = "https://www.hipflat.co.th/en/projects/l8-residence-xxvfpy"
COORDINATE_SOURCE = "https://www.google.com/maps/search/?api=1&query=13.747004%2C100.549181"
COORDINATE_VERIFICATION = "https://lazudi.com/th-en/bangkok/project/l8-residence-1377"
DD_RENT_PROJECT = "https://www.ddproperty.com/en/condo-for-rent/at-l8-residence-6838"
DD_SALE_PROJECT = "https://www.ddproperty.com/en/condo-for-sale/at-l8-residence-6838"
RENT_LISTING = "https://www.ddproperty.com/en/property/l8-residence-bangkok-for-rent-500653943"

sample = {
    "id": "500653943",
    "price": 75000,
    "area": 175,
    "priceSqm": 429,
    "beds": 3,
    "roomType": "3BR",
    "title": "L8 Residence，3 房，175 ㎡，฿75,000/月（來源分類：Apartment）",
    "url": RENT_LISTING,
    "sourceName": "DDproperty",
    "projectName": PROJECT,
    "updated": "2026-10-16",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_canonical_address",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "propertyType": "apartment",
    "verificationNote": "DDproperty 單筆頁於 2026-10-16 刊登，列 ฿75,000/月、3 房、175㎡；地址為 7 Soi Nai Lert, Wireless Road, Lumphini, Pathum Wan。來源將單位分類為 Apartment；Hipflat 專案頁亦將 L8 Residence 列為 apartment and condo，故作為同專案出租樣本保留，類別差異需留意。可租狀態仍待刊登者確認。",
}


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str, compact: bool = False) -> None:
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, **options) + suffix, encoding="utf-8")


# The Hipflat directory record has an incorrect district/address variant.
# Correct the display address while retaining its Hipflat project link.
for filename, symbol, compact in [
    ("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", True),
    ("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", True),
]:
    prefix, rows, suffix = load_array(filename, symbol)
    project = next((row for row in rows if int(row.get("id", -1)) == PROJECT_ID), None)
    if project is None:
        raise RuntimeError(f"L8 Residence {PROJECT_ID} missing from {filename}")
    project.update({"address": CANONICAL_ADDRESS, "locationSourceUrl": COORDINATE_SOURCE})
    if filename == "bangkok-catalogue.js":
        project["locationVerified"] = True
        project["dataCompleteness"] = {**project.get("dataCompleteness", {}), "coordinates": True, "rentSample": True, "yield": False}
        project["marketDataStatus"] = "verified_coordinates_and_recent_direct_rent_sample_no_current_sale"
    save_array(filename, prefix, rows, suffix, compact=compact)

coord_prefix, coord_rows, coord_suffix = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coord = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT,
    "lat": COORDINATES[0],
    "lng": COORDINATES[1],
    "locationVerified": True,
    "sourceName": "Google Maps 嵌入點位（Lazudi 專案頁）",
    "sourceUrl": COORDINATE_SOURCE,
    "verificationSourceUrl": COORDINATE_VERIFICATION,
    "corroborationSourceUrl": "https://www.ddproperty.com/en/project/6838-l8-residence",
    "verificationMethod": "Lazudi L8 Residence project page exposes a Google Maps embed centered at 13.747004,100.549181 and gives address 23/1 Thanon Witthayu, Lumphini, Pathum Wan, Bangkok 10330. DDproperty independently identifies the project at 7 Soi Nai Lert, Wireless Road, Lumphini, Pathum Wan and locates it 610 m from BTS Phloen Chit. Hipflat's 1673 Witthayu Rd, Makkasan, Ratchathewi, 10400 address variant is not used for the pin.",
}
existing_coord = next((row for row in coord_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing_coord is None:
    coord_rows.append(coord)
else:
    existing_coord.update(coord)
save_array("bangkok-verified-coordinates.js", coord_prefix, coord_rows, coord_suffix, compact=True)

manual_prefix, manual_rows, manual_suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
manual.update({
    "asOf": CHECKED_AT,
    "rent": {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": 75000,
        "minimum": 75000,
        "minimumArea": 175,
        "minimumSampleUpdated": "2026-10-16",
        "averageSqm": 429,
        "minimumSqm": 429,
        "minimumSqmSampleUpdated": "2026-10-16",
        "asOf": CHECKED_AT,
        "sourceName": "DDproperty 個別出租掛牌",
        "source": DD_RENT_PROJECT,
        "minimumSourceUrl": RENT_LISTING,
        "minimumSqmSourceUrl": RENT_LISTING,
        "samples": [sample],
        "byBedroom": {
            "3": {
                "count": 1,
                "minimum": 75000,
                "area": 175,
                "minimumArea": 175,
                "priceSqm": 75000 / 175,
                "minimumSqm": 75000 / 175,
                "sourceUrl": RENT_LISTING,
                "minimumSourceUrl": RENT_LISTING,
                "minimumSqmSourceUrl": RENT_LISTING,
            }
        },
    },
})
save_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix, compact=True)

cross_prefix, cross_rows, cross_suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "DDproperty + Hipflat",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": DD_SALE_PROJECT,
        "note": "DDproperty 專案出售頁於核對時沒有掛牌；Hipflat 專案頁目前亦未顯示出售單位。沒有可核實的購入價基準，不計投報率。",
        "listings": [],
    },
    "rent": {
        "activeListingCount": 1,
        "displayedResultCount": 1,
        "observedCount": 1,
        "sourceUrl": DD_RENT_PROJECT,
        "note": "DDproperty 單筆頁於 2026-10-16 刊登 3 房、175㎡、฿75,000/月。專案頁將 L8 Residence 分類為 apartment and condo；單筆分類為 Apartment，房型與價格列為同專案租屋樣本並保留分類差異。可租狀態待刊登者確認。",
        "listings": [{
            "listingId": "500653943",
            "price": 75000,
            "area": 175,
            "priceSqm": 75000 / 175,
            "bedrooms": 3,
            "listedAt": "2026-10-16",
            "url": RENT_LISTING,
            "sourceName": "DDproperty",
            "propertyType": "apartment",
            "statusLabel": "10/16 刊登；Apartment 分類；現況待刊登者確認",
        }],
    },
    "availabilitySources": [
        {"sourceName": "Google Maps 點位（Lazudi 專案頁嵌入地圖）", "url": COORDINATE_SOURCE, "statusLabel": "座標 13.747004, 100.549181；Lazudi 專案地址與地圖定位於 Pathum Wan。"},
        {"sourceName": "Lazudi L8 Residence 專案頁", "url": COORDINATE_VERIFICATION, "statusLabel": "地址 23/1 Thanon Witthayu, Lumphini, Pathum Wan, Bangkok 10330；頁面 Google Maps 嵌入點位與本案座標相符。"},
        {"sourceName": "DDproperty 出租單筆", "url": RENT_LISTING, "statusLabel": "3 房，175㎡，฿75,000/月；2026-10-16 刊登，單筆分類 Apartment。"},
        {"sourceName": "DDproperty 出售專案頁", "url": DD_SALE_PROJECT, "statusLabel": "目前沒有出售掛牌，因此不計投報率。"},
    ],
    "yieldStatus": "not_calculated_no_current_sale_listing",
    "yieldNote": "目前無可核實出售掛牌；雖已找到 3 房直連出租樣本，仍缺購入價基準，不計投報率。出租來源將房源分類為 Apartment，L8 Residence 專案來源則列為 apartment and condo。",
}
existing_crosscheck = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing_crosscheck is None:
    cross_rows.append(crosscheck)
else:
    existing_crosscheck.update(crosscheck)
save_array("bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED_AT,
    "coordinates": {"verified": True, "lat": COORDINATES[0], "lng": COORDINATES[1], "canonicalAddress": CANONICAL_ADDRESS, "sourceUrl": COORDINATE_SOURCE, "verificationSourceUrl": COORDINATE_VERIFICATION},
    "rentSample": sample,
    "saleStatus": "No current sale results on checked DDproperty project page or Hipflat project page.",
    "yieldStatus": "Not calculated: no current sale listing.",
    "sources": [HIPFLAT, COORDINATE_VERIFICATION, DD_RENT_PROJECT, RENT_LISTING, DD_SALE_PROJECT],
    "notes": [
        "Lazudi project page's Google Maps embed resolves to 13.747004,100.549181; DDproperty independently places the exact project at 7 Soi Nai Lert, Wireless Road, Lumphini, Pathum Wan.",
        "Hipflat's 1673 Witthayu Rd, Makkasan, Ratchathewi, 10400 address variant conflicts with the project-page address corroborated by Lazudi and DDproperty; the map now uses the latter.",
        "DDproperty direct rental listing 500653943 was listed 2026-10-16: 3 bedrooms, 175 sqm, ฿75,000/month (฿428.57/sqm/month). The listing is classified as Apartment; the project is described by Hipflat as apartment and condo.",
        "No current sale listing was found, so no yield is calculated.",
    ],
}
(REPORTS / "l8-residence-location-rent-enrichment-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
replacements = {
    "bangkok-catalogue.js?v=20261020-l8-residence-address-3413": "bangkok-catalogue.js?v=20261020-l8-address-3413",
    "bangkok-propertyhub-map.js?v=20261020-l8-residence-address-3413": "bangkok-propertyhub-map.js?v=20261020-l8-address-3413",
    "bangkok-verified-coordinates.js?v=20261020-l8-residence-coordinates-3413": "bangkok-verified-coordinates.js?v=20261020-l8-coordinates-3413",
    "bangkok-manual-market-samples.js?v=20261020-l8-residence-rent-3413": "bangkok-manual-market-samples.js?v=20261020-l8-rent-3413",
    "bangkok-market-crosschecks.js?v=20261020-l8-residence-rent-3413": "bangkok-market-crosschecks.js?v=20261020-l8-rent-3413",
    "app.js?v=20261020-recalculate-two-bedroom-yield-v202": "app.js?v=20261020-lowest-two-bedroom-yield-v203",
}
for old, new in replacements.items():
    if old not in html:
        raise RuntimeError(f"Missing cache-bust token: {old}")
    html = html.replace(old, new)
html_path.write_text(html, encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": COORDINATES, "rentTHB": 75000, "rentAreaSqm": 175, "rentTHBPerSqm": round(75000 / 175, 2), "sale": "no current verified listing", "yield": "not calculated"}, ensure_ascii=False))
