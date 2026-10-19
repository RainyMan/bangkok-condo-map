from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
HIPFLAT_ID = 3005

PROJECT_URL = "https://propertyhub.in.th/projects/chatuchak-condominium"
SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-chatuchak-condominium"
RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-chatuchak-condominium"
LISTING_URL = "https://propertyhub.in.th/en/listings/%EF%B8%8F-64-2-sq-m-condo-for-rent-high-floor-stunning-chatuchak-park-view-fully-furnished-move-in-ready---6242213"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/chatuchak-condominium-cpdwry"
AREA = 64.2
RENT = 33_000
RENT_PER_SQM = round(RENT / AREA, 2)


def load_array(filename: str, variable: str):
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot read {filename}")
    return path, text[: match.start(1)], json.loads(match.group(1)), text[match.end(1) :]


def save_array(data) -> None:
    path, prefix, rows, suffix = data
    compact = path.name == "bangkok-manual-market-samples.js"
    path.write_text(
        prefix + json.dumps(rows, ensure_ascii=False,
                            separators=(",", ":") if compact else None,
                            indent=None if compact else 2) + suffix,
        encoding="utf-8",
    )


rent_sample = {
    "id": "6242213",
    "kind": "rent",
    "price": RENT,
    "area": AREA,
    "priceSqm": RENT_PER_SQM,
    "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Chatuchak Condominium · 2 房 · 64.2 ㎡ · ฿33,000/月",
    "url": LISTING_URL,
    "sourceName": "PropertyHub 直接出租掛牌",
    "projectName": "Chatuchak Condominium",
    "checkedAt": AS_OF,
    "projectPageRefreshedAt": "2026-10-14",
    "matchedBy": "exact_PropertyHub_project_page_and_direct_listing",
    "listingStatus": "availability_unconfirmed_date_unknown",
    "availableFrom": "2026-06-30",
    "statusNote": "專案頁 2026-10-14 刷新後仍列此物件；單筆頁更新日未提供，並記載 2026-06-30 可入住（開始日期，非截止日）。現況請向刊登者確認。",
}

manual_data = load_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual_rows = manual_data[2]
manual = next(row for row in manual_rows if int(row["hipflatId"]) == HIPFLAT_ID)
manual["asOf"] = AS_OF
manual["rent"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": RENT,
    "minimum": RENT,
    "minimumArea": AREA,
    "averageSqm": round(RENT_PER_SQM),
    "minimumSqm": RENT_PER_SQM,
    "minimumSampleUpdated": None,
    "minimumSqmSampleUpdated": None,
    "asOf": AS_OF,
    "sourceName": "PropertyHub 直接出租掛牌",
    "source": RENT_URL,
    "minimumSourceUrl": LISTING_URL,
    "minimumSqmSourceUrl": LISTING_URL,
    "samples": [rent_sample],
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": RENT,
            "area": AREA,
            "minimumArea": AREA,
            "priceSqm": RENT_PER_SQM,
            "minimumSqm": RENT_PER_SQM,
            "averageSqm": RENT_PER_SQM,
            "sourceUrl": LISTING_URL,
            "minimumSourceUrl": LISTING_URL,
            "minimumSqmSourceUrl": LISTING_URL,
        }
    },
    "note": "PropertyHub 專案出租頁於 2026-10-14 刷新後仍列 1 筆；單筆頁核實 2 房、64.2㎡、฿33,000/月。單筆更新日未提供，2026-06-30 是可入住日期而非截止日；在架狀態仍請向刊登者確認。",
}
manual["replaceRent"] = True
save_array(manual_data)

crosscheck_data = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
crosscheck_rows = crosscheck_data[2]
crosscheck = next(row for row in crosscheck_rows if int(row["hipflatId"]) == HIPFLAT_ID)
crosscheck.update(
    {
        "asOf": AS_OF,
        "sourceName": "PropertyHub / Hipflat",
        "projectSourceUrl": HIPFLAT_URL,
        "sale": {
            "activeListingCount": 0,
            "sourceUrl": SALE_URL,
            "note": "PropertyHub 專案出售頁核對顯示 0 筆；Hipflat 專案頁亦未列本案現行單筆房源。未找到可核實出售樣本，不填售價。",
        },
        "rent": {
            "activeListingCount": 1,
            "displayedResultCount": 1,
            "listings": [
                {
                    "id": "6242213",
                    "price": RENT,
                    "area": AREA,
                    "priceSqm": RENT_PER_SQM,
                    "bedrooms": 2,
                    "url": LISTING_URL,
                    "statusLabel": "PropertyHub 專案頁於 2026-10-14 刷新後仍列出；單筆頁為 2 房、64.2㎡、฿33,000/月，單筆更新日未提供。頁面記載 2026-06-30 可入住（開始日期，非截止日），現況請向刊登者確認。",
                }
            ],
            "sourceUrl": RENT_URL,
            "note": "專案出租頁於 2026-10-14 刷新後仍列 1 筆；單筆頁列 2026-06-30 可入住（開始日，不是出租截止日），但單筆更新日未提供，實際在架狀態待向刊登者確認。",
        },
        "availabilitySources": [
            {
                "sourceName": "Hipflat 專案頁",
                "url": HIPFLAT_URL,
                "statusLabel": "頁面未列本案現行單筆出售／出租物件。",
            },
            {
                "sourceName": "PropertyHub 出售專案頁",
                "url": SALE_URL,
                "statusLabel": "核對日顯示 0 筆出售；未找到本案直接出售樣本。",
            },
            {
                "sourceName": "PropertyHub 出租專案頁",
                "url": RENT_URL,
                "statusLabel": "專案頁 2026-10-14 刷新後仍列 1 筆；單筆更新日未提供。",
            },
            {
                "sourceName": "PropertyHub 出租單筆",
                "url": LISTING_URL,
                "statusLabel": "฿33,000／月 · 64.2㎡ · 2 房；單筆更新日未提供，頁面記載 2026-06-30 可入住（開始日），請確認在架狀態。",
            },
        ],
        "yieldStatus": "no_current_sale_listing",
        "yieldNote": "目前有一筆可核對兩房租盤，但沒有本案出售掛牌，無可靠購入價基準，不計投報率。",
    }
)
save_array(crosscheck_data)

# Refresh the page's versioned URLs so the newly linked sample and corrected
# availability interpretation reach browsers with a cached dataset.
index = DIST / "index.html"
html = index.read_text(encoding="utf-8")
html = re.sub(
    r"bangkok-manual-market-samples\.js\?v=[^\"']+",
    "bangkok-manual-market-samples.js?v=20261019-chatuchak-rent",
    html,
    count=1,
)
html = re.sub(
    r"bangkok-market-crosschecks\.js\?v=[^\"']+",
    "bangkok-market-crosschecks.js?v=20261019-chatuchak-rent",
    html,
    count=1,
)
index.write_text(html, encoding="utf-8")

# Keep the auditable CSV in step with the primary data files.
report = ROOT / "reports" / "bangkok-coverage-2026-10-19.csv"
with report.open(encoding="utf-8-sig", newline="") as handle:
    report_rows = list(csv.DictReader(handle))
fields = list(report_rows[0])
for row in report_rows:
    if row["hipflat_id"] == str(HIPFLAT_ID):
        row["rent_sample"] = "yes"
        row["rent_individual_listing_link"] = "yes"
        row["rent_source"] = LISTING_URL
        row["rent_sample_updated"] = ""
        row["rent_availability_checked"] = "1"
        row["rent_availability_note"] = "PropertyHub project page refreshed 2026-10-14 still lists one 2BR, 64.2 sqm, ฿33,000/month unit; the direct ad has no update date and says available for rent from 2026-06-30; reconfirm availability."
        row["yield_status"] = "no_current_sale_listing"
        row["yield_note"] = "Current PropertyHub sale project page shows zero matching listings; no purchase baseline for yield."
        row["missing"] = "出售（目前無可核實掛牌）；投報待售價"
with report.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(report_rows)

# Keep the older availability artefacts consistent with the latest direct
# listing page: "Available for rent" is a start date, not an end date.
availability_report = ROOT / "reports" / "chatuchak-condominium-availability-2026-10-18.json"
availability = json.loads(availability_report.read_text(encoding="utf-8"))
availability["asOf"] = AS_OF
availability["marketAvailability"]["rent"] = {
    "status": "listed_availability_unconfirmed",
    "sampleCount": 1,
    "sources": [RENT_URL, HIPFLAT_URL],
    "currentListing": {
        "url": LISTING_URL, "listingId": "6242213", "priceTHBPerMonth": RENT,
        "areaSqm": AREA, "bedrooms": 2, "availableForRentDate": "2026-06-30",
        "projectPageRefreshedAt": "2026-10-14", "individualListingUpdateDate": None,
    },
}
availability["marketAvailability"]["roi"] = {
    "status": "not_calculable",
    "reason": "No verified current sale listing or exact-project purchase-price baseline.",
}
availability_report.write_text(json.dumps(availability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

availability_csv = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_csv.open(encoding="utf-8-sig", newline="") as handle:
    availability_reader = csv.DictReader(handle)
    availability_fields = availability_reader.fieldnames
    availability_rows = list(availability_reader)
for availability_row in availability_rows:
    if availability_row["hipflat_id"] == str(HIPFLAT_ID) and availability_row["market"] == "rent":
        availability_row["checked_at"] = AS_OF
        availability_row["status"] = "listing_present_availability_unconfirmed"
        availability_row["verification_note"] = "PropertyHub exact-project page still lists 1 unit after its 2026-10-14 refresh; direct listing says 2BR, 64.2 sqm, THB 33,000/month, available for rent from 2026-06-30. The direct ad has no update date; confirm current availability."
        availability_row["source_1"] = LISTING_URL
        availability_row["source_2"] = RENT_URL
        availability_row["source_3"] = HIPFLAT_URL
with availability_csv.open("w", encoding="utf-8-sig", newline="") as handle:
    availability_writer = csv.DictWriter(handle, fieldnames=availability_fields)
    availability_writer.writeheader()
    availability_writer.writerows(availability_rows)

print(
    json.dumps(
        {
            "hipflatId": HIPFLAT_ID,
            "rent": RENT,
            "area": AREA,
            "rentPerSqm": RENT_PER_SQM,
            "saleListings": 0,
            "yieldStatus": "no_current_sale_listing",
        },
        ensure_ascii=False,
    )
)
