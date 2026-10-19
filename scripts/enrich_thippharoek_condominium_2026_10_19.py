"""Record a direct dated rent listing and cross-checked coordinates for Thippharoek Condominium."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3956
PROJECT_NAME = "Thippharoek Condominium"
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/thippharoek-condominium-wpnhdl"
PROPERTYHUB_RENT_PROJECT = "https://assets3.propertyhub.in.th/en/condo-for-rent/project-thippharoek-condominium--2"
PROPERTYHUB_RENT_LISTING = "https://asset-direct-v2.propertyhub.in.th/en/listings/quick-rent-thipphayaroek-condominium-pinklao-soi-borommaratchachonnani-12-near-eye-ear-nose-throat-hospital-near-central-pinklao---6288412"
DDPROPERTY_LOWEST_2BR_SALE = "https://www.ddproperty.com/en/property/thippharoek-condominium-bangkok-for-sale-500476271"
PROPERTYHUB_LOWEST_2BR_SALE = DDPROPERTY_LOWEST_2BR_SALE
THINK_OF_LIVING = "https://thinkofliving.com/project/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/12323/"


def load_js_array(filename: str, variable: str) -> tuple[str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript array format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_js_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


def upsert(rows: list[dict], record: dict) -> None:
    index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record


coordinates = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.7867527,
    "lng": 100.471813,
    "locationVerified": True,
    "sourceName": "ThinkOfLiving 專案座標",
    "sourceUrl": THINK_OF_LIVING,
    "verificationSourceUrl": HIPFLAT,
    "verificationMethod": "專案名稱、Bang Phlat 區與 Soi Borommaratchachonnani 12 相符；Hipflat 專案頁確認地址為 978 Rung Pracha Rd., Bang Bamru, Bang Phlat。",
}
prefix, rows, suffix = load_js_array("bangkok-verified-coordinates.js", "window.BANGKOK_VERIFIED_COORDINATES")
upsert(rows, coordinates)
save_js_array("bangkok-verified-coordinates.js", prefix, rows, suffix)

rent_rate = round(10_000 / 46, 2)
rent_sample = {
    "id": "6288412",
    "price": 10_000,
    "area": 46,
    "priceSqm": rent_rate,
    "beds": 1,
    "roomType": "1BR",
    "title": "Thippharoek Condominium · 1 房 · 46 ㎡ · ฿10,000/月",
    "url": PROPERTYHUB_RENT_LISTING,
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "updated": "2026-08-09",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_listing_id_room_type_area_and_rent_index",
    "listingStatus": "availability_unconfirmed_update_over_30d",
    "verificationNote": "PropertyHub 專案出租頁列出此 1 房、46㎡、฿10,000/月物件及更新時間 09/08/2026；個別房源頁核對專案名稱、房號 978/18、房型、面積、租金及可入住日期 31/08/2026。更新超過 30 日，現況未確認，不納入自動投報。",
}
rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 10_000,
    "minimum": 10_000,
    "minimumArea": 46,
    "minimumSampleUpdated": "2026-08-09",
    "averageSqm": round(rent_rate),
    "minimumSqm": rent_rate,
    "minimumSqmSampleUpdated": "2026-08-09",
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub 單筆出租掛牌（歷史參考）",
    "source": PROPERTYHUB_RENT_PROJECT,
    "minimumSourceUrl": PROPERTYHUB_RENT_LISTING,
    "minimumSqmSourceUrl": PROPERTYHUB_RENT_LISTING,
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": 10_000,
            "area": 46,
            "minimumSqm": rent_rate,
            "minimumSourceUrl": PROPERTYHUB_RENT_LISTING,
            "minimumSqmSourceUrl": PROPERTYHUB_RENT_LISTING,
        }
    },
    "samples": [rent_sample],
}
sale_sample = {
    "id": "6268605",
    "price": 3_690_000,
    "area": 104,
    "priceSqm": round(3_690_000 / 104),
    "beds": 2,
    "roomType": "2BR",
    "title": "Thippharoek Condominium · 2 房 · 104 ㎡ · ฿3,690,000（最低兩房總價）",
    "url": PROPERTYHUB_LOWEST_2BR_SALE,
    "sourceName": "DDproperty／PropertyHub 交叉核對",
    "alternateSourceUrls": ["https://propertyhub.in.th/en/condo-for-sale/project-thippharoek-condominium--2"],
    "projectName": PROJECT_NAME,
    "updated": "2026-10-07",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_listing_id_room_type_price_and_area_crosschecked_with_ddproperty",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "verificationNote": "PropertyHub 單筆頁及 DDproperty 同案頁均列 Thippharoek Condominium 兩房、104㎡、฿3,690,000；作為目前可核實的最低兩房購入基準，面積與價格取自同一物件。",
}
sale = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 3_690_000,
    "minimum": 3_690_000,
    "minimumArea": 104,
    "minimumSampleUpdated": "2026-10-07",
    "averageSqm": round(3_690_000 / 104),
    "minimumSqm": round(3_690_000 / 104),
    "minimumSqmSampleUpdated": "2026-10-07",
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub 兩房單筆出售掛牌",
    "source": "https://assets3.propertyhub.in.th/en/condo-for-sale/project-thippharoek-condominium--2",
    "minimumSourceUrl": PROPERTYHUB_LOWEST_2BR_SALE,
    "minimumSqmSourceUrl": PROPERTYHUB_LOWEST_2BR_SALE,
    "byBedroom": {"2": {"count": 1, "minimum": 3_690_000, "area": 104, "minimumArea": 104, "minimumSqm": round(3_690_000 / 104), "minimumSourceUrl": PROPERTYHUB_LOWEST_2BR_SALE, "sourceUrl": PROPERTYHUB_LOWEST_2BR_SALE}},
    "samples": [sale_sample],
}
prefix, rows, suffix = load_js_array("bangkok-manual-market-samples.js", "window.BANGKOK_MANUAL_MARKET_SAMPLES")
upsert(rows, {"hipflatId": PROJECT_ID, "name": PROJECT_NAME, "sale": sale, "rent": rent})
save_js_array("bangkok-manual-market-samples.js", prefix, rows, suffix)

crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub 單筆租盤與 Hipflat 專案資料核對",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 1,
        "sourceUrl": "https://assets3.propertyhub.in.th/en/condo-for-sale/project-thippharoek-condominium--2",
        "listings": [{"id": "6268605", "price": 3_690_000, "area": 104, "priceSqm": round(3_690_000 / 104), "bedrooms": 2, "listedAt": "2026-10-07", "url": PROPERTYHUB_LOWEST_2BR_SALE, "alternateSourceUrl": DDPROPERTY_LOWEST_2BR_SALE}],
        "note": "兩房最低價和面積均來自同一直接掛牌，並由 DDproperty 專案單筆頁交叉核對。",
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 1,
        "sourceUrl": PROPERTYHUB_RENT_PROJECT,
        "listings": [{
            "id": "6288412",
            "price": 10_000,
            "area": 46,
            "priceSqm": rent_rate,
            "bedrooms": 1,
            "listedAt": "2026-08-09",
            "url": PROPERTYHUB_RENT_LISTING,
            "listingStatus": "availability_unconfirmed_update_over_30d",
            "note": "更新超過 30 日，刊登者尚未確認現況；保留歷史參考，不作現行 ROI 基準。",
        }],
        "note": "PropertyHub 專案頁仍顯示 1 筆租盤，但更新日為 2026-08-09；以超過 30 日未更新的歷史樣本保留，不視為確認在架。",
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT_PROJECT, "statusLabel": "顯示 1 筆出租結果，房源最後更新 2026-08-09；超過 30 日，現況待確認。"},
        {"sourceName": "PropertyHub 出租單筆頁", "url": PROPERTYHUB_RENT_LISTING, "statusLabel": "核對專案、1 房、46㎡、฿10,000/月、房號 978/18；頁面列可入住日 2026-08-31，未確認目前仍在架。"},
    ],
    "yieldStatus": "not_calculated_same_bedroom_rent_stale",
    "yieldNote": "已核對兩房最低出售樣本，但唯一直接租盤是一房且超過 30 日未更新；不以舊租盤或跨房型資料重算兩房投報。",
}
prefix, rows, suffix = load_js_array("bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS")
upsert(rows, crosscheck)
save_js_array("bangkok-market-crosschecks.js", prefix, rows, suffix)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
replacements = {
    "bangkok-verified-coordinates.js?v=20261019-the-great-condo-coordinate-crosscheck": "bangkok-verified-coordinates.js?v=20261019b-thippharoek-thinkofliving-address-crosscheck",
    "bangkok-manual-market-samples.js?v=20261019-the-great-condo-rent-samples": "bangkok-manual-market-samples.js?v=20261019b-thippharoek-dated-rent-sample",
    "bangkok-market-crosschecks.js?v=20261019-the-great-condo-market-crosscheck": "bangkok-market-crosschecks.js?v=20261019b-thippharoek-stale-rent-crosscheck",
}
for old, new in replacements.items():
    if old in html:
        html = html.replace(old, new, 1)
    elif new not in html:
        raise RuntimeError(f"Expected cache tag not found: {old}")
index_path.write_text(html, encoding="utf-8")

REPORTS.mkdir(exist_ok=True)
report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "coordinates": {"lat": coordinates["lat"], "lng": coordinates["lng"], "sourceUrl": THINK_OF_LIVING, "crosscheckUrl": HIPFLAT},
    "rentSample": {"priceThbPerMonth": 10_000, "areaSqm": 46, "priceThbPerSqmMonth": rent_rate, "sourceUrl": PROPERTYHUB_RENT_LISTING, "projectIndexUrl": PROPERTYHUB_RENT_PROJECT, "updated": "2026-08-09", "status": rent_sample["listingStatus"]},
    "lowestTwoBedroomSale": {
        "priceThb": 3_690_000,
        "areaSqm": 104,
        "priceThbPerSqm": 35_481,
        "sourceUrl": PROPERTYHUB_LOWEST_2BR_SALE,
        "crosscheckUrl": DDPROPERTY_LOWEST_2BR_SALE,
        "note": "PropertyHub 與 DDproperty 搜尋結果均對應 Thippharoek Condominium 兩房 104㎡、฿3,690,000。",
    },
    "twoBedroomYield": {"calculated": False, "reason": "No current, same-bedroom rent listing is verified; the direct one-bedroom sample is stale."},
    "limitation": "The source's available-from date is 31 August 2026, not proof that the unit remains available today.",
}
(REPORTS / "thippharoek-condominium-coordinate-rent-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": [coordinates["lat"], coordinates["lng"]], "rentSample": "10000 THB / 46 sqm = 217.39 THB/sqm/month (stale; excluded from yield)", "twoBedroomYield": "not recalculated without current 2BR rent"}, ensure_ascii=True))
