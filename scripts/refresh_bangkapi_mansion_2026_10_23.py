"""Refresh Bangkapi Mansion rental evidence after checking exact-project pages."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANUAL_PATH = DIST / "bangkok-manual-market-samples.js"
CROSSCHECK_PATH = DIST / "bangkok-market-crosschecks.js"
PROJECT_URL = "https://propertyhub.in.th/en/projects/bangkapi-mansion"
SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-bangkapi-mansion"
RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-bangkapi-mansion"
RENT_LISTING_URL = "https://propertyhub.in.th/en/listings/bangkapi-mansion-4-bedrooms-for-rent---3771245"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/bangkapi-mansion"


def load_js_array(path: Path, variable: str):
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(variable)}=(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Cannot parse {path.name}:{variable}")
    return text, json.loads(match.group(1))


def save_js_array(path: Path, variable: str, rows):
    path.write_text(
        f"window.{variable}={json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


manual_text, manual_rows = load_js_array(MANUAL_PATH, "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_row = next((row for row in manual_rows if int(row["hipflatId"]) == 3082), None)
if manual_row is None:
    manual_row = {"hipflatId": 3082, "name": "Bangkapi Mansion"}
    manual_rows.append(manual_row)

rent_sample = {
    "id": "3771245",
    "kind": "rent",
    "beds": 4,
    "roomType": "FOUR_BED_ROOM",
    "price": 110000,
    "area": 380,
    "priceSqm": 289.47,
    "title": "Bangkapi Mansion 4 bedrooms, for rent",
    "url": RENT_LISTING_URL,
    "updated": "2026-10-16T01:00:00+07:00",
    "listingStatus": "active_as_listed_unconfirmed",
}
manual_row["replaceRent"] = True
manual_row["rent"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 110000,
    "minimum": 110000,
    "minimumArea": 380,
    "minimumSampleUpdated": rent_sample["updated"],
    "averageSqm": 289.47,
    "minimumSqm": 289.47,
    "minimumSqmSampleUpdated": rent_sample["updated"],
    "asOf": "2026-10-23",
    "sourceName": "PropertyHub 精確專案及單筆租盤",
    "source": RENT_URL,
    "minimumSourceUrl": RENT_LISTING_URL,
    "minimumSqmSourceUrl": RENT_LISTING_URL,
    "byBedroom": {
        "4": {
            "count": 1,
            "minimum": 110000,
            "minimumArea": 380,
            "area": 380,
            "priceSqm": 289.47,
            "minimumSqm": 289.47,
            "sourceUrl": RENT_LISTING_URL,
            "minimumSourceUrl": RENT_LISTING_URL,
            "minimumSqmSourceUrl": RENT_LISTING_URL,
        }
    },
    "samples": [rent_sample],
}

save_js_array(MANUAL_PATH, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

crosscheck_text, crosschecks = load_js_array(CROSSCHECK_PATH, "BANGKOK_MARKET_CROSSCHECKS")
record = {
    "hipflatId": 3082,
    "projectName": "Bangkapi Mansion",
    "asOf": "2026-10-23",
    "sourceName": "PropertyHub / Hipflat / KaiBaanThai 專案及單筆掛牌核對",
    "projectSourceUrl": HIPFLAT_URL,
    "sale": {
        "activeListingCount": 0,
        "sourceUrl": SALE_URL,
        "note": "PropertyHub 精確專案出售頁顯示 0 筆；未以附近專案售價代替。",
    },
    "rent": {
        "activeListingCount": 1,
        "displayedResultCount": 6,
        "sourceUrl": RENT_URL,
        "listings": [
            {
                "id": "3771245",
                "price": 110000,
                "area": 380,
                "priceSqm": 289.47,
                "bedrooms": 4,
                "url": RENT_LISTING_URL,
                "updated": "2026-10-16",
                "statusLabel": "PropertyHub 精確專案頁最新刷新日期 2026-10-16；單筆頁確認 Condo、4 房、380㎡、฿110,000/月，單筆頁自身更新日期未提供。列為刊登中待聯絡確認。",
            }
        ],
        "excludedListings": [
            {
                "price": 40000,
                "area": 190,
                "bedrooms": 2,
                "url": RENT_URL,
                "statusLabel": "PropertyHub 專案頁兩房卡片最後刷新 2025-08-19；過舊，不作現行租金樣本。",
            },
            {
                "price": 60000,
                "area": 190,
                "bedrooms": 2,
                "url": "https://www.kaibaanthai.com/en/property-rent/2-bedroom-condo-for-rent-at-bangkapi-mansion-in-khlong-toei-bangkok-u1079820",
                "statusLabel": "KaiBaanThai/FazWaz 鏡像頁列 2023-08-16 刊登、更新 4 個月前、入住狀態 Check Availability；只作歷史線索，不計現行樣本。",
            },
        ],
        "note": "PropertyHub 專案頁顯示 6 筆出租，4 房掛牌於 2026-10-16 刷新。兩房最低價卡片最後刷新於 2025-08-19，未納入。相同項目跨站可能是鏡像，不重複計數。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT_URL, "statusLabel": "作為 3,555 個曼谷專案目錄及專案識別來源。"},
        {"sourceName": "PropertyHub 專案資訊與租盤頁", "url": PROJECT_URL, "statusLabel": "本次核對列 6 筆出租、0 筆出售；專案資料列 1998 年完工、21 層、52 戶；最新四房租卡於 2026-10-16 刷新。"},
        {"sourceName": "PropertyHub 出售頁", "url": SALE_URL, "statusLabel": "精確專案頁顯示 0 筆出售。"},
        {"sourceName": "PropertyHub 出租單筆", "url": RENT_LISTING_URL, "statusLabel": "4 房、380㎡、฿110,000/月；單筆頁自身更新日未提供，專案頁刷新日 2026-10-16。"},
        {"sourceName": "KaiBaanThai/FazWaz 兩房租盤鏡像（排除）", "url": "https://www.kaibaanthai.com/en/property-rent/2-bedroom-condo-for-rent-at-bangkapi-mansion-in-khlong-toei-bangkok-u1079820", "statusLabel": "2 房、190㎡、฿60,000/月；列 2023-08-16 刊登、4 個月前更新，並顯示 Check Availability。"},
    ],
    "yieldStatus": "no_current_sale_listing",
    "yieldNote": "有一筆可追溯的四房出租候選，但精確專案出售頁為零；無購入價基準，不計投報。",
}
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != 3082]
crosschecks.append(record)
save_js_array(CROSSCHECK_PATH, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report_dir = ROOT / "reports"
report_dir.mkdir(exist_ok=True)
(report_dir / "bangkapi-mansion-market-check-2026-10-23.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": 3082, "currentRentSamples": 1, "rentTHB": 110000, "rentAreaSqm": 380, "saleSamples": 0, "yield": "not calculated"}, ensure_ascii=False))
