"""Add verified PropertyHub two-bedroom samples and Google Maps pin for MAXXI."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 4379
PROJECT_NAME = "MAXXI Condo Ratchayothin-Phaholyothin 34"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/projects/maxxi-condominium"
SALE_URL = "https://propertyhub.in.th/en/listings/md-26066902-rare-find-beautiful-unit-priced-below-market-value-at-maxxi-ratchayothin-phahonyothin-34-book-now-before-its-gone---6407606"
RENT_URL = "https://asset-direct-v2.propertyhub.in.th/en/listings/for-rent-condo-maxxi-ratchayothin-phaholyothin-34-duplex-nice-view-bts-kasetsart-university-sena-nikhom-chatuchak-bangkok-cx-154896-live-chat-with-us-add-line-connexproperty--b60a09d5---6064407"
GOOGLE_MAPS_URL = "https://www.google.com/maps/place/%E0%B9%81%E0%B8%A1%E0%B8%81%E0%B8%8B%E0%B9%8C%E0%B8%8B%E0%B8%B5%E0%B9%88%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/@13.8379127,100.5900611,14.19z/data=!4m5!3m4!1s0x0:0x1e93722873f8a5e2!8m2!3d13.8373516!4d100.583827?shorturl=1"


def read_array(filename: str, variable: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{variable} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript data format in {filename}")
    return json.loads(text[len(prefix):].rstrip().removesuffix(";"))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    rendered = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    (DIST / filename).write_text(f"window.{variable} = {rendered};\n", encoding="utf-8")


sale = {
    "id": "6407606",
    "price": 2_050_000,
    "area": 34.42,
    "priceSqm": round(2_050_000 / 34.42),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_URL,
    "title": "MAXXI · 2 房 · 34.42 ㎡ · ฿2,050,000",
    "sourceName": "PropertyHub",
    "projectName": "MAXXI Condominium",
    "checkedAt": AS_OF,
    "updated": "2026-10-14",
    "matchedBy": "PropertyHub MAXXI project listing and direct listing detail; project name, 2-bedroom type, price and area match",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "6064407",
    "price": 14_500,
    "area": 33,
    "priceSqm": round(14_500 / 33),
    "beds": 2,
    "roomType": "2BR",
    "url": RENT_URL,
    "title": "MAXXI · 2 房 · 33 ㎡（依掛牌標示；專案標準格局 34–37 ㎡）· ฿14,500/月",
    "sourceName": "PropertyHub",
    "projectName": "MAXXI Condominium",
    "checkedAt": AS_OF,
    "updated": "2026-10-13",
    "matchedBy": "PropertyHub direct 2-bedroom listing; project name and attached Google Maps pin match MAXXI; listing area retained as published",
    "listingStatus": "active_as_listed",
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "fee": {
        "rate": 50,
        "note": "PropertyHub 專案頁公布每平方米每月 50 泰銖；實際應繳費用請向管委會確認。",
        "source": PROJECT_URL,
        "status": "published_indicative",
    },
    "sale": {"samples": [sale]},
    "rent": {"samples": [rent]},
})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

coordinates = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinates = [row for row in coordinates if int(row.get("hipflatId", 0)) != PROJECT_ID]
coordinates.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.8373516,
    "lng": 100.583827,
    "locationVerified": True,
    "sourceName": "Google Maps 座標（PropertyHub 房源頁所附地圖）",
    "sourceUrl": GOOGLE_MAPS_URL,
    "verificationSourceUrl": RENT_URL,
    "verificationMethod": "Google Maps destination pin on direct MAXXI listing; matches project name and address",
})
coordinates.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinates)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_app_cache = 'app.js?v=20261019-recalculate-two-bedroom-roi-v133'
new_app_cache = 'app.js?v=20261019-maxxi-two-bedroom-roi-v134'
if html.count(new_app_cache) == 1:
    pass
elif html.count(old_app_cache) == 1:
    html = html.replace(old_app_cache, new_app_cache, 1)
    html_path.write_text(html, encoding="utf-8")
else:
    raise ValueError("Expected the current app cache key exactly once")

old_cache = "bangkok-manual-market-samples.js?v=20261019-noble-ora-direct-listings"
new_cache = "bangkok-manual-market-samples.js?v=20261019-maxxi-two-bedroom-samples"
if html.count(new_cache) == 1:
    pass
elif html.count(old_cache) == 1:
    html_path.write_text(html.replace(old_cache, new_cache, 1), encoding="utf-8")
else:
    raise ValueError("Expected the current manual-sample cache key exactly once")

app_path = DIST / "app.js"
app = app_path.read_text(encoding="utf-8")
old_storage_key = "const yieldStorageKey = 'bangkokCondoYieldInputsV127';"
new_storage_key = "const yieldStorageKey = 'bangkokCondoYieldInputsV128';"
if app.count(new_storage_key) == 1:
    pass
elif app.count(old_storage_key) == 1:
    app_path.write_text(app.replace(old_storage_key, new_storage_key, 1), encoding="utf-8")
else:
    raise ValueError("Expected the current yield storage key exactly once")

html = html_path.read_text(encoding="utf-8")
old_coordinate_cache = "bangkok-verified-coordinates.js?v=20261019-maison-garden-coordinate-crosscheck"
new_coordinate_cache = "bangkok-verified-coordinates.js?v=20261019-maxxi-google-pin"
if html.count(new_coordinate_cache) == 1:
    pass
elif html.count(old_coordinate_cache) == 1:
    html_path.write_text(html.replace(old_coordinate_cache, new_coordinate_cache, 1), encoding="utf-8")
else:
    raise ValueError("Could not identify the verified-coordinate cache key")

sale_price, sale_area, rent_price, rent_area, fee_rate = 2_050_000, 34.42, 14_500, 33, 50
rent_rate = rent_price / rent_area
monthly_comparable_rent = round(rent_rate * sale_area)
net_yield = (monthly_comparable_rent * 11 - fee_rate * sale_area * 12) / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "verifiedCoordinates": [13.8373516, 100.583827],
    "saleLowestTwoBedroomTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rentListingTHBPerSqmMonth": round(rent_rate, 2),
    "comparableMonthlyRentTHB": monthly_comparable_rent,
    "commonFeeRateTHBPerSqmMonth": fee_rate,
    "netYieldAfterFeeAndOneAgentMonthPercent": round(net_yield, 2),
}, ensure_ascii=True, indent=2))
