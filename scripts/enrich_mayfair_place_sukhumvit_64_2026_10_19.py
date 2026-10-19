"""Add checked direct sale/rent listings and project facts for Mayfair Place Sukhumvit 64."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 4463
PROJECT_NAME = "Mayfair Place Sukhumvit 64"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/projects/mayfair-place"
SALE_URL = "https://propertyhub.in.th/listings/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-%E0%B8%82%E0%B8%B2%E0%B8%A2-mayfair-place-sukhumvit-64-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-bts-%E0%B8%9B%E0%B8%B8%E0%B8%93%E0%B8%93%E0%B8%A7%E0%B8%B4%E0%B8%96%E0%B8%B5-id-3264173---6366984"
RENT_URL = "https://propertyhub.in.th/listings/a124522-15-9-69-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-mayfair-place-sukhumvit-64%E0%B8%AA%E0%B8%AD%E0%B8%9A%E0%B8%96%E0%B8%B2%E0%B8%A1-ld-line-condoboy---6410647"


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
    "id": "6366984",
    "price": 4_700_000,
    "area": 56.51,
    "priceSqm": round(4_700_000 / 56.51),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_URL,
    "title": "Mayfair Place Sukhumvit 64 · 2 房最低總價 · 56.51 ㎡ · ฿4,700,000",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-09-14",
    "matchedBy": "PropertyHub project feed and direct listing 6366984 (headline unit ID 3264173) match Mayfair Place Sukhumvit 64, 2 bedrooms, 56.51 sqm and ฿4,700,000; lower than the other visible 2BR project listings reviewed.",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "6410647",
    "price": 15_000,
    "area": 44.44,
    "priceSqm": round(15_000 / 44.44, 2),
    "beds": 2,
    "roomType": "2BR",
    "url": RENT_URL,
    "title": "Mayfair Place Sukhumvit 64 · 2 房 · 44.44 ㎡ · ฿15,000/月",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-09-15",
    "matchedBy": "PropertyHub direct listing 6410647, titled #A124522 dated 15/9/69, explicitly states Mayfair Place Sukhumvit 64, 2 bedrooms, 44.44 sqm and ฿15,000/month; this is the lowest 2BR rent per sqm among checked project listings.",
    "listingStatus": "active_as_listed",
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "fee": {
        "rate": 45,
        "note": "PropertyHub 專案頁標示每平方米每月 ฿45；現行應繳費率請向管委會確認。",
        "source": PROJECT_URL,
        "status": "published_indicative",
    },
    "completedYear": 2014,
    "completedYearSourceUrl": PROJECT_URL,
    "sale": {"samples": [sale]},
    "rent": {"samples": [rent]},
})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_manual = "bangkok-manual-market-samples.js?v=20261019-lumpini-narathiwas-direct-listings"
new_manual = "bangkok-manual-market-samples.js?v=20261019-mayfair-sukhumvit-64-direct-listings"
if html.count(new_manual) != 1:
    if html.count(old_manual) != 1:
        raise ValueError("Could not identify manual market samples cache key")
    html = html.replace(old_manual, new_manual, 1)
html_path.write_text(html, encoding="utf-8")

sale_price, sale_area, rent_price, rent_area, fee_rate = 4_700_000, 56.51, 15_000, 44.44, 45
rent_rate = rent_price / rent_area
comparable_monthly_rent = round(rent_rate * sale_area)
net_yield = (comparable_monthly_rent * 11 - fee_rate * sale_area * 12) / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "sale2BRMinimumTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rent2BRListingTHBMonthly": rent_price,
    "rent2BRListingAreaSqm": rent_area,
    "rentTHBPerSqmMonthly": round(rent_rate, 2),
    "comparableMonthlyRentTHB": comparable_monthly_rent,
    "publishedFeeTHBPerSqmMonthly": fee_rate,
    "netYieldAfterFeeAndOneAgentMonthPercent": round(net_yield, 2),
    "completedYear": 2014,
}, ensure_ascii=False, indent=2))
