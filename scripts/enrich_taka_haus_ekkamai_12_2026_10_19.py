from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_ID = 5056
NAME = "Taka Haus Ekamai 12"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/taka-haus-ekamai-12-wkhnod"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/taka-haus-ekkamai"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_samples = [
    {
        "id": "6352791", "price": 5_800_000, "area": 47.5, "priceSqm": 122_105,
        "beds": 2, "roomType": "2BR",
        "url": "https://propertyhub.in.th/en/listings/2-br-condo-for-sale-at-taka-haus-ekamai-12-near-bts-ekkamai-id-3257743---6352791",
        "title": "Taka Haus Ekkamai 12，2 房，47.5 ㎡，฿5,800,000",
        "sourceName": "PropertyHub", "projectName": NAME, "checkedAt": AS_OF,
        "updated": "2026-10-02", "matchedBy": "exact_project_listing_on_propertyhub_project_page",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "3335555", "price": 7_990_000, "area": 62, "priceSqm": 128_871,
        "beds": 2, "roomType": "2BR",
        "url": "https://propertyhub.in.th/en/listings/2-br-condo-for-sale-at-taka-haus-ekamai-12-near-bts-ekkamai-id-3335555",
        "title": "Taka Haus Ekkamai 12，2 房，62 ㎡，฿7,990,000",
        "sourceName": "PropertyHub", "projectName": NAME, "checkedAt": AS_OF,
        "updated": "2026-10-17", "matchedBy": "exact_project_listing_on_propertyhub_project_page",
        "listingStatus": "active_as_listed",
    },
]
rent_samples = [
    {
        "id": "6401257", "price": 25_000, "area": 48, "priceSqm": 521,
        "beds": 2, "roomType": "2BR",
        "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-taka-haus-ekamai-12-near-bts-ekkamai-id-2883975---6401257",
        "title": "Taka Haus Ekkamai 12，2 房，48 ㎡，฿25,000／月",
        "sourceName": "PropertyHub", "projectName": NAME, "checkedAt": AS_OF,
        "updated": "2026-10-17", "matchedBy": "exact_project_listing_on_propertyhub_project_page",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "4665174", "price": 29_000, "area": 49, "priceSqm": 592,
        "beds": 2, "roomType": "2BR",
        "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-taka-haus-ekamai-12-near-bts-ekkamai-id-1805859---4665174",
        "title": "Taka Haus Ekkamai 12，2 房，49 ㎡，฿29,000／月",
        "sourceName": "PropertyHub", "projectName": NAME, "checkedAt": AS_OF,
        "updated": "2026-10-17", "matchedBy": "exact_project_listing_on_propertyhub_project_page",
        "listingStatus": "active_as_listed",
    },
]

markets = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
project = next((row for row in markets if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": NAME}
    markets.append(project)

for kind, samples in (("sale", sale_samples), ("rent", rent_samples)):
    market = project.setdefault(kind, {})
    by_url = {sample.get("url"): sample for sample in market.get("samples", []) if sample.get("url")}
    for sample in samples:
        by_url[sample["url"]] = sample
    combined = list(by_url.values())
    minimum = min(combined, key=lambda sample: float(sample["price"]))
    minimum_sqm = min(combined, key=lambda sample: float(sample["price"]) / float(sample["area"]))
    bedroom = {}
    for beds in sorted({int(sample["beds"]) for sample in combined if sample.get("beds")}):
        room_samples = [sample for sample in combined if int(sample["beds"]) == beds]
        lowest_total = min(room_samples, key=lambda sample: float(sample["price"]))
        lowest_rate = min(room_samples, key=lambda sample: float(sample["price"]) / float(sample["area"]))
        bedroom[str(beds)] = {
            "count": len(room_samples), "minimum": lowest_total["price"],
            "area": lowest_total["area"], "minimumArea": lowest_total["area"],
            "priceSqm": round(float(lowest_total["price"]) / float(lowest_total["area"])),
            "minimumSqm": round(float(lowest_rate["price"]) / float(lowest_rate["area"])),
            "minimumSourceUrl": lowest_total["url"], "sourceUrl": lowest_total["url"],
            "minimumSqmSourceUrl": lowest_rate["url"],
        }
    market.update({
        "count": len(combined), "observedCount": len(combined),
        "countKind": "manual_verified_listing", "samples": combined,
        "minimum": minimum["price"], "minimumArea": minimum["area"],
        "minimumSourceUrl": minimum["url"],
        "minimumSqm": round(float(minimum_sqm["price"]) / float(minimum_sqm["area"])),
        "minimumSqmSourceUrl": minimum_sqm["url"], "byBedroom": bedroom,
        "asOf": AS_OF, "sourceName": "PropertyHub 個別掛牌",
        "source": PROPERTYHUB_PROJECT_URL,
    })

project["fee"] = {
    "rate": 77,
    "note": "PropertyHub 專案頁公布公共管理費 ฿77／㎡／月；請向管委會確認現行實收費率。",
    "source": PROPERTYHUB_PROJECT_URL,
    "status": "published_indicative",
}
markets.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

coordinate_rows = read_array("bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS")
coordinate = next((row for row in coordinate_rows if int(row.get("hipflatId", 0)) == PROJECT_ID), {})
purchase = min((sample for sample in sale_samples if sample["beds"] == 2), key=lambda sample: sample["price"])
rent = min((sample for sample in rent_samples if sample["beds"] == 2), key=lambda sample: sample["price"] / sample["area"])
monthly_rent = round(float(rent["price"]) / float(rent["area"]) * float(purchase["area"]))
annual_fee = 77 * float(purchase["area"]) * 12
net_yield = (monthly_rent * 11 - annual_fee) / float(purchase["price"]) * 100
report = {
    "hipflatId": PROJECT_ID, "name": NAME, "asOf": AS_OF,
    "projectSources": {
        "hipflat": HIPFLAT_URL, "propertyhub": PROPERTYHUB_PROJECT_URL,
        "locationEvidence": "Project address and PropertyScout map pin correspond to Taka Haus Ekkamai 12; existing verified coordinate retained.",
        "completedYear": 2019, "completedYearSource": PROPERTYHUB_PROJECT_URL,
        "feeTHBPerSqmPerMonth": 77, "feeSource": PROPERTYHUB_PROJECT_URL,
    },
    "coordinates": {"lat": coordinate.get("lat"), "lng": coordinate.get("lng"), "source": coordinate.get("locationSourceUrl")},
    "saleSamples": sale_samples, "rentSamples": rent_samples,
    "yieldScenario": {
        "beds": 2, "purchasePriceTHB": purchase["price"], "purchaseAreaSqm": purchase["area"],
        "saleSourceUrl": purchase["url"],
        "rentRateTHBPerSqmPerMonth": round(float(rent["price"]) / float(rent["area"]), 2),
        "estimatedMonthlyRentTHB": monthly_rent, "rentSourceUrl": rent["url"],
        "deductOneAgentMonth": True, "deductCommonFee": True,
        "annualCommonFeeTHB": round(annual_fee), "netAnnualYieldPercent": round(net_yield, 2),
        "formula": "((round((25000 / 48) * 47.5) * 11 - 77 * 47.5 * 12) / 5800000) * 100",
    },
}
(ROOT / "reports" / "taka-haus-ekkamai-12-enrichment-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "twoBedroomLowestSaleTHB": purchase["price"], "pairedAreaSqm": purchase["area"], "netYieldPercent": round(net_yield, 2)}, ensure_ascii=False))
