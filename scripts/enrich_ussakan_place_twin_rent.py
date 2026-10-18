"""Add Hipflat's directly linked rental listing for Ussakan Place Twin Condo."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET_FILE = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT_FILE = ROOT / "reports" / f"ussakan-place-twin-rent-{date.today().isoformat()}.json"
PROJECT_ID = 3038
PROJECT_NAME = "Ussakan Place Twin Condo"
PROJECT_URL = "https://www.hipflat.co.th/projects/ussakan-place-twin-condo-uprazd"
LISTING_URL = "https://www.hipflat.co.th/ads/2a0a0aa081tl8cnn841984eu3ul38t9u"
MONTHLY_RENT = 8000
AREA_SQM = 38
RATE = round(MONTHLY_RENT / AREA_SQM)
CHECKED_AT = date.today().isoformat()


def main() -> None:
    content = MARKET_FILE.read_text(encoding="utf-8")
    match = re.fullmatch(
        r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*",
        content,
        re.S,
    )
    if not match:
        raise ValueError("Could not parse the manual market samples array")
    rows = json.loads(match.group(1))
    project = next((row for row in rows if row.get("hipflatId") == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
        rows.append(project)

    rent = project.setdefault("rent", {})
    samples = rent.setdefault("samples", [])
    sample = {
        "id": "CX-118532",
        "price": MONTHLY_RENT,
        "area": AREA_SQM,
        "priceSqm": RATE,
        "beds": 1,
        "roomType": "1BR",
        "title": f"{PROJECT_NAME}，1 房，38 ㎡，฿8,000/月",
        "url": LISTING_URL,
        "sourceName": "Hipflat",
        "projectName": PROJECT_NAME,
        "updated": CHECKED_AT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_page_unit",
        "listingStatus": "active_as_listed",
    }
    samples[:] = [row for row in samples if row.get("url") != LISTING_URL]
    samples.append(sample)
    rent.update(
        {
            "count": max(int(rent.get("count", 0) or 0), 1),
            "observedCount": max(int(rent.get("observedCount", 0) or 0), 1),
            "countKind": "manual_verified_listing",
            "average": MONTHLY_RENT,
            "minimum": MONTHLY_RENT,
            "minimumArea": AREA_SQM,
            "minimumSampleUpdated": CHECKED_AT,
            "averageSqm": RATE,
            "minimumSqm": RATE,
            "minimumSqmSampleUpdated": CHECKED_AT,
            "asOf": CHECKED_AT,
            "sourceName": "Hipflat 個別出租掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": LISTING_URL,
            "minimumSqmSourceUrl": LISTING_URL,
            "byBedroom": {
                "1": {
                    "count": 1,
                    "minimum": MONTHLY_RENT,
                    "area": AREA_SQM,
                    "minimumSqm": MONTHLY_RENT / AREA_SQM,
                    "averageSqm": MONTHLY_RENT / AREA_SQM,
                    "sourceUrl": LISTING_URL,
                    "minimumSqmSourceUrl": LISTING_URL,
                }
            },
        }
    )
    MARKET_FILE.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    report = {
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT_NAME,
        "checkedAt": CHECKED_AT,
        "rentalListing": {
            "id": "CX-118532",
            "monthlyRentThb": MONTHLY_RENT,
            "areaSqm": AREA_SQM,
            "rentThbPerSqmMonth": round(MONTHLY_RENT / AREA_SQM, 2),
            "bedrooms": 1,
            "updatedAt": "2026-10-18T00:40:02",
            "projectPage": PROJECT_URL,
            "listingPage": LISTING_URL,
            "verification": "Hipflat project page links to this exact listing; listing detail confirms project name, rent, area, bedroom count, and update timestamp.",
        },
        "locationReview": {
            "status": "project_coordinates_verified; listing address conflict noted",
            "coordinates": {"lat": 13.8102772, "lng": 100.5628531},
            "coordinateSource": "https://www.thaigerproperty.com/projects/thailand/bangkok/chatuchak/chomphon/ussakan-place-twin-condo",
            "crossCheckSource": PROJECT_URL,
            "reason": "The current coordinate feed matches Thaiger Property's exact project slug and the Hipflat project page's Chatuchak address. The linked rental advert's lower description also mentions Ramkhamhaeng 105/1, Hua Mak/Bang Kapi, while the advert header and project-page relationship identify Ussakan Place Twin Condo in Chatuchak. Keep the project pin from the independently cross-checked project pages and flag the conflicting advert text for later reconciliation.",
        },
        "yield": {
            "status": "not_calculated",
            "reason": "No linked sale listing is available in this sample, so a project purchase baseline cannot be paired with this rent sample.",
        },
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"project": PROJECT_NAME, "rentThb": MONTHLY_RENT, "areaSqm": AREA_SQM, "rentThbPerSqm": RATE, "listing": LISTING_URL, "coordinateStatus": "project_verified_with_listing_address_conflict_note", "yield": "not_calculated"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
