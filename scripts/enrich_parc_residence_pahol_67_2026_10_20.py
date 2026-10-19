"""Add verified location and linked sale/rent samples for Parc Residence @ Pahol 67."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3441
NAME = "Parc Residence @Pahol 67"
CHECKED_AT = "2026-10-20"
ADDRESS = "318 Phahonyothin Road, Soi Phahonyothin 67, Anusawari, Bang Khen, Bangkok 10220, THA"
LAT, LNG = 13.888333, 100.600059
GOOGLE_MAPS = "https://www.google.com/maps/search/?api=1&query=13.888333%2C100.600059"
COORD_SOURCE = "https://www.homenayoo.com/parc-residence-pahol/"
DD_PROJECT = "https://www.ddproperty.com/en/project/8851-parc-residence-pahol67"
DD_SALE = "https://www.ddproperty.com/property/parc-residence-pahol67-%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%84-%E0%B9%80%E0%B8%A3%E0%B8%AA%E0%B8%8B%E0%B8%B4%E0%B9%80%E0%B8%94%E0%B9%87%E0%B8%99%E0%B8%8B%E0%B9%8C-%E0%B9%81%E0%B8%97%E0%B8%97-%E0%B8%9E%E0%B8%AB%E0%B8%A5-67-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B8%82%E0%B8%B2%E0%B8%A2-11851317"
PH_PROJECT_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-parc-residence-phahol"
PH_RENT = "https://propertyhub.in.th/en/listings/for-rent-parc-residence-phaholyothin-67---6274352"

sale_sample = {
    "id": "11851317", "price": 1390000, "area": 29.25, "priceSqm": 47521,
    "beds": 1, "roomType": "1BR", "title": "Parc Residence @Pahol 67，1 房，29.25 ㎡，฿1,390,000",
    "url": DD_SALE, "sourceName": "DDproperty", "projectName": NAME,
    "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_address",
    "listingStatus": "active_as_listed",
    "verificationNote": "DDproperty 單筆列 1 房、29.25㎡、฿1,390,000；DD 專案頁核對時列 3 筆出售且起價฿1,390,000。",
}
rent_sample = {
    "id": "6274352", "price": 8000, "area": 29.26, "priceSqm": 273,
    "beds": 1, "roomType": "1BR", "title": "Parc Residence @ Phahol，1 房，29.26 ㎡，฿8,000/月",
    "url": PH_RENT, "sourceName": "PropertyHub", "projectName": NAME,
    "updated": "2026-08-04", "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_project_listing_page",
    "listingStatus": "availability_unconfirmed_update_over_30d",
    "verificationNote": "PropertyHub 專案出租頁列一筆 1 房、29.26㎡、฿8,000/月，最新刷新日 2026-08-04；DDproperty 專案頁核對時出租 0 筆。刊登存續與可租狀態未確認，逾 30 日不納入投報基準。",
}


def load_array(filename: str, symbol: str):
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format: {filename}")
    return path, match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(path: Path, prefix: str, rows: list[dict], suffix: str, compact: bool = True):
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    path.write_text(prefix + json.dumps(rows, ensure_ascii=False, **options) + suffix, encoding="utf-8")


def upsert(rows: list[dict], key: str, value: dict):
    row = next((item for item in rows if int(item.get(key, -1)) == PROJECT_ID), None)
    if row is None:
        rows.append(value)
    else:
        row.update(value)
    return row or value


# Catalogue/address and current cached PropertyHub coordinate layer.
for filename, symbol, key in [
    ("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", "id"),
    ("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", "id"),
]:
    path, prefix, rows, suffix = load_array(filename, symbol)
    project = next((row for row in rows if int(row.get(key, -1)) == PROJECT_ID), None)
    if not project:
        raise RuntimeError(f"Project {PROJECT_ID} missing from {filename}")
    project.update({"address": ADDRESS, "completedYear": 2016, "completedYearSourceUrl": COORD_SOURCE})
    if filename == "bangkok-catalogue.js":
        project.update({
            "locationVerified": True,
            "locationSourceUrl": GOOGLE_MAPS,
            "locationVerificationSourceUrl": COORD_SOURCE,
            "marketDataStatus": "verified_coordinates_and_linked_sale_rent_samples_rent_stale",
            "dataCompleteness": {**project.get("dataCompleteness", {}), "coordinates": True, "saleSample": True, "rentSample": True, "yield": False},
        })
    else:
        project.update({"locationVerified": True, "locationSourceUrl": GOOGLE_MAPS, "locationVerificationSourceUrl": COORD_SOURCE})
    save_array(path, prefix, rows, suffix)

# Source-linked project coordinate; Homenayoo publishes the map coordinates and
# describes the same project on Soi Phahonyothin 67 near BTS Sai Yud.
path, prefix, rows, suffix = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
upsert(rows, "hipflatId", {
    "hipflatId": PROJECT_ID, "name": NAME, "lat": LAT, "lng": LNG,
    "locationVerified": True, "sourceName": "Homenayoo 專案頁 Google Maps 座標",
    "sourceUrl": GOOGLE_MAPS, "verificationSourceUrl": COORD_SOURCE,
    "corroborationSourceUrl": DD_PROJECT,
    "verificationMethod": "Published Google Maps coordinates on the project review; project address independently matches Phahonyothin 67 on DDproperty.",
})
save_array(path, prefix, rows, suffix)

# Manual market data preserves both direct listing links. The older rent is
# retained for provenance but excluded from ROI until availability is refreshed.
path, prefix, rows, suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": NAME}
    rows.append(manual)
manual.update({
    "asOf": CHECKED_AT,
    "replaceSale": True,
    "sale": {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": 1390000, "minimum": 1390000, "minimumArea": 29.25,
        "minimumSampleUpdated": None, "averageSqm": 47521, "minimumSqm": 47521,
        "minimumSqmSampleUpdated": None, "asOf": CHECKED_AT,
        "sourceName": "DDproperty 個別出售掛牌", "source": DD_PROJECT,
        "minimumSourceUrl": DD_SALE, "minimumSqmSourceUrl": DD_SALE,
        "samples": [sale_sample],
        "byBedroom": {"1": {"count": 1, "minimum": 1390000, "area": 29.25, "minimumArea": 29.25, "priceSqm": 1390000 / 29.25, "minimumSqm": 1390000 / 29.25, "sourceUrl": DD_SALE, "minimumSourceUrl": DD_SALE, "minimumSqmSourceUrl": DD_SALE}},
    },
    "replaceRent": True,
    "rent": {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": 8000, "minimum": 8000, "minimumArea": 29.26,
        "minimumSampleUpdated": "2026-08-04", "averageSqm": 273, "minimumSqm": 273,
        "minimumSqmSampleUpdated": "2026-08-04", "asOf": CHECKED_AT,
        "sourceName": "PropertyHub 個別出租掛牌；現況待確認", "source": PH_PROJECT_RENT,
        "minimumSourceUrl": PH_RENT, "minimumSqmSourceUrl": PH_RENT,
        "samples": [rent_sample],
        "byBedroom": {"1": {"count": 1, "minimum": 8000, "area": 29.26, "minimumArea": 29.26, "priceSqm": 8000 / 29.26, "minimumSqm": 8000 / 29.26, "sourceUrl": PH_RENT, "minimumSourceUrl": PH_RENT, "minimumSqmSourceUrl": PH_RENT}},
    },
})
save_array(path, prefix, rows, suffix)

# Cross-check the freshness disagreement; don't compute yield from an older
# unconfirmed rent when DDproperty has no rent listings for this project.
path, prefix, rows, suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
upsert(rows, "hipflatId", {
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": CHECKED_AT,
    "sourceName": "DDproperty + PropertyHub + Homenayoo",
    "projectSourceUrl": "https://www.hipflat.co.th/en/projects/parc-residence-at-pahol-kforqw",
    "sale": {"activeListingCount": 3, "displayedResultCount": 3, "observedCount": 1, "sourceUrl": DD_PROJECT,
             "note": "DDproperty 專案頁核對列出售 3 筆，起價฿1,390,000；其中一筆單筆頁可核對 1 房、29.25㎡、฿1,390,000。", "listings": [{"listingId": "11851317", "price": 1390000, "area": 29.25, "priceSqm": 1390000 / 29.25, "bedrooms": 1, "url": DD_SALE, "sourceName": "DDproperty", "statusLabel": "DD 專案頁列 3 筆出售；現行狀態待點入確認"}]},
    "rent": {"activeListingCount": 1, "displayedResultCount": 1, "observedCount": 1, "sourceUrl": PH_PROJECT_RENT,
             "note": "PropertyHub 專案頁列 1 筆 1 房出租，29.26㎡、฿8,000/月，最後刷新 2026-08-04；已超過 30 日。DDproperty 專案頁同時顯示出租 0 筆，故可用狀態未核實，不納入投報試算。", "listings": [{"listingId": "6274352", "price": 8000, "area": 29.26, "priceSqm": 8000 / 29.26, "bedrooms": 1, "listedAt": None, "lastRefreshed": "2026-08-04", "url": PH_RENT, "sourceName": "PropertyHub", "statusLabel": "超過 30 日未刷新；DD 專案頁顯示 0 筆出租，現況待確認"}]},
    "availabilitySources": [
        {"sourceName": "Homenayoo 專案與座標頁", "url": COORD_SOURCE, "statusLabel": "專案位於 Soi Phahonyothin 67；頁面公布 Google Maps 座標 13.888333, 100.600059，並標示 2016 完工。"},
        {"sourceName": "Google Maps 點位", "url": GOOGLE_MAPS, "statusLabel": "13.888333, 100.600059。"},
        {"sourceName": "DDproperty 個別出售掛牌", "url": DD_SALE, "statusLabel": "1 房、29.25㎡、฿1,390,000；DD 專案頁列出售 3 筆。"},
        {"sourceName": "PropertyHub 個別出租掛牌", "url": PH_RENT, "statusLabel": "1 房、29.26㎡、฿8,000/月；頁面顯示可租開始日 2026-08-09，專案頁最後刷新 2026-08-04；現況待確認。"},
        {"sourceName": "DDproperty 出租專案頁", "url": "https://www.ddproperty.com/en/condo-for-rent/at-parc-residence-pahol67-8851", "statusLabel": "核對時顯示 0 筆出租，與 PropertyHub 舊掛牌可用狀態不一致。"},
    ],
    "yieldStatus": "not_calculated_rent_availability_unconfirmed",
    "yieldNote": "有可核對的出售掛牌，但租盤最後刷新於 2026-08-04 且另一平台顯示 0 筆出租；為避免用過期租金冒充現行報酬率，暫不計投報。",
})
save_array(path, prefix, rows, suffix, compact=False)

# Cache bust the five changed runtime data assets.
html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
for name in ["bangkok-catalogue.js", "bangkok-propertyhub-map.js", "bangkok-verified-coordinates.js", "bangkok-manual-market-samples.js", "bangkok-market-crosschecks.js"]:
    html = re.sub(rf"({re.escape(name)}\?v=)[^\"']+", rf"\g<1>20261020-parc-residence-3441", html)
html_path.write_text(html, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": CHECKED_AT,
    "coordinates": {"lat": LAT, "lng": LNG, "source": GOOGLE_MAPS, "verificationSource": COORD_SOURCE},
    "sale": sale_sample, "rent": rent_sample,
    "yieldStatus": "not_calculated_rent_availability_unconfirmed",
    "sources": [COORD_SOURCE, DD_PROJECT, DD_SALE, PH_PROJECT_RENT, PH_RENT],
    "notes": ["PropertyHub rent page last refreshed 2026-08-04; DDproperty rent page showed zero listings, so present availability is not verified.", "No ROI is calculated until a current rent sample is confirmed."],
}
(REPORTS / "parc-residence-pahol-67-enrichment-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": [LAT, LNG], "sale": 1390000, "rent": 8000, "yield": "withheld_until_rent_availability_is_verified"}, ensure_ascii=False))
