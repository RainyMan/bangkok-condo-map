"""Add current, individually linked rent listings for two Bangkok catalogue gaps."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET_FILE = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT_FILE = ROOT / "reports" / "verified-rent-gap-samples-2026-10-18.json"


def read_array() -> list[dict]:
    text = MARKET_FILE.read_text(encoding="utf-8")
    match = re.search(r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError("Could not read BANGKOK_MANUAL_MARKET_SAMPLES")
    return json.loads(match.group(1))


def write_array(rows: list[dict]) -> None:
    MARKET_FILE.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    checked = "2026-10-18"
    baan_samples = [
        {
            "id": "500643578", "price": 14500, "area": 72, "priceSqm": 201,
            "beds": 2, "roomType": "2BR",
            "title": "Baan Ruenrom Bangna，2 房，72 ㎡，฿14,500/月",
            "url": "https://www.ddproperty.com/property/baan-ruenrom-bangna-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%A3%E0%B8%B7%E0%B9%88%E0%B8%99%E0%B8%A3%E0%B8%A1%E0%B8%A2%E0%B9%8C-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%99%E0%B8%B2-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-500643578",
            "sourceName": "DDproperty", "projectName": "Baan Ruenrom Bangna",
            "checkedAt": checked, "updated": checked,
            "matchedBy": "exact_project_name_and_project_details_address_floor_area_bedrooms",
            "listingStatus": "active_as_listed",
        },
        {
            "id": "10392381", "price": 14500, "area": 64, "priceSqm": 227,
            "beds": 2, "roomType": "2BR",
            "title": "Baan Ruenrom Bangna，2 房，64 ㎡，฿14,500/月",
            "url": "https://www.ddproperty.com/en/property/baan-ruenrom-bangna-bangkok-for-rent-10392381",
            "sourceName": "DDproperty", "projectName": "Baan Ruenrom Bangna",
            "checkedAt": checked, "updated": checked,
            "matchedBy": "exact_project_name_and_project_details_address_floor_area_bedrooms",
            "listingStatus": "active_as_listed",
        },
    ]
    namchoke_samples = [
        {
            "id": "V61052", "price": 3200, "area": 30.5, "priceSqm": 105,
            "beds": 0, "roomType": "STUDIO",
            "title": "Namchoke Condominium，Studio，30.5 ㎡，11 樓，฿3,200/月",
            "url": "https://zmyhome.com/property/V61052",
            "sourceName": "Zmyhome", "projectName": "Namchoke Condominium",
            "checkedAt": checked, "updated": "2026-09-14",
            "matchedBy": "exact_project_name_address_building_floor_and_active_listing_status",
            "listingStatus": "active_as_listed",
        }
    ]
    baan_rate_min = min(row["price"] / row["area"] for row in baan_samples)
    records = [
        {
            "hipflatId": 5474,
            "name": "Baan Ruenrom Bangna",
            "rent": {
                "count": 2, "observedCount": 2, "countKind": "manual_verified_listing",
                "average": 14500, "minimum": 14500, "minimumArea": 72,
                "minimumSampleUpdated": checked, "averageSqm": 214,
                "minimumSqm": round(baan_rate_min), "minimumSqmSampleUpdated": checked,
                "asOf": checked, "sourceName": "DDproperty 兩筆可見掛牌",
                "source": "https://www.ddproperty.com/en/condo-for-rent/at-baan-ruenrom-bangna-1758/partially-furnished",
                "minimumSourceUrl": baan_samples[0]["url"],
                "minimumSqmSourceUrl": baan_samples[0]["url"],
                "samples": baan_samples,
            },
        },
        {
            "hipflatId": 3777,
            "name": "Namchoke Condominium",
            "rent": {
                "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
                "average": 3200, "minimum": 3200, "minimumArea": 30.5,
                "minimumSampleUpdated": "2026-09-14", "averageSqm": 105,
                "minimumSqm": 105, "minimumSqmSampleUpdated": "2026-09-14",
                "asOf": checked, "sourceName": "Zmyhome 單筆掛牌",
                "source": "https://zmyhome.com/property/V61052",
                "minimumSourceUrl": namchoke_samples[0]["url"],
                "minimumSqmSourceUrl": namchoke_samples[0]["url"],
                "samples": namchoke_samples,
            },
        },
    ]

    rows = read_array()
    by_id = {int(row["hipflatId"]): row for row in rows}
    for record in records:
        existing = by_id.setdefault(record["hipflatId"], {"hipflatId": record["hipflatId"], "name": record["name"]})
        if existing.get("name") != record["name"]:
            raise RuntimeError(f"Hipflat ID/name mismatch for {record['hipflatId']}: {existing.get('name')}")
        existing["rent"] = record["rent"]
    write_array(sorted(by_id.values(), key=lambda row: int(row["hipflatId"])))

    sale_price, sale_area = 2_699_000, 65
    scaled_monthly_rent = round(baan_rate_min * sale_area)
    yield_percent = (scaled_monthly_rent * 11) / sale_price * 100
    report = {
        "checkedAt": checked,
        "additions": records,
        "baanRuenromTwoBedroomEstimate": {
            "salePrice": sale_price, "saleAreaSqm": sale_area,
            "saleListingUrl": "https://propertyhub.in.th/en/listings/for-sale-baan-ruanrom-bangna-no-112---6490387",
            "lowestRentPerSqm": round(baan_rate_min, 2),
            "rentScaledToSaleArea": scaled_monthly_rent,
            "agentFeeMonthsDeducted": 1, "commonFeeDeducted": False,
            "netYieldPercent": round(yield_percent, 2),
            "formula": "(monthly rent × 11) ÷ purchase price × 100; no verified common fee available",
        },
        "namchokeYield": "No default two-bedroom yield: available linked sale samples are one-bedroom and rental sample is a studio.",
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"addedProjects": [row["hipflatId"] for row in records], "verifiedRentListings": 3,
                      "baanTwoBedroomNetYieldPercent": round(yield_percent, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
