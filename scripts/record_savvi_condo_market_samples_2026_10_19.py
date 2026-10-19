"""Record source-linked Savvi Condo market and location evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-10-19"
HIPFLAT_ID = 3320
PROJECT_NAME = "Savvi Condo"
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/savvi-condo-zbpnsr"
PH_PROJECT = "https://propertyhub.in.th/en/projects/savvi-phahol-ari"
PH_SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-savvi-phahol-ari"
PH_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-savvi-phahol-ari"
SALE_1BR = "https://propertyhub.in.th/en/listings/for-sale-condo-savvi-phahol-ari-bts-ari-sam-sen-nai-phaya-thai-bangkok-cx-140337-live-chat-with-us-add-line-connexproperty--b1f509a8---5680452"
SALE_2BR_MIN = "https://propertyhub.in.th/en/listings/selling-a-burden-special-price-condo-good-location-savvi-phahol-ari-md-25044869--b36d09f7---5729680"
SALE_2BR_OTHER = "https://propertyhub.in.th/en/listings/savvi-phahol-ari-2-bedrooms-for-sale---3769913"
RENT_1BR = "https://propertyhub.in.th/en/listings/condo-for-rent-at-savvi-phahol-ari-j6904001---6015260"
COORD_URL = "https://maps.app.goo.gl/6NmnzR7ZzUotZFNr5"
COORD_CROSSCHECK = "https://www.ddproperty.com/en/project/11748-savvi-phahol-ari"


def read_rows(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"\s*window\.{symbol}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Could not parse {symbol} from {path}")
    return json.loads(match.group(1))


def write_rows(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_samples = [
    {
        "id": "5680452", "price": 4_500_000, "area": 35, "priceSqm": 128_571,
        "beds": 1, "roomType": "1BR", "title": "Savvi Phahol-Ari，1 房，35 ㎡，฿4,500,000",
        "url": SALE_1BR, "sourceName": "PropertyHub", "projectName": "Savvi Phahol - Ari",
        "updated": "2026-10-06", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id_on_project_sale_index",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
    {
        "id": "5729680", "price": 6_350_000, "area": 46, "priceSqm": 138_043,
        "beds": 2, "roomType": "2BR", "title": "Savvi Phahol-Ari，2 房，46 ㎡，฿6,350,000（兩房最低總價）",
        "url": SALE_2BR_MIN, "sourceName": "PropertyHub", "projectName": "Savvi Phahol - Ari",
        "updated": "2026-10-06", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_direct_listing_and_project_index_refresh",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
    {
        "id": "3769913", "price": 11_590_000, "area": 67.06, "priceSqm": 172_830,
        "beds": 2, "roomType": "2BR", "title": "Savvi Phahol-Ari，2 房，67.06 ㎡，฿11,590,000",
        "url": SALE_2BR_OTHER, "sourceName": "PropertyHub", "projectName": "Savvi Phahol - Ari",
        "updated": "2026-09-22", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_direct_listing_and_project_index_refresh",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
]
rent_samples = [
    {
        "id": "6015260", "price": 18_000, "area": 30, "priceSqm": 600,
        "beds": 1, "roomType": "1BR", "title": "Savvi Phahol-Ari，1 房，30 ㎡，฿18,000/月",
        "url": RENT_1BR, "sourceName": "PropertyHub", "projectName": "Savvi Phahol - Ari",
        "updated": "2026-10-06", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
]

coordinates_path = ROOT / "dist/bangkok-verified-coordinates.js"
coordinates = read_rows(coordinates_path, "BANGKOK_VERIFIED_COORDINATES")
coordinate = {
    "hipflatId": HIPFLAT_ID, "name": PROJECT_NAME, "lat": 13.7783517, "lng": 100.5465974,
    "locationVerified": True, "sourceName": "PropertyHub 房源的 Google Maps 專案點位",
    "sourceUrl": COORD_URL, "verificationSourceUrl": COORD_CROSSCHECK,
    "verificationMethod": "Google Maps 短連結解析至 SAVVI Phahol - Ari 專案點；Hipflat 完整地址與 PropertyHub 專案別名及 DDproperty 地址相符",
}
coordinates = [row for row in coordinates if int(row["hipflatId"]) != HIPFLAT_ID]
coordinates.append(coordinate)
write_rows(coordinates_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

sale_rates = [row["price"] / row["area"] for row in sale_samples]
rent_rates = [row["price"] / row["area"] for row in rent_samples]
market_record = {
    "hipflatId": HIPFLAT_ID,
    "name": PROJECT_NAME,
    "completedYear": 2017,
    "completedYearSourceUrl": PH_PROJECT,
    "fee": {
        "rate": 60, "status": "public",
        "note": "PropertyHub 專案資料公布管理費 ฿60/㎡/月；實際收費請向管委會確認。",
        "source": PH_PROJECT,
    },
    "sale": {
        "count": 14, "observedCount": len(sale_samples), "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in sale_samples) / len(sale_samples)),
        "minimum": 4_500_000, "minimumArea": 35,
        "averageSqm": round(sum(sale_rates) / len(sale_rates)), "minimumSqm": round(min(sale_rates)),
        "asOf": AS_OF, "sourceName": "PropertyHub 單筆出售掛牌",
        "source": PH_SALE_PROJECT, "samples": sale_samples,
        "byBedroom": {
            "1": {"beds": 1, "minimum": 4_500_000, "minimumArea": 35, "minimumSqm": 128_571, "minimumSourceUrl": SALE_1BR, "average": 4_500_000, "averageSqm": 128_571, "sampleCount": 1},
            "2": {"beds": 2, "minimum": 6_350_000, "minimumArea": 46, "minimumSqm": 138_043, "minimumSourceUrl": SALE_2BR_MIN, "average": 8_970_000, "averageSqm": round((6_350_000 / 46 + 11_590_000 / 67.06) / 2), "sampleCount": 2},
        },
    },
    "rent": {
        "count": 4, "observedCount": len(rent_samples), "countKind": "manual_verified_listing",
        "average": 18_000, "minimum": 18_000, "minimumArea": 30,
        "averageSqm": round(sum(rent_rates) / len(rent_rates)), "minimumSqm": round(min(rent_rates)),
        "asOf": AS_OF, "sourceName": "PropertyHub 單筆出租掛牌",
        "source": PH_RENT_PROJECT, "samples": rent_samples,
        "byBedroom": {"1": {"beds": 1, "minimum": 18_000, "area": 30, "minimumSqm": 600, "minimumSourceUrl": RENT_1BR, "average": 18_000, "averageSqm": 600, "sampleCount": 1}},
    },
}
markets_path = ROOT / "dist/bangkok-manual-market-samples.js"
markets = read_rows(markets_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
markets = [row for row in markets if int(row["hipflatId"]) != HIPFLAT_ID]
markets.append(market_record)
write_rows(markets_path, "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

crosschecks_path = ROOT / "dist/bangkok-market-crosschecks.js"
crosschecks = read_rows(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": HIPFLAT_ID, "projectName": "Savvi Condo (PropertyHub / DDproperty alias: SAVVI Phahol-Ari)",
    "asOf": AS_OF, "sourceName": "Hipflat / PropertyHub / DDproperty 多來源核對",
    "projectSourceUrl": HIPFLAT_PROJECT,
    "sale": {
        "activeListingCount": 14, "sourceUrl": PH_SALE_PROJECT,
        "listings": [{"id": row["id"], "bedrooms": row["beds"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"]} for row in sale_samples],
        "note": "PropertyHub 專案頁及單筆頁核對 14 筆在架出售掛牌；本次列出 3 筆可追溯單筆。兩房最低總價為 ฿6,350,000，面積 46㎡，採同一掛牌來源。",
    },
    "rent": {
        "activeListingCount": 4, "sourceUrl": PH_RENT_PROJECT,
        "listings": [{"id": row["id"], "bedrooms": row["beds"], "roomType": row["roomType"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"]} for row in rent_samples],
        "note": "目前可核對的同案租盤為一房 30㎡、฿18,000/月；沒有同案兩房出租掛牌可供兩房投報配對。Savvi Phahol 2 為不同 Hipflat 專案，未混入。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案地址及完工資料", "url": HIPFLAT_PROJECT, "statusLabel": "Savvi Condo，35 Soi Phahon Yothin 2，2017 年 1 月完工；8 層。"},
        {"sourceName": "PropertyHub 專案資料／管理費", "url": PH_PROJECT, "statusLabel": "別名 Savvi Phahol-Ari；66 戶、8 層、2017 年完工，公共管理費 ฿60/㎡/月。"},
        {"sourceName": "兩房最低出售掛牌", "url": SALE_2BR_MIN, "statusLabel": "PropertyHub 房源 5729680：兩房、46㎡、฿6,350,000；投報購入基準使用此最低兩房總價及同一房源面積。"},
        {"sourceName": "另一筆兩房出售掛牌", "url": SALE_2BR_OTHER, "statusLabel": "PropertyHub 房源 3769913：兩房、67.06㎡、฿11,590,000；作為同案比較樣本。"},
        {"sourceName": "一房最低出售掛牌", "url": SALE_1BR, "statusLabel": "PropertyHub 房源 5680452：一房、35㎡、฿4,500,000；不會蓋過兩房投報的購入基準。"},
        {"sourceName": "目前可核對的出租掛牌", "url": RENT_1BR, "statusLabel": "PropertyHub 房源 6015260：一房、30㎡、฿18,000/月；因沒有同案兩房租金，兩房投報顯示待補。"},
        {"sourceName": "座標來源（Google Maps）", "url": COORD_URL, "statusLabel": "PropertyHub 專案房源的 Google Maps 短連結指向 SAVVI Phahol - Ari，解析座標 13.7783517, 100.5465974。"},
        {"sourceName": "名稱／地址交叉核對", "url": COORD_CROSSCHECK, "statusLabel": "DDproperty 專案頁確認 SAVVI Phahol-Ari、Soi Phahon Yothin 2、2017 年、66 戶及 8 層；排除 2021 年的 Savvi Phahol 2。"},
    ],
    "yieldStatus": "unavailable_same_bedroom_rent_missing",
    "yieldNote": "預設採兩房最低售價 ฿6,350,000，面積 46㎡，來源連結指向同一個最低價房源。尚無可核實的同案兩房租盤，因此不將一房租金或相鄰 Savvi Phahol 2 的租金混入兩房投報。",
}
crosschecks = [row for row in crosschecks if int(row["hipflatId"]) != HIPFLAT_ID]
crosschecks.append(crosscheck)
write_rows(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": HIPFLAT_ID, "projectName": PROJECT_NAME, "asOf": AS_OF,
    "coordinate": coordinate, "saleSamples": sale_samples, "rentSamples": rent_samples,
    "yield": {"status": crosscheck["yieldStatus"], "note": crosscheck["yieldNote"], "twoBedroomPurchasePriceTHB": 6_350_000, "twoBedroomAreaSqm": 46, "twoBedroomSaleSourceUrl": SALE_2BR_MIN},
    "sources": crosscheck["availabilitySources"],
    "caveats": ["掛牌在架狀態尚未向仲介確認。", "未找到同案可核實的兩房出租掛牌，兩房投報保持待補。", "Savvi Phahol 2 是另一個 2021 年建案，沒有合併其售租資料。"],
}
(ROOT / "reports/savvi-condo-market-samples-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": HIPFLAT_ID, "coordinatesVerified": True, "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "twoBedroomLowestTHB": 6_350_000, "twoBedroomAreaSqm": 46, "yield": "waiting_for_same_project_two_bedroom_rent"}, ensure_ascii=False))
