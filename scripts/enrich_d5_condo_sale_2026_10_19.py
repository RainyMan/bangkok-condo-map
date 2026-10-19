from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 5008
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/d5-condo-rlkmch"
COORDS = "https://www.thaigerproperty.com/projects/thailand/bangkok/bueng-kum/nuan-chan/d5-condo"
DD_PROJECT = "https://www.ddproperty.com/en/condo-for-sale/at-d5-condo-11727/priced-under-3m-thb"
DD_SALE = "https://www.ddproperty.com/en/property/d5-condo-bangkok-for-sale-500639969"
PH_PROJECT_SALE = "https://propertyhub.in.th/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-d5-condominium"
PH_PROJECT_RENT = "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-d5-condominium"
PH_SALE = "https://propertyhub.in.th/listings/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-%E0%B8%9E%E0%B8%B7%E0%B9%89%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88-%E0%B9%80%E0%B8%9E%E0%B8%B5%E0%B8%A2%E0%B8%87-1-85-%E0%B8%A5%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%9A%E0%B8%B2%E0%B8%97-d5-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1---6262276"
DD_RENT_FEED = "https://www.ddproperty.com/en/property-for-rent/2?_freetextDisplay=Bueng+Kum%2C+Bangkok&districtCode=TH1027&isCommercial=false&listingType=rent&locale=en&minSize=30&order=desc&page=2&propertyTypeCode=CONDO&propertyTypeGroup=N&regionCode=TH10&slug=2&sort=size"
KBT_PROJECT = "https://www.kaibaanthai.com/en/projects/thailand/bangkok/bueng-kum/nuan-chan/d5-condo"
FAZWAZ_RENT = "https://www.fazwaz.co.th/en/property-for-rent/thailand/bangkok/bueng-kum/nuan-chan/at-d5-condo"


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    prefix, _, suffix = load_array(filename, symbol)
    indent = None if filename == "bangkok-manual-market-samples.js" else 2
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, indent=indent, separators=(",", ":") if indent is None else None) + suffix, encoding="utf-8")


price = 1_850_000
area = 56.76
price_sqm = round(price / area)
unit_sample = {
    "id": "500639969",
    "price": price,
    "area": area,
    "priceSqm": price_sqm,
    "beds": 2,
    "roomType": "2BR",
    "title": "D5 Condo，2 房，56.76 ㎡，฿1,850,000",
    "url": DD_SALE,
    "sourceName": "DDproperty",
    "projectName": "D5 Condo",
    "updated": "2026-10-14",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_direct_listing_page",
    "listingStatus": "active_as_listed",
    "verificationNote": "DDproperty 個別頁核對為 D5 Condo、2 房、56.76㎡、฿1,850,000，刊登日 2026-10-14。PropertyHub 專案頁另列同價、同房型、同面積之 2 房單位，視為可能重複刊登，只計一筆。",
}

manual_record = {
    "hipflatId": PROJECT_ID,
    "name": "D5 Condo",
    "asOf": CHECKED_AT,
    "sale": {
        "count": 4,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "minimumSampleUpdated": "2026-10-14",
        "averageSqm": price_sqm,
        "minimumSqm": price_sqm,
        "minimumSqmSampleUpdated": "2026-10-14",
        "asOf": CHECKED_AT,
        "sourceName": "DDproperty 個別出售掛牌",
        "source": DD_PROJECT,
        "minimumSourceUrl": DD_SALE,
        "minimumSqmSourceUrl": DD_SALE,
        "samples": [unit_sample],
        "byBedroom": {
            "2": {
                "count": 1,
                "minimum": price,
                "minimumArea": area,
                "area": area,
                "priceSqm": price_sqm,
                "minimumSqm": price_sqm,
                "averageSqm": price_sqm,
                "sourceUrl": DD_SALE,
                "minimumSourceUrl": DD_SALE,
                "minimumSqmSourceUrl": DD_SALE,
            }
        },
    },
    "rent": None,
}
# Omit the absent rent key; explicit null is not a market sample.
manual_record.pop("rent")
prefix, manual_rows, suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [row for row in manual_rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
manual_rows.append(manual_record)
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

availability = [
    {"sourceName": "DDproperty 出售專案頁", "url": DD_PROJECT, "statusLabel": "截至 2026-10-19 顯示 4 筆在架出售；個別核對其中 2 房、56.76㎡、฿1,850,000 一筆，刊登日 2026-10-14。"},
    {"sourceName": "DDproperty 兩房出售單筆", "url": DD_SALE, "statusLabel": "2 房 · 56.76㎡ · ฿1,850,000 · ฿32,593/㎡；刊登日 2026-10-14。"},
    {"sourceName": "PropertyHub 出售專案頁", "url": PH_PROJECT_SALE, "statusLabel": "專案頁列 3 筆出售；另有一筆同價、同房型、同面積的 2 房頁面，視為可能同一單位，不重複計數。"},
    {"sourceName": "PropertyHub 出售單筆交叉核對", "url": PH_SALE, "statusLabel": "同為 2 房、56.76㎡、฿1,850,000；更新日未提供，僅作重複刊登交叉核對，不另計樣本。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": PH_PROJECT_RENT, "statusLabel": "專案頁顯示目前 0 筆出租掛牌。"},
    {"sourceName": "DDproperty 區域出租搜尋", "url": DD_RENT_FEED, "statusLabel": "搜尋頁曾列出 D5 Condo 1 房、31㎡、฿9,000/月，刊登日 2026-07-02；超過 30 日，且不是同房型，排除於現行租金與投報。"},
    {"sourceName": "KaiBaanThai 專案頁", "url": KBT_PROJECT, "statusLabel": "頁面顯示租盤數量摘要，但可用房源區塊沒有匹配物件；無法建立可核對的直接租盤樣本。"},
    {"sourceName": "FazWaz 專案出租搜尋", "url": FAZWAZ_RENT, "statusLabel": "頁面摘要列出租盤數量與租金範圍，但未取得可核實的直接物件頁，未納入租金。"},
    {"sourceName": "Thaiger Property 專案頁座標", "url": COORDS, "statusLabel": "唯一專案 slug 與 D5 Condo 名稱相符；已用於本 Condo 的核實座標 (13.8345948, 100.6401289)。"},
]

cross_record = {
    "hipflatId": PROJECT_ID,
    "projectName": "D5 Condo",
    "asOf": CHECKED_AT,
    "sourceName": "DDproperty / PropertyHub",
    "projectSourceUrl": DD_PROJECT,
    "sale": {
        "activeListingCount": 4,
        "displayedResultCount": 1,
        "sourceUrl": DD_PROJECT,
        "note": "DDproperty 專案出售頁顯示 4 筆在架掛牌。個別核對其中一筆 2 房、56.76㎡、฿1,850,000，刊登日 2026-10-14；只將可直接核對的樣本納入行情。PropertyHub 專案頁的同價同面積兩房掛牌視為可能重複，不另計。",
        "listings": [{
            "listingId": "500639969",
            "price": price,
            "area": area,
            "priceSqm": price_sqm,
            "bedrooms": 2,
            "listedAt": "2026-10-14",
            "url": DD_SALE,
            "sourceName": "DDproperty",
        }],
    },
    "rent": {
        "activeListingCount": 0,
        "sourceUrl": PH_PROJECT_RENT,
        "note": "PropertyHub D5 Condominium 專案出租頁顯示 0 筆。DDproperty 搜尋索引另曾列 1 房、31㎡、฿9,000/月的 2026-07-02 掛牌，已超過 30 日且不符兩房房型；未取得現行直接租盤，不納入租金或投報。",
    },
    "availabilitySources": availability,
    "yieldStatus": "no_current_same_bedroom_rent",
    "yieldNote": "有可核對的兩房出售價與面積，但目前找不到同案現行出租物件；舊一房租盤逾 30 日，不能用來估兩房投報。",
}
_, cross_rows, _ = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = [row for row in cross_rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
cross_rows.append(cross_record)
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

# Record the independent availability and sale/rent decision as an auditable research artifact.
report = {
    "hipflatId": PROJECT_ID,
    "project": "D5 Condo",
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "lat": 13.8345948,
        "lng": 100.6401289,
        "source": COORDS,
        "verificationSource": HIPFLAT,
        "method": "Thaiger Property exact project title and unique D5 Condo project slug; same Bangkok district and address corroborated by DDproperty and PropertyHub listings.",
    },
    "sale": {
        "activeFeedCount": 4,
        "verifiedDirectSampleCount": 1,
        "samples": [unit_sample],
        "duplicateCrosscheck": {"url": PH_SALE, "price": price, "area": area, "bedrooms": 2, "countedSeparately": False},
    },
    "rent": {
        "currentDirectSampleCount": 0,
        "reason": "PropertyHub exact project rent page shows 0 listings. The DDproperty search feed's 1-bedroom listing was dated 2026-07-02 and is over 30 days old; do not use for current metrics or yield.",
        "sources": [PH_PROJECT_RENT, DD_RENT_FEED, KBT_PROJECT, FAZWAZ_RENT],
    },
    "yield": {"calculated": False, "reason": "No verified current same-project rent listing; no comparable rent baseline."},
    "sources": availability,
}
(ROOT / "reports/d5-condo-two-bedroom-sale-availability-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checks_path = ROOT / "reports/listing-availability-checks-2026-10-19.csv"
with checks_path.open("r", newline="", encoding="utf-8-sig") as f:
    check_rows = list(csv.DictReader(f))
check_rows = [row for row in check_rows if not (row.get("hipflat_id") == str(PROJECT_ID))]
check_rows.extend([
    {"hipflat_id": str(PROJECT_ID), "condo": "D5 Condo", "checked_at": CHECKED_AT, "market": "sale", "status": "direct_current_listing_verified", "verification_note": "DDproperty exact-project feed shows 4 listings; direct page 500639969 confirms 2BR, 56.76 sqm, ฿1,850,000, listed 2026-10-14. PropertyHub shows a same-price/same-area 2BR ad; treated as a possible duplicate, not a second sample.", "source_1": DD_PROJECT, "source_2": DD_SALE, "source_3": PH_PROJECT_SALE},
    {"hipflat_id": str(PROJECT_ID), "condo": "D5 Condo", "checked_at": CHECKED_AT, "market": "rent", "status": "no_current_matching_listing", "verification_note": "PropertyHub exact-project rent page shows 0. DDproperty search index surfaced a 1BR 31 sqm ฿9,000 listing dated 2026-07-02 (>30 days); excluded. No current rent sample or ROI.", "source_1": PH_PROJECT_RENT, "source_2": DD_RENT_FEED, "source_3": KBT_PROJECT},
])
with checks_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"])
    writer.writeheader()
    writer.writerows(check_rows)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html = html.replace("bangkok-manual-market-samples.js?v=20261019-31-residence-fresh-hipflat-listing", "bangkok-manual-market-samples.js?v=20261019-d5-condo-two-bedroom-sale-500639969")
html = html.replace("bangkok-market-crosschecks.js?v=20261019-donmuang-thong-thai-availability-3088-3063", "bangkok-market-crosschecks.js?v=20261019-d5-condo-sale-rent-check-5008")
index_path.write_text(html, encoding="utf-8")
print(json.dumps({"manualSamples": len(manual_rows), "crosschecks": len(cross_rows), "availabilityRows": len(check_rows), "salePrice": price, "saleArea": area, "salePricePerSqm": price_sqm, "rentSamples": 0, "yield": "not calculated"}, ensure_ascii=False, indent=2))
