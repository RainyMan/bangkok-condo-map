"""Record source attribution checks for Grand View Condominium, Chatuchak."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3070
PROJECT = "Grand View Condominium"
CHECKED = "2026-10-23"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/grand-view-condominium-cphufe"
RENT_URL = "https://www.hipflat.co.th/ads/9u3t0hau1l11uu7unlt13n0cn3u2770h"
DD_SALE_URL = "https://www.ddproperty.com/ขายคอนโด/ที่-แกรนด์วิว-คอนโด-1351"
DD_LOWEST_SALE_URL = (
    "https://www.ddproperty.com/property/แกรนด์วิว-คอนโด-กรุงเทพ-ขาย-500634892"
)
PH_SALE_URL = "https://propertyhub.in.th/ขายคอนโด/โครงการ-grand-view-condo"
DOT_URL = "https://www.dotproperty.co.th/en/condo/13046/grand-view-condominium"
THAI_PROPERTY_URL = "https://www.thailand-property.com/condo/13046/grand-view-condominium"
DD_CHECKED_SALES = [
    ("500634892", 2500000, 50),
    ("500637397", 3560000, 46.9),
    ("500637395", 3460000, 60.74),
    ("500634888", 3460000, 60),
    ("500626762", 3633000, 53.83),
]


def dd_listing_url(listing_id: str) -> str:
    return DD_LOWEST_SALE_URL.rsplit("-", 1)[0] + "-" + listing_id


def read_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript data format in {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def write_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


manual_prefix, manual_rows, manual_suffix = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if not manual or manual.get("name") != PROJECT:
    raise RuntimeError("Grand View manual sample not found; no data changed")
rent = manual.get("rent") or {}
sample = next((row for row in rent.get("samples", []) if row.get("id") == "903011"), None)
if not sample or sample.get("url") != RENT_URL:
    raise RuntimeError("Expected direct Hipflat rental sample not found; no data changed")

sample.update({
    "priceSqm": round(float(sample["price"]) / float(sample["area"]), 2),
    "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_over_30d",
    "verificationNote": (
        "Hipflat 專案頁於本次核查仍列 1 筆出租；直接物件頁確認屬於 Chatuchak 的 Grand View Condominium，"
        "3 房、230㎡、฿55,000/月。物件頁記錄的更新日為 2026-09-10，超過 30 日；"
        "保留為可追溯樣本，但在架狀態待確認，不用於投報率。"
    ),
})
rent.update({
    "averageSqm": round(float(sample["price"]) / float(sample["area"]), 2),
    "minimumSqm": round(float(sample["price"]) / float(sample["area"]), 2),
    "asOf": CHECKED,
    "note": "Hipflat 專案頁仍列 1 筆租盤；直接物件更新日為 2026-09-10，超過 30 日，現況待確認。",
})
manual["rent"] = rent
write_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix)

cross_prefix, cross_rows, cross_suffix = read_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
cross = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID, "projectName": PROJECT}
    cross_rows.append(cross)
cross.update({
    "projectName": PROJECT,
    "asOf": CHECKED,
    "sourceName": "Hipflat / DDproperty / PropertyHub / DotProperty / Thailand-Property",
    "projectSourceUrl": PROJECT_URL,
    "sale": {
        "activeListingCount": 0,
        "displayedResultCount": 7,
        "sourceUrl": DD_SALE_URL,
        "note": (
            "DDproperty 同名專案搜尋列 7 筆；已抽查 5 個個別頁（500634892、500637397、500637395、"
            "500634888、500626762），每頁都把房源描述為位於สัตหีบ（Sattahip），不是 Chatuchak。"
            "剩餘 2 筆尚未逐項核對；5 筆異地房源排除，未核對者也不當作本案樣本。PropertyHub 同名專案列於 Baan Amphur，"
            "亦為芭達雅案。DotProperty 與 Thailand-Property 的曼谷專案頁均顯示 0 筆售租。"
        ),
        "excludedListings": [
            {
                "id": listing_id,
                "url": dd_listing_url(listing_id),
                "displayedPrice": price,
                "displayedArea": area,
                "reason": "DDproperty 個別頁描述為 Sattahip 專案，排除於 Chatuchak 樣本。",
            }
            for listing_id, price, area in DD_CHECKED_SALES
        ],
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 1,
        "listings": [{
            "id": "903011",
            "price": 55000,
            "area": 230,
            "priceSqm": 239.13,
            "bedrooms": 3,
            "url": RENT_URL,
            "updated": "2026-09-10",
            "listingStatus": "availability_unconfirmed_update_over_30d",
        }],
        "sourceUrl": PROJECT_URL,
        "note": (
            "Hipflat 專案頁列 1 筆；直接掛牌確認為本案 3 房、230㎡、฿55,000/月。"
            "頁面更新日為 2026-09-10，距核查日超過 30 日；保留歷史樣本與連結，現況待確認，不計入投報。"
        ),
    },
    "availabilitySources": [
        {"sourceName": "Hipflat Bangkok 專案頁", "url": PROJECT_URL, "statusLabel": "列 1 筆出租；完成年 2012，9 層。"},
        {"sourceName": "Hipflat 出租單筆", "url": RENT_URL, "statusLabel": "3 房、230㎡、฿55,000/月；更新日 2026-09-10，逾 30 日，現況待確認。"},
        {"sourceName": "DDproperty 出售結果頁", "url": DD_SALE_URL, "statusLabel": "列 7 筆同名結果；已抽查最低價個別頁，內文指向 Sattahip，不能確認為 Chatuchak 本案。"},
        {"sourceName": "DDproperty 最低價個別頁（排除）", "url": DD_LOWEST_SALE_URL, "statusLabel": "結果列價 ฿2,500,000／50㎡；個別頁描述 Sattahip，排除於曼谷樣本。"},
        *[
            {
                "sourceName": f"DDproperty 同名售盤 {listing_id}（排除）",
                "url": dd_listing_url(listing_id),
                "statusLabel": f"個別頁描述 Sattahip；฿{price:,}／{area}㎡，排除於 Chatuchak 樣本。",
            }
            for listing_id, price, area in DD_CHECKED_SALES[1:]
        ],
        {"sourceName": "PropertyHub 同名專案（排除）", "url": PH_SALE_URL, "statusLabel": "頁面指向 Baan Amphur／Sattahip 的 Grand View Condo，非 Chatuchak 專案。"},
        {"sourceName": "DotProperty 曼谷專案頁", "url": DOT_URL, "statusLabel": "頁面列 0 筆出售及出租。"},
        {"sourceName": "Thailand-Property 曼谷專案頁", "url": THAI_PROPERTY_URL, "statusLabel": "頁面列 0 筆出售及出租。"},
    ],
    "yieldStatus": "not_calculated_no_verified_sale_and_rent_unconfirmed",
    "yieldNote": "同名出售結果無法核實為 Chatuchak 專案；唯一直接租盤更新已逾 30 日。沒有可靠、同期的配對樣本，不計投報率。",
})
write_array("bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED,
    "verifiedRentSample": {
        "id": "903011", "monthlyRent": 55000, "areaSqm": 230,
        "rentPerSqm": 239.13, "bedrooms": 3, "lastUpdated": "2026-09-10",
        "status": "availability_unconfirmed_update_over_30d", "url": RENT_URL,
    },
    "saleSearch": {
        "ddpropertyProjectUrl": DD_SALE_URL, "displayedResults": 7,
        "checkedListingIds": [listing_id for listing_id, _, _ in DD_CHECKED_SALES],
        "excludedListingIds": [listing_id for listing_id, _, _ in DD_CHECKED_SALES],
        "excludedLowestListing": DD_LOWEST_SALE_URL,
        "conflict": "Five checked direct listing pages say Sattahip; do not map to Chatuchak. Two project-page results remain unverified and are also excluded.",
        "propertyHubProjectUrl": PH_SALE_URL,
        "otherProjectChecks": [DOT_URL, THAI_PROPERTY_URL],
        "verifiedBangkokListings": 0,
    },
    "yieldStatus": "not_calculated_no_verified_sale_and_rent_unconfirmed",
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "grand-view-condominium-market-check-2026-10-23.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "saleResultsExcluded": 7, "rentSample": "903011", "yield": report["yieldStatus"]}, ensure_ascii=False))
