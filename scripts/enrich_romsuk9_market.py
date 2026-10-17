"""Add verifiable Hipflat sale listings and the published common fee for Romsuk 9."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_URL = "https://www.hipflat.co.th/projects/romsuk-9-condotown-gloeqm"
SALE_28_URL = "https://www.hipflat.co.th/ads/2enl443088at7814c92n92h93u09n9h7"
SALE_27_URL = "https://www.hipflat.co.th/ads/4u9l0aa788a09u07ea9cnhea3ul37el3"
RENT_URL = "https://propertyhub.in.th/listings/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%A3%E0%B9%88%E0%B8%A1%E0%B8%AA%E0%B8%B8%E0%B8%829%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C-%E0%B8%95%E0%B8%B4%E0%B8%94%E0%B8%96%E0%B8%99%E0%B8%99%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B1%E0%B8%87%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89%E0%B8%AA%E0%B8%99%E0%B8%B2%E0%B8%A1%E0%B8%9A%E0%B8%B4%E0%B8%99%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%A3%E0%B8%93%E0%B8%A0%E0%B8%B9%E0%B8%A1%E0%B8%B4---5290483"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    path = DIST / "bangkok-manual-market-samples.js"
    rows = read_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    samples = [
        {
            "id": "NI-085376",
            "price": 350000,
            "area": 28,
            "priceSqm": 12500,
            "title": "Romsuk 9 Condotown，28 ㎡，4 樓，฿350,000",
            "url": SALE_28_URL,
            "sourceName": "Hipflat",
            "projectName": "Romsuk 9 Condotown",
            "checkedAt": "2026-10-18",
            "updated": "2026-09-09",
            "matchedBy": "exact_hipflat_project_page_unit",
            "listingStatus": "availability_unconfirmed_update_over_30d",
        },
        {
            "id": "NI-085373",
            "price": 350000,
            "area": 27,
            "priceSqm": 12962,
            "title": "Romsuk 9 Condotown，27 ㎡，4 樓，฿350,000",
            "url": SALE_27_URL,
            "sourceName": "Hipflat",
            "projectName": "Romsuk 9 Condotown",
            "checkedAt": "2026-10-18",
            "updated": "2026-09-09",
            "matchedBy": "exact_hipflat_project_page_unit",
            "listingStatus": "availability_unconfirmed_update_over_30d",
        },
    ]
    record = {
        "hipflatId": 3107,
        "name": "Romsuk 9 Condotown",
        "sale": {
            "count": 2,
            "observedCount": 2,
            "countKind": "manual_verified_listing",
            "average": 350000,
            "minimum": 350000,
            "minimumArea": 28,
            "minimumSampleUpdated": "2026-09-09",
            "averageSqm": 12731,
            "minimumSqm": 12500,
            "minimumSqmSampleUpdated": "2026-09-09",
            "asOf": "2026-10-18",
            "sourceName": "Hipflat 個別掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": SALE_28_URL,
            "minimumSqmSourceUrl": SALE_28_URL,
            "samples": samples,
        },
        "rent": {
            "count": 1,
            "observedCount": 1,
            "countKind": "manual_verified_listing",
            "average": 2800,
            "minimum": 2800,
            "minimumArea": 28,
            "averageSqm": 100,
            "minimumSqm": 100,
            "asOf": "2026-10-18",
            "sourceName": "PropertyHub 個別掛牌",
            "source": RENT_URL,
            "minimumSourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
            "samples": [
                {
                    "id": "5290483",
                    "price": 2800,
                    "area": 28,
                    "priceSqm": 100,
                    "beds": 1,
                    "title": "Romsuk 9 Condotown，1 房，28 ㎡，4 樓，฿2,800/月",
                    "url": RENT_URL,
                    "sourceName": "PropertyHub",
                    "projectName": "Rumsuk 9 Condotown",
                    "checkedAt": "2026-10-18",
                    "updated": None,
                    "availableFrom": "2025-07-31",
                    "matchedBy": "exact_propertyhub_project_and_listing_page",
                    "listingStatus": "availability_unconfirmed_date_unknown",
                }
            ],
        },
        "fee": {
            "rate": 12.34,
            "status": "public",
            "note": "Hipflat 單筆出售掛牌註明每平方公尺管理費 ฿12.34/月；請向管委會確認最新費率。",
            "source": SALE_28_URL,
        },
    }
    existing = next((row for row in rows if int(row["hipflatId"]) == 3107), None)
    if existing:
        existing.update(record)
    else:
        rows.append(record)
        rows.sort(key=lambda row: int(row["hipflatId"]))
    path.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    report = {
        "hipflatId": 3107,
        "projectName": "Romsuk 9 Condotown",
        "checkedAt": "2026-10-18",
        "projectSource": PROJECT_URL,
        "saleListings": samples,
        "rentListing": record["rent"]["samples"][0],
        "fee": record["fee"],
        "notes": [
            "Hipflat Thai project page lists two active sale cards at ฿350,000 each; both unit pages were opened directly.",
            "Both unit listings show the same update date, 2026-09-09, and were still linked from the project page when checked 2026-10-18.",
            "Listing card areas are 28 m² and 27 m². The descriptions contain slightly more precise floor areas, while the project cards report rounded areas and per-square-metre rates; the compiled comparison uses card values consistently.",
            "The first unit description states common area fee ฿12.34/m²/month; confirm with the juristic office before purchase.",
            "PropertyHub direct listing page 5290483 identifies the exact Rumsuk 9 project, rent ฿2,800/month, 28 m², 1 bedroom and floor 4. Its last-updated field is blank and its ready-to-rent date is 2025-07-31, so current availability is unconfirmed; the UI labels it accordingly.",
            "PropertyHub search snippets also show a Romsuk 9 rental card at ฿3,000/month, 28.5 m², floor 1, with a 2026-06-12 update date, but the direct listing URL was not independently identified and the unit details conflict with listing 5290483. That result is excluded rather than merged.",
        ],
    }
    (ROOT / "reports" / "romsuk9-listings-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added two Hipflat sale listings and one PropertyHub rental listing for condo 3107; manual records: {len(rows)}")


if __name__ == "__main__":
    main()
