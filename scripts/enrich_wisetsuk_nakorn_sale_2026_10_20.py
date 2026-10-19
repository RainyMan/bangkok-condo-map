"""Add a current, directly linked sale listing for Wisetsuk Nakorn Condo."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3054
PROJECT = "Wisetsuk Nakorn Condo"
CHECKED_AT = "2026-10-20"
SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-wisetsuk-nakorn-condo"
RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-wisetsuk-nakorn-condo"
SALE_LISTING = "https://propertyhub.in.th/en/listings/condo-for-sale-at-wisetsuk-nakorn-condo-bang-khae-large-corner-unit-51-sq-m-fully-furnished-and-ready-to-move-in---6184765"

sample = {
    "id": "6184765",
    "price": 790000,
    "area": 51,
    "priceSqm": 15490,
    # PropertyHub gives conflicting room labels: Studio on the unit card and
    # listing details, but 1 bedroom in the bedroom-count field. Do not assign
    # it to a room-specific ROI baseline until the source is clarified.
    "beds": None,
    "roomType": "Studio / 1 房欄位不一致",
    "title": "Wisetsuk Nakorn Condo，51 ㎡，฿790,000",
    "url": SALE_LISTING,
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "updated": "2026-10-09",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_propertyhub_project_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "verificationNote": "PropertyHub 專案頁於 2026-10-09 顯示此掛牌最近刷新；個別物件頁列 ฿790,000、51㎡、管理費 ฿17/㎡/月。原始房型欄位同時寫 Studio 與 1 Bedroom，為避免混房型，保留房型未確認，不納入一房專屬試算；是否仍在架待賣方確認。",
}


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str, compact: bool = False) -> None:
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, **options) + suffix, encoding="utf-8")


manual_prefix, manual_rows, manual_suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
manual.update({
    "asOf": CHECKED_AT,
    "replaceSale": True,
    "sale": {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": 790000,
        "minimum": 790000,
        "minimumArea": 51,
        "minimumSampleUpdated": "2026-10-09",
        "averageSqm": 15490,
        "minimumSqm": 15490,
        "minimumSqmSampleUpdated": "2026-10-09",
        "asOf": CHECKED_AT,
        "sourceName": "PropertyHub 個別出售掛牌",
        "source": SALE_PROJECT,
        "minimumSourceUrl": SALE_LISTING,
        "minimumSqmSourceUrl": SALE_LISTING,
        "samples": [sample],
        "byBedroom": {},
    },
    "fee": {
        "rate": 17,
        "status": "public",
        "note": "PropertyHub 個別售房頁標示管理費 ฿17/㎡/月；實際金額仍須向管委會確認。",
        "source": SALE_LISTING,
    },
})
save_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix, compact=True)

cross_prefix, cross_rows, cross_suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub",
    "projectSourceUrl": SALE_PROJECT,
    "sale": {
        "activeListingCount": 1,
        "displayedResultCount": 1,
        "observedCount": 1,
        "sourceUrl": SALE_PROJECT,
        "note": "PropertyHub 專案頁列出一筆出售掛牌，最近刷新日為 2026-10-09；個別頁標示 ฿790,000、51㎡、฿15,490/㎡。Studio 與 1 Bedroom 房型欄位互相矛盾，因此列為未確認房型，暫不納入房型篩選或一房投報計算。",
        "listings": [{
            "listingId": "6184765",
            "price": 790000,
            "area": 51,
            "priceSqm": 15490,
            "bedrooms": None,
            "listedAt": "2026-10-09",
            "url": SALE_LISTING,
            "sourceName": "PropertyHub",
            "statusLabel": "專案頁近期刷新；房型欄位 Studio／1 房不一致，刊登現況待確認",
        }],
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": RENT_PROJECT,
        "note": "PropertyHub 出租專案頁目前顯示無符合掛牌；曾列 2026-06-26 刷新的 1 房、47㎡、฿25,000/月物件，但已超過 30 日且現行專案頁無結果，不納入租金或投報。",
        "listings": [],
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 出售專案頁", "url": SALE_PROJECT, "statusLabel": "目前列 1 筆掛牌，฿790,000、51㎡；專案頁最近刷新 2026-10-09。"},
        {"sourceName": "PropertyHub 出售單筆物件", "url": SALE_LISTING, "statusLabel": "฿790,000、51㎡、฿15,490/㎡；管理費 ฿17/㎡/月。房型欄位 Studio／1 房不一致。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": RENT_PROJECT, "statusLabel": "目前沒有符合出租掛牌；舊掛牌 2026-06-26 刷新，已超過 30 日，不納入行情。"},
    ],
    "yieldStatus": "not_calculated_no_current_rent_listing",
    "yieldNote": "已核實近期出售掛牌；PropertyHub 現行出租頁無房源，舊租盤超過 30 日，故不計投報率。出售樣本房型欄位有 Studio／1 房衝突，暫不代入一房投報。",
}
existing = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing is None:
    cross_rows.append(crosscheck)
else:
    existing.update(crosscheck)
save_array("bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED_AT,
    "coordinates": {"verified": True, "sourceUrl": "https://www.hipflat.co.th/en/projects/wisetsuk-nakorn-condo-npkjeq"},
    "saleSample": sample,
    "commonFeeTHBPerSqmMonth": 17,
    "rentStatus": "No current listings on PropertyHub project page; one historical listing last refreshed 2026-06-26 is excluded.",
    "yieldStatus": "Not calculated: no current verified rental listing; sale bedroom field conflicts.",
    "sources": [SALE_PROJECT, SALE_LISTING, RENT_PROJECT],
    "notes": [
        "PropertyHub project's sale list reports one listing and a latest refresh date of 2026-10-09.",
        "The direct listing page says ฿790,000 / 51 sqm and management fee ฿17/sqm/month.",
        "The source labels the unit both Studio and 1 bedroom. It is retained as an unclassified sale sample and excluded from bedroom-specific yield inputs.",
        "The rent project page returns no matching listings; the previous 1-bedroom rental at ฿25,000 / 47 sqm was last refreshed 2026-06-26 and is over 30 days old.",
    ],
}
(REPORTS / "wisetsuk-nakorn-sale-enrichment-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

html = (DIST / "index.html").read_text(encoding="utf-8")
html = html.replace("bangkok-manual-market-samples.js?v=20261020-baan-k-rent-3188", "bangkok-manual-market-samples.js?v=20261020-wisetsuk-sale-3054")
html = html.replace("bangkok-market-crosschecks.js?v=20261020-baan-k-rent-3188", "bangkok-market-crosschecks.js?v=20261020-wisetsuk-sale-3054")
(DIST / "index.html").write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "salePriceTHB": 790000, "areaSqm": 51, "saleRateTHBPerSqm": round(790000 / 51), "bedroomClassification": "conflicting source labels; excluded from bedroom-specific calculations", "rent": "no current listings", "yield": "not calculated"}, ensure_ascii=False))
