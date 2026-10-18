import json
import re
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKET_FILE = ROOT / "dist" / "bangkok-manual-market-samples.js"
PROJECT_ID = 3050
NAME = "Regent Royal Place 1"
CHECKED = "2026-10-18"
SALE_URL = "https://www.dotproperty.co.th/en/ads/2-bedroom-condo-for-sale-in-regent-royal-place-1-lumphini-bangkok_9a2fa1b9be2c-9ea1-f2d6-4c4a-a036e7e6"
RENT_URL = "https://propertyhub.in.th/en/listings/for-rent-condo-regent-royal-place-1-bts-ratchadamri-lumpini-pathum-wan-bangkok-cx-124891-live-chat-with-us-add-line-connexproperty---5245746"
RENT_RATE = 273
PRICE = 3_000_000
AREA = 84


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


samples = load_array(MARKET_FILE, "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in samples if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if record is None:
    record = {"hipflatId": PROJECT_ID, "name": NAME, "asOf": CHECKED}
    samples.append(record)

sale_sample = {
    "id": "U36809S",
    "price": PRICE,
    "area": AREA,
    "priceSqm": round(PRICE / AREA),
    "beds": 2,
    "roomType": "2BR",
    "title": f"{NAME}，2 房，84 ㎡，18 樓，฿3,000,000",
    "url": SALE_URL,
    "sourceName": "Dot Property",
    "projectName": NAME,
    "updated": "2026-08-09",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_and_individual_listing_detail",
    "listingStatus": "availability_unconfirmed_update_over_30d",
}
record["sale"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing_availability_unconfirmed",
    "average": PRICE,
    "minimum": PRICE,
    "minimumArea": AREA,
    "minimumSampleUpdated": "2026-08-09",
    "averageSqm": round(PRICE / AREA),
    "minimumSqm": round(PRICE / AREA),
    "minimumSqmSampleUpdated": "2026-08-09",
    "asOf": CHECKED,
    "sourceName": "Dot Property 單筆出售掛牌（更新日較久，現況待確認）",
    "source": "https://www.dotproperty.co.th/en/condos-for-sale/regent-royal-place-1_p2001",
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "byBedroom": {
        "2": {
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
write_array(MARKET_FILE, "BANGKOK_MANUAL_MARKET_SAMPLES", samples)

estimated_monthly_rent = RENT_RATE * AREA
annual_rent_after_agent_month = estimated_monthly_rent * 11
net_yield_before_unknown_common_fee = round(annual_rent_after_agent_month / PRICE * 100, 2)
evidence = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "sale": {
        "source": "Dot Property",
        "url": SALE_URL,
        "listingId": "U36809S",
        "bedrooms": 2,
        "areaSqm": AREA,
        "priceThb": PRICE,
        "pricePerSqmThb": round(PRICE / AREA),
        "floor": 18,
        "updatedAt": "2026-08-09",
        "availability": "unconfirmed; listing page is accessible, but its update date is over 30 days old",
    },
    "rentBaseline": {
        "source": "PropertyHub two-bedroom project listing snapshot",
        "url": RENT_URL,
        "rentPerSqmPerMonthThb": RENT_RATE,
        "asOf": "2026-10-17",
        "calculatedMonthlyRentThb": estimated_monthly_rent,
    },
    "yieldEstimate": {
        "purchasePriceThb": PRICE,
        "purchaseAreaSqm": AREA,
        "estimatedAnnualRentAfterOneAgentMonthThb": annual_rent_after_agent_month,
        "netAnnualYieldBeforeUnknownCommonFeePercent": net_yield_before_unknown_common_fee,
        "formula": "(273 THB/sqm/month × 84 sqm × 11 months) ÷ 3,000,000 THB × 100",
        "commonFee": "not verified; not deducted",
        "otherExcludedCosts": ["tax", "maintenance", "vacancy", "purchase transaction costs"],
    },
    "decision": "Included as a direct two-bedroom listing sample with an explicit availability warning; do not treat its current availability as confirmed.",
}
(ROOT / "reports" / "regent-royal-place-1-sale-enrichment-2026-10-18.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

availability_log = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_log.open("r", newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames or []
    rows = list(reader)
if not any(row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "sale" for row in rows):
    rows.append({
        "hipflat_id": str(PROJECT_ID),
        "condo": NAME,
        "checked_at": CHECKED,
        "market": "sale",
        "status": "availability_unconfirmed_update_over_30d",
        "verification_note": "Dot Property direct detail identifies Regent Royal Place 1, 2 bedrooms, 84 sqm, THB 3,000,000, listing U36809S. Page was accessible when checked, but says Updated At Aug 9, 2026; current availability cannot be confirmed.",
        "source_1": SALE_URL,
        "source_2": "https://www.dotproperty.co.th/en/condos-for-sale/regent-royal-place-1_p2001",
        "source_3": "https://propertyhub.in.th/en/projects/the-royal-place-1",
    })
    with availability_log.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

print(json.dumps({"project": NAME, "salePriceThb": PRICE, "areaSqm": AREA, "saleThbPerSqm": round(PRICE / AREA), "estimatedNetYieldPercent": net_yield_before_unknown_common_fee, "availability": sale_sample["listingStatus"]}, ensure_ascii=False))
