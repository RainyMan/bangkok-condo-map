"""Add linked 2BR market samples and project facts for Lumpini Place Rama III-Riverview."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 4249
PROJECT_NAME = "Lumpini Place Rama III-Riverview"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/projects/lumpini-place-rama-iii-riverview"
SALE_URL = "https://www.ddproperty.com/en/property/lumpini-place-rama-3-riverview-for-sale-60124322"
RENT_URL = "https://assets2.propertyhub.in.th/en/listings/2-br-condo-at-lumpini-place-rama-iii-riverview-19th-floor-id-392984---6271514"
FEE_URL = "https://www.ennxo.com/product/957260"


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
    "id": "60124322",
    "price": 4_200_000,
    "area": 64,
    "priceSqm": round(4_200_000 / 64),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_URL,
    "title": "Lumpini Place Rama III-Riverview · 2 房 · 64 ㎡ · ฿4,200,000",
    "sourceName": "DDproperty",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-10-01",
    "matchedBy": "DDproperty direct listing ID 60124322; project name, 2 bedrooms, 64 sqm and ฿4,200,000 match its current project search result",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "392984",
    "price": 17_000,
    "area": 69,
    "priceSqm": round(17_000 / 69),
    "beds": 2,
    "roomType": "2BR",
    "url": RENT_URL,
    "title": "Lumpini Place Rama III-Riverview · 2 房 · 69 ㎡ · ฿17,000/月",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-09-29",
    "matchedBy": "PropertyHub project listing and direct listing ID 392984; 2 bedrooms, 69 sqm, ฿17,000/month; displayed as the project's lowest current 2BR rental rate",
    "listingStatus": "active_as_listed",
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "fee": {
        "rate": 36,
        "note": "參考房源列示每平方米每月 ฿36，來源較舊，實際應繳管理費及當年度費率請向管委會確認。",
        "source": FEE_URL,
        "status": "historical_indicative",
    },
    "completedYear": 2005,
    "completedYearSourceUrl": PROJECT_URL,
    "sale": {"samples": [sale]},
    "rent": {"samples": [rent]},
})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_manual = "bangkok-manual-market-samples.js?v=20261019-conner-ratchathewi-two-bedroom"
new_manual = "bangkok-manual-market-samples.js?v=20261019-lumpini-place-rama3-riverview"
if html.count(new_manual) != 1:
    if html.count(old_manual) != 1:
        raise ValueError("Could not identify manual market samples cache key")
    html = html.replace(old_manual, new_manual, 1)

app_path = DIST / "app.js"
app = app_path.read_text(encoding="utf-8")
old_storage = "const yieldStorageKey = 'bangkokCondoYieldInputsV129';"
new_storage = "const yieldStorageKey = 'bangkokCondoYieldInputsV130';"
if app.count(new_storage) != 1:
    if app.count(old_storage) != 1:
        raise ValueError("Could not identify yield storage key")
    app = app.replace(old_storage, new_storage, 1)
    app = app.replace("for (let version = 128; version >= 5; version--)", "for (let version = 129; version >= 5; version--)", 1)
    app_path.write_text(app, encoding="utf-8")

old_app = "app.js?v=20261019-conner-two-bedroom-roi-v135"
new_app = "app.js?v=20261019-lumpini-riverview-two-bedroom-roi-v136"
if html.count(new_app) != 1:
    if html.count(old_app) != 1:
        raise ValueError("Could not identify app cache key")
    html = html.replace(old_app, new_app, 1)
html_path.write_text(html, encoding="utf-8")

sale_price, sale_area, rent_price, rent_area, fee_rate = 4_200_000, 64, 17_000, 69, 36
rent_rate = rent_price / rent_area
comparable_monthly_rent = round(rent_rate * sale_area)
net_yield = (comparable_monthly_rent * 11 - fee_rate * sale_area * 12) / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "sale2BRMinimumTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rent2BRMinimumTHBMonthly": rent_price,
    "rentTHBPerSqmMonthly": round(rent_rate, 2),
    "comparableMonthlyRentTHB": comparable_monthly_rent,
    "indicativeFeeTHBPerSqmMonthly": fee_rate,
    "netYieldAfterFeeAndOneAgentMonthPercent": round(net_yield, 2),
}, ensure_ascii=True, indent=2))
