"""Add direct PropertyHub 1BR samples for Lumpini Place Narathiwatratchanakarin."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_IDS = [4152, 4298]
PROJECT_NAME = "Lumpini Place Narathiwatratchanakarin"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/projects/lumpini-place-narathiwatratchanakarin"
SALE_URL = "https://propertyhub.in.th/en/listings/a046416-lumpini-place-narathiwat---6213970"
RENT_URL = "https://propertyhub.in.th/listings/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-%E0%B8%A5%E0%B8%B8%E0%B8%A1%E0%B8%9E%E0%B8%B4%E0%B8%99%E0%B8%B5-%E0%B9%80%E0%B8%9E%E0%B8%A5%E0%B8%AA-%E0%B8%99%E0%B8%A3%E0%B8%B2%E0%B8%98%E0%B8%B4%E0%B8%A7%E0%B8%B2%E0%B8%AA%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%B4%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B9%8C-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88-%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%AD%E0%B8%A2%E0%B8%B9%E0%B9%88-%EF%B8%8F-%E0%B8%95%E0%B8%AD%E0%B8%9A%E0%B9%81%E0%B8%8A%E0%B8%97%E0%B9%84%E0%B8%A7-%E0%B8%A3%E0%B8%AB%E0%B8%B1%E0%B8%AA-b916---6474069"


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
    "id": "6213970",
    "price": 2_300_000,
    "area": 29.84,
    "priceSqm": round(2_300_000 / 29.84),
    "beds": 1,
    "roomType": "1BR",
    "url": SALE_URL,
    "title": "Lumpini Place Narathiwatratchanakarin · 1 房 · 29.84 ㎡ · ฿2,300,000",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-10-17",
    "matchedBy": "PropertyHub project listing and direct listing ID 6213970; project name, 1 bedroom, 29.84 sqm and ฿2,300,000 agree",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "6474069",
    "price": 11_999,
    "area": 49.7,
    "priceSqm": round(11_999 / 49.7),
    "beds": 1,
    "roomType": "1BR",
    "url": RENT_URL,
    "title": "Lumpini Place Narathiwatratchanakarin · 1 房 · 49.7 ㎡ · ฿11,999/月",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-10-18",
    "matchedBy": "PropertyHub project listing and direct listing ID 6474069; 1 bedroom, 49.7 sqm, ฿11,999/month; current project list shows the lowest 1BR rent per sqm",
    "listingStatus": "active_as_listed",
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) not in PROJECT_IDS]
for project_id in PROJECT_IDS:
    manual.append({
        "hipflatId": project_id,
        "name": PROJECT_NAME,
        "completedYear": 2007,
        "completedYearSourceUrl": PROJECT_URL,
        "sale": {"samples": [sale]},
        "rent": {"samples": [rent]},
    })
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_manual = "bangkok-manual-market-samples.js?v=20261019-lumpini-place-rama3-riverview"
new_manual = "bangkok-manual-market-samples.js?v=20261019-lumpini-narathiwas-direct-listings"
if html.count(new_manual) != 1:
    if html.count(old_manual) != 1:
        raise ValueError("Could not identify manual market samples cache key")
    html = html.replace(old_manual, new_manual, 1)

app_path = DIST / "app.js"
app = app_path.read_text(encoding="utf-8")
old_storage = "const yieldStorageKey = 'bangkokCondoYieldInputsV130';"
new_storage = "const yieldStorageKey = 'bangkokCondoYieldInputsV131';"
if app.count(new_storage) != 1:
    if app.count(old_storage) != 1:
        raise ValueError("Could not identify yield storage key")
    app = app.replace(old_storage, new_storage, 1)
    app = app.replace("for (let version = 129; version >= 5; version--)", "for (let version = 130; version >= 5; version--)", 1)
    app_path.write_text(app, encoding="utf-8")

old_app = "app.js?v=20261019-lumpini-riverview-two-bedroom-roi-v136"
new_app = "app.js?v=20261019-narathiwas-one-bedroom-roi-v137"
if html.count(new_app) != 1:
    if html.count(old_app) != 1:
        raise ValueError("Could not identify app cache key")
    html = html.replace(old_app, new_app, 1)
html_path.write_text(html, encoding="utf-8")

sale_price, sale_area, rent_price, rent_area = 2_300_000, 29.84, 11_999, 49.7
rent_per_sqm = rent_price / rent_area
comparable_monthly_rent = round(rent_per_sqm * sale_area)
net_yield_without_fee_after_one_agent_month = comparable_monthly_rent * 11 / sale_price * 100
print(json.dumps({
    "projectIds": PROJECT_IDS,
    "sale1BRMinimumTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rent1BRTHBPerSqmMonthly": round(rent_per_sqm, 2),
    "comparableMonthlyRentTHB": comparable_monthly_rent,
    "netYieldWithoutKnownFeeAndAfterOneAgentMonthPercent": round(net_yield_without_fee_after_one_agent_month, 2),
    "completedYear": 2007,
}, ensure_ascii=True, indent=2))
