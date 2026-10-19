from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 5012
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/s1-executive-residence-uschqt"
COORDS = "https://www.thaigerproperty.com/projects/thailand/bangkok/watthana/khlong-tan-nuea/s1-executive-residence"
FAZWAZ_RENT_FEED = "https://www.fazwaz.co.th/en/property-for-rent/thailand/bangkok/watthana/khlong-tan-nuea/at-s1-executive-residence"
FAZWAZ_RENT = "https://www.fazwaz.co.th/en/property-rent/1-bedroom-apartment-for-rent-at-s1-executive-residence-in-khlong-tan-nuea-bangkok-u6543736"
DOT_PROJECT = "https://www.dotproperty.co.th/en/condo/23639/s1-executive-residence"
THAILAND_PROPERTY = "https://www.thailand-property.com/condo/23639/s1-executive-residence"
PH_MISATTRIBUTED_SALE = "https://propertyhub.in.th/en/listings/a046530-s1-executive-residence---6214097"
PH_RAM9_PROJECT = "https://propertyhub.in.th/en/projects/s1-rama-9"


def load_array(filename: str, symbol: str):
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, symbol: str, rows: list[dict], compact: bool = False):
    prefix, _, suffix = load_array(filename, symbol)
    kwargs = {"separators": (",", ":")} if compact else {"indent": 2}
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, **kwargs) + suffix, encoding="utf-8")


sample = {
    "id": "U6543736",
    "price": 45_000,
    "area": 60,
    "priceSqm": 750,
    "beds": 1,
    "roomType": "1BR",
    "title": "S1 Executive Residence，1 房，60 ㎡，฿45,000/月",
    "url": FAZWAZ_RENT,
    "sourceName": "FazWaz",
    "projectName": "S1 Executive Residence",
    "updated": CHECKED_AT,
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_direct_listing_page",
    "listingStatus": "active_as_listed",
    "verificationNote": "FazWaz 個別頁列 1 房、60㎡、฿45,000/月；刊登日 2026-07-01，頁面查核時顯示 46 分鐘前更新。",
}
manual_rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 45_000,
    "minimum": 45_000,
    "minimumArea": 60,
    "minimumSampleUpdated": CHECKED_AT,
    "averageSqm": 750,
    "minimumSqm": 750,
    "minimumSqmSampleUpdated": CHECKED_AT,
    "asOf": CHECKED_AT,
    "sourceName": "FazWaz 個別出租掛牌",
    "source": FAZWAZ_RENT_FEED,
    "minimumSourceUrl": FAZWAZ_RENT,
    "minimumSqmSourceUrl": FAZWAZ_RENT,
    "samples": [sample],
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": 45_000,
            "minimumArea": 60,
            "area": 60,
            "priceSqm": 750,
            "minimumSqm": 750,
            "averageSqm": 750,
            "sourceUrl": FAZWAZ_RENT,
            "minimumSourceUrl": FAZWAZ_RENT,
            "minimumSqmSourceUrl": FAZWAZ_RENT,
        }
    },
}
_, manual_rows, _ = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [r for r in manual_rows if int(r.get("hipflatId", -1)) != PROJECT_ID]
manual_rows.append({"hipflatId": PROJECT_ID, "name": "S1 Executive Residence", "asOf": CHECKED_AT, "rent": manual_rent})
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows, compact=True)

sources = [
    {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "專案頁列出 9 筆出租，完成年份 2011、8 層、29 戶。"},
    {"sourceName": "FazWaz 個別 1 房租盤", "url": FAZWAZ_RENT, "statusLabel": "1 房、60㎡、฿45,000/月；刊登日 2026-07-01，查核時頁面顯示 46 分鐘前更新。"},
    {"sourceName": "FazWaz 專案出租頁", "url": FAZWAZ_RENT_FEED, "statusLabel": "專案出租頁列出 9 筆；個別樣本只納入可直接核實的一筆。"},
    {"sourceName": "DotProperty 專案出售／出租頁", "url": DOT_PROJECT, "statusLabel": "頁面顯示 0 筆出售、9 筆出租；未找到本案現行出售物件。"},
    {"sourceName": "Thailand-Property 專案頁", "url": THAILAND_PROPERTY, "statusLabel": "專案頁列出 9 筆出租，租金範圍 ฿43,500–฿45,500/月；沒有出售掛牌。"},
    {"sourceName": "排除：PropertyHub 相似名稱出售物件", "url": PH_MISATTRIBUTED_SALE, "statusLabel": "฿5,300,000、2 房、65㎡的掛牌位置標示 S1 Rama 9 / Suan Luang，與本案 Thong Lo 23 / Watthana 不符，不納入本案出售樣本。"},
    {"sourceName": "PropertyHub 相似專案頁", "url": PH_RAM9_PROJECT, "statusLabel": "S1 Rama 9 專案在 Suan Luang，與 S1 Executive Residence 不同專案，排除。"},
    {"sourceName": "Thaiger 專案座標", "url": COORDS, "statusLabel": "專案地址與 Hipflat 的 Thong Lo 23、Khlong Tan Nuea、Watthana 相符，用於核實本案位置。"},
]
cross_record = {
    "hipflatId": PROJECT_ID,
    "projectName": "S1 Executive Residence",
    "asOf": CHECKED_AT,
    "sourceName": "FazWaz / DotProperty / Thailand-Property / Hipflat",
    "projectSourceUrl": HIPFLAT,
    "sale": {"activeListingCount": 0, "sourceUrl": DOT_PROJECT, "note": "DotProperty 專案頁顯示 0 筆出售。PropertyHub 的 ฿5,300,000 掛牌實際標示 S1 Rama 9 / Suan Luang，位置不符，排除。"},
    "rent": {"activeListingCount": 9, "displayedResultCount": 9, "observedCount": 1, "sourceUrl": FAZWAZ_RENT_FEED, "note": "FazWaz 專案頁列 9 筆出租，並核實其中一筆 1 房、60㎡、฿45,000/月的個別掛牌；個別頁顯示 46 分鐘前更新。" , "samples": [sample]},
    "availabilitySources": sources,
    "yieldStatus": "no_current_sale_sample",
    "yieldNote": "已有現行 1 房租金樣本，但沒有經核實的本案出售物件；不能建立購入價，因此不計投報率。",
}
_, cross_rows, _ = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = [r for r in cross_rows if int(r.get("hipflatId", -1)) != PROJECT_ID]
cross_rows.append(cross_record)
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

report = {
    "hipflatId": PROJECT_ID,
    "project": "S1 Executive Residence",
    "checkedAt": CHECKED_AT,
    "coordinates": {"source": COORDS, "verificationSource": HIPFLAT, "lat": 13.7383873, "lng": 100.5804242},
    "sale": {"verifiedCurrentDirectListingCount": 0, "sources": [DOT_PROJECT, THAILAND_PROPERTY], "excluded": {"url": PH_MISATTRIBUTED_SALE, "reason": "Listing explicitly locates the unit in S1 Rama 9 / Suan Luang, not S1 Executive Residence in Watthana."}},
    "rent": {"projectDisplayedCount": 9, "verifiedDirectSampleCount": 1, "samples": [sample]},
    "yield": {"calculated": False, "reason": "No verified current project sale sample."},
    "sources": sources,
}
(ROOT / "reports/s1-executive-residence-rent-availability-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

csv_path = ROOT / "reports/listing-availability-checks-2026-10-19.csv"
with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
    checks = [r for r in csv.DictReader(f) if r.get("hipflat_id") != str(PROJECT_ID)]
checks.extend([
    {"hipflat_id": str(PROJECT_ID), "condo": "S1 Executive Residence", "checked_at": CHECKED_AT, "market": "sale", "status": "no_current_matching_listing", "verification_note": "DotProperty exact project page shows 0 sale listings. Excluded PropertyHub A046530 ฿5.3M because its actual location is S1 Rama 9 / Suan Luang, not Thong Lo 23 / Watthana.", "source_1": DOT_PROJECT, "source_2": PH_MISATTRIBUTED_SALE, "source_3": PH_RAM9_PROJECT},
    {"hipflat_id": str(PROJECT_ID), "condo": "S1 Executive Residence", "checked_at": CHECKED_AT, "market": "rent", "status": "direct_current_listing_verified", "verification_note": "FazWaz direct unit U6543736: 1BR, 60 sqm, ฿45,000/month; listed 2026-07-01 and page reported updated 46 minutes before check. Project feed displays 9 rentals.", "source_1": FAZWAZ_RENT, "source_2": FAZWAZ_RENT_FEED, "source_3": HIPFLAT},
])
with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"])
    writer.writeheader()
    writer.writerows(checks)

index = DIST / "index.html"
html = index.read_text(encoding="utf-8")
html = re.sub(r'bangkok-manual-market-samples\.js\?v=[^" ]+', "bangkok-manual-market-samples.js?v=20261019-s1-executive-residence-rent-u6543736", html)
html = re.sub(r'bangkok-market-crosschecks\.js\?v=[^" ]+', "bangkok-market-crosschecks.js?v=20261019-s1-executive-residence-rent-check-5012", html)
index.write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "rentSamples": 1, "rent": 45_000, "area": 60, "saleSamples": 0, "yield": "not calculated"}, ensure_ascii=False))
