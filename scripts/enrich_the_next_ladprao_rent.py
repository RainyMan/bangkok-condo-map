"""Add the current direct Hipflat rental listing for The Next Ladprao."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3472
NAME = "The Next Ladprao"
CHECKED = "2026-10-18"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/the-next-ladprao-ucclbd"
RENT_URL = "https://www.hipflat.co.th/en/ads/ul0h4t8h83uahu3001n0n2tu3u0he3he"
SALE_URL = "https://propertyhub.in.th/en/listings/for-sale-the-next-ladprao-44-large-2-bedroom-condo-next-to-mrt-phawana-special-price---5972290"


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Cannot parse {symbol} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    price, area, beds = 12_000, 46, 1
    rate = price / area
    rent_sample = {
        "id": "U1635652",
        "price": price,
        "area": area,
        "priceSqm": round(rate, 2),
        "beds": beds,
        "roomType": "1BR",
        "title": "The Next Ladprao，1 房，46 ㎡，3 樓，฿12,000/月",
        "url": RENT_URL,
        "sourceName": "Hipflat",
        "projectName": NAME,
        "updated": CHECKED,
        "checkedAt": CHECKED,
        "matchedBy": "Hipflat exact project page links to this unit; direct unit page names The Next Ladprao",
        "listingStatus": "active_as_listed",
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "minimumSampleUpdated": CHECKED,
        "averageSqm": round(rate, 2),
        "minimumSqm": round(rate, 2),
        "minimumSqmSampleUpdated": CHECKED,
        "asOf": CHECKED,
        "sourceName": "Hipflat 直接出租掛牌",
        "source": PROJECT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": price,
                "area": area,
                "minimumSqm": round(rate, 2),
                "sourceUrl": RENT_URL,
                "minimumSqmSourceUrl": RENT_URL,
            }
        },
        "samples": [rent_sample],
    }

    rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    record = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(record)
    record.update({"asOf": CHECKED, "rent": rent})
    rows.sort(key=lambda row: int(row["hipflatId"]))
    (DIST / "bangkok-manual-market-samples.js").write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    # Default calculation: 2BR low sale total and paired area from PropertyHub;
    # when no 2BR rental is published, the app transparently scales the 1BR
    # rent-per-sqm to that same 66 sqm purchase area.
    purchase_price, purchase_area = 3_699_000, 66
    estimated_monthly_rent = round(rate * purchase_area)
    fee_per_sqm_month = 30
    annual_rent_after_agent = estimated_monthly_rent * 11
    annual_fee = fee_per_sqm_month * purchase_area * 12
    net_yield = (annual_rent_after_agent - annual_fee) / purchase_price * 100
    report = {
        "hipflatId": PROJECT_ID,
        "projectName": NAME,
        "checkedAt": CHECKED,
        "projectSourceUrl": PROJECT_URL,
        "rentListing": rent_sample,
        "rentSourceEvidence": {
            "priceTHBMonthly": price,
            "areaSqm": area,
            "bedrooms": beds,
            "floor": 3,
            "listed": "2026-02-12",
            "lastUpdatedAtCheck": "1 hour ago",
            "pageStatesAvailableForRent": True,
        },
        "saleListing": {
            "priceTHB": purchase_price,
            "areaSqm": purchase_area,
            "bedrooms": 2,
            "sourceUrl": SALE_URL,
        },
        "yieldEstimate": {
            "calculation": "((monthly rent estimate × 11 months) − annual common fee) / lowest 2BR purchase total",
            "rentRateSource": "1BR rent sample scaled to the 2BR sale listing's 66 sqm area because no 2BR rental is shown",
            "estimatedMonthlyRentTHB": estimated_monthly_rent,
            "commonFeeTHBPerSqmMonthly": fee_per_sqm_month,
            "deductAgentMonths": 1,
            "annualRentAfterAgentTHB": annual_rent_after_agent,
            "annualCommonFeeTHB": annual_fee,
            "netAnnualYieldPercent": round(net_yield, 2),
        },
        "notes": [
            "Hipflat project page links to the direct rental unit page. The unit page identifies The Next Ladprao, 1 bedroom, 46 sqm, floor 3, ฿12,000/month, listed 2026-02-12 and updated one hour before the 2026-10-18 check.",
            "The default investment estimate uses the lowest linked 2-bedroom PropertyHub sale listing at ฿3,699,000 for 66 sqm. The direct sale detail independently confirms 2 bedrooms, 66 sqm, and the same total.",
            "No 2-bedroom rental is published on the checked Hipflat project page. The app therefore labels the ROI rent as a 1-bedroom per-sqm rate scaled to the 2-bedroom sale unit's area. Defaults deduct one agent month and the PropertyHub-published indicative common fee of ฿30/sqm/month.",
        ],
    }
    (REPORTS / "the-next-ladprao-rent-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"hipflatId": PROJECT_ID, "rent": price, "areaSqm": area,
                      "ratePerSqm": round(rate, 2), "estimatedNetYieldPercent": round(net_yield, 2)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
