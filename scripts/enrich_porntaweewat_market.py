"""Add current Hipflat unit listings for Porntaweewat Condotown Petchkasem."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/porntaweewat-condotown-petchkasem-nkmubl"
SALE_440_URL = "https://www.hipflat.co.th/ads/l32008h78a8u39l232nec7a83u0c3el3"
SALE_500_URL = "https://www.hipflat.co.th/ads/n744lehu817luac8eaa1e9hn3u0h1430"
RENT_URL = "https://www.hipflat.co.th/ads/3lutt3l1822et7u37e0l04743u0h14u4"


def read_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    path = DIST / "bangkok-manual-market-samples.js"
    rows = read_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    sale_samples = [
        {
            "id": "N0603024",
            "price": 440000,
            "area": 25,
            "priceSqm": 17600,
            "beds": 1,
            "roomType": "1BR",
            "title": "Porntaweewat Condotown Petchkasem，1 房，25 ㎡，6 樓，฿440,000",
            "url": SALE_440_URL,
            "sourceName": "Hipflat",
            "projectName": "Porntaweewat Condotown Petchkasem",
            "checkedAt": "2026-10-18",
            "updated": "2026-09-09",
            "matchedBy": "exact_hipflat_project_page_unit",
            "listingStatus": "listed_on_project_page_update_over_30d",
        },
        {
            "id": "U5994920",
            "price": 500000,
            "area": 25,
            "priceSqm": 20000,
            "roomType": "STUDIO_OR_1BR_UNCLEAR",
            "title": "Porntaweewat Condotown Petchkasem，25 ㎡，3 樓，฿500,000",
            "url": SALE_500_URL,
            "sourceName": "Hipflat",
            "projectName": "Porntaweewat Condotown Petchkasem",
            "checkedAt": "2026-10-18",
            "matchedBy": "exact_hipflat_project_page_unit",
            "listingStatus": "active_as_listed",
        },
    ]
    rent_samples = [
        {
            "id": "U1692072",
            "price": 3000,
            "area": 26,
            "priceSqm": round(3000 / 26, 2),
            "beds": 1,
            "roomType": "1BR",
            "title": "Porntaweewat Condotown Petchkasem，1 房，26 ㎡，6 樓，฿3,000/月",
            "url": RENT_URL,
            "sourceName": "Hipflat",
            "projectName": "Porntaweewat Condotown Petchkasem",
            "checkedAt": "2026-10-18",
            "matchedBy": "exact_hipflat_project_page_unit",
            "listingStatus": "active_as_listed",
        }
    ]
    existing = next((row for row in rows if int(row["hipflatId"]) == 3132), None)
    record = {
        "hipflatId": 3132,
        "name": "Porntaweewat Condotown Petchkasem",
        "sale": {
            "count": 2,
            "observedCount": 2,
            "countKind": "manual_verified_listing",
            "average": 470000,
            "minimum": 440000,
            "minimumArea": 25,
            "minimumSampleUpdated": "2026-09-09",
            "averageSqm": 18800,
            "minimumSqm": 17600,
            "minimumSqmSampleUpdated": "2026-09-09",
            "asOf": "2026-10-18",
            "sourceName": "Hipflat 個別掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": SALE_440_URL,
            "minimumSqmSourceUrl": SALE_440_URL,
            "samples": sale_samples,
            "byBedroom": {
                "1": {
                    "count": 1,
                    "minimum": 440000,
                    "area": 25,
                    "priceSqm": 17600,
                    "minimumSqm": 17600,
                    "sourceUrl": SALE_440_URL,
                    "minimumSqmSourceUrl": SALE_440_URL,
                }
            },
        },
        "rent": {
            "count": 1,
            "observedCount": 1,
            "countKind": "manual_verified_listing",
            "average": 3000,
            "minimum": 3000,
            "minimumArea": 26,
            "minimumSampleUpdated": "2026-10-18",
            "averageSqm": round(3000 / 26, 2),
            "minimumSqm": round(3000 / 26, 2),
            "minimumSqmSampleUpdated": "2026-10-18",
            "asOf": "2026-10-18",
            "sourceName": "Hipflat 個別掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
            "samples": rent_samples,
            "byBedroom": {
                "1": {
                    "count": 1,
                    "minimum": 3000,
                    "area": 26,
                    "priceSqm": round(3000 / 26, 2),
                    "minimumSqm": round(3000 / 26, 2),
                    "sourceUrl": RENT_URL,
                    "minimumSqmSourceUrl": RENT_URL,
                }
            },
        },
    }
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

    coordinates_path = DIST / "bangkok-verified-coordinates.js"
    coordinates = read_array(coordinates_path, "BANGKOK_VERIFIED_COORDINATES")
    coordinate = next(row for row in coordinates if int(row["hipflatId"]) == 3132)
    coordinate["corroborationSourceUrl"] = SALE_440_URL
    coordinates_path.write_text(
        "window.BANGKOK_VERIFIED_COORDINATES = "
        + json.dumps(coordinates, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    report = {
        "hipflatId": 3132,
        "projectName": record["name"],
        "checkedAt": "2026-10-18",
        "projectSource": PROJECT_URL,
        "saleListings": sale_samples,
        "rentListings": rent_samples,
        "coordinateCorroboration": {
            "publishedCoordinate": [13.706467, 100.366343],
            "listingSource": SALE_440_URL,
            "existingProjectCoordinateSource": coordinate["sourceUrl"],
            "existingProjectCoordinate": [coordinate["lat"], coordinate["lng"]],
            "note": "Individual listing coordinate is approximately 140 m from the Thaiger project pin and matches the same project/address; retained Thaiger project pin and added as a corroborating source.",
        },
        "notes": [
            "Hipflat project page lists two sale units at ฿440,000–฿500,000 and one rental at ฿3,000/month.",
            "Lowest sale listing last updated 2026-09-09; Hipflat still lists it on the project page checked 2026-10-18.",
            "The ฿500,000 unit page has conflicting Studio/1-bedroom text, so no bedroom count was assigned to it.",
            "The market has no verified two-bedroom sale sample; ROI uses the one-bedroom baseline only when that room type is selected/available.",
        ],
    }
    (ROOT / "reports" / "porntaweewat-hipflat-listings-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added verified Hipflat samples for condo 3132; total manual market records: {len(rows)}")


if __name__ == "__main__":
    main()
