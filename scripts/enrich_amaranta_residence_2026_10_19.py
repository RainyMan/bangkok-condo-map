"""Attach linked sale/rent listings and a cross-checked map pin to Amaranta Residence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_ID = 6550
PROJECT_NAME = "Amaranta Residence"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/amaranta-residence"
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/amaranta-residence-mrbdhz"
CONDONAYOO_SOURCE = "https://www.condonayoo.com/amaranta-residence/"
HOMENAYOO_SOURCE = "https://www.homenayoo.com/amaranta-residence/"

SALE_SOURCE = "https://propertyhub.in.th/en/listings/2-bed-2-bath-amaranta-residence-condo-for-sale---5416099"
RENT_32K_SOURCE = "https://propertyhub.in.th/en/listings/for-rent-condo-amaranta-residence-building-1-floor-3-2-bed-room-room-size-61-00-sqm--ae67093d---6462338"
RENT_34K_SOURCE = "https://propertyhub.in.th/en/listings/dl26090035-condo-for-rent-amaranta-residence-near-mrt-huai-khwang-ready-to-move-in-call-urgently-0614453194-lineid-952jdxxk---6343823"


def read_array(filename: str, variable: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{variable} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript data format in {filename}")
    return json.loads(text[len(prefix):].rstrip().removesuffix(";"))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    rendered = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    (DIST / filename).write_text(f"window.{variable} = {rendered};\n", encoding="utf-8")


sale_samples = [{
    "id": "5416099",
    "price": 6_590_000,
    "area": 58,
    "priceSqm": round(6_590_000 / 58),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_SOURCE,
    "title": "Amaranta Residence · 2 房 · 58 ㎡ · ฿6,590,000",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "matchedBy": "exact_project_name_and_district_on_direct_listing",
    "listingStatus": "active_as_listed",
}]

rent_samples = [
    {
        "id": "6462338",
        "price": 32_000,
        "area": 61,
        "priceSqm": round(32_000 / 61),
        "beds": 2,
        "roomType": "2BR",
        "url": RENT_32K_SOURCE,
        "title": "Amaranta Residence · 2 房 · 61 ㎡ · ฿32,000/月",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_address_on_direct_listing",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6343823",
        "price": 34_000,
        "area": 61.77,
        "priceSqm": round(34_000 / 61.77),
        "beds": 2,
        "roomType": "2BR",
        "url": RENT_34K_SOURCE,
        "title": "Amaranta Residence · 2 房 · 61.77 ㎡ · ฿34,000/月",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "checkedAt": AS_OF,
        "updated": "2026-09-26",
        "matchedBy": "exact_project_name_and_address_on_direct_listing",
        "listingStatus": "active_as_listed",
    },
]

manual_rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [row for row in manual_rows if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual_rows.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "completedYear": 2018,
    "completedYearSourceUrl": PROPERTYHUB_PROJECT,
    "fee": {
        "rate": 60,
        "note": "PropertyHub 專案頁公布每平方米每月 60 泰銖；現行費率請向管委會確認。",
        "source": PROPERTYHUB_PROJECT,
        "status": "published_indicative",
    },
    "sale": {"samples": sale_samples},
    "rent": {"samples": rent_samples},
})
manual_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

coordinate_rows = read_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
coordinate = next(row for row in coordinate_rows if int(row.get("hipflatProjectId", 0)) == PROJECT_ID)
coordinate.update({
    "lat": 13.779406,
    "lng": 100.575932,
    "locationVerified": True,
    "locationSourceName": "Condonayoo 專案 Google Maps 座標",
    "locationSourceUrl": CONDONAYOO_SOURCE,
    "locationVerificationSourceUrl": HOMENAYOO_SOURCE,
    "coordinateSourceVerified": True,
    "verificationMethod": "Condonayoo 與 Homenayoo 均刊載同一 Google Maps 座標；Hipflat 與 PropertyHub 專案頁核對樓盤名稱及地址。",
    "asOf": AS_OF,
})
write_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS", coordinate_rows)

html = (DIST / "index.html").read_text(encoding="utf-8")
cache_updates = {
    "bangkok-propertyhub-guessed-details.js?v=20261019a-wisetsuk-same-name-candidate-excluded":
        "bangkok-propertyhub-guessed-details.js?v=20261019b-amaranta-map-pin-crosscheck",
    "bangkok-manual-market-samples.js?v=20261019-kensington-kaset-taka-haus-listings":
        "bangkok-manual-market-samples.js?v=20261019-amaranta-two-bedroom-samples",
    "app.js?v=20261019-recalculate-two-bedroom-roi-v131":
        "app.js?v=20261019-recalculate-two-bedroom-roi-v132",
}
for old, new in cache_updates.items():
    if html.count(old) != 1:
        raise ValueError(f"Expected one cache key: {old}")
    html = html.replace(old, new, 1)
(DIST / "index.html").write_text(html, encoding="utf-8")

app_path = DIST / "app.js"
app = app_path.read_text(encoding="utf-8")
old_key = "const yieldStorageKey = 'bangkokCondoYieldInputsV125';"
new_key = "const yieldStorageKey = 'bangkokCondoYieldInputsV126';"
old_range = "for (let version = 124; version >= 5; version--) {"
new_range = "for (let version = 125; version >= 5; version--) {"
if app.count(old_key) != 1 or app.count(old_range) != 1:
    raise ValueError("Expected the current ROI storage key and migration range")
app_path.write_text(app.replace(old_key, new_key, 1).replace(old_range, new_range, 1), encoding="utf-8")

sale_price, sale_area = sale_samples[0]["price"], sale_samples[0]["area"]
rent_rate = min(sample["price"] / sample["area"] for sample in rent_samples)
monthly_comparable_rent = round(rent_rate * sale_area)
net_yield = (monthly_comparable_rent * 11 - 60 * sale_area * 12) / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "coordinates": [13.779406, 100.575932],
    "saleBaselineTHB": sale_price,
    "saleAreaSqm": sale_area,
    "rentRateTHBPerSqmMonth": round(rent_rate, 2),
    "comparableMonthlyRentTHB": monthly_comparable_rent,
    "netYieldAfterFeeAndOneAgentMonthPercent": round(net_yield, 2),
}, ensure_ascii=False))
