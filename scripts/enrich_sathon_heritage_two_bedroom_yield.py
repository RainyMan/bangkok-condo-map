import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT = ROOT / "reports" / "sathon-heritage-two-bedroom-yield-2026-10-18.json"
SYMBOL = "BANGKOK_MANUAL_MARKET_SAMPLES"

sale = {
    "id": "5893715", "price": 11900000, "area": 116, "priceSqm": 102586,
    "beds": 2, "roomType": "TWO_BED_ROOM",
    "title": "LTH2841 – Sathorn Heritage FOR SALE 2 beds 2 baths size 116 Sq.M.",
    "url": "https://asset-direct-v2.propertyhub.in.th/en/listings/lth2841-sathorn-heritage-for-sale-2-beds-2-baths-size-116-sq-m-nearby-bts-chong-nonsi-station-only-11-9-mb---5893715",
    "sourceName": "PropertyHub", "projectName": "Sathorn Heritage",
    "updated": "2026-10-11", "checkedAt": "2026-10-18",
    "matchedBy": "exact_project_page_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_under_30d",
}
rent = {
    "id": "2999130", "price": 45000, "area": 116, "priceSqm": 388,
    "beds": 2, "roomType": "TWO_BED_ROOM",
    "title": "1 bed Good Location BTS Surasak Sathorn Heritage Residences / Condo For Rent",
    "url": "https://propertyhub.in.th/en/listings/1-bed-good-location-bts-surasak-sathorn-heritage-residences-condo-for-rent-sathorn-heritage-residences---2999130",
    "sourceName": "PropertyHub", "projectName": "Sathorn Heritage",
    "updated": "2026-09-30", "checkedAt": "2026-10-18",
    "matchedBy": "exact_project_page_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_under_30d",
}

text = TARGET.read_text(encoding="utf-8")
match = re.search(rf"window\.{SYMBOL}\s*=\s*(\[.*\]);", text, re.S)
if not match:
    raise SystemExit(f"Cannot locate {SYMBOL}")
rows = json.loads(match.group(1))
entry = next((row for row in rows if int(row.get("hipflatId", 0)) == 4258), None)
if entry is None:
    entry = {"hipflatId": 4258, "name": "Sathon Heritage Residences"}
    rows.append(entry)
for kind, sample in (("sale", sale), ("rent", rent)):
    market = entry.setdefault(kind, {})
    samples = market.setdefault("samples", [])
    if not any(row.get("url") == sample["url"] for row in samples):
        samples.append(sample)
TARGET.write_text(f"window.{SYMBOL} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

rate = rent["price"] / rent["area"]
monthlyRentOnSaleUnit = rate * sale["area"]
result = {
    "hipflatId": 4258,
    "projectName": "Sathon Heritage Residences",
    "checkedAt": "2026-10-18",
    "saleListing": sale,
    "rentListing": rent,
    "yieldEstimate": {
        "bedrooms": 2,
        "purchasePriceThb": sale["price"],
        "saleAreaSqm": sale["area"],
        "rentRateThbPerSqmMonth": round(rate, 2),
        "estimatedMonthlyRentOnSaleAreaThb": round(monthlyRentOnSaleUnit, 2),
        "grossAnnualYieldPercent": round(monthlyRentOnSaleUnit * 12 / sale["price"] * 100, 2),
        "annualYieldAfterOneAgentMonthPercent": round(monthlyRentOnSaleUnit * 11 / sale["price"] * 100, 2),
        "commonFeeDeducted": False,
        "reason": "Two bedroom sale and rent listing pages both identify the same project. Rent uses the 2BR listing rate per sqm multiplied by the 116 sqm sale unit area. Property management fee is not available as a verified amount.",
    },
    "sources": [
        {"url": sale["url"], "finding": "Direct sale item page: Sathorn Heritage, 2 bedrooms, 116 sqm, THB 11,900,000. Project listing index showed refresh on 11 October 2026."},
        {"url": rent["url"], "finding": "Direct rent item page: Sathorn Heritage, 2 bedrooms, 116 sqm, THB 45,000/month. Current project listing index showed refresh on 30 September 2026."},
        {"url": "https://propertyhub.in.th/en/projects/sathorn-heritage--2", "finding": "Exact PropertyHub project page identifies the 2BR unit types and current sale and rent listings."},
    ],
    "limitations": ["Listing refresh dates do not guarantee that the rooms remain available; confirm with the advertiser.", "No verified common fee was found, so the yield estimate does not deduct it."],
}
REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": result["projectName"], "grossYieldPct": result["yieldEstimate"]["grossAnnualYieldPercent"], "afterAgentPct": result["yieldEstimate"]["annualYieldAfterOneAgentMonthPercent"], "report": str(REPORT)}, ensure_ascii=False))
