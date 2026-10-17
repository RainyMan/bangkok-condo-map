"""Add directly verified sale and rental listings for Niche Mono Itsaraphap."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3369
PROJECT = "Niche Mono Itsaraphap"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-niche-mono-itsaraphap"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-niche-mono-itsaraphap"
LISTING_URL = "https://propertyhub.in.th/en/listings/1bed-1bath-mrt-itsaraphap-30sqm-thb-13-000-mo-fl-4-niche-mono-itsaraphap-bangkok---6368947"
SALE_LISTING_URL = "https://propertyhub.in.th/en/listings/a046959-niche-mono-itsaraphap---6220174"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    checked = "2026-10-18"
    updated = "2026-10-03"
    sample = {
        "id": "6368947",
        "price": 13000,
        "area": 30,
        "priceSqm": round(13000 / 30, 2),
        "beds": 1,
        "roomType": "1BR",
        "title": "Niche Mono Itsaraphap，1 房，30 ㎡，4 樓，฿13,000/月",
        "url": LISTING_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "checkedAt": checked,
        "updated": updated,
        "availableFrom": "2026-09-03",
        "matchedBy": "exact_propertyhub_project_and_listing_page",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    sale_sample = {
        "id": "6220174",
        "price": 2900000,
        "area": 28.42,
        "priceSqm": round(2900000 / 28.42),
        "beds": 1,
        "roomType": "1BR",
        "title": "A046959 Niche Mono Itsaraphap，1 房，28.42 ㎡，4 樓，฿2,900,000",
        "url": SALE_LISTING_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "checkedAt": checked,
        "updated": "2026-10-02",
        "matchedBy": "exact_propertyhub_project_and_listing_page",
        "listingStatus": "active_as_listed",
    }
    record = {
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "sale": {
            "count": 1,
            "observedCount": 1,
            "countKind": "manual_verified_listing",
            "average": 2900000,
            "minimum": 2900000,
            "minimumArea": 28.42,
            "minimumSampleUpdated": "2026-10-02",
            "averageSqm": round(2900000 / 28.42),
            "minimumSqm": round(2900000 / 28.42),
            "minimumSqmSampleUpdated": "2026-10-02",
            "asOf": checked,
            "sourceName": "PropertyHub 個別掛牌",
            "source": SALE_PROJECT_URL,
            "minimumSourceUrl": SALE_LISTING_URL,
            "minimumSqmSourceUrl": SALE_LISTING_URL,
            "samples": [sale_sample],
        },
        "rent": {
            "count": 1,
            "observedCount": 1,
            "countKind": "manual_verified_listing",
            "average": 13000,
            "minimum": 13000,
            "minimumArea": 30,
            "minimumSampleUpdated": updated,
            "averageSqm": 433,
            "minimumSqm": round(13000 / 30),
            "minimumSqmSampleUpdated": updated,
            "asOf": checked,
            "sourceName": "PropertyHub 個別掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": LISTING_URL,
            "minimumSqmSourceUrl": LISTING_URL,
            "samples": [sample],
        },
    }
    market_path = DIST / "bangkok-manual-market-samples.js"
    rows = read_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    existing = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if existing:
        existing.update(record)
    else:
        rows.append(record)
        rows.sort(key=lambda row: int(row["hipflatId"]))
    market_path.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    report = {
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "checkedAt": checked,
        "saleProjectSource": SALE_PROJECT_URL,
        "saleListing": sale_sample,
        "rentProjectSource": PROJECT_URL,
        "rentListing": sample,
        "defaultYieldEstimate": {
            "bedrooms": 1,
            "purchasePrice": 2900000,
            "purchaseAreaSqm": 28.42,
            "sourceRentMonthly": 13000,
            "sourceRentAreaSqm": 30,
            "estimatedMonthlyRentAtPurchaseArea": 12315,
            "commonFeePerSqmMonthly": 57,
            "deductAgentMonths": 1,
            "annualRentAfterAgent": 135465,
            "annualCommonFee": 19439.28,
            "netAnnualYieldPercent": 4.0009,
        },
        "notes": [
            "PropertyHub's exact project rent page showed three rental listings when checked on 2026-10-18; the listing page opened directly and identifies the project, one bedroom, 30 sqm, THB 13,000/month and floor 4.",
            "The project result card was refreshed 2026-10-03. The direct listing states available from 2026-09-03, a date already passed at verification; the listing remains visible, but current vacancy is unconfirmed and is labeled in the UI.",
            "The listing's rent per square metre is THB 433.33/month. The manually verified sample set contains only this directly inspected rental, not all three result cards.",
            "PropertyHub's exact sale page showed the 1-bedroom A046959 card at THB 2,900,000 for 28.42 sqm, last refreshed 2026-10-02; its direct detail page was opened and confirmed project name, sale price, bedroom count, floor, and area. The project result page showed no active two-bedroom sale sample, so the ROI baseline remains explicitly one-bedroom.",
            "Using the lowest verified 1-bedroom sale sample, the directly verified rental rate scaled to 28.42 sqm, THB 57/sqm/month common fee, one agent month, and 12 months of common fees, the default net annual ROI is approximately 4.00%. Taxes, vacancy, maintenance, and purchase costs are excluded.",
        ],
    }
    (ROOT / "reports" / "niche-mono-itsaraphap-market-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added exact PropertyHub sale and rent samples for Hipflat condo {PROJECT_ID}.")


if __name__ == "__main__":
    main()
