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
LISTING_URL = (
    "https://propertyhub.in.th/listings/%EF%B8%8F-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-"
    "%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%9464-2-%E0%B8%95%E0%B8%A3-%E0%B8%A1-"
    "%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B8%AA%E0%B8%A7%E0%B8%99%E0%B8%88%E0%B8%95%E0%B8%B8%E0%B8%88%E0%B8%B1%E0%B8%81%E0%B8%A3-"
    "%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99%E0%B8%AA%E0%B8%B9%E0%B8%87-"
    "%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B9%81%E0%B8%95%E0%B9%88%E0%B8%87%E0%B8%84%E0%B8%A3%E0%B8%9A-"
    "%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%AD%E0%B8%A2%E0%B8%B9%E0%B9%88---6242213"
)
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/chatuchak-condominium-cpdwry"
AREA = 64.2
RENT = 33_000
RENT_PER_SQM = round(RENT / AREA, 2)


def load_array(filename: str, variable: str):
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(\[.*\]);", text)
    if not match:
        raise RuntimeError(f"Cannot read {filename}")
    return path, text[: match.start(1)], json.loads(match.group(1)), text[match.end(1) :]


def save_array(data) -> None:
    path, prefix, rows, suffix = data
    path.write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
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
    "updated": "2026-10-14",
    "checkedAt": AS_OF,
    "matchedBy": "exact_PropertyHub_project_page_and_direct_listing",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "availableFrom": "2026-06-30",
    "statusNote": "專案出租頁於 2026-10-14 再次更新並仍列此物件；物件頁記載自 2026-06-30 可入住，無法單靠日期確認目前仍在架，請向刊登者確認。",
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
    "minimumSampleUpdated": "2026-10-14",
    "minimumSqmSampleUpdated": "2026-10-14",
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
    "note": "PropertyHub 專案出租頁於 2026-10-14 更新並列 1 筆；單筆頁核實 2 房、64.2㎡、฿33,000/月。單筆記載 2026-06-30 可入住，近期仍被專案頁列出；在架狀態建議向刊登者確認。",
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
                    "listedAt": "2026-10-14",
                    "statusLabel": "PropertyHub 專案出租頁於 2026-10-14 更新並列出；單筆頁為 2 房、64.2㎡、฿33,000/月。單筆頁記載可入住日 2026-06-30，現況仍請向刊登者確認。",
                }
            ],
            "sourceUrl": RENT_URL,
            "note": "專案出租頁於 2026-10-14 更新並仍列 1 筆；單筆頁記載 2026-06-30 可入住（開始日，不是出租截止日）。按近期更新納入樣本，實際在架狀態待向刊登者確認。",
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
                "statusLabel": "核對頁面列 1 筆出租，更新日期 2026-10-14。",
            },
            {
                "sourceName": "PropertyHub 出租單筆",
                "url": LISTING_URL,
                "statusLabel": "฿33,000／月 · 64.2㎡ · 2 房；頁面記載 2026-06-30 可入住，請向刊登者確認在架狀態。",
            },
        ],
        "yieldStatus": "no_current_sale_listing",
        "yieldNote": "目前有可核對的兩房租盤，但出售專案頁為 0 筆，無可靠購入價基準，暫不計投報率。",
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
        row["rent_sample_updated"] = "2026-10-14"
        row["rent_availability_checked"] = "1"
        row["rent_availability_note"] = "PropertyHub project page updated 2026-10-14 lists one 2BR, 64.2 sqm, ฿33,000/month unit; current availability to reconfirm."
        row["yield_status"] = "no_current_sale_listing"
        row["yield_note"] = "Current PropertyHub sale project page shows zero matching listings; no purchase baseline for yield."
        row["missing"] = "出售（目前無可核實掛牌）；投報待售價"
with report.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(report_rows)

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
