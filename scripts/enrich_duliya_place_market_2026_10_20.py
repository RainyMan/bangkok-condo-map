"""Add directly checked current Duliya Place sale and rent samples."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 4517
PROJECT = "Duliya Place"
CHECKED_AT = "2026-10-20"

HIPFLAT = "https://www.hipflat.co.th/en/projects/duliya-place-rdqpii"
PH_PROJECT = "https://propertyhub.in.th/en/projects/duliya-place"
PH_SALE = "https://propertyhub.in.th/en/listings/a034160-duliya-place---6005535"
PH_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-duliya-place-condo"
LI_SALE_PROJECT = "https://www.livinginsider.com/en/project/duliya-place-condo-buysell"
LI_SALE_1100 = "https://www.livinginsider.com/detail/condo-for-sale-duliya-place-1bedroom-3225607"
LI_SALE_1190 = "https://www.livinginsider.com/detail/condo-for-sale-duliya-place-1bedroom-3072808"
LI_RENT_PROJECT = "https://www.livinginsider.com/en/project/duliya-place-condo-rent"
LI_RENT = "https://www.livinginsider.com/detail/condo-for-rent-duliya-place-1bedroom-3194410"
PH_OLD_STUDIO = "https://propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%94%E0%B8%B8%E0%B8%A5%E0%B8%B4%E0%B8%A2%E0%B8%B2-%E0%B9%80%E0%B8%9E%E0%B8%A5%E0%B8%AA-26-7-%E0%B8%95%E0%B8%A3%E0%B8%A1-%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88-2-%E0%B8%8B%E0%B8%AD%E0%B8%A2%E0%B8%99%E0%B8%B2%E0%B8%84%E0%B8%99%E0%B8%B4%E0%B8%A7%E0%B8%B2%E0%B8%AA-37-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B8%B2%E0%B8%A7---5956798"


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str, compact: bool = False) -> None:
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, **options) + suffix, encoding="utf-8")


sale_samples = [
    {
        "id": "3225607", "price": 1100000, "area": 39, "priceSqm": 28205,
        "beds": 1, "roomType": "1BR",
        "title": "Duliya Place，1 房，39 ㎡，฿1,100,000",
        "url": LI_SALE_1100, "sourceName": "LivingInsider", "projectName": PROJECT,
        "updated": "2026-10-14", "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_name_thai_address_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
        "verificationNote": "個別頁列 Duliya Place、1 房、39㎡、฿1,100,000；頁面標示約 6 日前推送，日期按 2026-10-20 查核日換算。位置列明 Soi Nakniwat 37，需向刊登者確認是否仍在架。",
    },
    {
        "id": "3072808", "price": 1190000, "area": 28, "priceSqm": 42500,
        "beds": 1, "roomType": "1BR",
        "title": "Duliya Place，1 房，28 ㎡，฿1,190,000",
        "url": LI_SALE_1190, "sourceName": "LivingInsider", "projectName": PROJECT,
        "updated": "2026-10-17", "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_name_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
        "verificationNote": "個別頁列 Duliya Place、1 房、28㎡、฿1,190,000；建立日 2026-05-13，頁面標示約 3 日前推送，日期按 2026-10-20 查核日換算。需向刊登者確認是否仍在架。",
    },
    {
        "id": "6005535", "price": 2190000, "area": 65, "priceSqm": 33692,
        "beds": 1, "roomType": "1BR",
        "title": "Duliya Place，1 房，65 ㎡，฿2,190,000",
        "url": PH_SALE, "sourceName": "PropertyHub", "projectName": PROJECT,
        "updated": "2026-10-17", "checkedAt": CHECKED_AT,
        "matchedBy": "exact_propertyhub_project_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
        "verificationNote": "PropertyHub 個別頁列本案 1 房、65㎡、฿2,190,000；專案頁於 2026-10-17 顯示最近刷新。個別頁未提供明確刊登日，現況待賣方確認。",
    },
]

rent_samples = [
    {
        "id": "3194410", "price": 6500, "area": 39, "priceSqm": 167,
        "beds": 1, "roomType": "1BR",
        "title": "Duliya Place，1 房，39 ㎡，฿6,500/月",
        "url": LI_RENT, "sourceName": "LivingInsider", "projectName": PROJECT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_name_thai_address_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
        "verificationNote": "個別頁列 Duliya Place、1 房、39㎡、฿6,500/月；建立日 2026-08-19，頁面標示約一週前推送；同案出租專案頁標示昨日推送，兩處相對更新時間略有差異。依 2026-10-20 查核仍列近期樣本，是否可租須向刊登者確認。",
    },
]

sale_total_avg = round(sum(x["price"] for x in sale_samples) / len(sale_samples))
sale_sqm_avg = round(sum(x["price"] / x["area"] for x in sale_samples) / len(sale_samples))
rent_rate = rent_samples[0]["price"] / rent_samples[0]["area"]
rent_at_purchase_area = round(rent_rate * sale_samples[0]["area"])
annual_net = rent_at_purchase_area * 11 - 15 * sale_samples[0]["area"] * 12
net_yield = round(annual_net / sale_samples[0]["price"] * 100, 2)

manual_prefix, manual_rows, manual_suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
sale = {
    "count": 22,
    "observedCount": len(sale_samples),
    "countKind": "manual_verified_listing",
    "average": sale_total_avg,
    "minimum": 1100000,
    "minimumArea": 39,
    "minimumSampleUpdated": "2026-10-14",
    "averageSqm": sale_sqm_avg,
    "minimumSqm": 28205,
    "minimumSqmSampleUpdated": "2026-10-14",
    "asOf": CHECKED_AT,
    "sourceName": "LivingInsider / PropertyHub 個別出售掛牌",
    "source": LI_SALE_PROJECT,
    "minimumSourceUrl": LI_SALE_1100,
    "minimumSqmSourceUrl": LI_SALE_1100,
    "samples": sale_samples,
    "byBedroom": {
        "1": {
            "count": 3,
            "minimum": 1100000,
            "minimumArea": 39,
            "area": 39,
            "priceSqm": 28205,
            "minimumSqm": 28205,
            "averageSqm": sale_sqm_avg,
            "sourceUrl": LI_SALE_1100,
            "minimumSourceUrl": LI_SALE_1100,
            "minimumSqmSourceUrl": LI_SALE_1100,
        }
    },
}
rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 6500,
    "minimum": 6500,
    "minimumArea": 39,
    "averageSqm": 167,
    "minimumSqm": 167,
    "asOf": CHECKED_AT,
    "sourceName": "LivingInsider 個別出租掛牌",
    "source": LI_RENT_PROJECT,
    "minimumSourceUrl": LI_RENT,
    "minimumSqmSourceUrl": LI_RENT,
    "samples": rent_samples,
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": 6500,
            "minimumArea": 39,
            "area": 39,
            "priceSqm": 167,
            "minimumSqm": 167,
            "averageSqm": 167,
            "sourceUrl": LI_RENT,
            "minimumSourceUrl": LI_RENT,
            "minimumSqmSourceUrl": LI_RENT,
        }
    },
}
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
manual.update({"asOf": CHECKED_AT, "sale": sale, "rent": rent})
save_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix, compact=True)

cross_prefix, cross_rows, cross_suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
sale_listings = [
    {
        "listingId": row["id"], "price": row["price"], "area": row["area"],
        "priceSqm": row["priceSqm"], "bedrooms": 1, "listedAt": row.get("updated", ""),
        "url": row["url"], "sourceName": row["sourceName"],
        "statusLabel": "近期更新；現況仍請向刊登者確認",
    }
    for row in sale_samples
]
rent_listings = [
    {
        "listingId": row["id"], "price": row["price"], "area": row["area"],
        "priceSqm": row["priceSqm"], "bedrooms": 1, "listedAt": "近期推送（頁面標示約 1 週／昨日；日期不一致）",
        "url": row["url"], "sourceName": row["sourceName"],
        "statusLabel": "近期更新；是否可租請向刊登者確認",
    }
    for row in rent_samples
]
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "LivingInsider / PropertyHub",
    "projectSourceUrl": LI_SALE_PROJECT,
    "sale": {
        "activeListingCount": 22,
        "displayedResultCount": 21,
        "observedCount": len(sale_samples),
        "sourceUrl": LI_SALE_PROJECT,
        "note": "LivingInsider 專案出售頁列 21 筆房源；另核對 PropertyHub 一筆 1 房、65㎡、฿2,190,000 專案掛牌。可直接核對的 1 房樣本共 3 筆，最低總價為 LivingInsider 的 ฿1,100,000 / 39㎡。PropertyHub 舊專案索引曾列 ฿800,000、約 26.8㎡，但頁面日期 2026-09-09 已超過 30 日，且房型欄位同時標示 Studio 與 1 房，排除於現行行情與投報。",
        "listings": sale_listings,
    },
    "rent": {
        "activeListingCount": 1,
        "displayedResultCount": 1,
        "observedCount": 1,
        "sourceUrl": LI_RENT_PROJECT,
        "note": "LivingInsider 專案出租頁列 1 筆 1 房、39㎡、฿6,500/月；個別頁與專案頁的相對更新時間略有差異，保留為近期樣本並標示待向刊登者確認。PropertyHub 出租頁顯示的舊房源日期為 2025-06-04，未納入現行租金。",
        "listings": rent_listings,
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "Duliya Place 專案位址為 Rotdee / Soi Nakniwat 37，完成年 1995；頁面目前列出售單位。"},
        {"sourceName": "PropertyHub 專案／管理費／位置", "url": PH_PROJECT, "statusLabel": "專案頁核對地址 12/10 Soi Nakniwat 37、1995 完工、858 戶、8 層及管理費 ฿15/㎡/月；座標沿用本案已核對專案圖釘。"},
        {"sourceName": "LivingInsider 最低 1 房出售單筆", "url": LI_SALE_1100, "statusLabel": "1 房、39㎡、฿1,100,000（฿28,205/㎡）；頁面標示約 6 日前更新。"},
        {"sourceName": "LivingInsider 1 房出售單筆", "url": LI_SALE_1190, "statusLabel": "1 房、28㎡、฿1,190,000（฿42,500/㎡）；建立日 2026-05-13，頁面標示約 3 日前推送。"},
        {"sourceName": "PropertyHub 1 房出售單筆", "url": PH_SALE, "statusLabel": "1 房、65㎡、฿2,190,000（฿33,692/㎡）；專案頁標示 2026-10-17 最近刷新。"},
        {"sourceName": "LivingInsider 出租專案頁", "url": LI_RENT_PROJECT, "statusLabel": "列 1 筆本案租盤；頁面租金 ฿6,500/月、39㎡、1 房。"},
        {"sourceName": "LivingInsider 1 房出租單筆", "url": LI_RENT, "statusLabel": "1 房、39㎡、฿6,500/月（฿167/㎡/月）；個別頁及專案頁的相對更新時間不一致，實際可租待確認。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PH_RENT_PROJECT, "statusLabel": "目前查核頁顯示舊的 2025-06-04 租盤，不作現行樣本；近期租金以 LivingInsider 直接掛牌為準。"},
        {"sourceName": "排除：PropertyHub 舊低價出售單筆", "url": PH_OLD_STUDIO, "statusLabel": "฿800,000、26.79㎡；頁面日期為 2026-09-09，超過 30 日，且同頁房型欄位 Studio / 1 房不一致，排除於目前行情與投報。"},
    ],
    "yieldStatus": "calculated_same_bedroom_lowest_sale_and_rent",
    "yieldNote": "目前可比房型為 1 房（未找到兩房直接樣本）。購入基準採最低 1 房總價 ฿1,100,000 與同一物件面積 39㎡；月租以 1 房最低租金單價 ฿6,500/39㎡ × 39㎡估算為 ฿6,500。扣 1 個月仲介費及管理費 ฿15/㎡/月後，淨年投報率為 5.86%。",
    "yieldEstimate": {
        "bedrooms": 1,
        "purchasePriceTHB": 1100000,
        "purchaseAreaSqm": 39,
        "purchaseSourceUrl": LI_SALE_1100,
        "rentSampleTHBPerMonth": 6500,
        "rentSampleAreaSqm": 39,
        "rentRateTHBPerSqmMonth": round(rent_rate, 2),
        "estimatedMonthlyRentAtPurchaseAreaTHB": rent_at_purchase_area,
        "agentMonthsDeducted": 1,
        "commonFeeTHBPerSqmMonth": 15,
        "annualCommonFeeTHB": 15 * 39 * 12,
        "netAnnualYieldPercent": net_yield,
        "rentSourceUrl": LI_RENT,
        "formula": "((฿6,500 × 11) − (฿15/㎡/月 × 39㎡ × 12)) ÷ ฿1,100,000 × 100 = 5.86%",
        "caveat": "租盤頁的相對更新時間有差異，現況待刊登者確認；未計稅、維修與交易成本。",
    },
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
    "coordinates": {"verified": True, "latitude": 13.8092339, "longitude": 100.6036577, "sourceUrl": PH_PROJECT},
    "commonFeeTHBPerSqmMonth": 15,
    "saleSamples": sale_samples,
    "rentSamples": rent_samples,
    "excluded": [{"url": PH_OLD_STUDIO, "price": 800000, "areaSqm": 26.79, "reason": "2026-09-09 頁面日期已超過 30 日，且 Studio / 1 房欄位衝突；不納入目前行情或 1 房投報。"}],
    "yieldEstimate": crosscheck["yieldEstimate"],
    "sources": [HIPFLAT, PH_PROJECT, PH_SALE, PH_RENT_PROJECT, LI_SALE_PROJECT, LI_SALE_1100, LI_SALE_1190, LI_RENT_PROJECT, LI_RENT],
}
(REPORTS / "duliya-place-market-enrichment-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": PROJECT, "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "lowestSaleTHB": 1100000, "purchaseAreaSqm": 39, "rentRateTHBPerSqmMonth": round(rent_rate, 2), "netYieldPercent": net_yield}, ensure_ascii=False))
