"""Enrich CONNER Ratchathewi with current minimum 2BR PropertyHub samples."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/projects/conner-ratchathewi"
SALE_URL = "https://asset-direct-v2.propertyhub.in.th/en/listings/2-br-condo-at-conner-ratchathewi-near-bts-ratchathewi-id-1537718--b85e0973---4475541"
RENT_URL = "https://propertyhub.in.th/en/listings/for-rentcondo-conner-ratchathewi-bts-ratchathewi-cx-108792-1---6355524"
PROJECT_IDS = [3118, 3564, 6493, 6536]


def read_array(filename: str, variable: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{variable} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JS data format in {filename}")
    return json.loads(text[len(prefix):].rstrip().removesuffix(";"))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    rendered = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    (DIST / filename).write_text(f"window.{variable} = {rendered};\n", encoding="utf-8")

sale = {
    "id": "1537718",
    "price": 14_000_000,
    "area": 50.1,
    "priceSqm": round(14_000_000 / 50.1),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_URL,
    "title": "CONNER Ratchathewi · 2 房最低總價 · 50.1 ㎡（依掛牌標示）· ฿14,000,000",
    "sourceName": "PropertyHub",
    "projectName": "CONNER Ratchathewi",
    "checkedAt": AS_OF,
    "updated": "2026-10-11",
    "matchedBy": "PropertyHub CONNER Ratchathewi project feed refreshed 2026-10-19 and direct listing ID 1537718 agree on 2 bedrooms, 50.1 sqm and ฿14,000,000. Note: PropertyHub project plan states 2BR 69–73 sqm; this listing is smaller, retained as the lowest currently published 2BR total per the user's rule.",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "CX-108792",
    "price": 53_900,
    "area": 70,
    "priceSqm": round(53_900 / 70),
    "beds": 2,
    "roomType": "2BR",
    "url": RENT_URL,
    "title": "CONNER Ratchathewi · 2 房 · 70 ㎡ · ฿53,900/月",
    "sourceName": "PropertyHub",
    "projectName": "CONNER Ratchathewi",
    "checkedAt": AS_OF,
    "updated": "2026-10-19",
    "matchedBy": "PropertyHub project page and direct Connex listing CX-108792; 2-bedroom, 70 sqm, ฿53,900/month; project page refreshed 2026-10-19",
    "listingStatus": "active_as_listed",
}
manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) not in PROJECT_IDS]
for project_id in PROJECT_IDS:
    manual.append({
        "hipflatId": project_id,
        "name": "CONNER Ratchathewi",
        "fee": {"rate": 90, "note": "PropertyHub 專案頁公布每平方米每月 90 泰銖；實際應繳費用請向管委會確認。", "source": PROJECT_URL, "status": "published_indicative"},
        "completedYear": 2021,
        "completedYearSourceUrl": PROJECT_URL,
        "sale": {"samples": [sale]},
        "rent": {"samples": [rent]},
    })
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_manual = "bangkok-manual-market-samples.js?v=20261019-maxxi-two-bedroom-samples"
new_manual = "bangkok-manual-market-samples.js?v=20261019-conner-ratchathewi-two-bedroom"
if html.count(new_manual) != 1:
    if html.count(old_manual) != 1:
        raise ValueError("Could not identify manual market samples cache key")
    html = html.replace(old_manual, new_manual, 1)
old_app = "const yieldStorageKey = 'bangkokCondoYieldInputsV128';"
new_app = "const yieldStorageKey = 'bangkokCondoYieldInputsV129';"
app_path = DIST / "app.js"
app = app_path.read_text(encoding="utf-8")
if app.count(new_app) != 1:
    if app.count(old_app) != 1:
        raise ValueError("Could not identify yield storage key")
    app = app.replace(old_app, new_app, 1)
    app_path.write_text(app, encoding="utf-8")
html = html.replace("app.js?v=20261019-maxxi-two-bedroom-roi-v134", "app.js?v=20261019-conner-two-bedroom-roi-v135", 1)
if "app.js?v=20261019-conner-two-bedroom-roi-v135" not in html:
    raise ValueError("Could not identify app cache key")
html_path.write_text(html, encoding="utf-8")

sale_price, sale_area, rent_price, rent_area, fee_rate = 14_000_000, 50.1, 53_900, 70, 90
rent_per_sqm = rent_price / rent_area
comparable_rent = round(rent_per_sqm * sale_area)
net_yield = (comparable_rent * 11 - fee_rate * sale_area * 12) / sale_price * 100
print(json.dumps({
    "projectIds": PROJECT_IDS,
    "sale": {"priceTHB": sale_price, "areaSqmFromSameLowestTwoBedroomListing": sale_area, "priceTHBPerSqm": round(sale_price / sale_area)},
    "rent": {"monthlyTHB": rent_price, "areaSqm": rent_area, "rentTHBPerSqmMonthly": round(rent_per_sqm, 2), "comparableMonthlyRentForSaleAreaTHB": comparable_rent},
    "commonFeeTHBPerSqmMonthly": fee_rate,
    "netYieldAfterFeeAndOneAgentMonthPercent": round(net_yield, 2),
    "completedYear": 2021,
}, ensure_ascii=True, indent=2))


