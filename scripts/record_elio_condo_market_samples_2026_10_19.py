"""Record source-linked Elio Sukhumvit 64 market and location evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-10-19"
HIPFLAT_ID = 3389
PROJECT_NAME = "Elio Condo"
PH_SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-elio-sukhumvit-64"
PH_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-elio-sukhumvit-64"
PH_PROJECT = "https://propertyhub.in.th/en/projects/elio-sukhumvit-64"
SALE_URL = "https://assets2.propertyhub.in.th/en/listings/a010571-elio-sukhumvit-64---6445422"
RENT_STUDIO_URL = "https://propertyhub.in.th/en/listings/p-57284-condo-for-rent-elio-sukhumvit-64-near-bts-udom-suk-line-easythaihome-085-592-2897---6489425"
RENT_ONE_BED_URL = "https://propertyhub.in.th/en/listings/for-rent-elio-sukhumvit-64-near-bts-udomsuk-and-bts-punnawithi-line-id-condobkk-with-code-h2824---5225134"
COORD_URL = "https://propertyscout.co.th/en/bangkok/condo/elio-sukhumvit-64/"
COORD_CROSSCHECK_URL = "https://thelivinginsight.com/elio-sukhumvit-64/"


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
        "id": "6445422", "price": 1_230_000, "area": 22, "priceSqm": 55_909,
        "beds": 1, "roomType": "1BR", "title": "A010571 Elio Sukhumvit 64，1 房，22 ㎡，฿1,230,000",
        "url": SALE_URL, "sourceName": "PropertyHub", "projectName": "Elio Sukhumvit 64",
        "updated": "2026-10-15", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id_on_project_sale_index",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }
]
rent_samples = [
    {
        "id": "6489425", "price": 8_000, "area": 22, "priceSqm": 364,
        "beds": 0, "roomType": "STUDIO",
        "title": "P-57284 Elio Sukhumvit 64，Studio，22 ㎡，฿8,000/月（不含洗衣機）",
        "url": RENT_STUDIO_URL, "sourceName": "PropertyHub", "projectName": "Elio Sukhumvit 64",
        "updated": "2026-10-17", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
    {
        "id": "5225134", "price": 11_000, "area": 30, "priceSqm": 367,
        "beds": 1, "roomType": "1BR",
        "title": "Elio Sukhumvit 64，1 房，30 ㎡，8 樓，฿11,000/月",
        "url": RENT_ONE_BED_URL, "sourceName": "PropertyHub", "projectName": "Elio Sukhumvit 64",
        "updated": "2026-10-17", "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
]

coordinates_path = ROOT / "dist/bangkok-verified-coordinates.js"
coordinates = read_rows(coordinates_path, "BANGKOK_VERIFIED_COORDINATES")
coordinate = {
    "hipflatId": HIPFLAT_ID, "name": PROJECT_NAME, "lat": 13.68524746, "lng": 100.6042924,
    "locationVerified": True, "sourceName": "PropertyScout 專案地圖座標",
    "sourceUrl": COORD_URL, "verificationSourceUrl": COORD_CROSSCHECK_URL,
    "verificationMethod": "exact_project_name_and_full_Hipflat_address_cross_checked_with_independent_Google_Maps_coordinates",
}
if any(int(row["hipflatId"]) == HIPFLAT_ID for row in coordinates):
    coordinates = [coordinate if int(row["hipflatId"]) == HIPFLAT_ID else row for row in coordinates]
else:
    coordinates.append(coordinate)
write_rows(coordinates_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

sale_rates = [row["price"] / row["area"] for row in sale_samples]
rent_rates = [row["price"] / row["area"] for row in rent_samples]
market_record = {
    "hipflatId": HIPFLAT_ID,
    "name": PROJECT_NAME,
    "completedYear": 2014,
    "completedYearSourceUrl": PH_PROJECT,
    "fee": {
        "rate": 45, "status": "public",
        "note": "PropertyHub 專案資料公布管理費 ฿45/㎡/月；實際收費請向管委會確認。",
        "source": PH_PROJECT,
    },
    "sale": {
        "count": 30, "observedCount": len(sale_samples), "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in sale_samples) / len(sale_samples)),
        "minimum": min(row["price"] for row in sale_samples), "minimumArea": 22,
        "averageSqm": round(sum(sale_rates) / len(sale_rates)), "minimumSqm": round(min(sale_rates)),
        "asOf": AS_OF, "sourceName": "PropertyHub 單筆出售掛牌",
        "source": PH_SALE_PROJECT, "samples": sale_samples,
    },
    "rent": {
        "count": 71, "observedCount": len(rent_samples), "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in rent_samples) / len(rent_samples)),
        "minimum": min(row["price"] for row in rent_samples), "minimumArea": 22,
        "averageSqm": round(sum(rent_rates) / len(rent_rates)), "minimumSqm": round(min(rent_rates)),
        "asOf": AS_OF, "sourceName": "PropertyHub 單筆出租掛牌",
        "source": PH_RENT_PROJECT, "samples": rent_samples,
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
    "hipflatId": HIPFLAT_ID, "projectName": "Elio Sukhumvit 64 (Hipflat alias: Elio Condo)",
    "asOf": AS_OF, "sourceName": "Hipflat / PropertyHub / PropertyScout 多來源核對",
    "projectSourceUrl": "https://www.hipflat.co.th/en/projects/elio-condo-neiweo",
    "sale": {
        "activeListingCount": 30, "sourceUrl": PH_SALE_PROJECT,
        "listings": [{"id": row["id"], "bedrooms": row["beds"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"]} for row in sale_samples],
        "note": "PropertyHub 專案頁目前列 30 個出售掛牌；逐筆確認最低售價樣本 A010571：1 房、22㎡、฿1,230,000。",
    },
    "rent": {
        "activeListingCount": 71, "sourceUrl": PH_RENT_PROJECT,
        "listings": [{"id": row["id"], "bedrooms": row["beds"], "roomType": row["roomType"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"]} for row in rent_samples],
        "note": "PropertyHub 專案頁目前列 71 個出租掛牌；兩筆房型和單價取自同專案直接掛牌頁。排除名稱含 Elio Del Ray 的相鄰專案。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": "https://www.hipflat.co.th/en/projects/elio-condo-neiweo", "statusLabel": "Hipflat 名稱 Elio Condo，完整地址指向 Elio Sukhumvit 64，115 Soi Sukhumvit 64。"},
        {"sourceName": "PropertyHub 專案資料", "url": PH_PROJECT, "statusLabel": "同案別名 Elio Condo；2014 完工、4 棟、8 層、962 戶，管理費 45 THB/㎡/月。"},
        {"sourceName": "最低出售單筆掛牌", "url": SALE_URL, "statusLabel": "PropertyHub 專案列表於 2026-10-15 更新 A010571；1 房、22㎡、฿1,230,000。"},
        {"sourceName": "Studio 出租單筆掛牌", "url": RENT_STUDIO_URL, "statusLabel": "P-57284 頁列 22㎡ Studio、無洗衣機方案฿8,000/月；頁面亦列含洗衣機฿8,500/月。"},
        {"sourceName": "1 房出租單筆掛牌", "url": RENT_ONE_BED_URL, "statusLabel": "H2824 頁列 Elio Sukhumvit 64、1 房、30㎡、฿11,000/月。"},
        {"sourceName": "座標來源", "url": COORD_URL, "statusLabel": "PropertyScout 專案頁提供 13.68524746,100.6042924；同頁列 2014 完工、962 戶、8 層。"},
        {"sourceName": "Google Maps 座標交叉核對", "url": COORD_CROSSCHECK_URL, "statusLabel": "TheLivingInsight 標示專案 Google Maps 點位 13.685225,100.604271，與主座標相距約 3 公尺。"},
    ],
    "yield": {
        "status": "estimated_from_matched_room_type",
        "purchasePriceTHB": 1_230_000, "purchaseAreaSqm": 22,
        "matchedRentListing": RENT_ONE_BED_URL, "rentRateTHBPerSqmPerMonth": round(11_000 / 30, 2),
        "imputedMonthlyRentTHB": round(11_000 / 30 * 22), "commonFeeTHBPerSqmPerMonth": 45,
        "netAfterOneMonthAgentAndCommonFeePercent": round((((11_000 / 30 * 22) * 11) - 45 * 22 * 12) / 1_230_000 * 100, 2),
        "formula": "((1 房月租 11,000 ÷ 30㎡ × 最低 1 房出售樣本 22㎡ × 11 個收租月) − 45 × 22㎡ × 12) ÷ 1,230,000 × 100",
        "note": "未找到可核實兩房買賣掛牌，因此未混用房型；按目前可配對的最低一房出售掛牌及一房出租樣本估算。",
    },
}
crosschecks = [row for row in crosschecks if int(row["hipflatId"]) != HIPFLAT_ID]
crosschecks.append(crosscheck)
write_rows(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": HIPFLAT_ID, "projectName": PROJECT_NAME, "asOf": AS_OF,
    "coordinate": coordinate, "saleSamples": sale_samples, "rentSamples": rent_samples,
    "yield": crosscheck["yield"], "sources": crosscheck["availabilitySources"],
    "caveats": ["售租掛牌的現況尚未向刊登者確認。", "目前找到的出售掛牌均未證實為兩房，故以同房型一房售租配對估算，未假設兩房資料。"],
}
(ROOT / "reports/elio-condo-market-samples-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": HIPFLAT_ID, "coordinatesVerified": True, "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "yieldPercent": crosscheck["yield"]["netAfterOneMonthAgentAndCommonFeePercent"]}, ensure_ascii=False))
