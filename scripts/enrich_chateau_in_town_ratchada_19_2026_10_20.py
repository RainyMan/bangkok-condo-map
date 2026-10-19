from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3918
CHECKED_AT = "2026-10-20"
PROJECT = "Chateau In Town Ratchada 19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/chateau-in-town-ratchada-19-pixbbz"
HIPFLAT_ALT = "https://www.hipflat.co.th/projects/chateau-in-town-ratchada-19-48ue07e310a3ne13823l4eaehnenhh89"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/chateau-in-town-ratchada-19"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/listings/1-bedroom-condo-for-sale-on-ratchadaphisek-din-daeng-2nd-floor-south-facing---6315718"
LIVINGINSIDER_RENT = "https://www.livinginsider.com/livingdetail_en/2844572/Condo-for-rent%3A-Chateau-In-Town-Ratchada-19%3A-Chateau-In-Town-Ratchada-19-next-to-MRT-Ratchadaphisek.html"
PROPERTYHUB_MISMATCH_RENT = "https://propertyhub.in.th/en/listings/for-rent-chateau-in-town-ratchada-19-2-bedrooms-2-bathrooms-fully-furnished-and-equipped-with-appliances"
OLD_DD_RENT = "https://www.ddproperty.com/en/property/chateau-in-town-ratchada-19-bangkok-for-rent-500444386"
GOOGLE_MAPS_SHORT = "https://goo.gl/maps/oMrCcSfJCG6uQ8fx6"
GOOGLE_MAPS_PLACE = "https://www.google.com/maps/place/Chateau+In+Town+Ratchada+19/@13.7993893,100.5716573,17z/data=!3m1!4b1!4m6!3m5!1s0x30e29c353a453183:0xf5cdc55379f82a58!8m2!3d13.7993893!4d100.573846!16s%2Fg%2F11bx5q51n6"


def load_array(filename: str, symbol: str):
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, symbol: str, rows: list[dict], compact: bool = False):
    prefix, _, suffix = load_array(filename, symbol)
    kwargs = {"separators": (",", ":")} if compact else {"indent": 2}
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, **kwargs) + suffix, encoding="utf-8")


purchase_price = 2_490_000
purchase_area = 32.98
monthly_rent = 12_500
rent_area = 33.0
rent_rate = monthly_rent / rent_area
estimated_monthly_rent = round(rent_rate * purchase_area)
annual_rent_after_agent = estimated_monthly_rent * 11
annual_common_fee = 40 * purchase_area * 12
net_yield = (annual_rent_after_agent - annual_common_fee) / purchase_price * 100

rent_sample = {
    "id": "2844572",
    "price": monthly_rent,
    "area": rent_area,
    "priceSqm": round(rent_rate),
    "beds": 1,
    "roomType": "1BR",
    "title": f"{PROJECT}，1 房，33 ㎡，฿12,500/月",
    "url": LIVINGINSIDER_RENT,
    "sourceName": "LivingInsider",
    "projectName": PROJECT,
    "updated": CHECKED_AT,
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "verificationNote": "LivingInsider 個別頁列本案 1 房、33㎡、฿12,500/月，並標示約 43 分鐘前建立；已於 2026-10-20 查核，仍需向刊登者確認可租。",
}
manual_rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": monthly_rent,
    "minimum": monthly_rent,
    "minimumArea": rent_area,
    "minimumSampleUpdated": CHECKED_AT,
    "averageSqm": round(rent_rate),
    "minimumSqm": round(rent_rate),
    "minimumSqmSampleUpdated": CHECKED_AT,
    "asOf": CHECKED_AT,
    "sourceName": "LivingInsider 個別出租掛牌",
    "source": LIVINGINSIDER_RENT,
    "minimumSourceUrl": LIVINGINSIDER_RENT,
    "minimumSqmSourceUrl": LIVINGINSIDER_RENT,
    "samples": [rent_sample],
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": monthly_rent,
            "minimumArea": rent_area,
            "area": rent_area,
            "priceSqm": round(rent_rate),
            "minimumSqm": round(rent_rate),
            "averageSqm": round(rent_rate),
            "sourceUrl": LIVINGINSIDER_RENT,
            "minimumSourceUrl": LIVINGINSIDER_RENT,
            "minimumSqmSourceUrl": LIVINGINSIDER_RENT,
        }
    },
}

_, coordinates, _ = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
coordinates.append({
    "hipflatId": PROJECT_ID,
    "name": PROJECT,
    "lat": 13.7993893,
    "lng": 100.573846,
    "locationVerified": True,
    "sourceName": "Google Maps 專案點位（由 PropertyHub 個別出售頁地圖連結解析）",
    "sourceUrl": GOOGLE_MAPS_PLACE,
    "verificationSourceUrl": HIPFLAT,
    "corroborationSourceUrl": PROPERTYHUB_SALE,
    "verificationMethod": "PropertyHub 直接出售掛牌的 Google Maps 短連結解析為標示 Chateau In Town Ratchada 19 的 Place，座標 13.7993893, 100.573846；與既有專案地圖點相差約 4 公尺。",
})
save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinates, compact=True)

_, manual_rows, _ = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [row for row in manual_rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
manual_rows.append({"hipflatId": PROJECT_ID, "name": PROJECT, "asOf": CHECKED_AT, "rent": manual_rent})
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows, compact=True)

sale_sample = {
    "id": "6315718",
    "price": purchase_price,
    "area": purchase_area,
    "priceSqm": round(purchase_price / purchase_area),
    "beds": 1,
    "roomType": "1BR",
    "title": f"{PROJECT}，1 房，32.98 ㎡，฿2,490,000",
    "url": PROPERTYHUB_SALE,
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "updated": "2026-10-19",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "verificationNote": "PropertyHub 專案頁及個別掛牌均列 1 房、32.98㎡、฿2,490,000；專案結果於 2026-10-19 刷新，同日多個相同價位掛牌，不重複計數。",
}
cross_record = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub / LivingInsider / Google Maps / Hipflat",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 12,
        "displayedResultCount": 12,
        "observedCount": 1,
        "sourceUrl": PROPERTYHUB_PROJECT,
        "note": "PropertyHub 專案出售結果顯示多筆更新至 2026-10-19 的掛牌；最低可核實 1 房總價 ฿2,490,000、面積 32.98㎡。重複代理刊登不重複計數。",
        "listings": [sale_sample],
    },
    "rent": {
        "displayedResultCount": 1,
        "observedCount": 1,
        "sourceUrl": LIVINGINSIDER_RENT,
        "note": "LivingInsider 個別頁列 1 房、33㎡、฿12,500/月，標示約 43 分鐘前建立。PropertyHub 所列 2 房租盤與其專案房型範圍 1 房、32–40㎡不符，未納入；DDproperty ฿10,000/34㎡掛牌刊登於 2026-07-22，超過 30 日未更新，排除於目前租金與投報樣本。",
        "listings": [rent_sample],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "確認本案名稱、Ratchada 19 / Din Daeng 地址；其中一個專案頁目前未列房源。"},
        {"sourceName": "PropertyHub 專案頁", "url": PROPERTYHUB_PROJECT, "statusLabel": "本案 1 房戶型約 32–40㎡、管理費 ฿40/㎡/月、2015 完工；出售掛牌中可核實最低 1 房樣本 ฿2,490,000、32.98㎡。"},
        {"sourceName": "PropertyHub 最低出售樣本", "url": PROPERTYHUB_SALE, "statusLabel": "直接掛牌列 1 房、32.98㎡、฿2,490,000；專案頁最近刷新日期為 2026-10-19。"},
        {"sourceName": "LivingInsider 1 房出租樣本", "url": LIVINGINSIDER_RENT, "statusLabel": "直接頁面列 1 房、33㎡、฿12,500/月，頁面標示約 43 分鐘前建立；目前在架狀態仍建議向刊登者確認。"},
        {"sourceName": "排除：PropertyHub 不符房型出租頁", "url": PROPERTYHUB_MISMATCH_RENT, "statusLabel": "專案頁顯示的 2 房租盤與該專案已列 1 房、32–40㎡房型不符，沒有納入。"},
        {"sourceName": "排除：DDproperty 舊租盤", "url": OLD_DD_RENT, "statusLabel": "฿10,000/月、34㎡的 1 房樣本刊登於 2026-07-22；超過 30 日未更新，未作為目前最低租金或投報基準。"},
        {"sourceName": "Google Maps 座標", "url": GOOGLE_MAPS_PLACE, "statusLabel": "PropertyHub 個別出售掛牌地圖連結解析為本案 Google Maps Place，座標 13.7993893, 100.573846。"},
    ],
    "yieldStatus": "calculated_same_bedroom_lowest_sale_and_rent",
    "yieldEstimate": {
        "bedrooms": 1,
        "purchasePriceTHB": purchase_price,
        "purchaseAreaSqm": purchase_area,
        "purchaseSourceUrl": PROPERTYHUB_SALE,
        "rentSampleTHBPerMonth": monthly_rent,
        "rentSampleAreaSqm": rent_area,
        "rentRateTHBPerSqmMonth": round(rent_rate, 2),
        "estimatedMonthlyRentAtPurchaseAreaTHB": estimated_monthly_rent,
        "agentMonthsDeducted": 1,
        "commonFeeTHBPerSqmMonth": 40,
        "annualCommonFeeTHB": round(annual_common_fee, 2),
        "netAnnualYieldPercent": round(net_yield, 2),
        "rentSourceUrl": LIVINGINSIDER_RENT,
        "formula": "((฿12,492 × 11) − (฿40/㎡/月 × 32.98㎡ × 12)) ÷ ฿2,490,000 × 100 = 4.88%",
        "caveat": "租盤頁標示新刊登，但實際可租仍需向刊登者確認；未計稅、維修與交易成本。",
    },
}
_, cross_rows, _ = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = [row for row in cross_rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
cross_rows.append(cross_record)
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT,
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "lat": 13.7993893,
        "lng": 100.573846,
        "sourceUrl": GOOGLE_MAPS_PLACE,
        "shortUrlFromListing": GOOGLE_MAPS_SHORT,
        "verificationSourceUrl": PROPERTYHUB_SALE,
        "hipflatProjectUrl": HIPFLAT,
    },
    "sale": {"sampleCountVerified": 1, "minimumSameBedroomTotalTHB": purchase_price, "bedrooms": 1, "areaSqm": purchase_area, "sourceUrl": PROPERTYHUB_SALE},
    "rent": {"sampleCountVerified": 1, "monthlyRentTHB": monthly_rent, "bedrooms": 1, "areaSqm": rent_area, "sourceUrl": LIVINGINSIDER_RENT, "availabilityStatus": rent_sample["listingStatus"]},
    "excluded": [
        {"sourceUrl": PROPERTYHUB_MISMATCH_RENT, "reason": "PropertyHub 專案頁展示 2 房租盤，但該案列出的房型只有 1 房、32–40㎡，且沒有直接物件頁供核實，排除。"},
        {"sourceUrl": OLD_DD_RENT, "reason": "DDproperty 個別頁刊登日 2026-07-22，超過 30 日無更新，僅保留為過往市場參考，不用於目前投報。"},
        {"sourceUrl": "https://www.thaimidtown.com/post?asid=136579", "reason": "฿1,900,000 特價掛牌有效期間只到 2026-06-30，已過期，不作為最低現行購入基準。"},
    ],
    "yield": cross_record["yieldEstimate"],
    "sources": cross_record["availabilitySources"],
}
(ROOT / "reports/chateau-in-town-ratchada-19-market-yield-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

checks_path = ROOT / "reports/listing-availability-checks-2026-10-20.csv"
checks = [
    {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": CHECKED_AT, "market": "sale", "status": "direct_current_listing_verified", "verification_note": "PropertyHub 專案頁顯示 2026-10-19 刷新的出售樣本；最低可核實 1 房 32.98㎡、฿2,490,000。", "source_1": PROPERTYHUB_PROJECT, "source_2": PROPERTYHUB_SALE, "source_3": HIPFLAT},
    {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": CHECKED_AT, "market": "rent", "status": "direct_recent_listing_verified_availability_unconfirmed", "verification_note": "LivingInsider 直接頁列 1 房 33㎡、฿12,500/月，標示約 43 分鐘前建立；與出售 1 房樣本同房型。尚需向刊登者確認可租。", "source_1": LIVINGINSIDER_RENT, "source_2": PROPERTYHUB_PROJECT, "source_3": OLD_DD_RENT},
]
with checks_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"])
    writer.writeheader()
    writer.writerows(checks)

index = DIST / "index.html"
html = index.read_text(encoding="utf-8")
html = re.sub(r'bangkok-verified-coordinates\.js\?v=[^" ]+', "bangkok-verified-coordinates.js?v=20261020-chateau-ratchada-19-map-pin", html)
html = re.sub(r'bangkok-manual-market-samples\.js\?v=[^" ]+', "bangkok-manual-market-samples.js?v=20261020-chateau-ratchada-19-rent-2844572", html)
html = re.sub(r'bangkok-market-crosschecks\.js\?v=[^" ]+', "bangkok-market-crosschecks.js?v=20261020-chateau-ratchada-19-market-check", html)
index.write_text(html, encoding="utf-8")

print(json.dumps({
    "hipflatId": PROJECT_ID,
    "project": PROJECT,
    "coordinate": [13.7993893, 100.573846],
    "purchase": f"{purchase_price:,} THB / {purchase_area} sqm, 1BR",
    "rent": f"{monthly_rent:,} THB/mo / {rent_area} sqm, 1BR",
    "estimatedMonthlyRentAtPurchaseArea": estimated_monthly_rent,
    "netAnnualYieldAfterAgentMonthAndCommonFee": round(net_yield, 2),
}, ensure_ascii=False))
