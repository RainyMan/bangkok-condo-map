import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3099
NAME = "Polo Park"
CHECKED = "2026-10-18"
SALE_URL = "https://www.thaihometown.com/condo/4682807"
RENT_URL = "https://propertyhub.in.th/en/listings/polo-park-condominium-luxurious-2-bed-condo-in-ratchadamri-br9559cd---5602848"
PRICE = 38_000_000
AREA = 241
BEDROOMS = 2
UPDATED = "2024-10-28"
PRICE_SQM = round(PRICE / AREA)
RENT_RATE = 360  # PropertyHub: 90,000 THB / 250 sqm, refreshed 2026-10-15.
ANNUAL_RENT_AFTER_AGENT = round(RENT_RATE * AREA * 11)
ESTIMATED_YIELD = round(ANNUAL_RENT_AFTER_AGENT / PRICE * 100, 2)


def load_array(path: Path, variable: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}\s*=\s*(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Could not parse window.{variable} from {path}")
    return json.loads(match.group(1))


def write_array(path: Path, variable: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{variable} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


market_file = ROOT / "dist" / "bangkok-manual-market-samples.js"
rows = load_array(market_file, "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if record is None:
    record = {"hipflatId": PROJECT_ID, "name": NAME}
    rows.append(record)

sample = {
    "id": "P17CR2006073SALE4",
    "price": PRICE,
    "area": AREA,
    "priceSqm": PRICE_SQM,
    "beds": BEDROOMS,
    "roomType": "2BR",
    "title": f"{NAME}，2 房，241 ㎡，฿{PRICE:,}；刊登於 {UPDATED}",
    "url": SALE_URL,
    "sourceName": "ThaiHometown（Incube Realty）",
    "projectName": NAME,
    "checkedAt": CHECKED,
    "updated": UPDATED,
    "matchedBy": "exact_project_name_listing_code_room_count_area_and_direct_detail",
    "listingStatus": "availability_unconfirmed_stale_over_year",
}
record.update({
    "asOf": CHECKED,
    "replaceSale": True,
    "sale": {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing_availability_unconfirmed",
        "average": PRICE,
        "minimum": PRICE,
        "minimumArea": AREA,
        "minimumSampleUpdated": UPDATED,
        "averageSqm": PRICE_SQM,
        "minimumSqm": PRICE_SQM,
        "minimumSqmSampleUpdated": UPDATED,
        "asOf": CHECKED,
        "sourceName": "ThaiHometown 兩房直接掛牌（2024 年刊登，現況待確認）",
        "source": "https://www.thaihometown.com/condo/4682807",
        "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL,
        "byBedroom": {
            "2": {
                "count": 1,
                "minimum": PRICE,
                "area": AREA,
                "priceSqm": PRICE_SQM,
                "minimumSqm": PRICE_SQM,
                "sourceUrl": SALE_URL,
                "minimumSqmSourceUrl": SALE_URL,
            }
        },
        "samples": [sample],
    },
})
write_array(market_file, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

availability_file = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_file.open("r", newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames or []
    availability_rows = list(reader)
availability_rows = [row for row in availability_rows if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "sale")]
availability_rows.append({
    "hipflat_id": str(PROJECT_ID),
    "condo": NAME,
    "checked_at": CHECKED,
    "market": "sale",
    "status": "availability_unconfirmed_stale_over_year",
    "verification_note": "ThaiHometown direct detail #4682807 / Incube reference P17CR2006073 identifies Polo Park, 2 bedrooms, 241 sqm, THB 38,000,000; page says posted 2024-10-28. Exact listing data is retained as a historical benchmark only; current availability and price are not confirmed.",
    "source_1": SALE_URL,
    "source_2": "https://propertyhub.in.th/en/condo-for-sale/project-polo-park",
    "source_3": RENT_URL,
})
with availability_file.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(availability_rows)

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "sale": {
        "source": "ThaiHometown / Incube Realty",
        "url": SALE_URL,
        "reference": "P17CR2006073 / page #4682807",
        "listedAt": UPDATED,
        "bedrooms": BEDROOMS,
        "areaSqm": AREA,
        "priceThb": PRICE,
        "pricePerSqmThb": PRICE_SQM,
        "availability": "historical listing; no current availability or price confirmation",
        "decision": "Included with an explicit over-one-year stale label as a linked historical sample. It is not represented as current inventory.",
    },
    "rentBaseline": {
        "source": "PropertyHub individual listing",
        "url": RENT_URL,
        "bedrooms": 2,
        "monthlyRentThb": 90_000,
        "areaSqm": 250,
        "rentPerSqmPerMonthThb": RENT_RATE,
        "updatedAt": "2026-10-15",
    },
    "yieldEstimate": {
        "purchasePriceThb": PRICE,
        "purchaseAreaSqm": AREA,
        "estimatedMonthlyRentThb": round(RENT_RATE * AREA),
        "estimatedAnnualRentAfterOneAgentMonthThb": ANNUAL_RENT_AFTER_AGENT,
        "yieldPercentBeforeUnknownCommonFee": ESTIMATED_YIELD,
        "formula": f"({RENT_RATE} THB/sqm/month × {AREA} sqm × 11 months) ÷ {PRICE} THB × 100",
        "commonFee": "not independently verified; not deducted",
        "caveat": "Yield is indicative only because the sale baseline is from a 2024 listing and current availability and sale price are unconfirmed.",
    },
}
(ROOT / "reports" / "polo-park-sale-enrichment-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"project": NAME, "salePrice": PRICE, "areaSqm": AREA, "salePerSqm": PRICE_SQM, "listingDate": UPDATED, "yieldBeforeUnknownFee": ESTIMATED_YIELD, "availability": sample["listingStatus"]}, ensure_ascii=False))
