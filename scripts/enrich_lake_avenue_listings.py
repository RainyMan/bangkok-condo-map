"""Add directly linked PropertyHub sale and rent samples for Lake Avenue."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET_FILE = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT_FILE = ROOT / "reports" / f"lake-avenue-listings-{date.today().isoformat()}.json"
PROJECT_ID = 3267
PROJECT_NAME = "LAKE AVENUE Sukhumvit 16"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/lake-avenue-sukhumvit-16-ofsqrc"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/lake-avenue"
CHECKED_AT = date.today().isoformat()

SALE = {
    "id": "5640578",
    "price": 10_490_000,
    "area": 126,
    "beds": 2,
    "roomType": "2BR",
    "title": "For Sale!! Prime Location!! LAKE AVENUE Sukhumvit 16 MD-25085538",
    "url": "https://propertyhub.in.th/en/listings/for-sale-prime-location-lake-avenue-sukhumvit-16-md-25085538---5640578",
}
RENT = {
    "id": "5602448",
    "price": 48_000,
    "area": 130,
    "beds": 2,
    "roomType": "2BR",
    "title": "Lake Avenue | Very Spacious 2 Bed Condo For Rent in Asoke - BR14424CD",
    "url": "https://propertyhub.in.th/en/listings/lake-avenue-very-spacious-2-bed-condo-for-rent-in-asoke-br14424cd---5602448",
}


def main() -> None:
    content = MARKET_FILE.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*", content, re.S)
    if not match:
        raise ValueError("Could not parse the manual market samples array")
    rows = json.loads(match.group(1))
    project = next((row for row in rows if row.get("hipflatId") == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
        rows.append(project)

    samples_by_kind = {}
    for kind, source in (("sale", SALE), ("rent", RENT)):
        sample = {
            **source,
            "priceSqm": round(source["price"] / source["area"]),
            "sourceName": "PropertyHub",
            "projectName": "Lake Avenue",
            "checkedAt": CHECKED_AT,
            "matchedBy": "exact_propertyhub_project_page_unit",
            "listingStatus": "availability_unconfirmed_date_unknown",
        }
        market = project.setdefault(kind, {})
        samples = market.setdefault("samples", [])
        samples[:] = [item for item in samples if item.get("url") != sample["url"]]
        samples.append(sample)
        samples_by_kind[kind] = sample

    MARKET_FILE.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    REPORT_FILE.write_text(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "projectName": PROJECT_NAME,
                "checkedAt": CHECKED_AT,
                "projectPage": PROJECT_URL,
                "propertyHubProjectPage": PROPERTYHUB_PROJECT_URL,
                "saleSample": {
                    **samples_by_kind["sale"],
                    "verification": "PropertyHub direct listing states Lake Avenue, sale price, 2 bedrooms, and 126 sqm; exact listing is linked from the Lake Avenue project listing results.",
                },
                "rentSample": {
                    **samples_by_kind["rent"],
                    "verification": "PropertyHub direct listing states Lake Avenue, rent, 2 bedrooms, and 130 sqm; exact listing is linked from the Lake Avenue project listing results.",
                },
                "freshness": "Both individual listing pages omit an update date, so availability remains unconfirmed.",
                "yieldInputs": {
                    "bedrooms": 2,
                    "saleTotalThb": SALE["price"],
                    "saleAreaSqm": SALE["area"],
                    "rentRateThbPerSqmMonth": round(RENT["price"] / RENT["area"], 2),
                    "monthlyRentForSaleAreaThb": round(RENT["price"] / RENT["area"] * SALE["area"]),
                    "netYieldWithOneAgentMonthPercent": round(
                        ((RENT["price"] / RENT["area"] * SALE["area"]) * 11 / SALE["price"]) * 100,
                        2,
                    ),
                    "commonFee": "Not publicly verified; excluded from this estimate.",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"hipflatId": PROJECT_ID, "sale": [SALE["price"], SALE["area"], SALE["url"]], "rent": [RENT["price"], RENT["area"], RENT["url"]], "freshness": "unknown; flagged"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
