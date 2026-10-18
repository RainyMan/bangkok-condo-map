import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_PATH = ROOT / "dist" / "bangkok-manual-market-samples.js"
AVAILABILITY_PATH = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
REPORT_PATH = ROOT / "reports" / "cc-29-rent-enrichment-2026-10-18.json"

PROJECT_ID = 3545
PROJECT_NAME = "C&C 29 Condo"
RENT_URL = "https://www.ddproperty.com/en/property/c-c-29-condo-bangkok-for-rent-60204711"
RENT_PRICE = 16000
RENT_AREA = 35
RENT_RATE = round(RENT_PRICE / RENT_AREA)


def read_js_array(path: Path, global_name: str):
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{global_name} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected data format in {path}")
    return json.loads(text[len(prefix):].strip().rstrip(";"))


def write_js_array(path: Path, global_name: str, rows):
    path.write_text(
        f"window.{global_name} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


rows = read_js_array(MANUAL_PATH, "BANGKOK_MANUAL_MARKET_SAMPLES")
project = next((row for row in rows if row.get("hipflatId") == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    rows.append(project)

rent = project.setdefault("rent", {})
samples = rent.setdefault("samples", [])
sample = {
    "id": "60204711",
    "price": RENT_PRICE,
    "area": RENT_AREA,
    "priceSqm": RENT_RATE,
    "beds": 2,
    "roomType": "2BR",
    "title": "C&C 29 Condo，2 房，35 ㎡，฿16,000/月",
    "url": RENT_URL,
    "sourceName": "DDproperty",
    "projectName": PROJECT_NAME,
    "updated": "2026-10-16",
    "checkedAt": "2026-10-18",
    "matchedBy": "exact_project_name_and_cross_post_reference_CX-133306",
    "listingStatus": "availability_unconfirmed",
}
samples[:] = [row for row in samples if row.get("url") != RENT_URL]
samples.append(sample)
rent.update({
    "count": max(1, len(samples)),
    "observedCount": max(1, len(samples)),
    "countKind": "manual_verified_listing",
    "average": RENT_PRICE,
    "minimum": RENT_PRICE,
    "minimumArea": RENT_AREA,
    "minimumSampleUpdated": "2026-10-16",
    "averageSqm": RENT_RATE,
    "minimumSqm": RENT_RATE,
    "minimumSqmSampleUpdated": "2026-10-16",
    "asOf": "2026-10-18",
    "sourceName": "DDproperty 單筆租賃掛牌",
    "source": RENT_URL,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": RENT_PRICE,
            "area": RENT_AREA,
            "minimumSqm": RENT_RATE,
            "averageSqm": RENT_RATE,
            "sourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
        }
    },
})
write_js_array(MANUAL_PATH, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

columns = [
    "hipflat_id", "condo", "checked_at", "market", "status", "verification_note",
    "source_1", "source_2", "source_3",
]
with AVAILABILITY_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
    existing = list(csv.DictReader(handle))
entry = {
    "hipflat_id": str(PROJECT_ID),
    "condo": PROJECT_NAME,
    "checked_at": "2026-10-18",
    "market": "rent",
    "status": "listing_found_availability_unconfirmed",
    "verification_note": "DDproperty 個別掛牌：2 房、35 ㎡、฿16,000/月；PropertyHub 相同 CX-133306 房源於 2026-10-16 顯示刷新。未聯絡刊登者確認仍可出租。",
    "source_1": RENT_URL,
    "source_2": "https://propertyhub.in.th/en/condo-for-rent/project-c-c-29",
    "source_3": "https://propertyhub.in.th/en/projects/c-c-29",
}
existing = [row for row in existing if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "rent")]
existing.append(entry)
with AVAILABILITY_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    writer.writerows(existing)

sale_price, sale_area = 4_000_000, 35
rent_monthly_at_sale_area = round(RENT_PRICE / RENT_AREA * sale_area)
annual_rent_after_agent = rent_monthly_at_sale_area * 11
net_yield = annual_rent_after_agent / sale_price * 100
report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": "2026-10-18",
    "saleSample": {
        "priceThb": sale_price,
        "bedrooms": 2,
        "areaSqm": sale_area,
        "source": "https://propertyhub.in.th/en/listings/a046297-c-c-29-condo---6213853",
        "projectPageLastRefreshed": "2026-10-17",
    },
    "rentSample": {
        "monthlyRentThb": RENT_PRICE,
        "bedrooms": 2,
        "areaSqm": RENT_AREA,
        "rentThbPerSqmMonth": round(RENT_PRICE / RENT_AREA, 2),
        "source": RENT_URL,
        "matchedCrossPostReference": "CX-133306",
        "propertyHubLastRefreshed": "2026-10-16",
        "availability": "unconfirmed with advertiser",
    },
    "managementFee": {"rateThbPerSqmMonth": None, "status": "not verified; excluded from yield"},
    "yieldEstimate": {
        "purchasePriceThb": sale_price,
        "purchaseAreaSqm": sale_area,
        "monthlyRentThbAtPurchaseArea": rent_monthly_at_sale_area,
        "agentMonthsDeducted": 1,
        "annualRentAfterAgentThb": annual_rent_after_agent,
        "annualCommonFeeThb": 0,
        "netYieldPercent": round(net_yield, 2),
        "formula": "(monthly rent × 11 − verified annual common fee) ÷ purchase price",
    },
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "rentSource": RENT_URL, "rentPerSqm": RENT_RATE, "netYieldPercent": round(net_yield, 2)}))
