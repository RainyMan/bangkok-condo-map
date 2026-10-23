"""Record a directly linked rental listing for P. Pinklao Condominium 2."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3799
PROJECT = "P. Pinklao Condominium 2"
CHECKED_AT = "2026-10-23"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-p-pinklao-condominium-2"
LISTING_URL = "https://propertyhub.in.th/en/listings/a-nice-studio-room-fully-furnished-good-price---6450428"

sample = {
    "id": "6450428",
    "price": 6500,
    "area": 28,
    "priceSqm": 232.14,
    # PropertyHub labels this both Studio and 1 Bed. Retain the listing, but
    # leave bedroom count unknown so it cannot enter a 1BR ROI calculation.
    "beds": None,
    "roomType": "Studio (bedroom field inconsistent)",
    "title": "P. Pinklao Condominium 2 · Studio · 28 ㎡ · ฿6,500/月",
    "url": LISTING_URL,
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_on_direct_listing_and_project_link",
    "listingStatus": "availability_unconfirmed_current_project_page_listing",
    "verificationNote": "PropertyHub 個別頁標示本案、฿6,500/月、28㎡，可入住日為 2026-09-30；頁面未提供最近更新日，且房型同時標示 Studio 與 1 Bed。專案出租頁目前列 1 筆。保留為房型未確認、在架狀態待確認的租盤，不納入一房投報。",
}


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


manual_prefix, manual_rows, manual_suffix = load_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
manual.update({
    "asOf": CHECKED_AT,
    "replaceRent": True,
    "rent": {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": 6500,
        "minimum": 6500,
        "minimumArea": 28,
        "averageSqm": 232.14,
        "minimumSqm": 232.14,
        "asOf": CHECKED_AT,
        "sourceName": "PropertyHub 個別出租掛牌（房型待確認）",
        "source": PROJECT_URL,
        "minimumSourceUrl": LISTING_URL,
        "minimumSqmSourceUrl": LISTING_URL,
        "samples": [sample],
        "byBedroom": {},
    },
})
save_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix)

cross_prefix, cross_rows, cross_suffix = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub",
    "projectSourceUrl": PROJECT_URL,
    "sale": {
        "activeListingCount": 3,
        "displayedResultCount": 3,
        "observedCount": 3,
        "sourceUrl": "https://www.ddproperty.com/en/project/12322-p-pinklao-condominium-2",
        "note": "DDproperty 專案頁的三筆出售樣本分別為 ฿480,000、฿500,000、฿500,000，面積 23.8–24.1㎡；最低總價樣本可直接開啟核對。",
        "listings": [
            {"listingId": "500520759", "price": 480000, "area": 23.8, "bedrooms": 1, "listedAt": "2026-10-03", "url": "https://www.ddproperty.com/en/property/p-pinklao-condominium-2-bangkok-for-sale-500520759", "sourceName": "DDproperty", "statusLabel": "專案頁樣本，最近刷新 2026-10-03"},
            {"listingId": "500520799", "price": 500000, "area": 23.8, "bedrooms": 1, "listedAt": "2026-10-03", "url": "https://www.ddproperty.com/en/property/p-pinklao-condominium-2-bangkok-for-sale-500520799", "sourceName": "DDproperty", "statusLabel": "專案頁樣本，最近刷新 2026-10-03"},
            {"listingId": "500520819", "price": 500000, "area": 24.1, "bedrooms": 1, "listedAt": "2026-10-03", "url": "https://www.ddproperty.com/en/property/p-pinklao-condominium-2-bangkok-for-sale-500520819", "sourceName": "DDproperty", "statusLabel": "專案頁樣本，最近刷新 2026-10-03"},
        ],
    },
    "rent": {
        "activeListingCount": 1,
        "displayedResultCount": 1,
        "observedCount": 1,
        "sourceUrl": PROJECT_URL,
        "note": "PropertyHub 專案出租頁目前列 1 筆；直接掛牌標示 ฿6,500/月、28㎡、可入住日 2026-09-30，但最近更新日為空。房型欄位同時標示 Studio 與 1 Bed，保留未分類租盤供核對，不納入一房投報；實際仍在架狀態待確認。",
        "listings": [{
            "listingId": "6450428", "price": 6500, "area": 28, "priceSqm": 232.14,
            "bedrooms": None, "availableAt": "2026-09-30", "url": LISTING_URL,
            "sourceName": "PropertyHub",
            "statusLabel": "專案頁列 1 筆；更新日未提供，可入住日已過，房型 Studio／1 Bed 不一致，狀態待確認",
        }],
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 出租專案頁", "url": PROJECT_URL, "statusLabel": "目前列 1 筆本案出租掛牌。"},
        {"sourceName": "PropertyHub 出租單筆物件", "url": LISTING_URL, "statusLabel": "฿6,500/月、28㎡；Studio 與 1 Bed 欄位不一致，更新日未提供。"},
        {"sourceName": "DDproperty 出售專案頁", "url": "https://www.ddproperty.com/en/project/12322-p-pinklao-condominium-2", "statusLabel": "三筆掛牌，價位 ฿480,000–฿500,000。"},
    ],
    "yieldStatus": "not_calculated_rental_room_type_and_availability_unconfirmed",
    "yieldNote": "出售樣本為一房，但唯一直接租盤同時標示 Studio 與 1 Bed，且最近更新日未提供、可入住日已過。為避免房型錯配及採用失效租盤，不以此租盤計算一房投報率。",
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
    "rentalSample": sample,
    "saleSamples": crosscheck["sale"]["listings"],
    "yieldStatus": crosscheck["yieldStatus"],
    "sources": [PROJECT_URL, LISTING_URL, crosscheck["sale"]["sourceUrl"]],
    "notes": [
        "PropertyHub direct page classifies the listing as a condominium and links it to the exact P. Pinklao Condominium 2 project.",
        "The project page currently lists one rental listing.",
        "The direct listing displays 6,500 THB/month, 28 sqm, available for rent 2026-09-30, and no last-update date.",
        "Studio and 1 Bed labels conflict, so bedroom count remains null and ROI is not calculated from this listing.",
        "The unit's current availability needs landlord confirmation because its availability date has passed.",
    ],
}
(REPORTS / "p-pinklao-condominium-2-rent-2026-10-23.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(json.dumps({
    "hipflatId": PROJECT_ID,
    "rentTHBPerMonth": 6500,
    "areaSqm": 28,
    "rentTHBPerSqmMonth": round(6500 / 28, 2),
    "roomClassification": "unknown: Studio / 1 Bed conflict",
    "availability": "unconfirmed; listed on project page, update date absent",
    "yield": "not calculated",
}, ensure_ascii=False))
