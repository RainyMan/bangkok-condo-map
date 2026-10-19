from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 5010
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/dynasty-complex-heoidd"
COORDS = "https://propertyhub.in.th/en/projects/dynasty-complex"
FAZWAZ_FEED = "https://www.fazwaz.co.th/en/property-for-sale/thailand/bangkok/wang-thong-lang/saphan-song/at-dynasty-complex"
FAZWAZ_SALE = "https://www.fazwaz.co.th/en/property-sales/2-bedroom-condo-for-sale-at-dynasty-complex-in-saphan-song-bangkok-u6793602"
DD_SALE = "https://www.ddproperty.com/en/property/dynasty-condominium-bangkok-for-sale-500609671"
PH_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-dynasty-complex"
PH_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-dynasty-complex"
PH_RENT_1 = "https://propertyhub.in.th/en/listings/for-rent-condo-dynasty-complex-building-1-floor-3-1-bed-room-room-size-33-sqm--b4770969---5287445"
PH_RENT_2 = "https://propertyhub.in.th/en/listings/condo-for-rent-at-dynasty-complex-c6807069---5279526"
FAZWAZ_RENT = "https://www.fazwaz.co.th/en/property-rent/7-bedroom-condo-for-rent-at-dynasty-complex-in-saphan-song-bangkok-u1991456"


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


samples = [
    {"id": "U6793602", "price": 3_200_000, "area": 71.72, "priceSqm": 44_618, "beds": 2, "roomType": "2BR", "title": "Dynasty Complex，2 房，71.72 ㎡，฿3,200,000", "url": FAZWAZ_SALE, "sourceName": "FazWaz", "projectName": "Dynasty Complex", "updated": CHECKED_AT, "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_direct_listing_page", "listingStatus": "active_as_listed", "verificationNote": "FazWaz 個別頁列 2 房、71.72㎡、฿3,200,000；刊登日 2026-10-09，查核時顯示 3 小時前更新。"},
    {"id": "500609671", "price": 2_800_000, "area": 60.15, "priceSqm": 46_550, "beds": 3, "roomType": "3BR", "title": "Dynasty Condominium，3 房，60.15 ㎡，฿2,800,000", "url": DD_SALE, "sourceName": "DDproperty", "projectName": "Dynasty Complex", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_alias_address_and_direct_listing_page", "listingStatus": "active_as_listed", "verificationNote": "DDproperty 搜尋結果列 Dynasty Condominium、12 Soi Lat Phrao 71、3 房、60.15㎡、฿2,800,000；地址與專案相符，個別頁刊登日期未能核實。"},
]
two, three = samples
sale = {
    "count": 2, "observedCount": 2, "countKind": "manual_verified_listing", "average": 3_000_000,
    "minimum": 2_800_000, "minimumArea": 60.15, "minimumSampleUpdated": None,
    "averageSqm": 45_584, "minimumSqm": 44_618, "minimumSqmSampleUpdated": CHECKED_AT,
    "asOf": CHECKED_AT, "sourceName": "FazWaz / DDproperty 個別掛牌", "source": FAZWAZ_FEED,
    "minimumSourceUrl": DD_SALE, "minimumSqmSourceUrl": FAZWAZ_SALE, "samples": samples,
    "byBedroom": {
        "2": {"count": 1, "minimum": two["price"], "minimumArea": two["area"], "area": two["area"], "priceSqm": two["priceSqm"], "minimumSqm": two["priceSqm"], "averageSqm": two["priceSqm"], "sourceUrl": two["url"], "minimumSourceUrl": two["url"], "minimumSqmSourceUrl": two["url"]},
        "3": {"count": 1, "minimum": three["price"], "minimumArea": three["area"], "area": three["area"], "priceSqm": three["priceSqm"], "minimumSqm": three["priceSqm"], "averageSqm": three["priceSqm"], "sourceUrl": three["url"], "minimumSourceUrl": three["url"], "minimumSqmSourceUrl": three["url"]},
    },
}
_, manual_rows, _ = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [r for r in manual_rows if int(r.get("hipflatId", -1)) != PROJECT_ID]
manual_rows.append({"hipflatId": PROJECT_ID, "name": "Dynasty Complex", "asOf": CHECKED_AT, "sale": sale})
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows, compact=True)

sources = [
    {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "專案頁目前列出 1 個出售單位，摘要價格 ฿3,200,000。"},
    {"sourceName": "FazWaz 2 房個別出售掛牌", "url": FAZWAZ_SALE, "statusLabel": "2 房、71.72㎡、฿3,200,000；刊登日 2026-10-09，查核時顯示 3 小時前更新。"},
    {"sourceName": "FazWaz 專案出售頁", "url": FAZWAZ_FEED, "statusLabel": "專案頁列出 1 個現行 2 房出售單位。"},
    {"sourceName": "DDproperty 3 房個別出售掛牌", "url": DD_SALE, "statusLabel": "搜尋結果列 3 房、60.15㎡、฿2,800,000，地址與本案相符；刊登日期未能核實。"},
    {"sourceName": "PropertyHub 專案出租頁", "url": PH_RENT, "statusLabel": "索引列 2 筆 1 房、33㎡、฿12,500/月；日期 2026-09-05 與 2026-09-12，超過 30 日，現況未核實，不納入現行租金或投報。"},
    {"sourceName": "PropertyHub 租盤 1", "url": PH_RENT_1, "statusLabel": "專案頁索引租盤；最後可見日期 2026-09-12，超過 30 日，現況未確認。"},
    {"sourceName": "PropertyHub 租盤 2", "url": PH_RENT_2, "statusLabel": "專案頁索引租盤；最後可見日期 2026-09-05，超過 30 日，現況未確認。"},
    {"sourceName": "FazWaz 舊租盤", "url": FAZWAZ_RENT, "statusLabel": "7 房、200㎡、฿60,000/月；刊登於 2024-12-27，逾一年未更新，排除於現行行情與投報。"},
    {"sourceName": "PropertyHub 專案座標與身份", "url": COORDS, "statusLabel": "專案頁座標已與 Hipflat 專案名稱和地址交叉比對。"},
]
cross_record = {
    "hipflatId": PROJECT_ID, "projectName": "Dynasty Complex", "asOf": CHECKED_AT,
    "sourceName": "FazWaz / DDproperty / PropertyHub / Hipflat", "projectSourceUrl": HIPFLAT,
    "sale": {"activeListingCount": 2, "displayedResultCount": 2, "sourceUrl": FAZWAZ_FEED, "note": "已核對兩筆不同物件：FazWaz 2 房 71.72㎡、฿3,200,000（近期更新），以及 DDproperty 3 房 60.15㎡、฿2,800,000；各房型分開取最低價。", "samples": samples},
    "rent": {"activeListingCount": 0, "displayedResultCount": 2, "sourceUrl": PH_RENT, "note": "PropertyHub 索引的兩筆 1 房租盤最後可見日期為 2026-09-05、09-12，查核日已超過 30 日，無法確認仍可租；另有 FazWaz 7 房租盤逾一年未更新。沒有可核實的現行兩房租金，不計兩房投報。"},
    "availabilitySources": sources,
    "yieldStatus": "no_current_same_bedroom_rent",
    "yieldNote": "最低兩房購入價為 ฿3,200,000，面積 71.72㎡；沒有可核實的現行兩房租金樣本，故不計投報率。",
}
_, cross_rows, _ = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = [r for r in cross_rows if int(r.get("hipflatId", -1)) != PROJECT_ID]
cross_rows.append(cross_record)
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

report = {
    "hipflatId": PROJECT_ID, "project": "Dynasty Complex", "checkedAt": CHECKED_AT,
    "coordinates": {"lat": 13.79188744088282, "lng": 100.6085798078375, "source": COORDS, "verificationSource": HIPFLAT},
    "sale": {"verifiedCurrentDirectListingCount": 2, "samples": samples},
    "rent": {"currentlyVerifiedDirectListingCount": 0, "staleListingsObserved": [{"url": PH_RENT_1, "price": 12500, "area": 33, "bedrooms": 1, "lastVisibleDate": "2026-09-12"}, {"url": PH_RENT_2, "price": 12500, "area": 33, "bedrooms": 1, "lastVisibleDate": "2026-09-05"}, {"url": FAZWAZ_RENT, "price": 60000, "area": 200, "bedrooms": 7, "lastUpdated": "over one year ago"}]},
    "yield": {"calculated": False, "reason": "No currently verified same-bedroom rent listing; two-bedroom rent is unavailable."}, "sources": sources,
}
(ROOT / "reports/dynasty-complex-two-bedroom-sale-rent-check-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

csv_path = ROOT / "reports/listing-availability-checks-2026-10-19.csv"
with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
    checks = [r for r in csv.DictReader(f) if r.get("hipflat_id") != str(PROJECT_ID)]
checks.extend([
    {"hipflat_id": str(PROJECT_ID), "condo": "Dynasty Complex", "checked_at": CHECKED_AT, "market": "sale", "status": "direct_current_listing_verified", "verification_note": "FazWaz 2BR 71.72 sqm ฿3,200,000 listed Oct 9 and updated 3 hours before check; DDproperty direct result shows distinct 3BR 60.15 sqm ฿2,800,000 at same project address.", "source_1": FAZWAZ_SALE, "source_2": DD_SALE, "source_3": FAZWAZ_FEED},
    {"hipflat_id": str(PROJECT_ID), "condo": "Dynasty Complex", "checked_at": CHECKED_AT, "market": "rent", "status": "no_current_matching_listing", "verification_note": "PropertyHub lists two 1BR 33 sqm ฿12,500 listings last visible Sep 5 and Sep 12 (>30d); FazWaz 7BR listing has not been updated for over a year. Current availability not confirmed; no current same-bedroom rent or yield.", "source_1": PH_RENT, "source_2": PH_RENT_1, "source_3": FAZWAZ_RENT},
])
with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"])
    writer.writeheader()
    writer.writerows(checks)

index = DIST / "index.html"
html = index.read_text(encoding="utf-8")
html = re.sub(r'bangkok-manual-market-samples\.js\?v=[^" ]+', "bangkok-manual-market-samples.js?v=20261019-dynasty-complex-sale-500609671-u6793602", html)
html = re.sub(r'bangkok-market-crosschecks\.js\?v=[^" ]+', "bangkok-market-crosschecks.js?v=20261019-dynasty-complex-crosscheck-5010", html)
index.write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "saleListings": len(samples), "twoBedroomMinimum": two["price"], "twoBedroomArea": two["area"], "rentCurrentVerified": 0, "yield": "not calculated"}, ensure_ascii=False))
