"""Add one directly linked, cross-checked rental sample for 31 Residence."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3006
PROJECT_NAME = "31 Residence"
RENT_URL = "https://propertyhub.in.th/en/listings/superb-2-bedroom-apartment-for-rent-in-phrom-phong-area-br20889ap---6075482"
DD_URL = "https://www.ddproperty.com/en/property/31-residence-bangkok-for-rent-60211462"
RENT_PRICE = 77_000
RENT_AREA = 160
RENT_RATE = RENT_PRICE / RENT_AREA


def load_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


manual_path = DIST / "bangkok-manual-market-samples.js"
projects = load_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
project = next((row for row in projects if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    projects.append(project)
project["asOf"] = "2026-10-18"
rent = project.setdefault("rent", {})
sample = {
    "id": "6075482",
    "price": RENT_PRICE,
    "area": RENT_AREA,
    "priceSqm": round(RENT_RATE),
    "beds": 2,
    "roomType": "2BR",
    "title": "31 Residence，2 房，160 ㎡，฿77,000/月",
    "url": RENT_URL,
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "updated": "2026-10-17",
    "checkedAt": "2026-10-18",
    "matchedBy": "exact_project_name_and_cross_checked_DDproperty_listing_60211462",
    "listingStatus": "active_as_listed",
}
samples = [item for item in rent.get("samples", []) if item.get("url") != RENT_URL]
samples.append(sample)
rent.update({
    "count": len(samples),
    "observedCount": len(samples),
    "countKind": "manual_verified_listing",
    "average": RENT_PRICE,
    "minimum": RENT_PRICE,
    "minimumArea": RENT_AREA,
    "minimumSampleUpdated": "2026-10-17",
    "averageSqm": round(RENT_RATE),
    "minimumSqm": round(RENT_RATE),
    "minimumSqmSampleUpdated": "2026-10-17",
    "asOf": "2026-10-18",
    "sourceName": "PropertyHub 個別租賃掛牌（DDproperty 交叉核對）",
    "source": RENT_URL,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "samples": samples,
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
save_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", projects)

availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_path.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
    columns = list(rows[0]) if rows else [
        "hipflat_id", "condo", "checked_at", "market", "status",
        "verification_note", "source_1", "source_2", "source_3",
    ]
rows = [row for row in rows if not (row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") == "rent")]
rows.append({
    "hipflat_id": str(PROJECT_ID),
    "condo": PROJECT_NAME,
    "checked_at": "2026-10-18",
    "market": "rent",
    "status": "direct_listing_cross_checked_active_as_listed",
    "verification_note": "PropertyHub 個別頁列出 2 房、160㎡、฿77,000/月，專案頁於 2026-10-17 刷新；DDproperty 個別頁 60211462 同列該專案、房型、面積與租金。未聯絡刊登者確認空置。該案目前無出售掛牌，故無法計算投報率。",
    "source_1": RENT_URL,
    "source_2": DD_URL,
    "source_3": "https://propertyhub.in.th/en/condo-for-rent/project-31-residence",
})
with availability_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": "2026-10-18",
    "coordinates": {
        "status": "verified",
        "source": "https://propertyhub.in.th/en/projects/31-residence",
        "latitude": 13.73879969843466,
        "longitude": 100.5671876103064,
    },
    "rentListing": {
        "monthlyRentThb": RENT_PRICE,
        "bedrooms": 2,
        "areaSqm": RENT_AREA,
        "rentThbPerSqmMonth": round(RENT_RATE, 2),
        "url": RENT_URL,
        "crossCheckUrl": DD_URL,
        "projectPageRefreshed": "2026-10-17",
        "availability": "active as listed; vacancy not confirmed with advertiser",
    },
    "saleListing": {"status": "no matching project listing found", "source": "https://propertyhub.in.th/en/condo-for-sale/project-31-residence"},
    "managementFee": {"status": "not published", "deducted": False},
    "yieldEstimate": {"status": "not calculated because no verified sale listing is available"},
}
(ROOT / "reports" / "31-residence-rent-enrichment-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "rentThb": RENT_PRICE, "areaSqm": RENT_AREA, "rentThbPerSqmMonth": round(RENT_RATE, 2), "rentSource": RENT_URL, "saleListing": "not found; yield not calculated"}, ensure_ascii=False))
