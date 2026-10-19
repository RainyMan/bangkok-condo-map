"""Add current, directly linked two-bedroom sale and rent evidence for Hipflat 3797."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKED = "2026-10-19"
PROJECT_ID = 3797
NAME = "Supalai Park Ekamai - Thonglor"
SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-supalai-park-ekkamai-thonglor"
RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-supalai-park-ekkamai-thonglor"
SALE_URL = "https://propertyhub.in.th/en/listings/30th-floor-2-br-supalai-park-ekamai-thonglor-near-arl-ramkhamhaeng-id-3240351---6341897"
RENT_URL = "https://propertyhub.in.th/en/listings/for-rent-condo-supalai-park-ekkamai-thonglor-building-1-floor-17-2-bed-room-room-size-82-sqm--add9092e---6223334"


def read_array(filename: str, symbol: str):
    path = DIST / filename
    match = re.fullmatch(rf"(window\.{symbol}\s*=\s*)(\[.*\])(\s*;?\s*)", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Unexpected {symbol} format")
    return path, match, json.loads(match.group(2))


def write_array(path: Path, match, rows):
    path.write_text(match.group(1) + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + match.group(3), encoding="utf-8")


sale = {
    "id": "6341897",
    "price": 4_990_000,
    "area": 82,
    "priceSqm": 60_854,
    "beds": 2,
    "roomType": "2BR",
    "title": "Supalai Park Ekkamai - Thonglor · 2 房 · 82 ㎡ · ฿4,990,000",
    "url": SALE_URL,
    "sourceName": "PropertyHub",
    "projectName": NAME,
    "updated": "2026-10-18",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_room_type_price_area_and_individual_listing_detail",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "statusNote": "PropertyHub 專案清單顯示 2026-10-18 更新；單筆頁未提供 Last Update 日期，現況仍待聯絡確認。",
}
rent = {
    "id": "6223334",
    "price": 25_000,
    "area": 82,
    "priceSqm": 305,
    "beds": 2,
    "roomType": "2BR",
    "title": "Supalai Park Ekkamai - Thonglor · 2 房 · 82 ㎡ · ฿25,000/月",
    "url": RENT_URL,
    "sourceName": "PropertyHub",
    "projectName": NAME,
    "updated": "2026-10-18",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_room_type_price_area_and_individual_listing_detail",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "statusNote": "PropertyHub 專案清單顯示 2026-10-18 更新；單筆頁確認 2 房、82㎡、月租 ฿25,000，最短一年合約；現況仍待聯絡確認。",
}

manual_path, manual_match, manual_rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if record is None:
    record = {"hipflatId": PROJECT_ID, "name": NAME}
    manual_rows.append(record)
record["asOf"] = CHECKED
for kind, sample in (("sale", sale), ("rent", rent)):
    market = record.setdefault(kind, {})
    samples = [row for row in market.get("samples", []) if str(row.get("id")) != sample["id"]]
    samples.append(sample)
    market.update({"samples": samples, "asOf": CHECKED, "sourceName": "PropertyHub 單筆掛牌"})
write_array(manual_path, manual_match, manual_rows)

cross_path, cross_match, cross_rows = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_record = {
    "hipflatId": PROJECT_ID,
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "PropertyHub 單筆掛牌核對",
    "projectSourceUrl": SALE_PROJECT,
    "sale": {
        "activeListingCount": 1,
        "sourceUrl": SALE_PROJECT,
        "listings": [{
            "listingId": "6341897", "price": sale["price"], "area": sale["area"],
            "priceSqm": sale["priceSqm"], "bedrooms": 2, "listedAt": sale["updated"],
            "url": SALE_URL, "sourceName": "PropertyHub", "listingStatus": sale["listingStatus"],
        }],
        "note": "專案清單顯示 2026-10-18 更新；已開啟單筆頁核對 2 房、82㎡、฿4,990,000。單筆頁未顯示自身更新日，仍列為現況待確認樣本。",
    },
    "rent": {
        "activeListingCount": 1,
        "sourceUrl": RENT_PROJECT,
        "listings": [{
            "listingId": "6223334", "price": rent["price"], "area": rent["area"],
            "priceSqm": rent["priceSqm"], "bedrooms": 2, "listedAt": rent["updated"],
            "url": RENT_URL, "sourceName": "PropertyHub", "listingStatus": rent["listingStatus"],
        }],
        "note": "專案清單顯示 2026-10-18 更新；單筆頁確認 2 房、82㎡、฿25,000/月和一年最低租期。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": "https://www.hipflat.co.th/en/projects/supalai-park-ekamai-thonglor-c3eel3h41lu8nan93200e4h9nl1ch4h4", "statusLabel": "核對專案名稱；地圖既有座標來源為 PropertyScout 專案頁。"},
        {"sourceName": "PropertyHub 出售單筆", "url": SALE_URL, "statusLabel": "2 房，82㎡，฿4,990,000；專案清單 2026-10-18 更新。"},
        {"sourceName": "PropertyHub 出租單筆", "url": RENT_URL, "statusLabel": "2 房，82㎡，฿25,000/月；一年最低租期，專案清單 2026-10-18 更新。"},
        {"sourceName": "PropertyHub 出售專案清單", "url": SALE_PROJECT, "statusLabel": "專案清單近期有更新掛牌；房型、面積和價格以單筆連結為準。"},
        {"sourceName": "PropertyHub 出租專案清單", "url": RENT_PROJECT, "statusLabel": "專案清單近期有更新掛牌；房型、面積和價格以單筆連結為準。"},
    ],
    "yieldStatus": "calculated_with_recent_linked_samples",
    "yieldNote": "兩房出售樣本 ฿4,990,000／82㎡；兩房月租樣本 ฿25,000／82㎡。以租金單價乘出售樣本面積估算月租 ฿25,000；預設扣一個月仲介費、未扣管理費（未核實），年租投報約 5.51%。單筆房源目前仍待聯絡確認可租售狀態。",
}
index = next((i for i, row in enumerate(cross_rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if index is None:
    cross_rows.append(cross_record)
else:
    cross_rows[index] = cross_record
write_array(cross_path, cross_match, cross_rows)

roi = ((rent["price"] / rent["area"] * sale["area"] * 11) / sale["price"]) * 100
report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "coordinates": {"status": "existing_verified", "source": "https://propertyscout.co.th/en/bangkok/condo/supalai-park-ekamai-thonglor/", "latitude": 13.742949, "longitude": 100.588961},
    "sale": {"price": sale["price"], "areaSqm": sale["area"], "bedrooms": 2, "listingId": sale["id"], "feedUpdated": sale["updated"], "url": SALE_URL},
    "rent": {"pricePerMonth": rent["price"], "areaSqm": rent["area"], "bedrooms": 2, "listingId": rent["id"], "minimumContractYears": 1, "feedUpdated": rent["updated"], "url": RENT_URL},
    "yield": {"formula": "(monthly rent rate × lowest 2BR sale area × 11 months) ÷ lowest linked 2BR sale price", "beforeCommonFeePercent": round(roi, 2), "commonFeeDeducted": False, "commonFeeReason": "未核實管理費", "availability": "近期專案清單更新；單筆頁未標示更新日，仍需聯絡確認實際可租售。"},
    "scopeNote": "฿4,990,000 是此次可直達並核對之兩房出售樣本最低總價，不宣稱為所有在架掛牌的絕對最低價。",
    "sources": [SALE_PROJECT, RENT_PROJECT, SALE_URL, RENT_URL],
}
(ROOT / "reports/supalai-park-ekkamai-thonglor-current-2br-samples-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Recorded direct 2BR sale and rent items for Hipflat {PROJECT_ID}; estimated yield after one agent month: {roi:.2f}% before common fee.")
