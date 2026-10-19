"""Add linked two-bedroom listing samples and completion year for NUE District R9."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 5602
PROJECT_NAME = "NUE District R9 Rama 9"
AS_OF = "2026-10-19"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-nue-district-r9-rama-9"
SALE_URL = "https://propertyhub.in.th/en/listings/2-br-condo-at-nue-district-r9-near-mrt-phra-ram-9-id-3364840---6471657"
RENT_URL = "https://propertyhub.in.th/en/listings/2-beds-large-room-high-fl-20-city-view-fully-furnished-condo-good-location-close-to-mrt-phra-ram-9-nue-district-r9---6430495"


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
    "id": "6471657",
    "price": 4_900_000,
    "area": 34.7,
    "priceSqm": round(4_900_000 / 34.7),
    "beds": 2,
    "roomType": "2BR",
    "url": SALE_URL,
    "title": "NUE District R9 · 2 房最低總價 ฿4,900,000 · 34.7 ㎡（低於專案格局資料 46 ㎡）",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-10-16",
    "matchedBy": "PropertyHub direct listing 6471657, title S090033, explicitly names NUE District R9, 2 bedrooms, 34.7 sqm and ฿4,900,000. It is the lowest visible 2BR total in the current project feed. Project page describes 2BR units as 46 sqm, so listing floor area is preserved verbatim and flagged for owner confirmation.",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "6430495",
    "price": 24_000,
    "area": 34.94,
    "priceSqm": round(24_000 / 34.94, 2),
    "beds": 2,
    "roomType": "2BR",
    "url": RENT_URL,
    "title": "NUE District R9 · 2 房 · 34.94 ㎡（低於專案格局資料 46 ㎡）· ฿24,000/月",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-10-18",
    "matchedBy": "PropertyHub direct listing 6430495 explicitly names NUE District R9 Rama 9, 2 bedrooms, 34.94 sqm and ฿24,000/month. It is the lowest visible checked 2BR rent rate per sqm on the project feed. Project page describes 2BR units as 46 sqm, so listing floor area is preserved verbatim and flagged for owner confirmation.",
    "listingStatus": "active_as_listed",
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "completedYear": 2025,
    "completedYearSourceUrl": PROJECT_URL,
    "fee": None,
    "sale": {"samples": [sale]},
    "rent": {"samples": [rent]},
})
manual.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old_manual = "bangkok-manual-market-samples.js?v=20261019-mayfair-sukhumvit-64-direct-listings"
new_manual = "bangkok-manual-market-samples.js?v=20261019-nue-district-r9-two-bedroom-listings"
if html.count(new_manual) != 1:
    if html.count(old_manual) != 1:
        raise ValueError("Could not identify manual market samples cache key")
    html = html.replace(old_manual, new_manual, 1)
html_path.write_text(html, encoding="utf-8")

sale_price, sale_area, rent_price, rent_area = 4_900_000, 34.7, 24_000, 34.94
rent_rate = rent_price / rent_area
comparable_monthly_rent = round(rent_rate * sale_area)
net_yield_without_fee = comparable_monthly_rent * 11 / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "sale2BRMinimumTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rent2BRListingTHBMonthly": rent_price,
    "rent2BRListingAreaSqm": rent_area,
    "rentTHBPerSqmMonthly": round(rent_rate, 2),
    "comparableMonthlyRentTHB": comparable_monthly_rent,
    "netYieldAfterOneAgentMonthBeforeUnknownFeePercent": round(net_yield_without_fee, 2),
    "completedYear": 2025,
    "areaMismatchFlag": "Both 2BR listings are below the project page's stated 46 sqm 2BR plan; verify with advertiser.",
}, ensure_ascii=False, indent=2))
