from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANUAL_PATH = DIST / "bangkok-manual-market-samples.js"
INDEX_PATH = DIST / "index.html"
REPORT_PATH = ROOT / "reports" / "31-residence-propertyhub-rents-2026-10-19.json"
CHECKED_AT = "2026-10-19"
PROJECT_ID = 3006
PROJECT_NAME = "31 Residence"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-31-residence"


def load_manual() -> list[dict]:
    text = MANUAL_PATH.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError("Unexpected manual market sample data format")
    return json.loads(match.group(1))


def save_manual(rows: list[dict]) -> None:
    MANUAL_PATH.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


samples = [
    {
        "id": "U37158",
        "price": 75_000,
        "area": 170,
        "priceSqm": 441,
        "beds": 2,
        "roomType": "2BR",
        "title": "31 Residence，2 房，170 ㎡，฿75,000/月",
        "url": "https://www.hipflat.co.th/en/ads/le7at2e78l17nthcu7ucta073u02u980",
        "sourceName": "Hipflat",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-18",
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_and_listing_detail",
        "listingStatus": "active_as_listed",
        "verificationNote": "Hipflat 專案頁及個別房源頁均核對為 31 Residence、2 房、170㎡、฿75,000/月；10 月 18 日檢查時仍列出。",
    },
    {
        "id": "6075482",
        "price": 77_000,
        "area": 160,
        "priceSqm": 481,
        "beds": 2,
        "roomType": "2BR",
        "title": "31 Residence，2 房，160 ㎡，฿77,000/月",
        "url": "https://propertyhub.in.th/en/listings/superb-2-bedroom-apartment-for-rent-in-phrom-phong-area-br20889ap---6075482",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-17",
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_name_and_direct_listing_page",
        "listingStatus": "active_as_listed",
        "verificationNote": "PropertyHub 專案頁列出此筆並標示 2026-10-17 更新；個別房源頁核對專案名、2 房、160㎡及 ฿77,000/月。頁面提醒現況可能變動，應向刊登者確認。",
    },
    {
        "id": "5583590",
        "price": 95_000,
        "area": 270,
        "priceSqm": 352,
        "beds": 3,
        "roomType": "3BR",
        "title": "31 Residence，3 房，270 ㎡，฿95,000/月",
        "url": "https://propertyhub.in.th/en/listings/expansive-3-bedroom-penthouse-apartment-in-phrom-phong-br0684ap---5583590",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-17",
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_page_and_direct_listing_page",
        "listingStatus": "active_as_listed",
        "crossListedSourceUrl": "https://www.hipflat.co.th/en/ads/928n422n88a2c28hh1t1hul33u0l0ehn",
        "verificationNote": "PropertyHub 專案頁列出此筆並標示 2026-10-17 更新；個別房源頁核對 31 Residence、3 房、270㎡及 ฿95,000/月。Hipflat 有同房型、面積和價格的交叉刊登，視作同一樣本，不重複計數。現況需向刊登者確認。",
    },
]

rows = load_manual()
project = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    rows.append(project)

rent = project.setdefault("rent", {})
old_samples = rent.get("samples", [])
by_id = {str(row.get("id")): row for row in old_samples if row.get("id") is not None}

# Preserve older direct sources as history, but exclude records whose update
# dates are over 30 days old from the current market statistics.
for stale_id in ("BR0684AP", "BR0474AP", "6058105"):
    if stale_id in by_id:
        by_id[stale_id]["listingStatus"] = "availability_unconfirmed_update_over_30d"

for sample in samples:
    by_id[sample["id"]] = sample

all_samples = sorted(by_id.values(), key=lambda row: (int(row.get("price") or 0), str(row.get("id"))))
current_samples = [
    row for row in all_samples
    if row.get("listingStatus") == "active_as_listed"
    and int(row.get("price") or 0) > 0
    and float(row.get("area") or 0) > 0
]
if len(current_samples) != len(samples):
    raise RuntimeError(f"Expected {len(samples)} current samples, found {len(current_samples)}")

lowest_total = min(current_samples, key=lambda row: int(row["price"]))
lowest_rate = min(current_samples, key=lambda row: int(row["price"]) / float(row["area"]))
rates = [int(row["price"]) / float(row["area"]) for row in current_samples]
by_bedroom: dict[str, dict] = {}
for beds in sorted({int(row["beds"]) for row in current_samples}):
    bedroom_samples = [row for row in current_samples if int(row["beds"]) == beds]
    low_total = min(bedroom_samples, key=lambda row: int(row["price"]))
    low_rate = min(bedroom_samples, key=lambda row: int(row["price"]) / float(row["area"]))
    room_rates = [int(row["price"]) / float(row["area"]) for row in bedroom_samples]
    by_bedroom[str(beds)] = {
        "count": len(bedroom_samples),
        "minimum": int(low_total["price"]),
        "area": float(low_total["area"]),
        "minimumArea": float(low_total["area"]),
        "priceSqm": round(int(low_rate["price"]) / float(low_rate["area"])),
        "minimumSqm": round(int(low_rate["price"]) / float(low_rate["area"]), 2),
        "averageSqm": round(sum(room_rates) / len(room_rates), 2),
        "sourceUrl": low_total["url"],
        "minimumSourceUrl": low_total["url"],
        "minimumSqmSourceUrl": low_rate["url"],
    }

project["asOf"] = CHECKED_AT
project["replaceRent"] = True
project["rent"] = {
    "count": len(current_samples),
    "observedCount": len(current_samples),
    "countKind": "manual_verified_listing",
    "average": round(sum(int(row["price"]) for row in current_samples) / len(current_samples)),
    "minimum": int(lowest_total["price"]),
    "minimumArea": float(lowest_total["area"]),
    "minimumSampleUpdated": lowest_total.get("updated"),
    "averageSqm": round(sum(rates) / len(rates)),
    "minimumSqm": round(int(lowest_rate["price"]) / float(lowest_rate["area"]), 2),
    "minimumSqmSampleUpdated": lowest_rate.get("updated"),
    "asOf": CHECKED_AT,
    "snapshotMethod": "Direct Hipflat and PropertyHub rental listings; matched project names, unit bedrooms, area and rent on individual listing pages. Old entries over 30 days are kept as history but excluded from current metrics.",
    "sourceName": "Hipflat／PropertyHub 個別出租掛牌",
    "source": PROJECT_URL,
    "minimumSourceUrl": lowest_total["url"],
    "minimumSqmSourceUrl": lowest_rate["url"],
    "byBedroom": by_bedroom,
    "samples": all_samples,
}
save_manual(rows)

index = INDEX_PATH.read_text(encoding="utf-8")
index, count = re.subn(
    r"bangkok-manual-market-samples\.js\?v=[^\"']+",
    "bangkok-manual-market-samples.js?v=20261019-31-residence-current-direct-rents",
    index,
    count=1,
)
if count != 1:
    raise RuntimeError("Could not update manual-market cache key")
INDEX_PATH.write_text(index, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "projectSource": PROJECT_URL,
    "saleSearch": {
        "propertyHub": "https://propertyhub.in.th/en/condo-for-sale/project-31-residence",
        "ddproperty": "https://www.ddproperty.com/en/project/6787-31-residence",
        "result": "No current exact-project sale listings were shown on the checked project pages.",
        "yield": "Not calculated: no verified asking price for purchase was found.",
    },
    "currentRentSamples": current_samples,
    "historicalSamplesExcludedFromCurrentMetrics": [
        row for row in all_samples if row.get("listingStatus") != "active_as_listed"
    ],
    "rentSummary": project["rent"],
    "notes": [
        "The lowest directly verified two-bedroom rental asking price in this refreshed sample is ฿75,000/month for 170 sqm; the same listing supplies both price and area.",
        "The PropertyHub project page shows 7 rental results; three direct unit pages were checked for this snapshot. The display sample count therefore means verified samples, not the project-wide listing count.",
        "Availability can change; confirm directly with each listing publisher.",
    ],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "hipflatId": PROJECT_ID,
    "currentSamples": len(current_samples),
    "lowestTwoBedroom": by_bedroom["2"]["minimum"],
    "lowestTwoBedroomArea": by_bedroom["2"]["area"],
    "lowestTwoBedroomUrl": by_bedroom["2"]["minimumSourceUrl"],
    "saleListings": 0,
    "yield": "not calculable without verified sale price",
}, ensure_ascii=False))
