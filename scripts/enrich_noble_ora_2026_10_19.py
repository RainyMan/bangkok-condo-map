"""Attach direct PropertyHub sale and rental listings to Noble Ora."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_ID = 4668
PROJECT_NAME = "Noble Ora"
PROJECT_URL = "https://propertyhub.in.th/en/projects/noble-ora-thonglor"
SALE_1099_URL = "https://asset-direct-v2.propertyhub.in.th/en/listings/open-view-best-price-2b2b-10-99mb-noble-ora-call-090-919-9898---6381542"
SALE_1325_URL = "https://assets2.propertyhub.in.th/en/listings/2-bed-2-bath-115-sqm-condo-for-rent-and-sale--a66f0917---5890167"
RENT_38_URL = "https://asset-direct-v2.propertyhub.in.th/en/listings/condo-for-rent-noble-ora-2-bed-with-bathtub-good-location-bts-thong-lo--a6dd0912---4195258"
RENT_475_URL = "https://propertyhub.in.th/en/listings/2-br-condo-at-noble-ora-near-bts-thong-lor-id-293954---5458213"


def read_array(filename: str, variable: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{variable} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript data format in {filename}")
    return json.loads(text[len(prefix):].rstrip().removesuffix(";"))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    rendered = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    (DIST / filename).write_text(f"window.{variable} = {rendered};\n", encoding="utf-8")


def listing(listing_id: str, price: int, area: float, url: str, title: str, updated: str) -> dict:
    return {
        "id": listing_id,
        "price": price,
        "area": area,
        "priceSqm": round(price / area),
        "beds": 2,
        "roomType": "2BR",
        "url": url,
        "title": title,
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "checkedAt": AS_OF,
        "updated": updated,
        "matchedBy": "PropertyHub project listing and direct listing detail",
        "listingStatus": "active_as_listed",
    }


sale_samples = [
    listing("6381542", 10_990_000, 104.95, SALE_1099_URL,
            "Noble Ora · 2 房 · 104.95 ㎡ · ฿10,990,000", "2026-10-10"),
    listing("5890167", 13_250_000, 115, SALE_1325_URL,
            "Noble Ora · 2 房 · 115 ㎡ · ฿13,250,000", "2026-10-07"),
]
rent_samples = [
    listing("4195258", 38_000, 108, RENT_38_URL,
            "Noble Ora · 2 房 · 108 ㎡ · ฿38,000/月", "2026-10-17"),
    listing("5458213", 47_500, 110, RENT_475_URL,
            "Noble Ora · 2 房 · 110 ㎡ · ฿47,500/月", "2026-10-17"),
]

rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
rows = [row for row in rows if int(row.get("hipflatId", 0)) != PROJECT_ID]
rows.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "fee": {
        "rate": 35,
        "note": "PropertyHub 專案頁標示每平方米每月 35 泰銖；現行收費請向管委會確認。",
        "source": PROJECT_URL,
        "status": "published_indicative",
    },
    "sale": {"samples": sale_samples},
    "rent": {"samples": rent_samples},
})
rows.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
old = "bangkok-manual-market-samples.js?v=20261019-amaranta-two-bedroom-samples"
new = "bangkok-manual-market-samples.js?v=20261019-noble-ora-direct-listings"
if html.count(new) == 1:
    pass
elif html.count(old) == 1:
    html_path.write_text(html.replace(old, new, 1), encoding="utf-8")
else:
    raise ValueError("Expected the current manual sample cache key exactly once")

sale_price, sale_area = 10_990_000, 104.95
rent_rate = min(sample["price"] / sample["area"] for sample in rent_samples)
monthly_comparable_rent = round(rent_rate * sale_area)
net_yield = (monthly_comparable_rent * 11 - 35 * sale_area * 12) / sale_price * 100
print(json.dumps({
    "project": PROJECT_NAME,
    "hipflatId": PROJECT_ID,
    "saleLowestTwoBedroomTHB": sale_price,
    "saleAreaSqmFromSameListing": sale_area,
    "rentLowRateTHBPerSqmMonth": round(rent_rate, 2),
    "comparableMonthlyRentTHB": monthly_comparable_rent,
    "commonFeeRateTHBPerSqmMonth": 35,
    "netYieldAfterFeeAndOneAgentMonthPercent": round(net_yield, 2),
}, ensure_ascii=False))
