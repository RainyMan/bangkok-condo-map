"""Add verified Commune 80 coordinates and direct sale samples."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
CHECKED = "2026-10-19"
PROJECT_ID = 3412
NAME = "Commune 80"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/commune-80-ohmrsq"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/commune-80-lat-phrao"
PROPERTYHUB_SALE_URLS = {
    "one_bed": "https://propertyhub.in.th/listings/a033884-commune-80---6005709",
    "two_bed_low": "https://propertyhub.in.th/listings/pet-friendly-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-commune-80-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-80-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88%E0%B8%AA%E0%B8%B8%E0%B8%94-%E0%B8%97%E0%B8%B1%E0%B9%89%E0%B8%87%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%A1%E0%B8%B5%E0%B9%81%E0%B8%84%E0%B9%88-20-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87-%E0%B9%80%E0%B8%A5%E0%B8%B5%E0%B9%89%E0%B8%A2%E0%B8%87%E0%B8%AA%E0%B8%B1%E0%B8%95%E0%B8%A7%E0%B9%8C%E0%B8%ได้-%E0%B9%80%E0%B8%9B%E0%B8%B4%E0%B8%94%E0%B9%80%E0%B8%9C%E0%B8%A2---6087703",
    "two_bed_second": "https://propertyhub.in.th/listings/cs528-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%84%E0%B8%AD%E0%B8%A1%E0%B8%A1%E0%B8%B9%E0%B8%99%E0%B9%80%E0%B8%AD%E0%B8%95%E0%B8%95%E0%B8%B5%E0%B9%89-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-mrt-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-064-665-4666---5667619",
}
TWO_BED_CROSSCHECK_URL = "https://www.livinginsider.com/detail/condo-for-sale-condo-commune-80-2bedroom-3180857"
ARCGIS_QUERY = "Commune 80 Lat Phrao, 21 Soi Lat Phrao 80, Yaek 22, Wang Thonglang, Bangkok 10310, Thailand"
LAT, LNG = 13.782609541, 100.602739134
ARCGIS_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?" + urlencode(
    {"SingleLine": ARCGIS_QUERY, "f": "json", "outFields": "*", "maxLocations": 1}
)
MAP_URL = f"https://www.google.com/maps/search/?api=1&query={LAT}%2C{LNG}"


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript array format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


def upsert(rows: list[dict], key: str, value: int, record: dict) -> None:
    index = next((i for i, row in enumerate(rows) if int(row.get(key, -1)) == value), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record


catalogue_prefix, catalogue, catalogue_suffix = load_array(
    "bangkok-catalogue.js", "window.BANGKOK_CONDO_CATALOGUE"
)
coordinates_prefix, coordinates, coordinates_suffix = load_array(
    "bangkok-verified-coordinates.js", "window.BANGKOK_VERIFIED_COORDINATES"
)
manual_prefix, manual_rows, manual_suffix = load_array(
    "bangkok-manual-market-samples.js", "window.BANGKOK_MANUAL_MARKET_SAMPLES"
)
cross_prefix, crosschecks, cross_suffix = load_array(
    "bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS"
)

project = next(row for row in catalogue if int(row["id"]) == PROJECT_ID)
project.update(
    {
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "locationSourceUrl": MAP_URL,
        "addressSourceUrl": HIPFLAT_URL,
    }
)
completeness = dict(project.get("dataCompleteness") or {})
completeness.update({"coordinates": True, "saleSample": True, "rentSample": False, "yield": False})
project["dataCompleteness"] = completeness
project["marketDataStatus"] = "verified_sale_listings_rentage_unavailable"

upsert(
    coordinates,
    "hipflatId",
    PROJECT_ID,
    {
        "hipflatId": PROJECT_ID,
        "name": NAME,
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "sourceName": "Google Maps 點位（ArcGIS 專案 POI 核對）",
        "sourceUrl": MAP_URL,
        "verificationSourceUrl": ARCGIS_URL,
        "corroborationSourceUrl": HIPFLAT_URL,
        "verificationMethod": "ArcGIS World Geocoding Service returned the named Commune 80 Lat Phrao estate POI at score 100, with matching address 21 Soi Lat Phrao 80 Yaek 22. Hipflat and PropertyHub project pages show the same project name and address.",
        "asOf": CHECKED,
    },
)

sale_samples = [
    {
        "id": "6005709",
        "kind": "sale",
        "price": 2_800_000,
        "area": 70,
        "priceSqm": 40_000,
        "beds": 1,
        "roomType": "1BR",
        "title": "A033884 Commune 80 · 1 房 · 70 ㎡ · ฿2,800,000",
        "url": PROPERTYHUB_SALE_URLS["one_bed"],
        "sourceName": "PropertyHub 直接出售掛牌",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "direct_listing_linked_from_exact_PropertyHub_project_page",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6087703",
        "kind": "sale",
        "price": 2_989_000,
        "area": 70,
        "priceSqm": 42_700,
        "beds": 2,
        "roomType": "2BR",
        "title": "Commune 80 · 2 房（廣告標示；第二房可由客廳轉換）· 70 ㎡ · ฿2,989,000",
        "url": PROPERTYHUB_SALE_URLS["two_bed_low"],
        "sourceName": "PropertyHub 直接出售掛牌",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "direct_listing_linked_from_exact_PropertyHub_project_page",
        "listingStatus": "active_as_listed",
        "bedroomDefinitionNote": "掛牌規格列 2 房、2 衛；說明指出第二房由客廳空間轉換。仍按賣方標示 2 房列入最低 2 房，供使用者開啟原物件確認。",
    },
    {
        "id": "5667619",
        "kind": "sale",
        "price": 3_090_000,
        "area": 70,
        "priceSqm": 44_142.86,
        "beds": 2,
        "roomType": "2BR",
        "title": "CS528 Commune 80 · 2 房 · 70 ㎡ · ฿3,090,000",
        "url": PROPERTYHUB_SALE_URLS["two_bed_second"],
        "sourceName": "PropertyHub 直接出售掛牌",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "direct_listing_linked_from_exact_PropertyHub_project_page",
        "listingStatus": "active_as_listed",
    },
]
prices = [row["price"] for row in sale_samples]
areas = [row["area"] for row in sale_samples]
sale_rates = [row["price"] / row["area"] for row in sale_samples]
by_bedroom = {
    "1": {
        "count": 1,
        "minimum": 2_800_000,
        "area": 70,
        "minimumArea": 70,
        "minimumSqm": 40_000,
        "averageSqm": 40_000,
        "sourceUrl": PROPERTYHUB_SALE_URLS["one_bed"],
        "minimumSourceUrl": PROPERTYHUB_SALE_URLS["one_bed"],
        "minimumSqmSourceUrl": PROPERTYHUB_SALE_URLS["one_bed"],
    },
    "2": {
        "count": 2,
        "minimum": 2_989_000,
        "area": 70,
        "minimumArea": 70,
        "minimumSqm": 42_700,
        "averageSqm": 43_421,
        "sourceUrl": PROPERTYHUB_SALE_URLS["two_bed_low"],
        "minimumSourceUrl": PROPERTYHUB_SALE_URLS["two_bed_low"],
        "minimumSqmSourceUrl": PROPERTYHUB_SALE_URLS["two_bed_low"],
    },
}
sale_market = {
    "count": 7,
    "observedCount": len(sale_samples),
    "countKind": "manual_verified_listing",
    "average": round(sum(prices) / len(prices)),
    "minimum": 2_800_000,
    "minimumArea": 70,
    "averageSqm": round(sum(sale_rates) / len(sale_rates)),
    "minimumSqm": 40_000,
    "asOf": CHECKED,
    "sourceName": "PropertyHub 直接出售掛牌",
    "source": PROPERTYHUB_PROJECT_URL,
    "minimumSourceUrl": PROPERTYHUB_SALE_URLS["one_bed"],
    "minimumSqmSourceUrl": PROPERTYHUB_SALE_URLS["one_bed"],
    "byBedroom": by_bedroom,
    "samples": sale_samples,
    "note": "平均值以三筆可直接開啟的挂牌樣本計算；兩房最低按賣方 2 房標示，物件描述指出第二房可由客廳轉換。",
}
rent_market = {
    "count": 0,
    "observedCount": 0,
    "countKind": "manual_availability_check",
    "asOf": CHECKED,
    "sourceName": "PropertyHub 專案頁／Hipflat 專案頁庫存核對",
    "source": PROPERTYHUB_PROJECT_URL,
    "samples": [],
}
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": NAME}
    manual_rows.append(manual)
manual.update(
    {
        "name": NAME,
        "asOf": CHECKED,
        "sale": sale_market,
        "rent": rent_market,
        "replaceSale": True,
        "replaceRent": True,
    }
)

upsert(
    crosschecks,
    "hipflatId",
    PROJECT_ID,
    {
        "hipflatId": PROJECT_ID,
        "projectName": NAME,
        "asOf": CHECKED,
        "sourceName": "PropertyHub／Hipflat／LivingInsider",
        "projectSourceUrl": PROPERTYHUB_PROJECT_URL,
        "sale": {
            "activeListingCount": 7,
            "sourceUrl": PROPERTYHUB_PROJECT_URL,
            "listings": [
                {
                    "url": PROPERTYHUB_SALE_URLS["one_bed"],
                    "price": 2_800_000,
                    "area": 70,
                    "bedrooms": 1,
                    "priceSqm": 40_000,
                    "checkedAt": CHECKED,
                },
                {
                    "url": PROPERTYHUB_SALE_URLS["two_bed_low"],
                    "price": 2_989_000,
                    "area": 70,
                    "bedrooms": 2,
                    "priceSqm": 42_700,
                    "checkedAt": CHECKED,
                },
                {
                    "url": PROPERTYHUB_SALE_URLS["two_bed_second"],
                    "price": 3_090_000,
                    "area": 70,
                    "bedrooms": 2,
                    "priceSqm": 44_143,
                    "checkedAt": CHECKED,
                },
            ],
            "note": "PropertyHub 詳細頁顯示 7 筆，另一個同專案掛牌頁顯示 8 筆；市場頁數有快取差異，已逐一記錄三筆直連物件。",
        },
        "rent": {
            "activeListingCount": 0,
            "sourceUrl": PROPERTYHUB_PROJECT_URL,
            "note": "PropertyHub 直接掛牌頁顯示本專案 0 筆出租；Hipflat 專案頁目前只列出售物件，故未估租金與投報率。",
        },
        "availabilitySources": [
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT_URL, "statusLabel": "列出 5 筆出售，無出租掛牌。"},
            {"sourceName": "PropertyHub 專案頁", "url": PROPERTYHUB_PROJECT_URL, "statusLabel": "檢視到 7–8 筆出售掛牌；租盤顯示 0 筆。"},
            {"sourceName": "PropertyHub 兩房直接掛牌", "url": PROPERTYHUB_SALE_URLS["two_bed_low"], "statusLabel": "賣方標示 2 房、70㎡、฿2,989,000；描述指出第二房由客廳轉換。"},
            {"sourceName": "PropertyHub 另一筆兩房掛牌", "url": PROPERTYHUB_SALE_URLS["two_bed_second"], "statusLabel": "2 房、70㎡、฿3,090,000。"},
            {"sourceName": "LivingInsider 兩房掛牌交叉核對", "url": TWO_BED_CROSSCHECK_URL, "statusLabel": "2 房、69.16㎡、฿3,500,000；作為獨立平台交叉資料。"},
        ],
        "yieldStatus": "not_calculated",
        "yieldNote": "找到兩房出售掛牌，但兩個房源網的專案頁目前都沒有出租掛牌；缺少同房型租金，故不計投報率。",
    },
)

save_array("bangkok-catalogue.js", catalogue_prefix, catalogue, catalogue_suffix)
save_array("bangkok-verified-coordinates.js", coordinates_prefix, coordinates, coordinates_suffix)
save_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix)
save_array("bangkok-market-crosschecks.js", cross_prefix, crosschecks, cross_suffix)

report = {
    "checkedAt": CHECKED,
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "coordinate": {"lat": LAT, "lng": LNG, "googleMaps": MAP_URL, "arcgis": ARCGIS_URL, "hipflat": HIPFLAT_URL},
    "saleSamples": [
        {"id": sample["id"], "beds": sample["beds"], "priceTHB": sample["price"], "areaSqm": sample["area"], "pricePerSqm": sample["priceSqm"], "url": sample["url"]}
        for sample in sale_samples
    ],
    "rentListingCount": 0,
    "roiCalculated": False,
    "roiReason": "No direct rental listing was available on the inspected project pages.",
    "sampleCountCaveat": "PropertyHub pages returned 7 versus 8 project sales; three directly accessible units were recorded. The lowest two-bedroom sample is seller-labelled 2BR but its description says its second room is convertible from the living room.",
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "commune-80-verified-market-enrichment-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index_path = DIST / "index.html"
index = index_path.read_text(encoding="utf-8")
for pattern, replacement in [
    (r"bangkok-catalogue\.js\?v=[^\"']+", "bangkok-catalogue.js?v=20261019-commune-80-verified-market"),
    (r"bangkok-verified-coordinates\.js\?v=[^\"']+", "bangkok-verified-coordinates.js?v=20261019-commune-80-verified-market"),
    (r"bangkok-manual-market-samples\.js\?v=[^\"']+", "bangkok-manual-market-samples.js?v=20261019-commune-80-verified-market"),
    (r"bangkok-market-crosschecks\.js\?v=[^\"']+", "bangkok-market-crosschecks.js?v=20261019-commune-80-verified-market"),
]:
    index, count = re.subn(pattern, replacement, index, count=1)
    if count != 1:
        raise RuntimeError(f"Could not update cache tag for {replacement}")
index_path.write_text(index, encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "coordinatesVerified": 1, "directSaleSamplesAdded": len(sale_samples), "directRentSamplesAdded": 0, "rentListings": 0, "roiCalculated": False}, ensure_ascii=False))
