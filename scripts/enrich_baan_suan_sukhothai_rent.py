"""Add a current direct DDproperty rental listing and refresh yield baseline."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3460
NAME = "Baan Suan Sukhothai"
CHECKED = "2026-10-18"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/baan-suan-sukhothai-mdigyz"
RENT_URL = "https://www.ddproperty.com/property/baan-suan-sukhothai-%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%AA%E0%B8%B8%E0%B9%82%E0%B8%82%E0%B8%97%E0%B8%B1%E0%B8%A2-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-500301121"
SALE_URL = "https://propertyhub.in.th/en/listings/2-br-condo-at-baan-suan-sukhothai-near-mrt-bang-phlat-id-2240593---5889375"


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Cannot parse {symbol} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    rent_price, rent_area, rent_beds = 18_000, 44, 1
    rent_rate = rent_price / rent_area
    rent_sample = {
        "id": "500301121",
        "price": rent_price,
        "area": rent_area,
        "priceSqm": round(rent_rate, 2),
        "beds": rent_beds,
        "roomType": "1BR",
        "title": "Baan Suan Sukhothai，1 房，44 ㎡，4 樓，฿18,000/月",
        "url": RENT_URL,
        "sourceName": "DDproperty",
        "projectName": NAME,
        "updated": "2026-09-30",
        "checkedAt": CHECKED,
        "matchedBy": "DDproperty direct listing names Baan Suan Sukhothai, one bedroom, 44 sqm, floor 4, building 4, and THB 18,000/month",
        "listingStatus": "active_as_listed",
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": rent_price,
        "minimum": rent_price,
        "minimumArea": rent_area,
        "minimumSampleUpdated": "2026-09-30",
        "averageSqm": round(rent_rate),
        "minimumSqm": round(rent_rate),
        "minimumSqmSampleUpdated": "2026-09-30",
        "asOf": CHECKED,
        "sourceName": "DDproperty 直接出租掛牌",
        "source": PROJECT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": rent_price,
                "area": rent_area,
                "priceSqm": round(rent_rate),
                "minimumSqm": round(rent_rate),
                "sourceUrl": RENT_URL,
                "minimumSqmSourceUrl": RENT_URL,
            }
        },
        "samples": [rent_sample],
    }

    rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    # SiriMetro's manual record duplicated a newer, lower PropertyHub sale; remove it.
    rows = [row for row in rows if int(row.get("hipflatId", -1)) != 3228]
    record = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(record)
    record.update({"asOf": CHECKED, "replaceRent": True, "rent": rent})
    rows.sort(key=lambda row: int(row["hipflatId"]))
    (DIST / "bangkok-manual-market-samples.js").write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    purchase_price, purchase_area = 5_500_000, 67
    estimated_monthly_rent = round(rent_rate * purchase_area)
    annual_rent_after_agent = estimated_monthly_rent * 11
    annual_common_fee = 0  # No verifiable common-fee amount found.
    net_yield = (annual_rent_after_agent - annual_common_fee) / purchase_price * 100
    report = {
        "hipflatId": PROJECT_ID,
        "projectName": NAME,
        "checkedAt": CHECKED,
        "projectSourceUrl": PROJECT_URL,
        "rentListing": rent_sample,
        "saleListing": {
            "priceTHB": purchase_price,
            "areaSqm": purchase_area,
            "bedrooms": 2,
            "sourceUrl": SALE_URL,
            "updated": "2026-10-16",
        },
        "yieldEstimate": {
            "calculation": "((18,000 / 44 sqm) × 67 sqm × 11 months) / 5,500,000 × 100",
            "purchasePriceTHB": purchase_price,
            "purchaseAreaSqm": purchase_area,
            "rentSampleBedroomCount": rent_beds,
            "rentRateTHBPerSqmMonth": round(rent_rate, 2),
            "estimatedMonthlyRentTHB": estimated_monthly_rent,
            "deductAgentMonths": 1,
            "annualRentAfterAgentTHB": annual_rent_after_agent,
            "commonFeeTHBPerSqmMonthly": None,
            "annualCommonFeeDeductedTHB": annual_common_fee,
            "netAnnualYieldPercent": round(net_yield, 2),
        },
        "notes": [
            "DDproperty direct listing was published 2026-09-30 and checked 2026-10-18; it identifies Baan Suan Sukhothai, one bedroom, 44 sqm, floor 4, and rent of THB 18,000 per month.",
            "The lowest linked two-bedroom sale listing is THB 5,500,000 for 67 sqm, refreshed 2026-10-16.",
            "No two-bedroom rent sample or verifiable common-fee amount was found. The interface will label the rent-rate fallback as one-bedroom and deducts one agent month by default. Yield is 5.48% before common fee.",
        ],
        "sources": {"HipflatProject": PROJECT_URL, "DDpropertyRent": RENT_URL, "PropertyHubSale": SALE_URL},
    }
    (REPORTS / "baan-suan-sukhothai-yield-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"hipflatId": PROJECT_ID, "rentTHB": rent_price, "rentPerSqm": round(rent_rate),
                      "lowestTwoBedroomSale": purchase_price, "purchaseAreaSqm": purchase_area,
                      "estimatedRentTHB": estimated_monthly_rent, "netYieldPercent": round(net_yield, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
