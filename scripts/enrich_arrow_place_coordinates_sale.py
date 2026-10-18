"""Verify Arrow Place's point and add its current Hipflat sale listing."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3182
PROJECT = "Arrow Place"
AS_OF = "2026-10-18"
LAT, LNG = 13.91247312, 100.582138
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/arrow-place-xiyzra"
HIPFLAT_LISTING = "https://www.hipflat.co.th/en/ads/271c0tth8ae4neaut813tc1t3u0h14u9"
COORDINATE_SOURCE = "https://thinkofliving.com/project/%E0%B9%81%E0%B8%AD%E0%B8%A3%E0%B9%8C%E0%B9%82%E0%B8%A3-%E0%B9%80%E0%B8%9E%E0%B8%A5%E0%B8%AA-10028/"


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Cannot parse {symbol} from {path}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


def main() -> None:
    coordinates = [row for row in load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
                   if int(row.get("hipflatId", -1)) != PROJECT_ID]
    coordinates.append({
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "sourceName": "ThinkOfLiving 專案座標",
        "sourceUrl": COORDINATE_SOURCE,
        "verificationSourceUrl": HIPFLAT_PROJECT,
        "projectSourceUrl": HIPFLAT_PROJECT,
        "verificationMethod": (
            "ThinkOfLiving Arrow Place project profile publishes coordinates 100.582138, 13.91247312 "
            "and identifies the location as Thanon Pracha Uthit, Don Mueang. Hipflat identifies "
            "Arrow Place at 34/430 Pracha Uthit 10, Don Mueang; project name, road and district match."
        ),
        "asOf": AS_OF,
    })
    coordinates.sort(key=lambda row: int(row.get("hipflatId", 0)))
    save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinates)

    price, area = 1_000_000, 43
    price_sqm = round(price / area)
    sale_url = HIPFLAT_LISTING
    sample = {
        "id": "U5735529", "price": price, "area": area, "priceSqm": price_sqm,
        "beds": 0, "roomType": "STUDIO",
        "title": "Arrow Place studio · 43 sqm · THB 1,000,000",
        "url": sale_url, "sourceName": "Hipflat", "projectName": PROJECT,
        "updated": AS_OF, "checkedAt": AS_OF,
        "matchedBy": "Hipflat exact project page links the unit; unit page names Arrow Place",
        "listingStatus": "active_as_listed",
    }
    sale = {
        "count": 1, "observedCount": 1,
        "countKind": "manual_verified_listing_availability_unconfirmed",
        "average": price, "minimum": price, "minimumArea": area,
        "minimumSampleUpdated": AS_OF,
        "averageSqm": price_sqm, "minimumSqm": price_sqm,
        "minimumSqmSampleUpdated": AS_OF, "asOf": AS_OF,
        "sourceName": "Hipflat 直接出售掛牌",
        "source": HIPFLAT_PROJECT,
        "minimumSourceUrl": sale_url, "minimumSqmSourceUrl": sale_url,
        "samples": [sample],
    }
    manual = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    record = next((row for row in manual if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": PROJECT}
        manual.append(record)
    record.update({"asOf": AS_OF, "replaceSale": True, "sale": sale})
    manual.sort(key=lambda row: int(row["hipflatId"]))
    save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "coordinates": {"lat": LAT, "lng": LNG, "sourceUrl": COORDINATE_SOURCE,
                        "crossCheckUrl": HIPFLAT_PROJECT, "verified": True},
        "sale": sample,
        "rent": {"status": "No rental listings shown on the checked Hipflat project page; no rent or yield imputed.",
                 "sourceUrl": HIPFLAT_PROJECT},
    }
    (REPORTS / "arrow-place-verification-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [LAT, LNG], "salePrice": price,
                      "areaSqm": area, "pricePerSqm": price_sqm, "rent": "not found"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
