"""Record direct sale and dated rental evidence for Good Day Sukhumvit 93."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 4476
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/good-day-sukhumvit-93-4a1e40u8189383391ctutnn17lna7unc"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/good-day-sukhumvit-93"
PROPERTYHUB_SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-good-day-sukhumvit-93"
PROPERTYHUB_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-good-day-sukhumvit-93"
SALE_LISTING = "https://propertyhub.in.th/en/listings/2-br-condo-at-good-day-sukhumvit-93-near-bts-bang-chak-id-3028194---6169503"
DD_SALE_MIRROR = "https://www.ddproperty.com/en/property/good-day-sukhumvit-93-bangkok-for-sale-500608688"
RENT_LISTING = "https://propertyhub.in.th/en/listings/for-rent-good-day-sukhumvit-93-brand-new-condo-near-bts-bang-chak-ready-to-move-in-90condo---6268353"

sale_sample = {
    "id": "6169503",
    "price": 4_400_000,
    "area": 52,
    "priceSqm": 84_615,
    "beds": 2,
    "roomType": "2BR",
    "title": "Good Day Sukhumvit 93，2 房，52 ㎡，฿4,400,000",
    "url": SALE_LISTING,
    "sourceName": "PropertyHub",
    "alternateSourceUrls": [DD_SALE_MIRROR],
    "updated": "2026-10-07",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_room_type_price_and_area",
    "listingStatus": "active_as_listed",
}
rent_sample = {
    "id": "6268353",
    "price": 15_000,
    "area": 35,
    "priceSqm": 429,
    "beds": 2,
    "roomType": "2BR",
    "title": "Good Day Sukhumvit 93，2 房，35 ㎡，฿15,000/月",
    "url": RENT_LISTING,
    "sourceName": "PropertyHub",
    "updated": "2026-09-15",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_room_type_price_and_area",
    "listingStatus": "availability_unconfirmed_update_over_30d",
}

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual_text = manual_path.read_text(encoding="utf-8")
manual_match = re.fullmatch(r"(window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*)(\[.*\])(\s*;?\s*)", manual_text, re.S)
if not manual_match:
    raise RuntimeError("Unexpected manual market data format")
manual_rows = json.loads(manual_match.group(2))
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": "Good Day Sukhumvit 93"}
    manual_rows.append(manual)
for kind, sample in (("sale", sale_sample), ("rent", rent_sample)):
    market = manual.setdefault(kind, {})
    samples = [row for row in market.get("samples", []) if str(row.get("id")) != sample["id"]]
    samples.append(sample)
    market["samples"] = samples
    market["asOf"] = CHECKED_AT
    market["sourceName"] = "PropertyHub 單筆掛牌"
manual_path.write_text(manual_match.group(1) + json.dumps(manual_rows, ensure_ascii=False, separators=(",", ":")) + manual_match.group(3), encoding="utf-8")

cross_path = ROOT / "dist/bangkok-market-crosschecks.js"
cross_text = cross_path.read_text(encoding="utf-8")
cross_match = re.fullmatch(r"(window\.BANGKOK_MARKET_CROSSCHECKS\s*=\s*)(\[.*\])(\s*;?\s*)", cross_text, re.S)
if not cross_match:
    raise RuntimeError("Unexpected market cross-check data format")
cross_rows = json.loads(cross_match.group(2))
cross_record = {
    "hipflatId": PROJECT_ID,
    "projectName": "Good Day Sukhumvit 93",
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub / DDproperty",
    "projectSourceUrl": PROPERTYHUB_SALE_PROJECT,
    "sale": {
        "activeListingCount": 1,
        "sourceUrl": PROPERTYHUB_SALE_PROJECT,
        "listings": [{
            "listingId": "6169503",
            "price": 4_400_000,
            "area": 52,
            "priceSqm": 84_615,
            "bedrooms": 2,
            "listedAt": "2026-10-07",
            "url": SALE_LISTING,
            "sourceName": "PropertyHub",
            "alternateSourceUrls": [DD_SALE_MIRROR],
        }],
        "note": "PropertyHub 專案頁 2026-10-07 顯示此兩房掛牌；DDproperty 有相同房型、面積與總價的交叉來源，視為同一物件，不重複計數。",
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 1,
        "sourceUrl": PROPERTYHUB_RENT_PROJECT,
        "listings": [{
            "listingId": "6268353",
            "price": 15_000,
            "area": 35,
            "priceSqm": 429,
            "bedrooms": 2,
            "listedAt": "2026-09-15",
            "url": RENT_LISTING,
            "sourceName": "PropertyHub",
            "listingStatus": "availability_unconfirmed_update_over_30d",
            "statusLabel": "更新逾 30 日，現況未確認；不作自動投報基準。",
        }],
        "note": "找到一筆兩房歷史租盤，但 PropertyHub 未提供該單筆的最新更新日，專案頁索引顯示最後刷新為 2026-09-15；超過 30 日，現況未確認。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "可核對專案身分與樓盤地址。"},
        {"sourceName": "PropertyHub 兩房出售單筆", "url": SALE_LISTING, "statusLabel": "฿4,400,000／52㎡；專案頁顯示 2026-10-07 刷新。"},
        {"sourceName": "DDproperty 出售交叉來源", "url": DD_SALE_MIRROR, "statusLabel": "相同兩房、52㎡、฿4,400,000；標示 2026-10-02 刊登，與 PropertyHub 視為同一物件。"},
        {"sourceName": "PropertyHub 兩房出租單筆", "url": RENT_LISTING, "statusLabel": "฿15,000／月、35㎡；最後刷新日期 2026-09-15，超過 30 日，現況未確認。"},
        {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE_PROJECT, "statusLabel": "專案有出售掛牌，含一筆兩房單筆來源。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT_PROJECT, "statusLabel": "專案頁有出租掛牌；未核實到 30 日內更新的兩房租盤。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "兩房購入基準為可核對的最低總價掛牌 ฿4,400,000／52㎡。目前唯一查到的兩房租盤更新逾 30 日且現況未確認，故不以此歷史租盤計算現行自動投報，也不以一房租金代替。",
}
index = next((i for i, row in enumerate(cross_rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if index is None:
    cross_rows.append(cross_record)
else:
    cross_rows[index] = cross_record
cross_path.write_text(cross_match.group(1) + json.dumps(cross_rows, ensure_ascii=False, separators=(",", ":")) + cross_match.group(3), encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": "Good Day Sukhumvit 93",
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "status": "existing_verified",
        "source": "https://propertyscout.co.th/en/bangkok/condo/good-day-sukhumvit-93/",
        "address": "149/114 Soi Sukhumvit 93, Sukhumvit Rd, Bang Chak, Phra Khanong, Bangkok 10260",
    },
    "sale": {"status": "direct_listing_cross_checked", "price": 4_400_000, "areaSqm": 52, "bedrooms": 2,
             "updated": "2026-10-07", "url": SALE_LISTING, "mirrorUrl": DD_SALE_MIRROR},
    "rent": {"status": "historical_availability_unconfirmed", "pricePerMonth": 15_000, "areaSqm": 35, "bedrooms": 2,
             "indexedRefreshDate": "2026-09-15", "url": RENT_LISTING},
    "yield": {"calculated": False, "reason": "No confirmed current two-bedroom rental sample; the only matched unit is over 30 days old."},
    "sources": [HIPFLAT, PROPERTYHUB_PROJECT, PROPERTYHUB_SALE_PROJECT, PROPERTYHUB_RENT_PROJECT, SALE_LISTING, DD_SALE_MIRROR, RENT_LISTING],
}
(ROOT / "reports/good-day-sukhumvit-93-market-samples-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Recorded one cross-checked two-bedroom sale and one dated, stale two-bedroom rent sample; automated yield remains unavailable until current rent is verified.")
