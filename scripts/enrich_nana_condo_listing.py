"""Add the directly observed Nana Condo sale listing and its embedded map pin."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3127
LISTING_URL = "https://propertyscout.co.th/en/2-br-condo-nana-condo-near-bts-nana-3169405/"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/nana-condo-setbyl"


def load_array(filename: str, symbol: str) -> tuple[str, list[dict]]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not find {symbol} in {filename}")
    return text, json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


def main() -> None:
    manual_file = "bangkok-manual-market-samples.js"
    _, manual = load_array(manual_file, "BANGKOK_MANUAL_MARKET_SAMPLES")
    sale = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": 1_890_000,
        "minimum": 1_890_000,
        "minimumArea": 52,
        "minimumSampleUpdated": "2026-07-06",
        "averageSqm": 36_346,
        "minimumSqm": 36_346,
        "minimumSqmSampleUpdated": "2026-07-06",
        "asOf": "2026-10-18",
        "sourceName": "PropertyScout 單筆房源",
        "source": LISTING_URL,
        "minimumSourceUrl": LISTING_URL,
        "minimumSqmSourceUrl": LISTING_URL,
        "samples": [
            {
                "id": "3169405",
                "price": 1_890_000,
                "area": 52,
                "priceSqm": 36_346,
                "beds": 2,
                "roomType": "2BR",
                "title": "Nana Condo，2 房，52 ㎡，฿1,890,000",
                "url": LISTING_URL,
                "sourceName": "PropertyScout",
                "projectName": "Nana Condo",
                "updated": "2026-07-06",
                "checkedAt": "2026-10-18",
                "matchedBy": "exact_project_name_and_listing_detail",
                "listingStatus": "availability_unconfirmed_update_over_30d",
            }
        ],
    }
    current = next((row for row in manual if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if current is None:
        manual.append({"hipflatId": PROJECT_ID, "name": "Nana Condo", "sale": sale})
    else:
        current["sale"] = sale
    write_array(manual_file, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

    _, guessed = load_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
    matched_location = next((row for row in guessed if int(row.get("hipflatProjectId", 0)) == PROJECT_ID), None)
    if matched_location is None:
        raise ValueError("Expected existing exact PropertyHub project match for Nana Condo")
    matched_location["locationSourceName"] = "PropertyHub 專案位置 + PropertyScout Google Maps 點位交叉核對"
    matched_location["locationSourceUrl"] = LISTING_URL
    matched_location["coordinateCorroborationSourceUrl"] = PROJECT_URL
    write_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS", guessed)

    # Keep the dedicated, directly selected verified-coordinate file free of a
    # duplicate pin; the existing exact PropertyHub match now links to the
    # independent map-pin corroboration source.
    coordinates_file = DIST / "bangkok-verified-coordinates.js"
    coordinate_text = coordinates_file.read_text(encoding="utf-8")
    coordinate_pattern = r',\{"hipflatId":3127,"name":"Nana Condo"[^\]]*?\}'
    coordinate_text, removed = re.subn(coordinate_pattern, "", coordinate_text, count=1)
    if removed:
        coordinates_file.write_text(coordinate_text, encoding="utf-8")

    log_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = rows[0].keys() if rows else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    rows = [row for row in rows if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] == "sale")]
    rows.append({
        "hipflat_id": str(PROJECT_ID),
        "condo": "Nana Condo",
        "checked_at": "2026-10-18",
        "market": "sale",
        "status": "visible_listing_availability_unconfirmed",
        "verification_note": "PropertyScout 個別物件頁核對到 2 房、52 ㎡、฿1,890,000；刊登日 2026-07-06，頁面標示需詢問可售狀態且更新逾 30 日，故保留為待確認樣本，不視為確定在售。頁面地圖嵌入座標為 13.739703,100.553408，專案名稱與 Hipflat 地址相符。",
        "source_1": LISTING_URL,
        "source_2": PROJECT_URL,
        "source_3": "https://www.google.com/maps/search/?api=1&query=13.739703%2C100.553408",
    })
    with log_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "projectId": PROJECT_ID,
        "name": "Nana Condo",
        "checkedAt": "2026-10-18",
        "coordinates": {"lat": 13.739703, "lng": 100.553408, "source": LISTING_URL, "corroboratedBy": PROJECT_URL},
        "saleListing": {"price": 1_890_000, "bedrooms": 2, "areaSqm": 52, "pricePerSqm": 36_346, "url": LISTING_URL, "listed": "2026-07-06", "availability": "unconfirmed; page says availability upon request and was updated over 30 days ago"},
        "yieldBaseline": {"purchasePrice": 1_890_000, "purchaseAreaSqm": 52, "rentRateThbPerSqmMonth": 403, "estimatedMonthlyRent": 20_956, "grossYield12MonthsPct": round(20_956 * 12 / 1_890_000 * 100, 2), "yield11MonthsPct": round(20_956 * 11 / 1_890_000 * 100, 2), "note": "Rent baseline is the existing one-bedroom per-sqm low; a two-bedroom rental listing is not yet verified. Common fee is unknown."},
    }
    (ROOT / "reports" / "nana-condo-enrichment-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"projectId": PROJECT_ID, "saleListing": LISTING_URL, "coordinates": [13.739703, 100.553408]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
