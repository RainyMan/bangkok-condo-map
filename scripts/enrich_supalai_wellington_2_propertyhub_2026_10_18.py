import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 5013
CHECKED = "2026-10-18"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/supalai-wellington-2-lrcyml"
SALE_PAGE = "https://propertyhub.in.th/en/condo-for-sale/project-supalai-wellington-ii"
RENT_PAGE = "https://propertyhub.in.th/en/condo-for-rent/project-supalai-wellington-ii"
COORDINATE_CORROBORATION = (
    "https://thinkofliving.com/คอนโด/supalai-wellington-2-คอนโด-high-rise-7-อาคาร-โปรห้อง-42-ตร-ม-2-75-ล้านบาท-พร้อมรถรับ-ส่ง-mrt-ศูนย์วัฒนธรรม-จาก-ศุภาลัย-รีวิวฉบับที่-2298-757275-รีวิวโครงการ/"
)
FEE_SOURCE = (
    "https://capital.sec.or.th/webapp/corp_fin/datafile/TO/0538000251250-22018-10-12e03.pdf?ts=1582344172"
)


def read_array(filename: str, variable: str):
    path = ROOT / "dist" / filename
    content = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}\s*=\s*(\[.*?\]);\s*$", content, re.S)
    if not match:
        raise RuntimeError(f"Could not parse {variable} from {path}")
    return path, content, json.loads(match.group(1))


def write_array(path: Path, content: str, variable: str, rows):
    replacement = f"window.{variable} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};"
    updated, count = re.subn(
        rf"window\.{variable}\s*=\s*\[.*?\];\s*$",
        replacement,
        content,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"Could not update {variable} in {path}")
    path.write_text(updated, encoding="utf-8", newline="")


def sample(listing_id, price, area, beds, title, url, updated, source_name="PropertyHub"):
    return {
        "id": str(listing_id),
        "price": price,
        "area": area,
        "priceSqm": round(price / area),
        "beds": beds,
        "roomType": f"{beds}BR",
        "title": title,
        "url": url,
        "sourceName": source_name,
        "projectName": "Supalai Wellington 2",
        "updated": updated,
        "checkedAt": CHECKED,
        "matchedBy": "exact_propertyhub_project_page_and_listing_id",
        "listingStatus": "active_as_listed",
    }


sale_rows = [
    sample(
        "3380089",
        5_300_000,
        56.56,
        2,
        "2-BR Condo at Supalai Wellington 2 near MRT Thailand Cultural Centre (ID 3380089)",
        "https://propertyhub.in.th/en/listings/2-br-condo-at-supalai-wellington-2-near-mrt-thailand-cultural-centre-id-3380089--a44408b6---6485800",
        "2026-10-16",
    ),
    sample(
        "6205851",
        5_300_000,
        66.56,
        2,
        "ขาย Condo Supalai Wellington II ห้องสวย วิวสระน้ำ 2 ห้องนอน 2 ห้องน้ำ",
        "https://propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2-condo-supalai-wellington-ii-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%A7%E0%B8%A2-%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B9%89%E0%B8%B3-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B9%89%E0%B8%B3---6205851",
        "2026-10-14",
    ),
]

rent_rows = [
    sample(
        "5011455",
        25_000,
        67.0,
        2,
        "#S3227 For Rent Supalai Wellington II",
        "https://propertyhub.in.th/en/listings/s3227-for-rent-supalai-wellington-ll---5011455",
        "2026-10-17",
    ),
    sample(
        "6219101",
        28_000,
        66.5,
        2,
        "FOR RENT condo Supalai Wellington 2 CX-75415",
        "https://propertyhub.in.th/en/listings/for-rent-condo-supalai-wellington-2-mrt-thailand-cultural-centre-huai-khwang-huai-khwang-bangkok-cx-75415-live-chat-with-us-add-line-connexproperty---6219101",
        "2026-09-19",
    ),
]

manual_path, manual_content, manual_rows = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
existing = next((row for row in manual_rows if row.get("hipflatId") == PROJECT_ID), None)
if existing is None:
    existing = {"hipflatId": PROJECT_ID, "name": "Supalai Wellington 2"}
    manual_rows.append(existing)

existing["completedYear"] = 2017
existing["completedYearSourceUrl"] = HIPFLAT_URL
existing["startedYear"] = None
existing["fee"] = {
    "rate": 36,
    "status": "historical_indicative",
    "note": "SEC 專案披露（2018 年資料）及 PS Property 公開專案頁列為 ฿36/㎡/月；屬歷史參考費率，並非管委會最新帳單，請再確認。",
    "source": FEE_SOURCE,
}

sale_url_set = {row["url"] for row in sale_rows}
rent_url_set = {row["url"] for row in rent_rows}
existing_sale = existing.setdefault("sale", {})
existing_rent = existing.setdefault("rent", {})
existing_sale_samples = [row for row in existing_sale.get("samples", []) if row.get("url") not in sale_url_set]
existing_rent_samples = [row for row in existing_rent.get("samples", []) if row.get("url") not in rent_url_set]
existing_sale_samples.extend(sale_rows)
existing_rent_samples.extend(rent_rows)

sale_minimum = min(sale_rows, key=lambda row: row["price"])
rent_min_rate = min(rent_rows, key=lambda row: row["priceSqm"])
existing_sale.update(
    {
        "count": len(existing_sale_samples),
        "observedCount": len(existing_sale_samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in existing_sale_samples) / len(existing_sale_samples)),
        "minimum": sale_minimum["price"],
        "minimumArea": sale_minimum["area"],
        "averageSqm": round(sum(row["priceSqm"] for row in existing_sale_samples) / len(existing_sale_samples)),
        "minimumSqm": min(row["priceSqm"] for row in existing_sale_samples),
        "minimumSampleUpdated": sale_minimum["updated"],
        "minimumSqmSampleUpdated": min(existing_sale_samples, key=lambda row: row["priceSqm"])["updated"],
        "asOf": CHECKED,
        "sourceName": "PropertyHub 專案頁核對的單筆掛牌",
        "source": SALE_PAGE,
        "minimumSourceUrl": sale_minimum["url"],
        "minimumSqmSourceUrl": min(existing_sale_samples, key=lambda row: row["priceSqm"])["url"],
        "byBedroom": {
            "2": {
                "count": len(existing_sale_samples),
                "minimum": sale_minimum["price"],
                "area": sale_minimum["area"],
                "minimumArea": sale_minimum["area"],
                "priceSqm": sale_minimum["priceSqm"],
                "minimumSqm": sale_minimum["priceSqm"],
                "minimumSourceUrl": sale_minimum["url"],
                "sourceUrl": sale_minimum["url"],
            }
        },
        "samples": existing_sale_samples,
    }
)
existing_rent.update(
    {
        "count": len(existing_rent_samples),
        "observedCount": len(existing_rent_samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in existing_rent_samples) / len(existing_rent_samples)),
        "minimum": min(row["price"] for row in existing_rent_samples),
        "minimumArea": min(existing_rent_samples, key=lambda row: row["price"])["area"],
        "averageSqm": round(sum(row["priceSqm"] for row in existing_rent_samples) / len(existing_rent_samples)),
        "minimumSqm": min(row["priceSqm"] for row in existing_rent_samples),
        "minimumSampleUpdated": min(existing_rent_samples, key=lambda row: row["price"])["updated"],
        "minimumSqmSampleUpdated": rent_min_rate["updated"],
        "asOf": CHECKED,
        "sourceName": "PropertyHub 專案頁核對的單筆掛牌",
        "source": RENT_PAGE,
        "minimumSourceUrl": min(existing_rent_samples, key=lambda row: row["price"])["url"],
        "minimumSqmSourceUrl": rent_min_rate["url"],
        "byBedroom": {
            "2": {
                "count": len(existing_rent_samples),
                "minimum": min(existing_rent_samples, key=lambda row: row["price"])["price"],
                "area": min(existing_rent_samples, key=lambda row: row["price"])["area"],
                "priceSqm": rent_min_rate["priceSqm"],
                "minimumSqm": min(row["priceSqm"] for row in existing_rent_samples),
                "minimumSourceUrl": min(existing_rent_samples, key=lambda row: row["price"])["url"],
                "minimumSqmSourceUrl": rent_min_rate["url"],
                "sourceUrl": rent_min_rate["url"],
            }
        },
        "samples": existing_rent_samples,
    }
)
write_array(manual_path, manual_content, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

hub_path, hub_content, hub_rows = read_array(
    "bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS"
)
hub_detail = next((row for row in hub_rows if row.get("hipflatId") == PROJECT_ID), None)
if hub_detail is None:
    hub_detail = {"hipflatId": PROJECT_ID, "name": "Supalai Wellington 2"}
    hub_rows.append(hub_detail)
hub_detail["completedYear"] = 2017
hub_detail["completedYearSourceUrl"] = HIPFLAT_URL
write_array(hub_path, hub_content, "BANGKOK_PROPERTYHUB_DETAILS", hub_rows)

detail_path, detail_content, detail_rows = read_array(
    "bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS"
)
detail = next(row for row in detail_rows if row.get("hipflatId") == PROJECT_ID)
detail["locationVerificationSourceUrl"] = COORDINATE_CORROBORATION
write_array(detail_path, detail_content, "BANGKOK_PROPERTYSCOUT_DETAILS", detail_rows)

cross_path, cross_content, cross_rows = read_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
cross_sale = [
    {
        "listingId": row["id"],
        "price": row["price"],
        "area": row["area"],
        "priceSqm": row["priceSqm"],
        "bedrooms": row["beds"],
        "listedAt": row["updated"],
        "url": row["url"],
        "sourceName": row["sourceName"],
    }
    for row in sale_rows
]
cross_rent = [
    {
        "listingId": row["id"],
        "price": row["price"],
        "area": row["area"],
        "priceSqm": row["priceSqm"],
        "bedrooms": row["beds"],
        "listedAt": row["updated"],
        "url": row["url"],
        "sourceName": row["sourceName"],
    }
    for row in rent_rows
]
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": "Supalai Wellington 2",
    "asOf": CHECKED,
    "sourceName": "PropertyHub",
    "projectSourceUrl": SALE_PAGE,
    "sale": {"listings": cross_sale, "sourceUrl": SALE_PAGE},
    "rent": {"listings": cross_rent, "sourceUrl": RENT_PAGE},
    "availabilitySources": [
        {
            "sourceName": "Hipflat 專案頁",
            "url": HIPFLAT_URL,
            "statusLabel": "標示 Thiam Ruam Mit Road、14 樓、2017 完工；專案售租統計會隨平台更新。",
        },
        {
            "sourceName": "座標交叉核對",
            "url": COORDINATE_CORROBORATION,
            "statusLabel": "ThinkOfLiving Google Maps 點位與現用 OpenStreetMap 專案建築點相差約 1.3 公尺；PropertyScout 點位相差約 47 公尺，地址一致。",
        },
    ],
}
cross_rows = [row for row in cross_rows if row.get("hipflatId") != PROJECT_ID]
cross_rows.append(crosscheck)
write_array(cross_path, cross_content, "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

roi_monthly_rent = round((rent_min_rate["price"] / rent_min_rate["area"]) * sale_minimum["area"])
annual_net = roi_monthly_rent * 11 - 36 * sale_minimum["area"] * 12
net_roi = annual_net / sale_minimum["price"] * 100
report = f"""# Supalai Wellington 2 listing and ROI verification ({CHECKED})

- Hipflat project: {HIPFLAT_URL}
- Project: Supalai Wellington II / Supalai Wellington 2, Hipflat project ID {PROJECT_ID}.
- Project facts: 7 buildings, 14 floors, 1,092 units, completed December 2017 (Hipflat and PropertyHub project details).
- Location: the map uses the exact-name OpenStreetMap building point `13.766263290909091, 100.58127999090908` (https://www.openstreetmap.org/way/1332578378). ThinkOfLiving gives Google Maps coordinates `13.76625965439585, 100.5812914837942`, approximately 1.3 m away. PropertyScout gives `13.766674382899332, 100.58137172024`, approximately 47 m away. The sources identify the same Thiam Ruam Mit Road project in Huai Khwang; both primary and corroborating coordinate links are exposed in the project card.

## Direct current listings

The PropertyHub sale project page ({SALE_PAGE}) displayed two active-as-listed two-bedroom listings at the lowest total price that were independently checked:

1. [PropertyHub listing 3380089](https://propertyhub.in.th/en/listings/2-br-condo-at-supalai-wellington-2-near-mrt-thailand-cultural-centre-id-3380089--a44408b6---6485800): ฿5,300,000, 56.56 m², 2 bedrooms; project page refreshed 2026-10-16.
2. [PropertyHub listing 6205851](https://propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2-condo-supalai-wellington-ii-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%A7%E0%B8%A2-%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B9%89%E0%B8%B3-2-%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-2-%E0%B8%AB%E0%B8%B้องน้ำ---6205851): ฿5,300,000, 66.56 m², 2 bedrooms; listing page confirms building 5, floor 12A and the unit area. The project result was updated 2026-10-14.

The PropertyHub rent project page ({RENT_PAGE}) displayed the following directly checked two-bedroom listings:

1. [PropertyHub listing 5011455](https://propertyhub.in.th/en/listings/s3227-for-rent-supalai-wellington-ll---5011455): ฿25,000/month, 67 m², 2 bedrooms, 6th floor; refreshed 2026-10-17. This is the lowest observed two-bedroom rent in the checked project results.
2. [PropertyHub listing 6219101 (CX-75415)](https://propertyhub.in.th/en/listings/for-rent-condo-supalai-wellington-2-mrt-thailand-cultural-centre-huai-khwang-huai-khwang-bangkok-cx-75415-live-chat-with-us-add-line-connexproperty---6219101): ฿28,000/month, 66.5 m², 2 bedrooms, 4th floor; the individual listing says last update 2026-09-19 and remained displayed on the project page at the 2026-10-18 check.

## Fee and ROI estimate

- The 2018 SEC-filed project disclosure lists common fees at ฿36/m²/month (one year prepaid). This is recorded as `historical_indicative`; it is not represented as the current juristic-office bill. Source: {FEE_SOURCE}
- PS Property also displays ฿36/m² utility fee: https://ps-property.co.th/projects/supalai-wellington-2/
- Default ROI uses the lowest total two-bedroom sale at ฿5,300,000 and keeps its own area of 56.56 m². It uses the 2-bedroom rent low of ฿25,000 / 67 m², scaled to the purchase unit area (about ฿21,104/month).
- With one agency month deducted and the historical fee reference deducted: `((21,104 × 11) − (36 × 56.56 × 12)) / 5,300,000 × 100` = approximately **3.92% net annual yield**. Fee and listing availability require direct confirmation; taxes, repairs, vacancy and transfer costs are excluded.

## Exclusions and uncertainty

- A PropertyHub two-bedroom rent result advertised as ฿27,000 has conflicting area fields (65.5 m² in the header versus 66.5 m² in its description); it was excluded from calculated sample data.
- PropertyHub project-page listing counts change between page snapshots. They are not used as property-level sale/rent samples.
- Hipflat's project page exposes an incorrect geocoder label (“Kasikorn Bank Ratchadapisek 15 Branch”) despite describing the project as on Thiam Ruam Mit Road. The map pin is based on the exact-name OSM building feature; the independent ThinkOfLiving Google Maps coordinate is within about 1.3 m.
"""
(ROOT / "reports" / f"supalai-wellington-2-enrichment-{CHECKED}.md").write_text(report, encoding="utf-8")

print(json.dumps({
    "hipflatId": PROJECT_ID,
    "saleSamples": len(sale_rows),
    "rentSamples": len(rent_rows),
    "lowestTwoBedroomSale": sale_minimum["price"],
    "lowestObservedTwoBedroomRent": rent_min_rate["price"],
    "estimatedMonthlyRent": roi_monthly_rent,
    "netAnnualYieldPercent": round(net_roi, 2),
}, ensure_ascii=False))
