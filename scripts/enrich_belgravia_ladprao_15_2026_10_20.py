"""Add verified location and current listing evidence for Hipflat project 3134."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
ID = 3134
NAME = "The Belgravia Ratchada-Ladprao 15"
FULL_NAME = "The Belgravia @ Ratchada-Ladprao 15"
CHECKED = "2026-10-20"
LAT, LNG = 13.8105112, 100.5738322
MAP_URL = "https://www.google.com/maps/search/?api=1&query=13.8105112%2C100.5738322"
PH_PROJECT = "https://propertyhub.in.th/en/projects/the-belgravia-ladprao-15"
PH_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-the-belgravia-ladprao-15"
PH_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-the-belgravia-ladprao-15"
DD_PROJECT = "https://www.ddproperty.com/en/project/6719-the-belgravia-ratchada-ladprao-15"
DD_SALE = "https://www.ddproperty.com/property/the-belgravia-ratchada-ladprao-15-%E0%B9%80%E0%B8%94%E0%B8%AD%E0%B8%B0-%E0%B9%80%E0%B8%9A%E0%B8%A5%E0%B8%81%E0%B8%A3%E0%B8%B2%E0%B9%80%E0%B8%A7%E0%B8%B5%E0%B8%A2-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-15-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B8%82%E0%B8%B2%E0%B8%A2-500348168"
DD_RENT = "https://www.ddproperty.com/en/property/the-belgravia-ratchada-ladprao-15-bangkok-for-rent-500590567"
PH_SALE_MIN = "https://asset-direct-v2.propertyhub.in.th/en/listings/for-sale-condo-the-belgravia-ratchada-ladprao-15-chomphon-chatuchak-bangkok-cx-156823-live-chat-with-us-add-line-connexproperty---6287017"
PH_RENT_2BR_OLD = "https://propertyhub.in.th/en/listings/2-br-condo-at-the-belgravia-ratchada-ladprao-15-near-mrt-ratchadaphisek-id-2362413---5509698"


def load(filename: str, symbol: str) -> tuple[Path, str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(\s*window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot parse {symbol} from {filename}")
    return path, match.group(1), json.loads(match.group(2)), match.group(3)


def save(path: Path, prefix: str, rows: list[dict], suffix: str) -> None:
    path.write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix, encoding="utf-8")


def upsert(rows: list[dict], key: str, value: dict) -> dict:
    row = next((item for item in rows if int(item.get(key, -1)) == ID), None)
    if row is None:
        rows.append(value)
        return value
    row.update(value)
    return row


# The Google Maps short link embedded in the matching sale listing resolves to
# the named building itself at 13.8105112, 100.5738322. DDproperty independently
# confirms the Lat Phrao 15 Yaek 2-4 project address and building particulars.
for filename, symbol in [
    ("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE"),
    ("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"),
]:
    path, prefix, rows, suffix = load(filename, symbol)
    project = next((row for row in rows if int(row.get("id", -1)) == ID), None)
    if project is None:
        raise RuntimeError(f"Hipflat project {ID} missing from {filename}")
    project.update({
        "lat": LAT, "lng": LNG,
        "address": "36 Soi Lat Phrao 15 Yaek 2-4, Chom Phon, Chatuchak, Bangkok 10900, Thailand",
        "completedYear": 2020, "completedYearSourceUrl": DD_PROJECT,
        "floors": 8, "units": 185, "beds": 1,
        "fee": {"rate": 45, "source": PH_PROJECT, "note": "PropertyHub 公開管理費 ฿45/㎡/月；實際收費請向管委會確認。"},
        "currentProjectName": FULL_NAME,
        "nameAliases": [FULL_NAME, "The Belgravia Ladprao 15", "The Belgravia @ Ratchada - Ladprao 15"],
        "propertyHubProjectUrl": PH_PROJECT,
        "propertyHubSaleUrl": PH_SALE, "propertyHubRentUrl": PH_RENT,
        "locationVerified": True, "locationSourceUrl": MAP_URL,
        "locationVerificationSourceUrl": DD_PROJECT,
    })
    if filename == "bangkok-catalogue.js":
        project.update({
            "marketDataStatus": "verified_coordinates_current_sale_rent_samples_and_yield",
            "dataCompleteness": {**project.get("dataCompleteness", {}), "coordinates": True, "saleSample": True, "rentSample": True, "yield": True},
            "sourceDescription": "Google Maps 點位由含 GPS 短連結的 PropertyHub 個別房源解析；DDproperty 專案頁交叉核對地址、樓層、戶數與完工年。售租均保留個別掛牌連結。",
        })
    save(path, prefix, rows, suffix)

coord_path, coord_prefix, coordinates, coord_suffix = load("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
upsert(coordinates, "hipflatId", {
    "hipflatId": ID, "name": NAME, "lat": LAT, "lng": LNG,
    "locationVerified": True,
    "sourceName": "PropertyHub 個別房源 Google Maps 點位",
    "sourceUrl": MAP_URL, "verificationSourceUrl": DD_PROJECT,
    "corroborationSourceUrl": PH_SALE_MIN,
    "verificationMethod": "PropertyHub 房源 CX-156823 的 Google Maps 短連結解析至 The Belgravia Condo Ratchada Ladprao15，13.8105112,100.5738322。DDproperty 確認同一案位於 Soi Lat Phrao 15 Yaek 2-4；PropertyHub 房源亦列出同案名稱及地址。",
})
save(coord_path, coord_prefix, coordinates, coord_suffix)

sale_samples = [
    {"id": "500348168", "price": 2_190_000, "area": 36, "priceSqm": 60_833.33, "beds": 1, "roomType": "1BR", "title": "The Belgravia @ Ratchada-Ladprao 15，1 房，36 ㎡，฿2,190,000", "url": DD_SALE, "sourceName": "DDproperty", "projectName": FULL_NAME, "updated": "2026-10-02", "checkedAt": CHECKED, "matchedBy": "exact_project_name_and_individual_listing_id_500348168", "listingStatus": "availability_unconfirmed_update_under_30d", "verificationNote": "DDproperty 專案出售頁於 2026-10-02 更新此一房掛牌；個別物件 ID 500348168，฿2,190,000、頁面顯示 36㎡。PropertyHub 交叉刊登相同 CX-156823 房源為 35.78㎡。"},
    {"id": "6287017", "price": 2_190_000, "area": 35.78, "priceSqm": round(2_190_000 / 35.78, 2), "beds": 1, "roomType": "1BR", "title": "For Sale Condo CX-156823，1 房，35.78 ㎡，฿2,190,000", "url": PH_SALE_MIN, "sourceName": "PropertyHub", "projectName": FULL_NAME, "updated": "2026-09-14", "checkedAt": CHECKED, "matchedBy": "same_cross_posted_CX_listing_id_as_DDproperty_500348168", "listingStatus": "availability_unconfirmed_update_over_30d", "verificationNote": "PropertyHub 相同 CX-156823 跨刊登房源提供 35.78㎡精確面積；此頁較舊，與 DDproperty 2026-10-02 專案掛牌交叉核對，不能視為另一個獨立物件。"},
    {"id": "6005777", "price": 3_000_000, "area": 29.29, "priceSqm": round(3_000_000 / 29.29, 2), "beds": 1, "roomType": "1BR", "title": "The Belgravia @ Ratchada-Ladprao 15，1 房，29.29 ㎡，฿3,000,000", "url": "https://propertyhub.in.th/en/listings/a033854-the-belgravia-ratchada-ladprao-15---6005777", "sourceName": "PropertyHub", "projectName": FULL_NAME, "updated": "2026-10-17", "checkedAt": CHECKED, "matchedBy": "exact_project_name_and_individual_listing_detail", "listingStatus": "availability_unconfirmed_update_under_30d"},
]
rent_samples = [
    {"id": "500590567", "price": 13_000, "area": 28.27, "priceSqm": round(13_000 / 28.27, 2), "beds": 1, "roomType": "1BR", "title": "The Belgravia @ Ratchada-Ladprao 15，1 房，28.27 ㎡，฿13,000/月", "url": DD_RENT, "sourceName": "DDproperty", "projectName": FULL_NAME, "updated": "2026-09-25", "checkedAt": CHECKED, "matchedBy": "exact_project_name_and_individual_listing_id_500590567", "listingStatus": "availability_unconfirmed_update_under_30d", "verificationNote": "DDproperty 個別出租頁列 1 房、28.27㎡、฿13,000/月，並列 2026-09-25 刊登日期。"},
    {"id": "5509698", "price": 20_000, "area": 36.1, "priceSqm": round(20_000 / 36.1, 2), "beds": 2, "roomType": "2BR", "title": "The Belgravia @ Ratchada-Ladprao 15，2 房，36.1 ㎡，฿20,000/月", "url": PH_RENT_2BR_OLD, "sourceName": "PropertyHub", "projectName": FULL_NAME, "updated": "2026-09-14", "checkedAt": CHECKED, "matchedBy": "exact_project_name_and_individual_listing_detail", "listingStatus": "availability_unconfirmed_update_over_30d", "verificationNote": "保留作歷史參考；2026-10-20 時已超過 30 日未刷新，不納入現行投報率。"},
]

sale_current = [row for row in sale_samples if "over_30d" not in row["listingStatus"]]
rent_current = [row for row in rent_samples if "over_30d" not in row["listingStatus"]]
sale_min = min(sale_current, key=lambda row: row["price"])
rent_rate_min = min(rent_current, key=lambda row: row["price"] / row["area"])
projected_monthly_rent = round(rent_rate_min["price"] / rent_rate_min["area"] * sale_min["area"])
management_fee_year = 45 * sale_min["area"] * 12
net_yield = round((projected_monthly_rent * 11 - management_fee_year) / sale_min["price"] * 100, 2)

market_path, market_prefix, markets, market_suffix = load("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
existing = next((row for row in markets if int(row.get("hipflatId", -1)) == ID), None)
if existing is None:
    existing = {"hipflatId": ID, "name": NAME}
    markets.append(existing)
sale_rates = [row["price"] / row["area"] for row in sale_current]
rent_rates = [row["price"] / row["area"] for row in rent_current]
existing.update({
    "asOf": CHECKED, "replaceSale": True, "replaceRent": True,
    "fee": {"rate": 45, "status": "public", "note": "PropertyHub 專案資料公布管理費 ฿45/㎡/月；實際收費依管委會確認。", "source": PH_PROJECT},
    "sale": {
        "count": 9, "observedCount": len(sale_current), "countKind": "project_page_count_and_manual_verified_listing",
        "average": round(sum(row["price"] for row in sale_current) / len(sale_current)),
        "minimum": sale_min["price"], "minimumArea": sale_min["area"],
        "averageSqm": round(sum(sale_rates) / len(sale_rates)), "minimumSqm": round(min(sale_rates)),
        "minimumSourceUrl": sale_min["url"], "minimumSqmSourceUrl": DD_SALE,
        "minimumSampleUpdated": "2026-10-02", "minimumSqmSampleUpdated": "2026-10-02",
        "asOf": CHECKED, "sourceName": "PropertyHub 專案掛牌及 DDproperty 個別掛牌交叉核對",
        "source": PH_SALE, "samples": sale_samples,
        "byBedroom": {"1": {"beds": 1, "minimum": sale_min["price"], "minimumArea": sale_min["area"], "area": sale_min["area"], "minimumSqm": round(min(sale_rates)), "minimumSourceUrl": DD_SALE, "minimumSqmSourceUrl": DD_SALE, "average": sale_min["price"], "averageSqm": round(min(sale_rates)), "sampleCount": 1}},
    },
    "rent": {
        "count": 17, "observedCount": len(rent_current), "countKind": "project_page_count_and_manual_verified_listing",
        "average": rent_rate_min["price"], "minimum": rent_rate_min["price"], "minimumArea": rent_rate_min["area"],
        "averageSqm": round(min(rent_rates)), "minimumSqm": round(min(rent_rates)),
        "minimumSourceUrl": DD_RENT, "minimumSqmSourceUrl": DD_RENT,
        "minimumSampleUpdated": "2026-09-25", "minimumSqmSampleUpdated": "2026-09-25",
        "asOf": CHECKED, "sourceName": "DDproperty 個別出租掛牌",
        "source": PH_RENT, "samples": rent_samples,
        "byBedroom": {"1": {"beds": 1, "minimum": rent_rate_min["price"], "minimumArea": rent_rate_min["area"], "area": rent_rate_min["area"], "minimumSqm": round(min(rent_rates)), "minimumSourceUrl": DD_RENT, "minimumSqmSourceUrl": DD_RENT, "average": rent_rate_min["price"], "averageSqm": round(min(rent_rates)), "sampleCount": 1}},
    },
})
save(market_path, market_prefix, markets, market_suffix)

cross_path, cross_prefix, crosschecks, cross_suffix = load("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": ID, "projectName": FULL_NAME, "asOf": CHECKED,
    "sourceName": "Hipflat / PropertyHub / DDproperty 多來源核對",
    "projectSourceUrl": "https://www.hipflat.co.th/en/projects/the-belgravia-at-ratchada-ladprao-15-cywrig",
    "sale": {"activeListingCount": 9, "displayedResultCount": 9, "observedCount": len(sale_current), "sourceUrl": PH_SALE,
             "note": "PropertyHub 專案出售頁顯示 9 筆；DDproperty 專案頁及 2026-10-02 的單筆頁顯示最低售價 ฿2,190,000。CX-156823 與 PropertyHub 6287017 為同一交叉刊登物件，不重複計樣本。",
             "listings": [{"id": row["id"], "bedrooms": row["beds"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"], "statusLabel": row["listingStatus"]} for row in sale_current]},
    "rent": {"activeListingCount": 17, "displayedResultCount": 17, "observedCount": len(rent_current), "sourceUrl": PH_RENT,
             "note": "PropertyHub 專案出租頁近期快照顯示 17 筆；DDproperty 個別頁於 2026-09-25 刊登一房 28.27㎡、฿13,000/月。另一筆兩房樣本超過 30 日未刷新，僅列歷史參考，不納入本次投報率。",
             "listings": [{"id": row["id"], "bedrooms": row["beds"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"], "statusLabel": row["listingStatus"]} for row in rent_current]},
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": "https://www.hipflat.co.th/en/projects/the-belgravia-at-ratchada-ladprao-15-cywrig", "statusLabel": "Hipflat 專案名稱與地址來源；售租價格摘要與單筆掛牌分開保留。"},
        {"sourceName": "Google Maps 點位", "url": MAP_URL, "statusLabel": f"PropertyHub CX-156823 的 Google Maps 短連結解析至專案點 {LAT}, {LNG}。"},
        {"sourceName": "DDproperty 專案核實", "url": DD_PROJECT, "statusLabel": "Soi Lat Phrao 15 Yaek 2-4；2020 完工、8 層、185 戶。"},
        {"sourceName": "PropertyHub 專案資料／管理費", "url": PH_PROJECT, "statusLabel": "The Belgravia Ladprao 15；2020 完工、8 層、185 戶，管理費 ฿45/㎡/月。"},
        {"sourceName": "最低出售掛牌", "url": DD_SALE, "statusLabel": "DDproperty 房源 500348168：1 房、約 36㎡、฿2,190,000；PropertyHub 對應 CX-156823 顯示精確面積 35.78㎡。"},
        {"sourceName": "出租掛牌", "url": DD_RENT, "statusLabel": "DDproperty 房源 500590567：1 房、28.27㎡、฿13,000/月；2026-09-25 刊登。"},
    ],
    "yieldStatus": "calculated_current_same_bedroom_listing",
    "yieldNote": f"現行一房基準：售價 ฿{sale_min['price']:,}、出售樣本面積 {sale_min['area']}㎡；租金單價 ฿{rent_rate_min['price'] / rent_rate_min['area']:.2f}/㎡/月，按售屋面積推估月租 ฿{projected_monthly_rent:,}。扣一個月仲介費和管理費 ฿45/㎡/月後淨年投報率 {net_yield:.2f}%。沒有同房型兩房出售樣本，不以跨房型方式計算。",
}
upsert(crosschecks, "hipflatId", crosscheck)
save(cross_path, cross_prefix, crosschecks, cross_suffix)

report = {
    "hipflatId": ID, "projectName": NAME, "currentProjectName": FULL_NAME, "checkedAt": CHECKED,
    "coordinates": {"verified": True, "lat": LAT, "lng": LNG, "sourceUrl": MAP_URL, "verificationSourceUrl": DD_PROJECT},
    "project": {"completedYear": 2020, "floors": 8, "units": 185, "commonFeeTHBPerSqmPerMonth": 45, "sourceUrl": PH_PROJECT},
    "saleSamples": sale_samples, "rentSamples": rent_samples,
    "yield": {"bedrooms": 1, "salePrice": sale_min["price"], "saleAreaSqm": sale_min["area"], "rentRateTHBPerSqmPerMonth": round(rent_rate_min["price"] / rent_rate_min["area"], 2), "estimatedMonthlyRent": projected_monthly_rent, "annualManagementFee": management_fee_year, "deductAgentMonths": 1, "netYieldPercent": net_yield},
    "sources": [PH_PROJECT, PH_SALE, PH_RENT, PH_SALE_MIN, DD_PROJECT, DD_SALE, DD_RENT, MAP_URL],
    "notes": ["PropertyHub CX-156823 and DDproperty 500348168 represent the same sale unit; not counted as two unique homes.", "Old 2-bedroom rent sample is retained but marked stale (>30 days) and excluded from the current ROI baseline.", "No current matched 2-bedroom sale sample was found; current one-bedroom ROI is used instead of mixing room types."],
}
(REPORTS / "belgravia-ladprao-15-location-market-yield-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
for token in ["bangkok-catalogue.js", "bangkok-propertyhub-map.js", "bangkok-verified-coordinates.js", "bangkok-manual-market-samples.js", "bangkok-market-crosschecks.js"]:
    html = re.sub(rf"{re.escape(token)}\?v=[^\"']+", f"{token}?v=20261020-belgravia-3134", html)
html = re.sub(r"app\.js\?v=[^\"']+", "app.js?v=20261020-belgravia-3134", html)
index_path.write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": ID, "coordinates": [LAT, LNG], "sale": [sale_min["price"], sale_min["area"]], "rent": [rent_rate_min["price"], rent_rate_min["area"]], "netYieldPercent": net_yield}, ensure_ascii=False))
