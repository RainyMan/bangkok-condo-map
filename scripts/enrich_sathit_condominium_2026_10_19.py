"""Verify Thai Sathit Condominium's map pin and current Hipflat rental units."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_ID = 3407
NAME = "Sathit Condominium"
HIPFLAT = "https://www.hipflat.co.th/en/projects/sathit-condominium-izqutx"
GOOGLE_MAPS = (
    "https://www.google.com/maps/place/%E0%B9%84%E0%B8%97%E0%B8%A2%E0%B8%AA%E0%B8%B2%E0%B8%98%E0%B8%B4%E0%B8%95+"
    "%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1/@13.7349043,"
    "100.5122288,155m/data=!3m1!1e3!4m5!3m4!1s0x30e298df5aab0e69:0xae9193955c9d0610!8m2!3d13.7347153!4d100.5121448?shorturl=1"
)
CONDONAYOO = "https://www.condonayoo.com/thai-sathit-condominium/"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-thai-sathit-condominium"
SALE_CHECK = "https://www.hipflat.co.th/en/projects/sathit-condominium-izqutx"
RENT_35 = "https://www.hipflat.co.th/ads/9e3a494l8nlh0ae7a7nt91173u02u9e1"
RENT_55 = "https://www.hipflat.co.th/ads/2l31047c8nth42ccnl2c91n93u0he377"


def load_array(filename: str, symbol: str):
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format in {filename}")
    return path, text[:match.start(1)], json.loads(match.group(1))


def save_array(path: Path, prefix: str, rows: list[dict], *, pretty: bool = False):
    body = json.dumps(rows, ensure_ascii=False, indent=2 if pretty else None,
                      separators=None if pretty else (",", ":"))
    path.write_text(prefix + body + ";\n", encoding="utf-8", newline="\n")


project_path, _, projects = load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
project = next(row for row in projects if int(row["id"]) == PROJECT_ID)
if project.get("name") != NAME or project.get("hipflatProjectUrl") != HIPFLAT:
    raise RuntimeError("Hipflat project identity does not match the reviewed Sathit page")

rent_samples = [
    {
        "id": "9e3a494l8nlh0ae7a7nt91173u02u9e1", "kind": "rent",
        "price": 12_000, "area": 35, "priceSqm": round(12_000 / 35, 2),
        "beds": 0, "roomType": "Studio", "title": "Sathit Condominium，Studio，35㎡，฿12,000/月",
        "url": RENT_35, "sourceName": "Hipflat",
        "projectName": NAME, "checkedAt": AS_OF,
        "matchedBy": "exact_project_page_and_direct_listing_link",
        "listingStatus": "availability_unconfirmed_date_unknown",
    },
    {
        "id": "2l31047c8nth42ccnl2c91n93u0he377", "kind": "rent",
        "price": 14_000, "area": 55, "priceSqm": round(14_000 / 55, 2),
        "beds": 1, "roomType": "1BR", "title": "Sathit Condominium，1 房，55㎡，฿14,000/月",
        "url": RENT_55, "sourceName": "Hipflat",
        "projectName": NAME, "checkedAt": AS_OF,
        "matchedBy": "exact_project_page_and_direct_listing_link",
        "listingStatus": "availability_unconfirmed_date_unknown",
    },
]
lowest_total = min(rent_samples, key=lambda row: row["price"])
lowest_rate = min(rent_samples, key=lambda row: row["priceSqm"])
rent_market = {
    "count": 2, "observedCount": 2, "countKind": "manual_verified_listings",
    "average": 13_000, "minimum": lowest_total["price"],
    "minimumArea": lowest_total["area"], "averageSqm": round(sum(row["priceSqm"] for row in rent_samples) / 2, 2),
    "minimumSqm": lowest_rate["priceSqm"], "asOf": AS_OF,
    "sourceName": "Hipflat 個別出租掛牌", "source": HIPFLAT,
    "minimumSourceUrl": lowest_total["url"], "minimumSqmSourceUrl": lowest_rate["url"],
    "samples": rent_samples,
    "byBedroom": {"1": {
        "count": 1, "minimum": 14_000, "area": 55, "minimumArea": 55,
        "priceSqm": lowest_rate["priceSqm"], "minimumSqm": lowest_rate["priceSqm"],
        "averageSqm": lowest_rate["priceSqm"], "sourceUrl": RENT_55,
        "minimumSourceUrl": RENT_55, "minimumSqmSourceUrl": RENT_55,
    }},
}

coordinates_path, coordinates_prefix, coordinates = load_array(
    "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = {int(row["hipflatId"]): row for row in coordinates}
coordinate_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": NAME,
    "lat": 13.7347153, "lng": 100.5121448, "locationVerified": True,
    "sourceName": "Google Maps 專案地點",
    "sourceUrl": GOOGLE_MAPS, "verificationSourceUrl": CONDONAYOO,
    "corroborationSourceUrl": HIPFLAT,
    "verificationMethod": "Condonayoo 的 Thai Sathit 專案頁連結至 Google Maps 同名專案地點；短網址解析後地圖地標為ไทยสาธิต คอนโดมิเนียม，點位 13.7347153,100.5121448。Condonayoo 同頁標示 Vanich 2、Samphanthawong 及專案座標 13.734829,100.512332；Hipflat 地址為 882 Song Wat Rd., Talat Noi，與同一建案及街區吻合。",
    "checkedAt": AS_OF,
}
save_array(coordinates_path, coordinates_prefix,
           [coordinate_rows[key] for key in sorted(coordinate_rows)])

manual_path, manual_prefix, manual = load_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = {int(row["hipflatId"]): row for row in manual}
manual_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": NAME,
    "rent": rent_market, "replaceRent": True,
    "completedYear": 1990, "completedYearSourceUrl": HIPFLAT,
}
save_array(manual_path, manual_prefix, [manual_rows[key] for key in sorted(manual_rows)])

cross_path, cross_prefix, crosschecks = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = {int(row["hipflatId"]): row for row in crosschecks}
cross_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "Hipflat / PropertyHub / Google Maps / Condonayoo",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 0, "sourceUrl": PROPERTYHUB_SALE,
        "note": "PropertyHub Thai Sathit 出售專案頁明確顯示沒有符合出售掛牌；Hipflat 同案頁列出出租單位，沒有出售單位。歷史成交或附近專案價格不作現行購入價。",
    },
    "rent": {
        "activeListingCount": 2, "listings": rent_samples, "sourceUrl": HIPFLAT,
        "note": "Hipflat 專案頁列兩筆出租單位：Studio 35㎡ ฿12,000/月及 1 房 55㎡ ฿14,000/月；個別連結保留於每筆樣本。Hipflat 頁面未提供更新日，實際空置仍待刊登者確認。",
    },
    "availabilitySources": [
        {"sourceName": "Google Maps 專案地點", "url": GOOGLE_MAPS, "statusLabel": "同名 Thai Sathit Condominium 地標點位 13.7347153, 100.5121448。"},
        {"sourceName": "Condonayoo 專案地址與地圖連結", "url": CONDONAYOO, "statusLabel": "列 Vanich 2、Samphanthawong 及專案 Google Maps 連結；頁面坐標 13.734829, 100.512332。"},
        {"sourceName": "Hipflat 專案頁與出租清單", "url": HIPFLAT, "statusLabel": "列同案地址、1990 完工、18 樓及兩筆出租掛牌，並連至兩筆個別物件頁。"},
        {"sourceName": "Hipflat Studio 出租物件", "url": RENT_35, "statusLabel": "Studio，35㎡，฿12,000/月；來源頁未提供更新日，空置狀態待確認。"},
        {"sourceName": "Hipflat 一房出租物件", "url": RENT_55, "statusLabel": "1 房，55㎡，฿14,000/月；來源頁未提供更新日，空置狀態待確認。"},
        {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE, "statusLabel": "頁面明確顯示 0 筆符合出售掛牌。"},
    ],
    "yieldStatus": "not_calculated_no_current_sale_listing",
    "yieldNote": "目前查到兩筆同案出租掛牌，但 PropertyHub 出售專案頁為 0 筆，Hipflat 同案頁亦沒有出售掛牌；沒有現行購入價基準，不以舊成交價或附近 Condo 代算投報。",
}
save_array(cross_path, cross_prefix,
           [cross_rows[key] for key in sorted(cross_rows)], pretty=True)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html = html.replace(
    "bangkok-verified-coordinates.js?v=20261019-residence187-osm-point",
    "bangkok-verified-coordinates.js?v=20261019-sathit-google-place",
).replace(
    "bangkok-manual-market-samples.js?v=20261019-residence187-ddproperty-sale-rent",
    "bangkok-manual-market-samples.js?v=20261019-sathit-hipflat-rent-samples",
).replace(
    "bangkok-market-crosschecks.js?v=20261019-residence187-exact-listings",
    "bangkok-market-crosschecks.js?v=20261019-sathit-rent-no-sale-check",
).replace(
    "app.js?v=20261019-roi-recalc-v188",
    "app.js?v=20261019-sathit-market-v189",
)
index_path.write_text(html, encoding="utf-8", newline="\n")

report = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": AS_OF,
    "coordinates": {"lat": 13.7347153, "lng": 100.5121448,
                    "googleMapsPlace": GOOGLE_MAPS,
                    "crosscheck": CONDONAYOO},
    "sale": {"status": "no_current_project_listing", "propertyHubProject": PROPERTYHUB_SALE,
             "hipflatProject": SALE_CHECK,
             "note": "No active exact-project sale listing; no current yield calculation."},
    "rentSamples": [{"type": row["roomType"], "priceTHBPerMonth": row["price"],
                     "areaSqm": row["area"], "priceTHBPerSqmPerMonth": row["priceSqm"],
                     "url": row["url"], "updated": "not shown on Hipflat project page"}
                    for row in rent_samples],
    "completionYear": {"year": 1990, "source": HIPFLAT},
    "yield": {"calculated": False,
              "reason": "No current exact-project sale listing; current rental listings alone cannot establish purchase price."},
}
report_path = ROOT / "reports" / "sathit-condominium-market-2026-10-19.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [13.7347153, 100.5121448],
                  "saleSamples": 0, "rentSamples": 2, "yield": "not calculated without current sale price",
                  "report": str(report_path)}, ensure_ascii=False))
