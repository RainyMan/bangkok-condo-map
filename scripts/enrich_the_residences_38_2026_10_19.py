"""Recalculate The Residences 38 two-bedroom ROI from linked listings."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 6203
PROJECT_NAME = "The Residences 38"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/projects/the-residences-38"
SALE_URL = "https://www.ddproperty.com/en/property/the-residences-38-bangkok-for-sale-500600426"
RENT_URL = "https://propertyhub.in.th/en/listings/lth13334-condo-for-rent-the-residences-38-88-sqm-2-beds-2-baths-185k-month-near-bts-thonglor---5484315"


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
    "id": "500600426",
    "price": 30_200_000,
    "area": 97.22,
    "priceSqm": round(30_200_000 / 97.22),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_URL,
    "title": "The Residences 38 · 2 房最低總價 ฿30,200,000 · 97.22 ㎡",
    "sourceName": "DDproperty",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-09-29",
    "matchedBy": "DDproperty direct listing 500600426 names The Residences 38, 2 bedrooms, 97.22 sqm and ฿30,200,000; cross-checked against the current PropertyHub project sale feed where this is the lowest visible 2BR total.",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "5484315",
    "price": 185_000,
    "area": 88,
    "priceSqm": round(185_000 / 88, 2),
    "beds": 2,
    "roomType": "2BR",
    "url": RENT_URL,
    "title": "The Residences 38 · 2 房最低租金單價 · 88 ㎡ · ฿185,000/月",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-10-08",
    "matchedBy": "PropertyHub project feed and direct listing 5484315 explicitly match The Residences 38, 2 bedrooms, 88 sqm and ฿185,000/month. Among the visible current 2BR listings this is the lowest rent per sqm (฿2,102.27/sqm/month), which is used for the investment estimate.",
    "listingStatus": "active_as_listed",
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "completedYear": 2025,
    "completedYearSourceUrl": PROJECT_URL,
    # Project data does not publish the current common fee; retain unknown.
    "sale": {"samples": [sale]},
    "rent": {"samples": [rent]},
})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_manual = "bangkok-manual-market-samples.js?v=20261019-nue-district-r9-two-bedroom-listings"
new_manual = "bangkok-manual-market-samples.js?v=20261019-residences-38-two-bedroom-roi"
if html.count(new_manual) != 1:
    if html.count(old_manual) != 1:
        raise ValueError("Could not identify manual market samples cache key")
    html = html.replace(old_manual, new_manual, 1)
html_path.write_text(html, encoding="utf-8")

sale_price, sale_area, rent_price, rent_area = 30_200_000, 97.22, 185_000, 88
rent_rate = rent_price / rent_area
comparable_monthly_rent = rent_rate * sale_area
yield_after_agent_month = comparable_monthly_rent * 11 / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "sale2BRMinimumTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rent2BRRateTHBPerSqmMonthly": round(rent_rate, 2),
    "rentAppliedToSaleAreaMonthlyTHB": round(comparable_monthly_rent),
    "yearlyYieldAfterOneAgentMonthBeforeUnknownCommonFeePercent": round(yield_after_agent_month, 2),
    "completedYear": 2025,
}, ensure_ascii=False, indent=2))
