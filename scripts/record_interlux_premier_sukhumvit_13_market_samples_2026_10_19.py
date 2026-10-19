"""Record direct listing samples and a matched two-bedroom yield for InterLux Premier Sukhumvit 13."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 4669
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/interlux-premier-sukhumvit-13-rotzoz"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/inter-lux-premier-sukhumvit-13"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-inter-lux-premier-sukhumvit-13"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-inter-lux-premier-sukhumvit-13"
PROPERTYSCOUT_PROJECT = "https://propertyscout.co.th/en/bangkok/condo/inter-lux-premier-sukhumvit-13/"
SALE_LOWEST = "https://propertyhub.in.th/en/listings/lth12249-interlux-premier-for-sale-size-57-sqm-2-beds-2-baths-near-bts-nana-station-only-6-5-mb---5051423"
SALE_6700 = "https://propertyhub.in.th/en/listings/2-br-condo-at-inter-lux-premier-sukhumvit-13-near-arl-makkasan-id-2873687--a5c608e4---6102633"
SALE_7200 = "https://propertyhub.in.th/en/listings/2-br-condo-at-inter-lux-premier-sukhumvit-13-near-arl-makkasan-id-2015955--a3290987---4915029"
RENT_35000 = "https://www.ddproperty.com/en/property/interlux-premier-sukhumvit-13-bangkok-for-rent-500570288"
FEE_SOURCE = PROPERTYHUB_PROJECT

sale_samples = [
    {
        "id": "5051423", "price": 6_500_000, "area": 57, "priceSqm": 114_035,
        "beds": 2, "roomType": "2BR", "title": "InterLux Premier Sukhumvit 13，2 房，57 ㎡，฿6,500,000",
        "url": SALE_LOWEST, "sourceName": "PropertyHub", "updated": "2026-10-14",
        "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_room_type_price_and_area",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6102633", "price": 6_700_000, "area": 49.34, "priceSqm": 135_792,
        "beds": 2, "roomType": "2BR", "title": "InterLux Premier Sukhumvit 13，2 房，49.34 ㎡，฿6,700,000",
        "url": SALE_6700, "sourceName": "PropertyHub", "updated": "2026-10-14",
        "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_room_type_price_and_area",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "4915029", "price": 7_200_000, "area": 50, "priceSqm": 144_000,
        "beds": 2, "roomType": "2BR", "title": "InterLux Premier Sukhumvit 13，2 房，50 ㎡，฿7,200,000",
        "url": SALE_7200, "sourceName": "PropertyHub", "updated": "2026-10-14",
        "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_room_type_price_and_area",
        "listingStatus": "active_as_listed",
    },
]
rent_samples = [
    {
        "id": "500570288", "price": 35_000, "area": 58, "priceSqm": 603,
        "beds": 2, "roomType": "2BR", "title": "InterLux Premier Sukhumvit 13，2 房，58 ㎡，฿35,000/月",
        "url": RENT_35000, "sourceName": "DDproperty", "updated": "2026-09-19",
        "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_room_type_price_and_area",
        "listingStatus": "active_as_listed",
    },
]

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual_text = manual_path.read_text(encoding="utf-8")
manual_match = re.fullmatch(r"(window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*)(\[.*\])(\s*;?\s*)", manual_text, re.S)
if not manual_match:
    raise RuntimeError("Unexpected manual market data format")
manual_rows = json.loads(manual_match.group(2))
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": "InterLux Premier Sukhumvit 13"}
    manual_rows.append(manual)
for kind, samples in (("sale", sale_samples), ("rent", rent_samples)):
    market = manual.setdefault(kind, {})
    by_id = {str(sample.get("id")): sample for sample in market.get("samples", [])}
    by_id.update({sample["id"]: sample for sample in samples})
    market["samples"] = list(by_id.values())
    market["asOf"] = CHECKED_AT
    market["sourceName"] = "PropertyHub / DDproperty 單筆掛牌"
manual["fee"] = {
    "rate": 50,
    "status": "public",
    "note": "PropertyHub 專案頁標示 Utility Fee ฿50/㎡；按公開管理費資料估算，請向管委會確認實際收費。",
    "source": FEE_SOURCE,
}
manual_path.write_text(manual_match.group(1) + json.dumps(manual_rows, ensure_ascii=False, separators=(",", ":")) + manual_match.group(3), encoding="utf-8")

cross_path = ROOT / "dist/bangkok-market-crosschecks.js"
cross_text = cross_path.read_text(encoding="utf-8")
cross_match = re.fullmatch(r"(window\.BANGKOK_MARKET_CROSSCHECKS\s*=\s*)(\[.*\])(\s*;?\s*)", cross_text, re.S)
if not cross_match:
    raise RuntimeError("Unexpected market cross-check data format")
cross_rows = json.loads(cross_match.group(2))
cross_record = {
    "hipflatId": PROJECT_ID,
    "projectName": "InterLux Premier Sukhumvit 13",
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub / DDproperty",
    "projectSourceUrl": PROPERTYHUB_SALE,
    "sale": {
        "activeListingCount": 28,
        "sourceUrl": PROPERTYHUB_SALE,
        "listings": [
            {"listingId": "5051423", "price": 6_500_000, "area": 57, "priceSqm": 114_035, "bedrooms": 2, "listedAt": "2026-10-14", "url": SALE_LOWEST, "sourceName": "PropertyHub"},
            {"listingId": "6102633", "price": 6_700_000, "area": 49.34, "priceSqm": 135_792, "bedrooms": 2, "listedAt": "2026-10-14", "url": SALE_6700, "sourceName": "PropertyHub"},
            {"listingId": "4915029", "price": 7_200_000, "area": 50, "priceSqm": 144_000, "bedrooms": 2, "listedAt": "2026-10-14", "url": SALE_7200, "sourceName": "PropertyHub"},
        ],
        "note": "PropertyHub 專案頁顯示 28 筆出售；所列為可直接開啟的三筆兩房樣本，最低總價為 ฿6,500,000／57㎡。",
    },
    "rent": {
        "activeListingCount": 43,
        "sourceUrl": PROPERTYHUB_RENT,
        "listings": [
            {"listingId": "500570288", "price": 35_000, "area": 58, "priceSqm": 603, "bedrooms": 2, "listedAt": "2026-09-19", "url": RENT_35000, "sourceName": "DDproperty"},
        ],
        "note": "PropertyHub 專案頁顯示 43 筆出租；另核到 DDproperty 兩房單筆於 2026-09-19 刊登，頁面目前仍可見。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "專案身分與 Sukhumvit 13 地址；地圖座標沿用已核實的 PropertyScout 專案點位。"},
        {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE, "statusLabel": "28 筆出售；2026-10-14 刷新中包含三筆兩房直達掛牌。"},
        {"sourceName": "PropertyHub 最低兩房售盤", "url": SALE_LOWEST, "statusLabel": "฿6,500,000／57㎡，兩房，專案頁顯示 2026-10-14 刷新。"},
        {"sourceName": "DDproperty 兩房租盤", "url": RENT_35000, "statusLabel": "฿35,000／月／58㎡，兩房，2026-09-19 刊登；頁面仍列出。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "專案頁顯示 43 筆出租。"},
        {"sourceName": "PropertyScout 房型行情與座標", "url": PROPERTYSCOUT_PROJECT, "statusLabel": "已核實地圖點位；兩房出租房型行情約 ฿600／㎡／月，可與單筆租盤交叉比較。"},
        {"sourceName": "PropertyHub 管理費", "url": FEE_SOURCE, "statusLabel": "專案頁標示 Utility Fee ฿50／㎡；管理費口徑應再向管委會確認。"},
    ],
    "yieldStatus": "calculated_estimate",
    "yieldEstimate": {
        "bedrooms": 2,
        "salePrice": 6_500_000,
        "saleAreaSqm": 57,
        "rentRatePerSqmPerMonth": 35_000 / 58,
        "estimatedMonthlyRent": 34_397,
        "feePerSqmPerMonth": 50,
        "netYieldWithOneAgentMonthPercent": 5.29,
        "netYieldWithoutAgentMonthPercent": 5.82,
        "rentRateSourceUrl": RENT_35000,
        "saleSampleUrl": SALE_LOWEST,
        "directRentSampleUrl": RENT_35000,
    },
    "yieldNote": "兩房最低出售樣本 ฿6,500,000／57㎡；兩房直接租盤為 ฿35,000／月／58㎡，換算租金單價後套用最低售盤面積，月租估算 ฿34,397。扣除管理費 ฿50／㎡／月後，扣一個月仲介費的淨年投報約 5.29%；不扣仲介費約 5.82%。PropertyScout 兩房行情約 ฿600／㎡／月，作為交叉參考。未含稅、維修與交易成本。",
}
index = next((i for i, row in enumerate(cross_rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if index is None:
    cross_rows.append(cross_record)
else:
    cross_rows[index] = cross_record
cross_path.write_text(cross_match.group(1) + json.dumps(cross_rows, ensure_ascii=False, separators=(",", ":")) + cross_match.group(3), encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": "InterLux Premier Sukhumvit 13",
    "checkedAt": CHECKED_AT,
    "identity": {
        "hipflatProjectUrl": HIPFLAT,
        "address": "61 Sukhumvit Rd, Khlong Toei Nuea, Vadhana, Bangkok 10110",
        "coordinates": {"lat": 13.747672, "lng": 100.558301, "source": PROPERTYSCOUT_PROJECT, "verification": "Existing verified project coordinate retained."},
        "completionYearSources": {"PropertyScout_and_direct_DDproperty": 2014, "PropertyHub_project_page": 2016, "status": "conflict; app's existing PropertyScout year is retained pending authoritative developer confirmation"},
        "utilityFeeBahtPerSqm": {"rate": 50, "source": FEE_SOURCE, "status": "public figure; confirm actual juristic-person charge"},
    },
    "sale": {"lowestTwoBedroom": {"price": 6_500_000, "areaSqm": 57, "pricePerSqm": 114_035, "bedrooms": 2, "updated": "2026-10-14", "url": SALE_LOWEST}, "additionalSamples": sale_samples[1:]},
    "rent": {"directSample": {"monthlyRent": 35_000, "areaSqm": 58, "rentPerSqm": 603, "bedrooms": 2, "listedAt": "2026-09-19", "url": RENT_35000}, "twoBedroomSummaryRateBahtPerSqm": 600, "summarySource": PROPERTYSCOUT_PROJECT},
    "yield": {"calculated": True, "formula": "((฿35,000 ÷ 58㎡) × 57㎡ × 11 − ฿50/㎡/月 × 57㎡ × 12) ÷ ฿6,500,000 × 100", "withOneAgentMonthPercent": 5.29, "withoutAgentMonthPercent": 5.82},
    "sources": [HIPFLAT, PROPERTYHUB_PROJECT, PROPERTYHUB_SALE, PROPERTYHUB_RENT, PROPERTYSCOUT_PROJECT, SALE_LOWEST, SALE_6700, SALE_7200, RENT_35000],
}
(ROOT / "reports/interlux-premier-sukhumvit-13-market-samples-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Recorded three current two-bedroom sale listings, one direct two-bedroom rent listing, public fee, and a matched-room net-yield estimate.")
