"""Refresh Supapong Place market samples against live PropertyHub project pages."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3765
NAME = "Supapong Place"
AS_OF = "2026-10-20"
SALE_PAGE = "https://propertyhub.in.th/en/condo-for-sale/project-supapong-place"
RENT_PAGE = "https://propertyhub.in.th/en/condo-for-rent/project-supapong-place"
LOWEST_SALE = "https://propertyhub.in.th/en/listings/s-sppp101-line-p2nproperty---4550347"
TWO_BED_SALE = "https://propertyhub.in.th/en/listings/a033874-supapong-place---6005652"


def read_array(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text[text.index("["):text.rindex("]") + 1])


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_samples = [
    {
        "id": "4550347", "price": 1_499_000, "area": 30.5,
        "priceSqm": 49_148, "beds": 1, "roomType": "ONE_BED_ROOM",
        "title": "Supapong Place · 1BR · 30.5 sqm · ฿1,499,000",
        "url": LOWEST_SALE, "sourceName": "PropertyHub",
        "projectName": NAME, "updated": "2026-10-16", "checkedAt": AS_OF,
        "matchedBy": "Exact PropertyHub project page and direct listing both identify Supapong Place; direct listing states 1 bedroom, 30.5 sqm, ฿1,499,000.",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6005652", "price": 2_400_000, "area": 60,
        "priceSqm": 40_000, "beds": 2, "roomType": "TWO_BED_ROOM",
        "title": "Supapong Place · 2BR · 60 sqm · ฿2,400,000",
        "url": TWO_BED_SALE, "sourceName": "PropertyHub",
        "projectName": NAME, "updated": "2026-10-17", "checkedAt": AS_OF,
        "matchedBy": "Exact PropertyHub project page and direct listing both identify Supapong Place; direct listing states 2 bedrooms, 60 sqm, ฿2,400,000.",
        "listingStatus": "active_as_listed",
    },
]

sale = {
    "count": 2, "observedCount": 2, "countKind": "manual_verified_listing",
    "average": 1_949_500, "minimum": 1_499_000, "minimumArea": 30.5,
    "minimumSampleUpdated": "2026-10-16", "averageSqm": 44_574,
    "minimumSqm": 40_000, "minimumSqmSampleUpdated": "2026-10-17",
    "asOf": AS_OF, "sourceName": "PropertyHub 專案頁與單筆掛牌",
    "source": SALE_PAGE, "minimumSourceUrl": LOWEST_SALE,
    "minimumSqmSourceUrl": TWO_BED_SALE, "samples": sale_samples,
    "byBedroom": {
        "1": {"count": 1, "minimum": 1_499_000, "area": 30.5,
              "minimumArea": 30.5, "priceSqm": 49_148,
              "minimumSqm": 49_148, "minimumSourceUrl": LOWEST_SALE,
              "sourceUrl": LOWEST_SALE},
        "2": {"count": 1, "minimum": 2_400_000, "area": 60,
              "minimumArea": 60, "priceSqm": 40_000,
              "minimumSqm": 40_000, "minimumSourceUrl": TWO_BED_SALE,
              "sourceUrl": TWO_BED_SALE},
    },
    "availabilityNote": "專案頁共顯示 10 張出售卡片；其中同一物件有重複卡片，本次只納入兩筆可由唯一單筆連結識別的掛牌。",
}

rent = {
    "count": 0, "observedCount": 0,
    "countKind": "manual_project_availability_check",
    "minimum": 0, "minimumSqm": 0, "asOf": AS_OF,
    "sourceName": "PropertyHub 專案出租頁",
    "source": RENT_PAGE, "samples": [],
    "availabilityNote": "2026-10-20 現查專案出租頁顯示 No matched properties for Rent；不以舊出租樣本計算投報。",
}

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual = read_array(manual_path)
manual = [row for row in manual if int(row.get("hipflatId", -1)) != PROJECT_ID]
manual.append({"hipflatId": PROJECT_ID, "name": NAME, "asOf": AS_OF,
               "replaceSale": True, "replaceRent": True,
               "sale": sale, "rent": rent})
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

crosscheck_path = ROOT / "dist/bangkok-market-crosschecks.js"
crosschecks = read_array(crosscheck_path)
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != PROJECT_ID]
crosschecks.append({
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "PropertyHub",
    "projectSourceUrl": SALE_PAGE,
    "sale": {"activeListingCount": 10, "displayedResultCount": 10,
              "sourceUrl": SALE_PAGE,
              "note": "頁面顯示 10 張卡片；目前只保留兩筆有唯一單筆頁可核實的掛牌，排除重複卡片。",
              "listings": [
                  {"url": LOWEST_SALE, "bedrooms": 1, "price": 1_499_000,
                   "area": 30.5, "priceSqm": 49_148, "listedAt": "2026-10-16",
                   "statusLabel": "單筆頁與專案頁吻合"},
                  {"url": TWO_BED_SALE, "bedrooms": 2, "price": 2_400_000,
                   "area": 60, "priceSqm": 40_000, "listedAt": "2026-10-17",
                   "statusLabel": "單筆頁與專案頁吻合"},
              ]},
    "rent": {"activeListingCount": 0, "displayedResultCount": 0,
             "sourceUrl": RENT_PAGE, "checkedAt": AS_OF,
             "note": "即時專案出租頁顯示 No matched properties for Rent。"},
    "availabilitySources": [
        {"sourceName": "PropertyHub 出售專案頁", "url": SALE_PAGE,
         "statusLabel": "頁面顯示 10 張卡片；核入兩筆唯一單筆連結可核實的掛牌。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": RENT_PAGE,
         "statusLabel": "2026-10-20 即時查核：No matched properties for Rent。"},
        {"sourceName": "PropertyHub 出售單筆", "url": LOWEST_SALE,
         "statusLabel": "1 房、30.5 ㎡、฿1,499,000；專案與房型吻合。"},
        {"sourceName": "PropertyHub 出售單筆", "url": TWO_BED_SALE,
         "statusLabel": "2 房、60 ㎡、฿2,400,000；頁面更新於 2026-10-17。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "現行出租專案頁無匹配掛牌；保留舊租金來源但不作現行樣本，不計投報率。",
})
write_array(crosscheck_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "project": NAME, "hipflatId": PROJECT_ID, "checkedAt": AS_OF,
    "sources": {"saleProject": SALE_PAGE, "rentProject": RENT_PAGE,
                "lowestSaleListing": LOWEST_SALE, "twoBedroomSaleListing": TWO_BED_SALE},
    "sale": {"projectPageDisplayedCards": 10,
             "deduplicatedDirectListings": [
                 {"id": "4550347", "bedrooms": 1, "priceThb": 1_499_000,
                  "areaSqm": 30.5, "updated": "2026-10-16"},
                 {"id": "6005652", "bedrooms": 2, "priceThb": 2_400_000,
                  "areaSqm": 60, "updated": "2026-10-17"}],
             "note": "Only direct listing URLs independently identified and checked against the exact project page are counted; duplicate cards are omitted."},
    "rent": {"activeMatchedListingCount": 0,
             "evidence": "Live exact-project page returned No matched properties for Rent on 2026-10-20.",
             "url": RENT_PAGE},
    "yield": {"status": "not_calculated",
              "note": "No current same-project rent listing is available to support an ROI estimate."},
}
(ROOT / "reports/supapong-place-market-reconciliation-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index_path = ROOT / "dist/index.html"
html = index_path.read_text(encoding="utf-8")
html = html.replace("bangkok-manual-market-samples.js?v=20261020-sirin-market-reconciled",
                    "bangkok-manual-market-samples.js?v=20261020-supapong-reconciled")
html = html.replace("bangkok-market-crosschecks.js?v=20261020-sirin-market-reconciled",
                    "bangkok-market-crosschecks.js?v=20261020-supapong-reconciled")
index_path.write_text(html, encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "saleSamples": len(sale_samples),
                  "saleMinimum": sale["minimum"], "twoBedroomMinimum": sale["byBedroom"]["2"]["minimum"],
                  "rentListings": rent["count"], "yield": "not_calculated"}, ensure_ascii=False))
