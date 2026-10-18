"""Add source-verified location and current sale/rent listings for The Unique 19."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3333
PROJECT = "The Unique Ratchada 19"
CHECKED = "2026-10-19"
GOOGLE_MAPS = "https://www.google.com/maps/place/The+Unique+Ratchada+19/@13.8019155,100.5722579,17z/"
HIPFLAT = "https://www.hipflat.co.th/en/projects/the-unique-ratchada-19-efxana"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/projects/the-unique-19"
SALE_TWO_BED = "https://propertyhub.in.th/listings/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-the-unique-19-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-mrt-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2%E0%B8%A0%E0%B8%B4%E0%B9%80%E0%B8%A9%E0%B8%81-300-%E0%B9%80%E0%B8%A1%E0%B8%95%E0%B8%A3-id-2862346---6402229"
SALE_ONE_BED = "https://www.livinginsider.com/en/detail/condo-for-sale-condo-the-unique-ratchada-19-1bedroom-3237231"
RENT_TWO_BED = "https://propertyhub.in.th/listings/%E0%B8%A7%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%AD%E0%B8%A2%E0%B8%B9%E0%B9%88-the-unique-19-2%E0%B8%99%E0%B8%AD%E0%B8%99-63%E0%B8%95%E0%B8%A3-%E0%B8%A1-line-id-pfagent---6280324"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.S,
    )
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    sale_samples = [
        {
            "id": "3237231",
            "price": 1_800_000,
            "area": 26,
            "priceSqm": round(1_800_000 / 26),
            "beds": 1,
            "roomType": "1BR",
            "title": "The Unique Ratchada 19，1 房，26 ㎡，฿1,800,000",
            "url": SALE_ONE_BED,
            "sourceName": "LivingInsider",
            "projectName": PROJECT,
            "checkedAt": CHECKED,
            "updated": "2026-10-12",
            "matchedBy": "exact_project_name_and_listing_detail",
            "listingStatus": "active_as_listed",
            "verificationNote": "Listing page identifies this exact project, 1 bedroom, 26 sqm, THB 1,800,000; page reported updated about one week before the check.",
        },
        {
            "id": "6402229",
            "price": 4_650_000,
            "area": 63,
            "priceSqm": round(4_650_000 / 63),
            "beds": 2,
            "roomType": "2BR",
            "title": "The Unique 19，2 房，63 ㎡，5 樓，฿4,650,000",
            "url": SALE_TWO_BED,
            "sourceName": "PropertyHub",
            "projectName": PROJECT,
            "checkedAt": CHECKED,
            "updated": CHECKED,
            "matchedBy": "exact_propertyhub_project_and_direct_listing_page",
            "listingStatus": "active_as_listed",
            "verificationNote": "Direct listing page confirmed the exact project, 2 bedrooms, 63 sqm, THB 4,650,000, floor 5; page showed an update on 2026-10-19.",
        },
    ]
    rent_samples = [
        {
            "id": "6280324",
            "price": 22_000,
            "area": 63,
            "priceSqm": round(22_000 / 63),
            "beds": 2,
            "roomType": "2BR",
            "title": "The Unique 19，2 房，63 ㎡，2 樓，฿22,000/月",
            "url": RENT_TWO_BED,
            "sourceName": "PropertyHub",
            "projectName": PROJECT,
            "checkedAt": CHECKED,
            "updated": "2026-09-22",
            "matchedBy": "exact_propertyhub_project_and_direct_listing_page",
            "listingStatus": "active_as_listed",
            "verificationNote": "Direct listing page identifies The Unique 19, 2 bedrooms, 63 sqm, THB 22,000/month, floor 2; the project page listed it as ready to move in and updated 2026-09-22.",
        }
    ]

    sale = {
        "count": len(sale_samples),
        "observedCount": len(sale_samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in sale_samples) / len(sale_samples)),
        "minimum": 1_800_000,
        "minimumArea": 26,
        "minimumSampleUpdated": "2026-10-12",
        "averageSqm": round(sum(row["priceSqm"] for row in sale_samples) / len(sale_samples)),
        "minimumSqm": round(1_800_000 / 26),
        "minimumSqmSampleUpdated": "2026-10-12",
        "asOf": CHECKED,
        "sourceName": "LivingInsider + PropertyHub 個別掛牌",
        "source": PROPERTYHUB_PROJECT,
        "minimumSourceUrl": SALE_ONE_BED,
        "minimumSqmSourceUrl": SALE_ONE_BED,
        "byBedroom": {
            "1": {"beds": 1, "count": 1, "minimum": 1_800_000, "area": 26, "minimumArea": 26, "minimumSqm": round(1_800_000 / 26), "minimumSourceUrl": SALE_ONE_BED, "sourceUrl": SALE_ONE_BED},
            "2": {"beds": 2, "count": 1, "minimum": 4_650_000, "area": 63, "minimumArea": 63, "minimumSqm": round(4_650_000 / 63), "minimumSourceUrl": SALE_TWO_BED, "sourceUrl": SALE_TWO_BED},
        },
        "samples": sale_samples,
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": 22_000,
        "minimum": 22_000,
        "minimumArea": 63,
        "minimumSampleUpdated": "2026-09-22",
        "averageSqm": round(22_000 / 63),
        "minimumSqm": round(22_000 / 63),
        "minimumSqmSampleUpdated": "2026-09-22",
        "asOf": CHECKED,
        "sourceName": "PropertyHub 個別掛牌",
        "source": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-the-unique-19",
        "minimumSourceUrl": RENT_TWO_BED,
        "minimumSqmSourceUrl": RENT_TWO_BED,
        "byBedroom": {
            "2": {"beds": 2, "count": 1, "minimum": 22_000, "area": 63, "minimumSqm": round(22_000 / 63), "minimumSourceUrl": RENT_TWO_BED, "minimumSqmSourceUrl": RENT_TWO_BED, "sourceUrl": RENT_TWO_BED},
        },
        "samples": rent_samples,
    }

    market_path = DIST / "bangkok-manual-market-samples.js"
    markets = read_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    record = next((row for row in markets if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": PROJECT}
        markets.append(record)
    record.update({"completedYear": 2015, "sale": sale, "rent": rent})
    markets.sort(key=lambda row: int(row["hipflatId"]))
    write_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

    coords_path = DIST / "bangkok-verified-coordinates.js"
    coordinates = read_array(coords_path, "BANGKOK_VERIFIED_COORDINATES")
    coordinate = next((row for row in coordinates if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if coordinate is None:
        coordinate = {"hipflatId": PROJECT_ID, "name": PROJECT}
        coordinates.append(coordinate)
    coordinate.update({
        "lat": 13.8019155,
        "lng": 100.5722579,
        "locationVerified": True,
        "sourceName": "Google Maps exact project place",
        "sourceUrl": GOOGLE_MAPS,
        "locationSourceUrl": GOOGLE_MAPS,
        "verificationSourceUrl": HIPFLAT,
        "verificationMethod": "Google Maps place name and address matched Hipflat's exact Lat Phrao 26 Yaek 2-1 project address; PropertyHub listing pages confirm the same project.",
        "verifiedAt": CHECKED,
    })
    coordinates.sort(key=lambda row: int(row["hipflatId"]))
    write_array(coords_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

    report = {
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "checkedAt": CHECKED,
        "coordinate": {"lat": 13.8019155, "lng": 100.5722579, "source": GOOGLE_MAPS, "crossCheck": HIPFLAT},
        "completedYear": {"year": 2015, "source": PROPERTYHUB_PROJECT},
        "saleSamples": sale_samples,
        "rentSamples": rent_samples,
        "twoBedroomYieldInputs": {"purchasePrice": 4_650_000, "purchaseAreaSqm": 63, "rentMonthly": 22_000, "rentPerSqmMonthly": round(22_000 / 63, 2), "grossYieldPercent": round(22_000 * 12 / 4_650_000 * 100, 2), "afterOneAgentMonthPercent": round(22_000 * 11 / 4_650_000 * 100, 2), "commonFee": "Not found in checked project/listing pages; excluded until a project-specific published rate is verified."},
        "sourceNotes": [
            "PropertyHub direct sale listing 6402229 was opened and showed the 2-bedroom, 63 sqm, THB 4,650,000 unit updated 2026-10-19.",
            "PropertyHub direct rental listing 6280324 was opened and showed the 2-bedroom, 63 sqm, THB 22,000/month unit; the project index showed it updated 2026-09-22.",
            "LivingInsider listing CX-174822 identifies the exact project and a 1-bedroom, 26 sqm, THB 1,800,000 sale, reported updated about one week before 2026-10-19.",
            "No project-specific common-fee rate was verified; the estimate therefore does not deduct common fees.",
        ],
    }
    (ROOT / "reports" / "the-unique-ratchada-19-market-verification-2026-10-19.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"hipflatId": PROJECT_ID, "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "coordinates": [13.8019155, 100.5722579]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
