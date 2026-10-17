"""Add current verified PropertyHub samples and a Google Maps point for Avenue 61."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3408
PROJECT_NAME = "The Avenue Sukhumvit 61"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/the-avenue-sukhumvit-61-wulzso"
SALE_URL = "https://propertyhub.in.th/en/listings/for-sale-condo-avenue-61-bts-thong-lo-khlong-tan-nuea-watthana-bangkok-cx-74320-live-chat-with-us-add-line-connexproperty--b5cd09b0---4026121"
RENT_102_URL = "https://propertyhub.in.th/en/listings/2-br-condo-at-avenue-61-condominium-near-bts-thong-lor-id-1852075--b5dd0984---4740685"
RENT_107_URL = "https://propertyhub.in.th/en/listings/sr146-special-deal-for-rent-condo-avenue-61--ad820934---2818834"
GOOGLE_MAPS_SHORT_URL = "https://goo.gl/maps/Au93FhkzX64F2qVm8"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    checked_at = "2026-10-18"
    sale = {
        "count": 23,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": 9_500_000,
        "minimum": 9_500_000,
        "minimumArea": 102,
        "minimumSampleUpdated": checked_at,
        "averageSqm": 93_137,
        "minimumSqm": round(9_500_000 / 102),
        "minimumSqmSampleUpdated": checked_at,
        "asOf": checked_at,
        "sourceName": "PropertyHub 單筆掛牌",
        "source": "https://propertyhub.in.th/en/condo-for-sale/project-avenue-61",
        "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL,
        "byBedroom": {
            "2": {
                "count": 1,
                "minimum": 9_500_000,
                "area": 102,
                "minimumSqm": round(9_500_000 / 102),
                "sourceUrl": SALE_URL,
            }
        },
        "samples": [
            {
                "id": "4026121",
                "price": 9_500_000,
                "area": 102,
                "priceSqm": round(9_500_000 / 102),
                "beds": 2,
                "roomType": "2BR",
                "title": "The Avenue Sukhumvit 61，2 房，102 ㎡，8 樓，฿9,500,000",
                "url": SALE_URL,
                "sourceName": "PropertyHub",
                "projectName": "Avenue 61",
                "checkedAt": checked_at,
                "updated": checked_at,
                "matchedBy": "exact_propertyhub_project_and_listing_page_google_maps_pin",
                "listingStatus": "active_as_listed",
            }
        ],
    }
    rent_samples = [
        {
            "id": "2818834",
            "price": 40_000,
            "area": 107.01,
            "priceSqm": round(40_000 / 107.01),
            "beds": 2,
            "roomType": "2BR",
            "title": "Avenue 61，2 房，107.01 ㎡，B 棟 4 樓，฿40,000/月",
            "url": RENT_107_URL,
            "sourceName": "PropertyHub",
            "projectName": "Avenue 61",
            "checkedAt": checked_at,
            "updated": "2026-10-17",
            "matchedBy": "exact_propertyhub_project_and_listing_page",
            "listingStatus": "active_as_listed",
        },
        {
            "id": "4740685",
            "price": 40_000,
            "area": 102,
            "priceSqm": round(40_000 / 102),
            "beds": 2,
            "roomType": "2BR",
            "title": "Avenue 61，2 房，102 ㎡，8 樓，฿40,000/月",
            "url": RENT_102_URL,
            "sourceName": "PropertyHub",
            "projectName": "Avenue 61",
            "checkedAt": checked_at,
            "updated": "2026-10-17",
            "matchedBy": "exact_propertyhub_project_and_listing_page",
            "listingStatus": "active_as_listed",
        },
    ]
    rent = {
        "count": 90,
        "observedCount": 2,
        "countKind": "manual_verified_listing",
        "average": 40_000,
        "minimum": 40_000,
        "minimumArea": 102,
        "minimumSampleUpdated": "2026-10-17",
        "averageSqm": round(sum(row["priceSqm"] for row in rent_samples) / len(rent_samples)),
        "minimumSqm": rent_samples[0]["priceSqm"],
        "minimumSqmSampleUpdated": "2026-10-17",
        "asOf": checked_at,
        "sourceName": "PropertyHub 兩筆可見掛牌",
        "source": "https://propertyhub.in.th/en/condo-for-rent/project-avenue-61",
        "minimumSourceUrl": RENT_102_URL,
        "minimumSqmSourceUrl": RENT_107_URL,
        "samples": rent_samples,
    }
    markets_path = DIST / "bangkok-manual-market-samples.js"
    markets = read_array(markets_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    record = {
        "hipflatId": PROJECT_ID,
        "name": PROJECT_NAME,
        "completedYear": 2005,
        "completedYearSourceUrl": "https://propertyhub.in.th/en/projects/avenue-61",
        "sale": sale,
        "rent": rent,
        "fee": {
            "rate": 35,
            "status": "public",
            "note": "PropertyHub 專案頁刊載管理費 ฿35/㎡/月；向管委會確認目前費率。",
            "source": "https://propertyhub.in.th/en/projects/avenue-61",
        },
    }
    existing = next((row for row in markets if int(row["hipflatId"]) == PROJECT_ID), None)
    if existing:
        existing.update(record)
    else:
        markets.append(record)
        markets.sort(key=lambda row: int(row["hipflatId"]))
    write_array(markets_path, "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

    coord_path = DIST / "bangkok-verified-coordinates.js"
    coordinates = read_array(coord_path, "BANGKOK_VERIFIED_COORDINATES")
    coordinate = {
        "hipflatId": PROJECT_ID,
        "name": PROJECT_NAME,
        "lat": 13.7247543,
        "lng": 100.582655,
        "locationVerified": True,
        "sourceName": "PropertyHub 出售物件所附 Google Maps 大樓點位",
        "sourceUrl": GOOGLE_MAPS_SHORT_URL,
        "verificationSourceUrl": HIPFLAT_URL,
        "corroborationSourceUrl": SALE_URL,
        "verificationMethod": "exact_avenue_61_listing_google_maps_place_pin_crosschecked_with_hipflat_project_name_and_sukhumvit_61_address",
        "asOf": checked_at,
    }
    old_coordinate = next((row for row in coordinates if int(row["hipflatId"]) == PROJECT_ID), None)
    if old_coordinate:
        old_coordinate.update(coordinate)
    else:
        coordinates.append(coordinate)
        coordinates.sort(key=lambda row: int(row["hipflatId"]))
    write_array(coord_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

    report = {
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT_NAME,
        "checkedAt": checked_at,
        "hipflatProject": HIPFLAT_URL,
        "coordinate": coordinate,
        "sale": sale,
        "rent": rent,
        "managementFee": record["fee"],
        "completedYear": {"year": 2005, "sourceUrl": record["completedYearSourceUrl"]},
        "defaultTwoBedroomNetYield": {
            "purchasePrice": 9_500_000,
            "purchaseListingAreaSqm": 102,
            "rentPerSqmPerMonth": rent_samples[0]["priceSqm"],
            "estimatedRentPerMonthForPurchaseArea": round(40_000 / 107.01 * 102),
            "agentFeeMonthsDeducted": 1,
            "annualCommonFee": 35 * 102 * 12,
            "netYieldPercent": round((round(40_000 / 107.01 * 102) * 11 - 35 * 102 * 12) / 9_500_000 * 100, 2),
        },
        "notes": [
            "PropertyHub 2026-10-17 project listing refresh identifies the two-bedroom sale at ฿9,500,000, 102 m², floor 8; its detail page update timestamp is 2026-10-18 00:10 local and includes the Google Maps short link.",
            "Two exact two-bedroom rental listing pages show ฿40,000/month at 102 m² and 107.01 m²; the latter is the lower rent per m² and the former ties for lowest total rent. Project result cards were refreshed 2026-10-17.",
            "PropertyHub project information lists utility/common fee ฿35/m²/month and completion year 2005. The project page has inconsistent unit totals, so unit count was not changed.",
            "Default two-bedroom net yield at checked source rates: purchase ฿9,500,000; selected sale unit 102 m²; rent rate ฿40,000 / 107.01 m²; estimated monthly rent scaled to 102 m²; deduct 1 agent month and ฿35/m²/month common fee. Other transaction costs, vacancy, tax, and maintenance are excluded.",
        ],
    }
    (ROOT / "reports" / "avenue61-listings-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Updated Avenue 61 market samples and coordinates; manual records: {len(markets)}")


if __name__ == "__main__":
    main()
