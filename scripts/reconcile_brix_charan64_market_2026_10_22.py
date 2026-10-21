"""Refresh Brix Condominium Charan 64 with current exact-project listings."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3199
NAME = "Brix Condominium Charan 64"
AS_OF = "2026-10-22"
SALE_PAGE = "https://propertyhub.in.th/en/condo-for-sale/project-brix-condominium"
RENT_PAGE = "https://propertyhub.in.th/en/condo-for-rent/project-brix-condominium"

SALE_ROWS = [
    # The exact project card calls this a Studio, but the linked item summary says 1 Bed.
    # Keep its verified total price and area for project-wide display, but exclude it
    # from bedroom-specific ROI calculations until the room type is reconciled.
    {"id": "4751629", "price": 1_850_000, "area": 22,
     "title": "Brix Condominium · ฿1,850,000 · 22 ㎡ · 房型標示不一致",
     "url": "https://propertyhub.in.th/en/listings/for-sale-brix-condominium--abd7096f---4751629",
     "updated": "2026-10-21", "beds": None,
     "roomType": "房型待核（專案卡標示 Studio，單筆頁摘要標示 1 Bed）",
     "listingStatus": "active_as_listed", "bedroomStatus": "conflicting_source_labels"},
    {"id": "6322301", "price": 2_200_000, "area": 27,
     "title": "Brix Condominium · 1 房 · 27 ㎡ · ฿2,200,000",
     "url": "https://propertyhub.in.th/en/listings/for-sale-brix-condominium-condo-only-2-200-000-thb---6322301",
     "updated": "2026-10-18", "beds": 1, "roomType": "1 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "4384326", "price": 3_450_000, "area": 34.6,
     "title": "Brix Condominium · 1 房 · 34.6 ㎡ · ฿3,450,000",
     "url": "https://propertyhub.in.th/en/listings/condo-for-sale-brix-condo-charansanitwong-64-1-bedroom-35-sqm-newly-renovated-fully-furnished-next-to-mrt-sirindhorn-mf23s-020---4384326",
     "updated": "2026-10-21", "beds": 1, "roomType": "1 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "6244624", "price": 4_200_000, "area": 42,
     "title": "Brix Condominium · 2 房 · 42 ㎡ · ฿4,200,000",
     "url": "https://propertyhub.in.th/en/listings/for-sale-brix-condominium-charan-64-connected-to-mrt-sirindhorn-station---6244624",
     "updated": "2026-10-20", "beds": 2, "roomType": "2 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "6424367", "price": 4_800_000, "area": 52.48,
     "title": "Brix Condominium · 2 房 · 52.48 ㎡ · ฿4,800,000",
     "url": "https://propertyhub.in.th/en/listings/40m-to-mrt-sirindhorn-2-br-at-brix-condominium-id-3119314---6424367",
     "updated": "2026-10-21", "beds": 2, "roomType": "2 Bedroom",
     "listingStatus": "active_as_listed"},
]

RENT_ROWS = [
    {"id": "1605556", "price": 10_500, "area": 25,
     "title": "Brix Condominium · 1 房 · 25 ㎡ · ฿10,500/月",
     "url": "https://propertyhub.in.th/en/listings/for-rent-brix-condominium-1-bed-25-sq-m-24th-floor--9d87088f---1605556",
     "updated": "2026-10-21", "beds": 1, "roomType": "1 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "4948603", "price": 11_000, "area": 30,
     "title": "Brix Condominium · 1 房 · 30 ㎡ · ฿11,000/月",
     "url": "https://propertyhub.in.th/en/listings/r2599-for-rent-brix-condominium-charan-64---4948603",
     "updated": "2026-10-21", "beds": 1, "roomType": "1 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "5172054", "price": 14_000, "area": 40,
     "title": "Brix Condominium · 1 房 · 40 ㎡ · ฿14,000/月",
     "url": "https://propertyhub.in.th/en/listings/mn2730-brix-condominium-full-furnitured---5172054",
     "updated": "2026-10-08", "beds": 1, "roomType": "1 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "6410879", "price": 18_000, "area": 43,
     "title": "Brix Condominium · 2 房 · 43 ㎡ · ฿18,000/月",
     "url": "https://propertyhub.in.th/en/listings/mn3885-brix-condominium-full-furnitured-and-electrical---6410879",
     "updated": "2026-10-08", "beds": 2, "roomType": "2 Bedroom",
     "listingStatus": "active_as_listed"},
    {"id": "5943031", "price": 22_000, "area": 52.2,
     "title": "Brix Condominium · 2 房 · 52.2 ㎡ · ฿22,000/月",
     "url": "https://propertyhub.in.th/en/listings/2-bedroom-condo-for-rent-brix-condominium---5943031",
     "updated": "2026-10-21", "beds": 2, "roomType": "2 Bedroom",
     "listingStatus": "active_as_listed"},
]


def read_array(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text[text.index("["):text.rindex("]") + 1])


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def normalized_sample(row: dict, kind: str) -> dict:
    sample = {
        **row,
        "priceSqm": round(row["price"] / row["area"]),
        "sourceName": "PropertyHub",
        "projectName": "Brix Condominium",
        "checkedAt": AS_OF,
        "matchedBy": "Live exact-project listing card and direct listing detail both identify Brix Condominium; price, area, and room type cross-checked.",
    }
    if row.get("bedroomStatus"):
        sample["matchedBy"] = "Exact project card and direct item both identify Brix Condominium and match price/area; the two pages disagree on Studio versus 1 Bed, so this sample is excluded from room-specific ROI."
    return sample


sales = [normalized_sample(row, "sale") for row in SALE_ROWS]
rents = [normalized_sample(row, "rent") for row in RENT_ROWS]
sale_prices = [row["price"] for row in SALE_ROWS]
sale_rates = [row["price"] / row["area"] for row in SALE_ROWS]
rent_prices = [row["price"] for row in RENT_ROWS]
rent_rates = [row["price"] / row["area"] for row in RENT_ROWS]


def by_bedroom(rows: list[dict], beds: int, is_rent: bool) -> dict:
    items = [row for row in rows if row.get("beds") == beds]
    lowest_total = min(items, key=lambda row: row["price"])
    lowest_rate = min(items, key=lambda row: row["price"] / row["area"])
    return {
        "count": len(items), "minimum": lowest_total["price"],
        "area": lowest_total["area"], "minimumArea": lowest_total["area"],
        "priceSqm": round(lowest_total["price"] / lowest_total["area"]),
        "minimumSqm": round(lowest_rate["price"] / lowest_rate["area"], 2),
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "sourceUrl": lowest_total["url"],
    }


sale = {
    "count": len(sales), "observedCount": len(sales),
    "countKind": "manual_verified_listing",
    "average": round(sum(sale_prices) / len(sale_prices)),
    "minimum": min(sale_prices), "minimumArea": 22,
    "minimumSampleUpdated": "2026-10-21",
    "averageSqm": round(sum(sale_rates) / len(sale_rates)),
    "minimumSqm": round(min(sale_rates), 2),
    "minimumSqmSampleUpdated": "2026-10-18",
    "asOf": AS_OF, "sourceName": "PropertyHub 專案頁與單筆掛牌",
    "source": SALE_PAGE,
    "minimumSourceUrl": SALE_ROWS[0]["url"],
    "minimumSqmSourceUrl": SALE_ROWS[1]["url"],
    "samples": sales,
    "byBedroom": {"1": by_bedroom(SALE_ROWS, 1, False),
                   "2": by_bedroom(SALE_ROWS, 2, False)},
    "availabilityNote": "專案頁顯示 15 筆出售結果；本批納入 5 筆不同單筆連結。最低總價卡片標示 Studio，但單筆頁摘要標示 1 Bed，保留總價與面積、排除房型投報。",
}

rent = {
    "count": len(rents), "observedCount": len(rents),
    "countKind": "manual_verified_listing",
    "average": round(sum(rent_prices) / len(rent_prices)),
    "minimum": min(rent_prices), "minimumArea": 25,
    "minimumSampleUpdated": "2026-10-21",
    "averageSqm": round(sum(rent_rates) / len(rent_rates)),
    "minimumSqm": round(min(rent_rates), 2),
    "minimumSqmSampleUpdated": "2026-10-08",
    "asOf": AS_OF, "sourceName": "PropertyHub 專案頁與單筆掛牌",
    "source": RENT_PAGE,
    "minimumSourceUrl": RENT_ROWS[0]["url"],
    "minimumSqmSourceUrl": RENT_ROWS[2]["url"],
    "samples": rents,
    "byBedroom": {"1": by_bedroom(RENT_ROWS, 1, True),
                   "2": by_bedroom(RENT_ROWS, 2, True)},
    "availabilityNote": "專案頁顯示 71 筆出租結果；本批抽核 5 筆不同單筆連結，包含各房型最低總租金與最低每㎡租金樣本。",
}

fee = {"rate": 50, "status": "published_indicative",
       "note": "PropertyHub 專案頁列管理費 ฿50/㎡/月；請向管委會確認現行費率。",
       "source": "https://propertyhub.in.th/en/projects/brix-condominium"}


def yield_estimate(beds: int) -> dict:
    purchase = sale["byBedroom"][str(beds)]
    rental = rent["byBedroom"][str(beds)]
    monthly_rent = round(rental["minimumSqm"] * purchase["area"])
    price = purchase["minimum"]
    annual_common_fee = fee["rate"] * purchase["area"] * 12
    return {
        "bedrooms": beds,
        "purchasePriceThb": price,
        "purchaseAreaSqm": purchase["area"],
        "purchaseListingUrl": purchase["minimumSourceUrl"],
        "minimumSameBedroomRentThbPerSqmMonth": rental["minimumSqm"],
        "rentRateListingUrl": rental["minimumSqmSourceUrl"],
        "estimatedMonthlyRentAtPurchaseAreaThb": monthly_rent,
        "grossAnnualYieldPercent": round(monthly_rent * 12 / price * 100, 2),
        "afterOneAgentMonthPercent": round(monthly_rent * 11 / price * 100, 2),
        "afterCommonFeePercent": round((monthly_rent * 12 - annual_common_fee) / price * 100, 2),
        "afterCommonFeeAndOneAgentMonthPercent": round(
            (monthly_rent * 11 - annual_common_fee) / price * 100, 2),
        "formula": "monthly rent = lowest same-bedroom rent THB/sqm/month × lowest same-bedroom sale listing area; annual yield = annual rent / exact sale price",
    }

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual_rows = [row for row in read_array(manual_path)
               if int(row.get("hipflatId", -1)) != PROJECT_ID]
manual_rows.append({"hipflatId": PROJECT_ID, "name": NAME, "asOf": AS_OF,
                    "replaceSale": True, "replaceRent": True,
                    "sale": sale, "rent": rent, "fee": fee})
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

crosscheck_path = ROOT / "dist/bangkok-market-crosschecks.js"
crosschecks = [row for row in read_array(crosscheck_path)
               if int(row.get("hipflatId", -1)) != PROJECT_ID]
crosschecks.append({
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "PropertyHub", "projectSourceUrl": SALE_PAGE,
    "sale": {"activeListingCount": 15, "displayedResultCount": 15,
             "sourceUrl": SALE_PAGE,
             "note": "專案頁 15 筆出售結果中，抽核 5 筆不同單筆連結；總價最低卡片的房型標籤與單筆頁摘要不一致，未用於房型投報。",
             "listings": [{"url": x["url"], "bedrooms": x.get("beds"),
                           "price": x["price"], "area": x["area"],
                           "priceSqm": round(x["price"] / x["area"]),
                           "listedAt": x["updated"],
                           "statusLabel": "房型標示不一致；不作房型投報" if x.get("bedroomStatus") else "單筆頁與專案卡核對"}
                          for x in SALE_ROWS]},
    "rent": {"activeListingCount": 71, "displayedResultCount": 71,
             "sourceUrl": RENT_PAGE,
             "note": "專案頁 71 筆出租結果中，抽核 5 筆不同單筆連結，涵蓋一房與兩房樣本。",
             "listings": [{"url": x["url"], "bedrooms": x["beds"],
                           "price": x["price"], "area": x["area"],
                           "priceSqm": round(x["price"] / x["area"]),
                           "listedAt": x["updated"],
                           "statusLabel": "單筆頁與專案卡核對"}
                          for x in RENT_ROWS]},
    "availabilitySources": [
        {"sourceName": "PropertyHub 出售專案頁", "url": SALE_PAGE,
         "statusLabel": "即時專案頁顯示 15 筆出售結果；本次抽核 5 個不同單筆連結。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": RENT_PAGE,
         "statusLabel": "即時專案頁顯示 71 筆出租結果；本次抽核 5 個不同單筆連結。"},
        {"sourceName": "PropertyHub 專案資訊", "url": fee["source"],
         "statusLabel": "完工年 2018；管理費標示 ฿50/㎡/月。"},
    ],
    "yieldStatus": "calculable",
    "yieldNote": "1 房與 2 房分別以同房型最低售價樣本、其單筆面積、同房型最低每㎡租金估算；Studio 標示不一致的最低總價樣本不參與房型投報。",
})
write_array(crosscheck_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "project": NAME, "hipflatId": PROJECT_ID, "checkedAt": AS_OF,
    "sources": {"saleProject": SALE_PAGE, "rentProject": RENT_PAGE,
                "projectDetails": fee["source"]},
    "displayedResults": {"sale": 15, "rent": 71},
    "saleSamples": sales, "rentSamples": rents,
    "saleSummary": {"minimumTotalThb": sale["minimum"],
                    "minimumPricePerSqmThb": sale["minimumSqm"],
                    "oneBedroomMinimum": sale["byBedroom"]["1"],
                    "twoBedroomMinimum": sale["byBedroom"]["2"]},
    "rentSummary": {"minimumMonthlyThb": rent["minimum"],
                    "minimumMonthlyPerSqmThb": rent["minimumSqm"],
                    "oneBedroomMinimum": rent["byBedroom"]["1"],
                    "twoBedroomMinimum": rent["byBedroom"]["2"]},
    "fee": fee,
    "yieldEstimates": {"1": yield_estimate(1), "2": yield_estimate(2)},
    "notes": [
        "All included direct listing URLs returned HTTP 200 on 2026-10-22; displayed price, area, bedroom count, and project name were checked against the listing detail page.",
        "The 2-bedroom sale ID 6424367 detail page states 52.48 sqm; that exact area is used rather than the rounded 52.5 sqm shown in the project card.",
        "The lowest-total sale listing ID 4751629 is 22 sqm and ฿1,850,000; the exact project card says Studio while the direct summary says 1 Bed. It is excluded from bedroom-specific ROI until resolved.",
        "Only five distinct direct links per market were selected from 15 sale and 71 rental results; this is a verified sample, not a deduplicated census of all project listings.",
    ],
}
(ROOT / "reports/brix-charan64-market-reconciliation-2026-10-22.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index_path = ROOT / "dist/index.html"
html = index_path.read_text(encoding="utf-8")
html = html.replace("bangkok-manual-market-samples.js?v=20261020-supapong-reconciled",
                    "bangkok-manual-market-samples.js?v=20261022-brix-market-reconciled")
html = html.replace("bangkok-market-crosschecks.js?v=20261020-supapong-reconciled",
                    "bangkok-market-crosschecks.js?v=20261022-brix-market-reconciled")
index_path.write_text(html, encoding="utf-8")

print(json.dumps({
    "hipflatId": PROJECT_ID, "saleSamples": len(sales), "rentSamples": len(rents),
    "saleMinimum": sale["minimum"], "saleMinimumSqm": sale["minimumSqm"],
    "oneBedPurchase": sale["byBedroom"]["1"]["minimum"],
    "twoBedPurchase": sale["byBedroom"]["2"]["minimum"],
    "oneBedRentSqm": rent["byBedroom"]["1"]["minimumSqm"],
    "twoBedRentSqm": rent["byBedroom"]["2"]["minimumSqm"],
    "fee": fee["rate"],
}, ensure_ascii=False))
