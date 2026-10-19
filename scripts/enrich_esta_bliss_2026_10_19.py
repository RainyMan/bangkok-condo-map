from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3473
NAME = "Esta Bliss"
AS_OF = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/esta-bliss-iffskg"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/esta-bliss-ramintra--add50a04"
PROPERTYHUB_SALE = "https://assets3.propertyhub.in.th/en/condo-for-sale/project-esta-bliss-ramintra--add50a04"
PROPERTYHUB_RENT = "https://assets3.propertyhub.in.th/en/condo-for-rent/project-esta-bliss-ramintra--add50a04"
SALE_2190 = "https://propertyhub.in.th/en/listings/sale-esta-bliss-ramintra-minburi-brand-new-never-occupied-unblocked-view-fully-furnished-ready-to-move-in-near-mrt-pink-line"
SALE_2900 = "https://propertyhub.in.th/en/listings/for-sell-condo-esta-bliss-building-b-floor-8-2-bed-room-room-size-47-sqm--a37608e7"
RENT_12000 = "https://propertyhub.in.th/en/listings/condo-for-rent-esta-bliss-ramintra-property-code-lnp-c14784"
COORD_SOURCE = "https://www.homenayoo.com/esta-bliss/"
COORD_CROSSCHECK = "https://www.bangkokre.com/projects/1323"
DEVELOPER_DISCLOSURE = "https://www.thaibma.or.th/Download/prospetus/ASW277A/%283%29130201_25680702.pdf"


def load_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot read {symbol}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_samples = [
    {
        "id": "ph-esta-bliss-sale-2190000",
        "price": 2_190_000,
        "area": 36.07,
        "priceSqm": round(2_190_000 / 36.07),
        "beds": 2,
        "roomType": "TWO_BED_ROOM",
        "title": "Esta Bliss Ramintra，2 房，36.07 ㎡，฿2,190,000",
        "url": SALE_2190,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "updated": "2026-10-02",
        "checkedAt": AS_OF,
        "matchedBy": "PropertyHub exact-project feed names Esta Bliss Ramintra and lists this individual two-bedroom unit at 36.07 sqm for THB 2,190,000.",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
    {
        "id": "a37608e7",
        "price": 2_900_000,
        "area": 47,
        "priceSqm": round(2_900_000 / 47),
        "beds": 2,
        "roomType": "TWO_BED_ROOM",
        "title": "Esta Bliss Ramintra，2 房，47 ㎡，฿2,900,000",
        "url": SALE_2900,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "updated": "2026-10-02",
        "checkedAt": AS_OF,
        "matchedBy": "PropertyHub exact-project feed names Esta Bliss Building B and lists this individual two-bedroom unit at 47 sqm for THB 2,900,000.",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
]
rent_samples = [
    {
        "id": "lnp-c14784",
        "price": 12_000,
        "area": 36,
        "priceSqm": round(12_000 / 36),
        "beds": 2,
        "roomType": "TWO_BED_ROOM",
        "title": "Esta Bliss Ramintra，2 房，36 ㎡，฿12,000/月",
        "url": RENT_12000,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "updated": "2026-10-02",
        "checkedAt": AS_OF,
        "matchedBy": "PropertyHub exact-project feed names Esta Bliss Ramintra Property Code LNP-C14784 and lists this two-bedroom unit at 36 sqm for THB 12,000 per month.",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }
]

sale_min = min(sale_samples, key=lambda row: row["price"])
sale_min_sqm = min(sale_samples, key=lambda row: row["priceSqm"])
rent_min = min(rent_samples, key=lambda row: row["price"])
rent_min_sqm = min(rent_samples, key=lambda row: row["priceSqm"])
sale_avg = round(sum(row["price"] for row in sale_samples) / len(sale_samples))
sale_avg_sqm = round(sum(row["priceSqm"] for row in sale_samples) / len(sale_samples))
rent_avg = round(sum(row["price"] for row in rent_samples) / len(rent_samples))
rent_avg_sqm = round(sum(row["priceSqm"] for row in rent_samples) / len(rent_samples))

manual = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
entry = next((row for row in manual if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if entry is None:
    entry = {"hipflatId": PROJECT_ID, "name": NAME}
    manual.append(entry)
entry.update({
    "asOf": AS_OF,
    "fee": {
        "rate": 50,
        "status": "published_indicative",
        "source": HIPFLAT,
        "note": "Hipflat 專案頁列 ฿50/㎡；PropertyHub 列 ฿45/㎡，來源數字不一致且均未註明收費週期。投報試算暫以較高的 ฿50/㎡作參考，請向管委會確認實際月費。",
    },
    "sale": {
        "count": 48,
        "observedCount": len(sale_samples),
        "countKind": "manual_verified_listing",
        "average": sale_avg,
        "minimum": sale_min["price"],
        "minimumArea": sale_min["area"],
        "minimumSampleUpdated": sale_min["updated"],
        "averageSqm": sale_avg_sqm,
        "minimumSqm": sale_min_sqm["priceSqm"],
        "minimumSqmSampleUpdated": sale_min_sqm["updated"],
        "asOf": AS_OF,
        "sourceName": "PropertyHub 直接出售掛牌",
        "source": PROPERTYHUB_SALE,
        "minimumSourceUrl": sale_min["url"],
        "minimumSqmSourceUrl": sale_min_sqm["url"],
        "byBedroom": {
            "2": {
                "count": len(sale_samples),
                "minimum": sale_min["price"],
                "area": sale_min["area"],
                "minimumArea": sale_min["area"],
                "priceSqm": sale_min["priceSqm"],
                "minimumSqm": sale_min_sqm["priceSqm"],
                "sourceUrl": sale_min["url"],
                "minimumSourceUrl": sale_min["url"],
                "minimumSqmSourceUrl": sale_min_sqm["url"],
            }
        },
        "samples": sale_samples,
    },
    "rent": {
        "count": 75,
        "observedCount": len(rent_samples),
        "countKind": "manual_verified_listing",
        "average": rent_avg,
        "minimum": rent_min["price"],
        "minimumArea": rent_min["area"],
        "minimumSampleUpdated": rent_min["updated"],
        "averageSqm": rent_avg_sqm,
        "minimumSqm": rent_min_sqm["priceSqm"],
        "minimumSqmSampleUpdated": rent_min_sqm["updated"],
        "asOf": AS_OF,
        "sourceName": "PropertyHub 直接出租掛牌",
        "source": PROPERTYHUB_RENT,
        "minimumSourceUrl": rent_min["url"],
        "minimumSqmSourceUrl": rent_min_sqm["url"],
        "byBedroom": {
            "2": {
                "count": len(rent_samples),
                "minimum": rent_min["price"],
                "area": rent_min["area"],
                "minimumArea": rent_min["area"],
                "priceSqm": rent_min["priceSqm"],
                "minimumSqm": rent_min_sqm["priceSqm"],
                "averageSqm": rent_avg_sqm,
                "sourceUrl": rent_min["url"],
                "minimumSourceUrl": rent_min["url"],
                "minimumSqmSourceUrl": rent_min_sqm["url"],
            }
        },
        "samples": rent_samples,
    },
    "replaceSale": True,
    "replaceRent": True,
})
manual.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

coords = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coords = [row for row in coords if int(row.get("hipflatId", -1)) != PROJECT_ID]
coords.append({
    "hipflatId": PROJECT_ID,
    "name": NAME,
    "lat": 13.812556,
    "lng": 100.715134,
    "locationVerified": True,
    "sourceName": "Homenayoo Google Maps 座標",
    "sourceUrl": COORD_SOURCE,
    "verificationSourceUrl": COORD_CROSSCHECK,
    "verificationMethod": "Homenayoo explicitly publishes Google Maps coordinates 13.812556,100.715134 for Esta Bliss. BangkokRE independently identifies the same project and publishes 13.812165,100.715068 (about 44 m away); both pins fall within the same project site area.",
    "addressMatch": "Esta Bliss, Ram Inthra Road / Soi Ram Inthra 88, Min Buri, Bangkok 10510",
})
coords.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coords)

catalogue = load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
project = next(row for row in catalogue if int(row["id"]) == PROJECT_ID)
project.update({
    "completedYear": 2016,
    "completedYearSourceUrl": HIPFLAT,
    "floors": 8,
    "units": 634,
    "locationVerified": True,
    "locationSourceUrl": COORD_SOURCE,
    "locationVerificationSourceUrl": COORD_CROSSCHECK,
    "marketDataStatus": "manual_verified_individual_listings",
    "dataCompleteness": {"coordinates": True, "saleSample": True, "rentSample": True, "yield": True},
})
save_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", catalogue)

crosschecks = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next((row for row in crosschecks if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID, "projectName": NAME}
    crosschecks.append(cross)
cross.update({
    "projectName": NAME,
    "asOf": AS_OF,
    "sourceName": "PropertyHub / Hipflat",
    "projectSourceUrl": PROPERTYHUB_PROJECT,
    "sale": {
        "activeListingCount": 48,
        "sourceUrl": PROPERTYHUB_SALE,
        "listings": [
            {"id": row["id"], "price": row["price"], "area": row["area"], "priceSqm": row["priceSqm"], "bedrooms": 2, "title": row["title"], "url": row["url"], "listedAt": row["updated"]}
            for row in sale_samples
        ],
    },
    "rent": {
        "activeListingCount": 75,
        "sourceUrl": PROPERTYHUB_RENT,
        "listings": [
            {"id": row["id"], "price": row["price"], "area": row["area"], "priceSqm": row["priceSqm"], "bedrooms": 2, "title": row["title"], "url": row["url"], "listedAt": row["updated"]}
            for row in rent_samples
        ],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "地址相符；列 2016 年完工、8 層。Hipflat 的戶數與 PropertyHub／FazWaz 不同，以多個來源一致的 634 戶為顯示參考。"},
        {"sourceName": "AssetWise 發行說明書", "url": DEVELOPER_DISCLOSURE, "statusLabel": "開發商資料列 1 房 448 戶、1 房 Plus 138 戶、2 房 46 戶與 2 商舖，合計 634 個單位。"},
        {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE, "statusLabel": "頁首顯示 48 筆出售掛牌；已核對兩筆 2 房直連樣本。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "頁首顯示 75 筆出租掛牌；已核對一筆 2 房直連樣本。"},
        {"sourceName": "管理費來源差異", "url": PROPERTYHUB_PROJECT, "statusLabel": "PropertyHub 列 ฿45/㎡；Hipflat 列 ฿50/㎡，週期未標示，試算暫以較高數值估算並提示需向管委會確認。"},
        {"sourceName": "座標交叉核對", "url": COORD_CROSSCHECK, "statusLabel": "BangkokRE 座標與 Homenayoo 公開 Google Maps 圖釘相距約 44 公尺，皆落在專案範圍。"},
    ],
})
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": NAME,
    "asOf": AS_OF,
    "coordinates": {"lat": 13.812556, "lng": 100.715134, "source": COORD_SOURCE, "crosscheck": COORD_CROSSCHECK, "crosscheckDistanceMeters": 44},
    "propertyData": {"completedYear": 2016, "floors": 8, "units": 634, "hipflatSource": HIPFLAT},
    "saleSamples": sale_samples,
    "rentSamples": rent_samples,
    "managementFee": {"rate": 50, "source": HIPFLAT, "conflictingSourceRate": 45, "conflictingSource": PROPERTYHUB_PROJECT, "note": "Neither source states the billing period."},
    "yieldBaseline": {"bedrooms": 2, "purchasePrice": sale_min["price"], "purchaseArea": sale_min["area"], "rentPerSqm": rent_min_sqm["priceSqm"], "rentPerMonthAtPurchaseArea": round(rent_min_sqm["price"] / rent_min_sqm["area"] * sale_min["area"]), "netPercentAfterOneAgentMonthAndIndicativeFee": round(((rent_min_sqm["price"] / rent_min_sqm["area"] * sale_min["area"] * 11) - 50 * sale_min["area"] * 12) / sale_min["price"] * 100, 2)},
    "sources": {"hipflat": HIPFLAT, "propertyHubProject": PROPERTYHUB_PROJECT, "saleProject": PROPERTYHUB_SALE, "rentProject": PROPERTYHUB_RENT, "developerDisclosure": DEVELOPER_DISCLOSURE},
    "notes": ["Listing feeds were checked on 2026-10-19; sampled units were last refreshed 2026-10-02, within 30 days.", "PropertyHub labels the 36.07 sqm two-bedroom rent as 12,000 THB/month; a separate 36 sqm listing is also 12,000 THB/month. The sample used for the rent-per-sqm low is the 36 sqm direct listing.", "Management fee is published as ฿50/sqm by Hipflat and ฿45/sqm by PropertyHub; the actual billing period and current juristic rate remain unconfirmed."],
}
(ROOT / "reports" / "esta-bliss-enrichment-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"project": NAME, "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "minimumTwoBedroomSale": sale_min["price"], "coordinates": [13.812556, 100.715134], "yieldPercent": report["yieldBaseline"]["netPercentAfterOneAgentMonthAndIndicativeFee"]}, ensure_ascii=False))
