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
            "listingStatus": "listed_on_project_page_update_over_30d",
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
            "listingStatus": "listed_on_project_page_update_over_30d",
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
        "fee": record["fee"],
        "notes": [
            "Hipflat Thai project page lists two active sale cards at ฿350,000 each; both unit pages were opened directly.",
            "Both unit listings show the same update date, 2026-09-09, and were still linked from the project page when checked 2026-10-18.",
            "Listing card areas are 28 m² and 27 m². The descriptions contain slightly more precise floor areas, while the project cards report rounded areas and per-square-metre rates; the compiled comparison uses card values consistently.",
            "The first unit description states common area fee ฿12.34/m²/month; confirm with the juristic office before purchase.",
            "No matching rental listing was displayed on the Hipflat project page, so rent and ROI remain unavailable for this project.",
        ],
    }
    (ROOT / "reports" / "romsuk9-hipflat-listings-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added two verified Hipflat sale listings and one fee reference for condo 3107; manual records: {len(rows)}")


if __name__ == "__main__":
    main()
