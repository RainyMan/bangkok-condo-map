"""Attach exact, source-linked location and listing records to Hipflat project 3348."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3348
NAME = "The Tree Ladprao-Wanghin"
CHECKED = "2026-10-18"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/the-tree-ladprao-wanghin-48h3t19c1tenunuttn20hn7hu0ch9l9h"
GOOGLE_MAPS_URL = "https://maps.app.goo.gl/Ukqb7WU2FgiJ3EG39?g_st=com.google.maps.preview.copy"
SALE_URL = "https://propertyhub.in.th/en/listings/a033228-the-tree-ladprao-ladprao-wang-hin--b2cc0996---6003543"
RENT_URL = "https://propertyhub.in.th/listings/r3399-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-the-tree-ladprao-wanghin---5035047"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-the-tree-condo-ladprao"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-the-tree-condo-ladprao"

SALE_PRICE = 1_350_000
SALE_AREA = 28.0
SALE_RATE = round(SALE_PRICE / SALE_AREA)
RENT_PRICE = 13_500
RENT_AREA = 58.22
RENT_RATE = round(RENT_PRICE / RENT_AREA)
ESTIMATED_MONTHLY_RENT = round(RENT_RATE * SALE_AREA)
ESTIMATED_NET_YIELD = round(ESTIMATED_MONTHLY_RENT * 11 / SALE_PRICE * 100, 2)


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Could not parse {symbol} from {path}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    sample_status = "availability_unconfirmed_date_unknown"
    sale_sample = {
        "id": "6003543",
        "price": SALE_PRICE,
        "area": SALE_AREA,
        "priceSqm": SALE_RATE,
        "beds": 1,
        "roomType": "ONE_BED_ROOM",
        "title": "A033228 The Tree Ladprao (Ladprao - Wang Hin)",
        "url": SALE_URL,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "exact_project_alias_wang_hin_and_propertyhub_listing_id_6003543; same_propertyhub_project_group_as_google_maps_verified_rent_listing",
        "listingStatus": sample_status,
    }
    rent_sample = {
        "id": "5035047",
        "price": RENT_PRICE,
        "area": RENT_AREA,
        "priceSqm": round(RENT_PRICE / RENT_AREA),
        "beds": 1,
        "roomType": "ONE_BED_ROOM",
        "title": "#R3399 For rent The Tree Ladprao-Wanghin",
        "url": RENT_URL,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "exact_listing_project_alias_and_google_maps_pin_at_129_2_lat_phrao_wang_hin_12",
        "listingStatus": sample_status,
    }

    sale = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing_availability_unconfirmed",
        "average": SALE_PRICE,
        "minimum": SALE_PRICE,
        "minimumArea": SALE_AREA,
        "averageSqm": SALE_RATE,
        "minimumSqm": SALE_RATE,
        "asOf": CHECKED,
        "sourceName": "PropertyHub 直接出售掛牌（A033228）",
        "source": SALE_PROJECT_URL,
        "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": SALE_PRICE,
                "area": SALE_AREA,
                "minimumSqm": SALE_RATE,
                "sourceUrl": SALE_URL,
                "minimumSqmSourceUrl": SALE_URL,
            }
        },
        "samples": [sale_sample],
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing_availability_unconfirmed",
        "average": RENT_PRICE,
        "minimum": RENT_PRICE,
        "minimumArea": RENT_AREA,
        "averageSqm": RENT_RATE,
        "minimumSqm": RENT_RATE,
        "asOf": CHECKED,
        "sourceName": "PropertyHub 直接出租掛牌（R3399）",
        "source": RENT_PROJECT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": RENT_PRICE,
                "area": RENT_AREA,
                "minimumSqm": RENT_RATE,
                "sourceUrl": RENT_URL,
                "minimumSqmSourceUrl": RENT_URL,
            }
        },
        "samples": [rent_sample],
    }

    markets_path = DIST / "bangkok-manual-market-samples.js"
    markets = read_array(markets_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    record = next((row for row in markets if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": NAME}
        markets.append(record)
    record.update({"asOf": CHECKED, "replaceSale": True, "sale": sale, "rent": rent})
    markets.sort(key=lambda row: int(row["hipflatId"]))
    write_array(markets_path, "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

    # The listing's Google Maps short URL resolves to the named business at
    # RH3R+Q7R, Lat Phrao Wang Hin 12 Alley. Decoding full code 7P52RH3R+Q7R
    # gives this center point (about 1.5 m code-cell precision).
    coordinates_path = DIST / "bangkok-verified-coordinates.js"
    coordinates = read_array(coordinates_path, "BANGKOK_VERIFIED_COORDINATES")
    coordinate = {
        "hipflatId": PROJECT_ID,
        "name": NAME,
        "lat": 13.8044875,
        "lng": 100.590640625,
        "locationVerified": True,
        "sourceName": "PropertyHub 出租物件所附 Google Maps 專案點位（Plus Code）",
        "sourceUrl": GOOGLE_MAPS_URL,
        "verificationSourceUrl": HIPFLAT_URL,
        "corroborationSourceUrl": RENT_URL,
        "verificationMethod": "google_maps_place_name_and_plus_code_at_lat_phrao_wang_hin_12_crosschecked_with_exact_hipflat_project_street_address",
        "asOf": CHECKED,
    }
    old_coordinate = next((row for row in coordinates if int(row["hipflatId"]) == PROJECT_ID), None)
    if old_coordinate:
        old_coordinate.update(coordinate)
    else:
        coordinates.append(coordinate)
    coordinates.sort(key=lambda row: int(row["hipflatId"]))
    write_array(coordinates_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

    availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with availability_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        availability = [
            row for row in reader
            if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") in {"sale", "rent"})
        ]
    availability.extend([
        {
            "hipflat_id": str(PROJECT_ID), "condo": NAME, "checked_at": CHECKED, "market": "sale",
            "status": sample_status,
            "verification_note": "PropertyHub direct listing #6003543 lists 1 bedroom, 28 sqm and THB 1,350,000. The current project listing index showed it refreshed 2026-10-17; direct detail page does not expose an update timestamp, so availability remains unconfirmed.",
            "source_1": SALE_URL, "source_2": SALE_PROJECT_URL, "source_3": HIPFLAT_URL,
        },
        {
            "hipflat_id": str(PROJECT_ID), "condo": NAME, "checked_at": CHECKED, "market": "rent",
            "status": sample_status,
            "verification_note": "PropertyHub direct listing #5035047 lists 1 bedroom, 58.22 sqm and THB 13,500/month and includes a Google Maps place for The Tree Ladprao-Wanghin at Lat Phrao Wang Hin 12. The project index showed it refreshed 2026-10-17; direct detail page does not expose an update timestamp, so availability remains unconfirmed.",
            "source_1": RENT_URL, "source_2": GOOGLE_MAPS_URL, "source_3": HIPFLAT_URL,
        },
    ])
    with availability_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(availability)

    report = {
        "hipflatId": PROJECT_ID,
        "project": NAME,
        "checkedAt": CHECKED,
        "hipflatProjectUrl": HIPFLAT_URL,
        "coordinate": coordinate,
        "sale": {"price": SALE_PRICE, "areaSqm": SALE_AREA, "priceSqm": SALE_RATE, "bedrooms": 1, "url": SALE_URL},
        "rent": {"monthlyRent": RENT_PRICE, "areaSqm": RENT_AREA, "rentSqm": RENT_RATE, "bedrooms": 1, "url": RENT_URL},
        "yieldEstimate": {
            "bedrooms": 1,
            "salePrice": SALE_PRICE,
            "saleAreaSqm": SALE_AREA,
            "rentPerSqm": RENT_RATE,
            "estimatedMonthlyRentOnSaleArea": ESTIMATED_MONTHLY_RENT,
            "annualRentWithOneAgentMonthDeducted": ESTIMATED_MONTHLY_RENT * 11,
            "yieldBeforeCommonFee": ESTIMATED_NET_YIELD,
            "managementFee": "unverified; not deducted",
        },
        "sourceIdentityNote": "The PropertyHub project page's long description mentions a conflicting Lat Phrao 15 address, but its project inventory (334 units, 2 buildings), Lat Phrao Wang Hin nearby-area records, the R3399 direct listing's exact Google Maps point, and the Hipflat 129/2 Lat Phrao Wang Hin 12 project address align with this Wanghin project. Broader PropertyHub project aggregates are excluded; only the two direct listings are used.",
    }
    (ROOT / "reports" / "the-tree-ladprao-wanghin-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": coordinate, "sale": sale_sample, "rent": rent_sample, "yieldEstimate": report["yieldEstimate"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
