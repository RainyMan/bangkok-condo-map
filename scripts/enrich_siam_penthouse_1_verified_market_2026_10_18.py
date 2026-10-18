"""Add current DDproperty sale and rental listings for Siam Penthouse 1."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED = "2026-10-18"
SALE_2BR_URL = (
    "https://www.ddproperty.com/property/siam-penthouse-1-"
    "%E0%B8%AA%E0%B8%A2%E0%B8%B2%E0%B8%A1-%E0%B9%80%E0%B8%9E%E0%B8%99%E0%B8%97%E0%B9%8C-"
    "%E0%B9%80%E0%B8%AE%E0%B8%B2%E0%B8%AA%E0%B9%8C-1-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87-"
    "%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B8%82%E0%B8%B2%E0%B8%A2-500031329"
)
SALE_3BR_URL = "https://www.ddproperty.com/en/property/siam-penthouse-1-bangkok-for-sale-10917691"
RENT_2BR_URL = "https://www.fazwaz.com/property-rent/2-bedroom-condo-for-rent-at-siam-penthouse-1-in-khlong-toei-bangkok-u6536784"


def load_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = ROOT / "dist" / filename
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{symbol} = "
    if not text.startswith(prefix) or not text.rstrip().endswith(";"):
        raise ValueError(f"Unexpected data file format: {filename}")
    return path, json.loads(text[len(prefix) : text.rfind(";")])


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    sales = [
        {
            "id": "500031329", "price": 7_500_000, "area": 80, "priceSqm": 93_750,
            "beds": 2, "roomType": "2BR",
            "title": "Siam Penthouse 1，2 房，80 ㎡，฿7,500,000",
            "url": SALE_2BR_URL, "sourceName": "DDproperty",
            "projectName": "Siam Penthouse 1", "checkedAt": CHECKED,
            "updated": "2026-09-25",
            "matchedBy": "exact_project_name_address_bedrooms_floor_area_and_project_identity",
            "listingStatus": "availability_unconfirmed_update_under_30d",
        },
        {
            "id": "10917691", "price": 10_900_000, "area": 120, "priceSqm": 90_833,
            "beds": 3, "roomType": "3BR",
            "title": "Siam Penthouse 1，3 房，120 ㎡，฿10,900,000",
            "url": SALE_3BR_URL, "sourceName": "DDproperty",
            "projectName": "Siam Penthouse 1", "checkedAt": CHECKED,
            "updated": "2026-09-15",
            "matchedBy": "exact_project_name_address_bedrooms_floor_area_and_project_identity",
            "listingStatus": "availability_unconfirmed_update_over_30d",
        },
    ]
    rent = {
        "id": "U6536784", "price": 27_000, "area": 80, "priceSqm": 337.5,
        "beds": 2, "roomType": "2BR",
        "title": "Siam Penthouse 1，2 房，80 ㎡，฿27,000/月",
        "url": RENT_2BR_URL, "sourceName": "FazWaz",
        "projectName": "Siam Penthouse 1", "checkedAt": CHECKED,
        "updated": CHECKED,
        "matchedBy": "exact_project_name_district_bedrooms_floor_area_and_updated_rental_page",
        "listingStatus": "active_as_listed",
    }
    sale_total = 18_400_000
    sale_average_sqm = round((93_750 + 90_833) / 2)
    sale = {
        "count": 2, "observedCount": 2, "countKind": "manual_verified_listing",
        "average": round(sale_total / 2), "minimum": 7_500_000,
        "minimumArea": 80, "minimumSampleUpdated": "2026-09-25",
        "averageSqm": sale_average_sqm, "minimumSqm": 90_833,
        "minimumSqmSampleUpdated": "2026-09-15", "asOf": CHECKED,
        "sourceName": "DDproperty 兩筆可見掛牌",
        "source": "https://www.ddproperty.com/en/condo-for-sale/at-siam-penthouse-1-87",
        "minimumSourceUrl": SALE_2BR_URL,
        "minimumSqmSourceUrl": SALE_3BR_URL,
        "samples": sales,
        "byBedroom": {
            "2": {"count": 1, "minimum": 7_500_000, "area": 80, "minimumArea": 80,
                  "priceSqm": 93_750, "minimumSqm": 93_750, "sourceUrl": SALE_2BR_URL,
                  "minimumSqmSourceUrl": SALE_2BR_URL},
            "3": {"count": 1, "minimum": 10_900_000, "area": 120, "minimumArea": 120,
                  "priceSqm": 90_833, "minimumSqm": 90_833, "sourceUrl": SALE_3BR_URL,
                  "minimumSqmSourceUrl": SALE_3BR_URL},
        },
    }
    manual_rent = {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": 27_000, "minimum": 27_000, "minimumArea": 80,
        "minimumSampleUpdated": CHECKED, "averageSqm": 338, "minimumSqm": 337.5,
        "minimumSqmSampleUpdated": CHECKED, "asOf": CHECKED,
        "sourceName": "FazWaz 單筆可見兩房掛牌", "source": RENT_2BR_URL,
        "minimumSourceUrl": RENT_2BR_URL, "minimumSqmSourceUrl": RENT_2BR_URL,
        "samples": [rent],
        "byBedroom": {
            "2": {"count": 1, "minimum": 27_000, "area": 80, "minimumSqm": 337.5,
                  "minimumSqmSourceUrl": RENT_2BR_URL, "sourceUrl": RENT_2BR_URL}
        },
    }

    market_path, market_rows = load_array(
        "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
    )
    record = next((row for row in market_rows if int(row["hipflatId"]) == 3325), None)
    if record is None:
        record = {"hipflatId": 3325, "name": "Siam Penthouse 1"}
        market_rows.append(record)
    if record.get("name") != "Siam Penthouse 1":
        raise ValueError(f"Hipflat ID 3325 has unexpected project name: {record.get('name')}")
    record["sale"] = sale
    record["rent"] = manual_rent
    record["completedYear"] = 1981
    record["completedYearSourceUrl"] = SALE_2BR_URL
    save_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES", sorted(market_rows, key=lambda r: int(r["hipflatId"])))

    report = {
        "checkedAt": CHECKED,
        "project": {"hipflatId": 3325, "name": "Siam Penthouse 1"},
        "saleListings": sales,
        "twoBedroomSaleAndRentYield": {
            "purchasePrice": 7_500_000, "purchaseAreaSqm": 80,
            "monthlyRentPerSqm": 337.5, "estimatedMonthlyRent": 27_000,
            "agentMonthsDeducted": 1, "commonFeeDeducted": False,
            "netYieldPercent": round(27_000 * 11 / 7_500_000 * 100, 2),
            "formula": "(2-bedroom rent per sqm × lowest 2-bedroom sale area × 11) ÷ lowest 2-bedroom sale price × 100",
            "note": "The two-bedroom sale price and area are from the same lowest-total-price listing. Management fee is not known and is not deducted.",
        },
    }
    report_path = ROOT / "reports" / "siam-penthouse-1-market-enrichment-2026-10-18.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": 3325, "saleListings": 2, "salePriceTwoBedroom": 7_500_000,
                      "saleAreaTwoBedroomSqm": 80, "rentTwoBedroom": 27_000,
                      "twoBedroomNetYieldPercent": report["twoBedroomSaleAndRentYield"]["netYieldPercent"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
