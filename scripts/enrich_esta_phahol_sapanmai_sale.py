import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3178
NAME = "Esta Phahol - Sapanmai"
CHECKED = "2026-10-18"
SALE_URL = "https://www.livinginsider.com/detail/condo-for-sale-condo-esta-phahol-sapanmai-2bedroom-2152509"
RENT_URL = "https://propertyhub.in.th/en/listings/esta-phahol-sapanmai-condo-for-rent--95f20837---4199933"
SALE_PRICE = 2_770_000
SALE_AREA = 43
RENT_PRICE = 15_000
RENT_AREA = 50
FEE_RATE = 45


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
    "id": "LI-2152509",
    "price": SALE_PRICE,
    "area": SALE_AREA,
    "priceSqm": round(SALE_PRICE / SALE_AREA),
    "beds": 2,
    "roomType": "2BR",
    "title": f"{NAME}，2 房，43 ㎡，7 樓，฿{SALE_PRICE:,}",
    "url": SALE_URL,
    "sourceName": "LivingInsider",
    "projectName": NAME,
    "updated": "2026-09-26",
    "created": "2024-05-05",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_and_individual_listing_detail",
    "listingStatus": "listed_recently_bumped_under_30d",
}
record["sale"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": SALE_PRICE,
    "minimum": SALE_PRICE,
    "minimumArea": SALE_AREA,
    "minimumSampleUpdated": "2026-09-26",
    "averageSqm": round(SALE_PRICE / SALE_AREA),
    "minimumSqm": round(SALE_PRICE / SALE_AREA),
    "minimumSqmSampleUpdated": "2026-09-26",
    "asOf": CHECKED,
    "sourceName": "LivingInsider 個別出售掛牌（最近更新 2026-09-26）",
    "source": "https://www.livinginsider.com/project/condo-esta-phahol-sapanmai-condo-buysell",
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": SALE_PRICE,
            "area": SALE_AREA,
            "priceSqm": round(SALE_PRICE / SALE_AREA),
            "minimumSqm": round(SALE_PRICE / SALE_AREA),
            "sourceUrl": SALE_URL,
            "minimumSqmSourceUrl": SALE_URL,
        }
    },
    "samples": [sale_sample],
}
write_array(market_file, "BANGKOK_MANUAL_MARKET_SAMPLES", samples)

rent_rate = RENT_PRICE / RENT_AREA
monthly_estimated_rent = rent_rate * SALE_AREA
annual_rent_after_agent_month = monthly_estimated_rent * 11
annual_indicative_fee = FEE_RATE * SALE_AREA * 12
net_yield_after_agent_and_indicative_fee = round(
    (annual_rent_after_agent_month - annual_indicative_fee) / SALE_PRICE * 100, 2
)
evidence = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "coordinates": {
        "lat": 13.889647427848436,
        "lng": 100.60651517544169,
        "source": "https://propertyhub.in.th/en/projects/esta-phahol-sapanmai",
        "status": "coordinate already present and marked verified in the catalogue overlay",
    },
    "sale": {
        "source": "LivingInsider",
        "url": SALE_URL,
        "listingId": "2152509",
        "bedrooms": 2,
        "areaSqm": SALE_AREA,
        "priceThb": SALE_PRICE,
        "pricePerSqmThb": round(SALE_PRICE / SALE_AREA),
        "floor": 7,
        "createdAt": "2024-05-05",
        "lastBumpedAt": "2026-09-26",
        "availability": "listing page accessible and bumped within 30 days; listing availability remains unconfirmed",
        "areaConflictDecision": "A cheaper separate two-bedroom ad lists 2,500,000 THB but its structured area (38 sqm) conflicts with the description (34 sqm); excluded from the ROI baseline pending area verification.",
    },
    "rent": {
        "source": "PropertyHub",
        "url": RENT_URL,
        "listingId": "4199933",
        "bedrooms": 2,
        "areaSqm": RENT_AREA,
        "monthlyRentThb": RENT_PRICE,
        "rentPerSqmPerMonthThb": round(rent_rate),
        "floor": 5,
        "lastObservedUpdatedAt": "2026-10-15T12:01:08.653Z",
    },
    "commonFee": {
        "rateThbPerSqmPerMonth": FEE_RATE,
        "source": "https://propertyhub.in.th/en/projects/esta-phahol-sapanmai",
        "status": "published indicative rate; requires confirmation with the juristic office",
    },
    "yieldEstimate": {
        "purchasePriceThb": SALE_PRICE,
        "purchaseAreaSqm": SALE_AREA,
        "estimatedMonthlyRentThb": round(monthly_estimated_rent),
        "annualRentAfterOneAgentMonthThb": round(annual_rent_after_agent_month),
        "annualIndicativeCommonFeeThb": round(annual_indicative_fee),
        "netAnnualYieldPercent": net_yield_after_agent_and_indicative_fee,
        "formula": "((15,000 / 50 × 43 × 11) − (45 × 43 × 12)) / 2,770,000 × 100",
        "otherExcludedCosts": ["tax", "maintenance", "vacancy", "purchase transaction costs"],
    },
}
(ROOT / "reports" / "esta-phahol-sapanmai-sale-enrichment-2026-10-18.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

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
    "status": "listed_recently_bumped_under_30d_availability_unconfirmed",
    "verification_note": "LivingInsider direct listing 2152509: 2BR, 43 sqm, THB 2,770,000, floor 7; created 2024-05-05 and last bumped 2026-09-26. Page accessible on check date; actual availability not independently confirmed. A cheaper listing with 38/34 sqm conflicting area was excluded from ROI.",
    "source_1": SALE_URL,
    "source_2": "https://www.livinginsider.com/project/condo-esta-phahol-sapanmai-condo-buysell",
    "source_3": "https://propertyhub.in.th/en/projects/esta-phahol-sapanmai",
}
rows = [row for row in rows if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "sale")]
rows.append(sale_log)
with availability_file.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print(json.dumps({
    "project": NAME,
    "salePriceThb": SALE_PRICE,
    "areaSqm": SALE_AREA,
    "saleThbPerSqm": round(SALE_PRICE / SALE_AREA),
    "rentThbPerSqmPerMonth": round(rent_rate),
    "estimatedNetYieldPercent": net_yield_after_agent_and_indicative_fee,
    "saleAvailability": sale_sample["listingStatus"],
}, ensure_ascii=False))
