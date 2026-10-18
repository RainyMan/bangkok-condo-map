import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3149
NAME = "The Grand Regent"
CHECKED = "2026-10-18"
SALE_URL = "https://www.accomasia.co.th/property/thegrandregent-for-rent-for-sale-ploenchit-bts-ratchadamri-bangkok-aa23254"
RENT_URL = "https://propertyhub.in.th/en/listings/for-rent-the-grand-regent-studio-bts-ratchadamri-fully-furnished-gtn-1008---6470781"
PRICE = 3_200_000
AREA = 80
BEDROOMS = 1


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
samples = load_array(market_file, "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in samples if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if record is None:
    record = {"hipflatId": PROJECT_ID, "name": NAME, "asOf": CHECKED}
    samples.append(record)

sale_sample = {
    "id": "AA23254",
    "price": PRICE,
    "area": AREA,
    "priceSqm": round(PRICE / AREA),
    "beds": BEDROOMS,
    "roomType": "1BR",
    "title": f"{NAME}，1 房，80 ㎡，฿{PRICE:,}（同物件另列出租）",
    "url": SALE_URL,
    "sourceName": "Accomasia",
    "projectName": NAME,
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_property_code_and_individual_listing_detail",
    "listingStatus": "availability_unconfirmed_source_requests_confirmation",
}
record["sale"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing_availability_unconfirmed",
    "average": PRICE,
    "minimum": PRICE,
    "minimumArea": AREA,
    "averageSqm": round(PRICE / AREA),
    "minimumSqm": round(PRICE / AREA),
    "asOf": CHECKED,
    "sourceName": "Accomasia 單筆出售掛牌（現況待確認）",
    "source": "https://www.accomasia.co.th/project/thegrandregent-100380",
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "byBedroom": {
        str(BEDROOMS): {
            "count": 1,
            "minimum": PRICE,
            "area": AREA,
            "priceSqm": round(PRICE / AREA),
            "minimumSqm": round(PRICE / AREA),
            "sourceUrl": SALE_URL,
            "minimumSqmSourceUrl": SALE_URL,
        }
    },
    "samples": [sale_sample],
}
write_array(market_file, "BANGKOK_MANUAL_MARKET_SAMPLES", samples)

availability_file = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_file.open("r", newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames or []
    rows = list(reader)
sale_log = {
    "hipflat_id": str(PROJECT_ID),
    "condo": NAME,
    "checked_at": CHECKED,
    "market": "sale",
    "status": "availability_unconfirmed_source_requests_confirmation",
    "verification_note": "Accomasia direct detail AA23254: The Grand Regent, 1 bedroom, 80 sqm, sale THB 3,200,000 (THB 40,000/sqm). The same property code also displays rent THB 35,000/month. Listing page says availability should be confirmed with agent; not counted as confirmed active inventory.",
    "source_1": SALE_URL,
    "source_2": "https://www.accomasia.co.th/project/thegrandregent-100380",
    "source_3": RENT_URL,
}
rows = [row for row in rows if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "sale")]
rows.append(sale_log)
with availability_file.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

evidence = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "sale": {
        "source": "Accomasia",
        "url": SALE_URL,
        "listingId": "AA23254",
        "bedrooms": BEDROOMS,
        "areaSqm": AREA,
        "priceThb": PRICE,
        "pricePerSqmThb": round(PRICE / AREA),
        "availability": "page accessible on check date; source asks the user to confirm because units sell or rent quickly",
    },
    "sameListingRent": {
        "source": "Accomasia",
        "url": SALE_URL,
        "monthlyRentThb": 35_000,
        "bedrooms": BEDROOMS,
        "areaSqm": AREA,
        "note": "Same property code AA23254 is also offered for rent; excluded from PropertyHub rent-market aggregates.",
    },
    "propertyHubRentBaseline": {
        "source": "PropertyHub",
        "url": RENT_URL,
        "monthlyRentThb": 15_000,
        "areaSqm": 42,
        "roomType": "Studio (also labeled 1 bed on the listing page)",
        "rentPerSqmPerMonthThb": 357,
        "availability": "listing says available 2026-11-11; keep as a future-dated rental sample",
    },
    "yieldEstimate": {
        "formula": "(357 THB/sqm/month × 80 sqm × 11 months) / 3,200,000 THB × 100",
        "netAnnualYieldBeforeUnknownCommonFeePercent": round((357 * AREA * 11) / PRICE * 100, 2),
        "commonFee": "not verified; not deducted",
        "otherExcludedCosts": ["tax", "maintenance", "vacancy", "purchase transaction costs"],
        "note": "The calculator uses the lowest 1-room-type rent rate in the existing market dataset rather than the same listing's 35,000 THB/month advertised rent.",
    },
}
(ROOT / "reports" / "the-grand-regent-sale-enrichment-2026-10-18.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(json.dumps({
    "project": NAME,
    "salePriceThb": PRICE,
    "areaSqm": AREA,
    "saleThbPerSqm": round(PRICE / AREA),
    "lowRentThbPerSqmPerMonth": 357,
    "netYieldBeforeUnknownCommonFeePercent": round((357 * AREA * 11) / PRICE * 100, 2),
    "availability": sale_sample["listingStatus"],
}, ensure_ascii=False))
