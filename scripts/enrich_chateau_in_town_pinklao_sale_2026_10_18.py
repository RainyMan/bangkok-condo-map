"""Add a checked direct DDproperty sale listing to Chateau In Town Pinklao."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED = "2026-10-18"
LISTING_URL = (
    "https://www.ddproperty.com/property/chateau-in-town-pinklao-siriraj-"
    "%E0%B8%8A%E0%B8%B2%E0%B9%82%E0%B8%95%E0%B8%A7%E0%B9%8C-"
    "%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C-"
    "%E0%B8%9B%E0%B8%B4%E0%B9%88%E0%B8%99%E0%B9%80%E0%B8%81%E0%B8%A5%E0%B9%89%E0%B8%B2-"
    "%E0%B8%A8%E0%B8%B4%E0%B8%A3%E0%B8%B4%E0%B8%A3%E0%B8%B2%E0%B8%8A-"
    "%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-"
    "%E0%B8%82%E0%B8%B2%E0%B8%A2-500029043"
)
COORDINATE_CROSSCHECK = (
    "https://thinkofliving.com/project/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/15090/"
)


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
    price = 2_390_000
    area = 29.0
    price_sqm = round(price / area)
    sample = {
        "id": "500029043",
        "price": price,
        "area": area,
        "priceSqm": price_sqm,
        "beds": 1,
        "roomType": "1BR",
        "title": "Chateau In Town Pinklao-Siriraj，1 房，29 ㎡，฿2,390,000",
        "url": LISTING_URL,
        "sourceName": "DDproperty",
        "projectName": "Chateau In Town Pinklao-Siriraj",
        "checkedAt": CHECKED,
        "updated": "2026-09-19",
        "matchedBy": "exact_project_name_address_completion_year_and_210_unit_project_details",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }
    sale = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "minimumSampleUpdated": "2026-09-19",
        "averageSqm": price_sqm,
        "minimumSqm": price_sqm,
        "minimumSqmSampleUpdated": "2026-09-19",
        "asOf": CHECKED,
        "sourceName": "DDproperty 單筆可見掛牌",
        "source": LISTING_URL,
        "minimumSourceUrl": LISTING_URL,
        "minimumSqmSourceUrl": LISTING_URL,
        "samples": [sample],
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": price,
                "area": area,
                "minimumArea": area,
                "priceSqm": price_sqm,
                "minimumSqm": price_sqm,
                "sourceUrl": LISTING_URL,
                "minimumSqmSourceUrl": LISTING_URL,
            }
        },
    }

    market_path, market_rows = load_array(
        "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
    )
    record = next((row for row in market_rows if int(row["hipflatId"]) == 3384), None)
    if record is None:
        record = {"hipflatId": 3384, "name": "Chateau In Town Pinklao"}
        market_rows.append(record)
    if record.get("name") != "Chateau In Town Pinklao":
        raise ValueError(f"Hipflat ID 3384 has unexpected project name: {record.get('name')}")
    record["sale"] = sale
    record["completedYear"] = 2024
    record["completedYearSourceUrl"] = COORDINATE_CROSSCHECK
    save_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES", sorted(market_rows, key=lambda r: int(r["hipflatId"])))

    coord_path, coord_rows = load_array(
        "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"
    )
    coord = next((row for row in coord_rows if int(row["hipflatId"]) == 3384), None)
    if coord is None:
        raise ValueError("Expected the existing verified coordinate for Hipflat ID 3384")
    coord["corroborationSourceUrl"] = COORDINATE_CROSSCHECK
    coord["verificationMethod"] = (
        "PropertyHub project pin cross-checked against ThinkOfLiving project page; "
        "coordinates differ by about 8 metres and both sources identify the 2024, "
        "five-floor, 210-unit Chateau In Town Pinklao-Siriraj project."
    )
    save_array(coord_path, "BANGKOK_VERIFIED_COORDINATES", coord_rows)

    report = {
        "checkedAt": CHECKED,
        "project": {"hipflatId": 3384, "name": "Chateau In Town Pinklao"},
        "coordinateCrosscheck": {
            "source": COORDINATE_CROSSCHECK,
            "latitude": 13.7658407,
            "longitude": 100.4889871,
            "existingProjectPinLatitude": 13.76589958034631,
            "existingProjectPinLongitude": 100.48908002357877,
            "separationMeters": 8,
        },
        "saleListing": sample,
        "rentalBaseline": {
            "monthlyPrice": 11_000,
            "areaSqm": 29.19,
            "minimumRentPerSqm": 377,
            "url": "https://propertyhub.in.th/en/listings/chateau-in-town-pinklao--be6c0a3b---6437186",
        },
        "oneBedroomNetYieldEstimate": {
            "purchasePrice": price,
            "purchaseAreaSqm": area,
            "rentPerSqmPerMonth": 377,
            "estimatedMonthlyRent": round(377 * area),
            "agentMonthsDeducted": 1,
            "commonFeeDeducted": False,
            "netYieldPercent": round(377 * area * 11 / price * 100, 2),
            "formula": "(lowest one-bedroom rent per sqm × sale listing area × 11) ÷ sale listing price × 100",
            "note": "Estimate is for one bedroom only; there is no linked two-bedroom sale listing for the default two-bedroom estimate.",
        },
    }
    report_path = ROOT / "reports" / "chateau-in-town-pinklao-sale-enrichment-2026-10-18.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": 3384, "verifiedSaleListingsAdded": 1,
                      "price": price, "areaSqm": area, "pricePerSqm": price_sqm,
                      "oneBedroomNetYieldPercent": report["oneBedroomNetYieldEstimate"]["netYieldPercent"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
