"""Add directly verifiable Menam Residences sale and rent listing samples."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 6546
AS_OF = "2026-10-19"

SALE_SOURCE = "https://assets2.propertyhub.in.th/en/listings/for-sale-condo-menam-residences-bts-saphan-taksin-wat-phraya-krai-bang-kho-laem-bangkok-cx-28563-live-chat-with-us-add-line-connexproperty--b21209c5---3940968"
RENT_38K_SOURCE = "https://propertyhub.in.th/en/listings/for-rent-condo-menam-residences-bts-saphan-taksin-wat-phraya-krai-bang-kho-laem-bangkok-cx-105123-live-chat-with-us-add-line-connexproperty--b395096e---4752692"
RENT_42K_SOURCE = "https://propertyhub.in.th/en/listings/the-most-competitively-priced-high-floor-corner-suite-with-majestic-chao-phraya-river-views---6208130"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/menam-residences"
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/condo-menam-residences-wkebqd"
COORDINATE_SOURCE = "https://www.thaigerproperty.com/projects/thailand/bangkok/bang-kho-laem/wat-phraya-krai/menam-residences-condominium"


def read_array(filename: str, variable: str) -> list[dict]:
    source = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{variable} = "
    if not source.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript data format in {filename}")
    return json.loads(source[len(prefix) :].rstrip().removesuffix(";"))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    rendered = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    (DIST / filename).write_text(f"window.{variable} = {rendered};\n", encoding="utf-8")


sale_samples = [
    {
        "id": "3940968",
        "price": 11_000_000,
        "area": 69,
        "priceSqm": 159_420,
        "beds": 2,
        "roomType": "2BR",
        "url": SALE_SOURCE,
        "title": "Menam Residences · 2 房 · 69 ㎡ · 17 樓 · ฿11,000,000",
        "sourceName": "PropertyHub / Connex Property",
        "projectName": "Menam Residences",
        "checkedAt": AS_OF,
        "updated": "2026-10-16",
        "matchedBy": "exact_project_and_address_on_direct_listing",
        "listingStatus": "active_as_listed",
    }
]
rent_samples = [
    {
        "id": "4752692",
        "price": 38_000,
        "area": 65,
        "priceSqm": 585,
        "beds": 2,
        "roomType": "2BR",
        "url": RENT_38K_SOURCE,
        "title": "Menam Residences · 2 房 · 65 ㎡ · 15 樓 · ฿38,000/月",
        "sourceName": "PropertyHub / Connex Property",
        "projectName": "Menam Residences",
        "checkedAt": AS_OF,
        "updated": "2026-10-10",
        "matchedBy": "exact_project_and_address_on_direct_listing",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6208130",
        "price": 42_000,
        "area": 77,
        "priceSqm": 545,
        "beds": 2,
        "roomType": "2BR",
        "url": RENT_42K_SOURCE,
        "title": "Menam Residences · 2 房 · 77 ㎡ · ฿42,000/月",
        "sourceName": "PropertyHub / The Elitz Real Estate",
        "projectName": "Menam Residences",
        "checkedAt": AS_OF,
        "updated": "2026-10-16",
        "matchedBy": "exact_project_and_address_on_direct_listing",
        "listingStatus": "active_as_listed",
    },
]

sale_rate = round(sum(row["priceSqm"] for row in sale_samples) / len(sale_samples))
rent_rate = min(row["price"] / row["area"] for row in rent_samples)
purchase_area = sale_samples[0]["area"]
purchase_price = sale_samples[0]["price"]
monthly_comparable_rent = round(rent_rate * purchase_area)
annual_net_after_fee_and_one_agent_month = (
    monthly_comparable_rent * 11 - 60 * purchase_area * 12
) / purchase_price * 100

manual_rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [row for row in manual_rows if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual_rows.append(
    {
        "hipflatId": PROJECT_ID,
        "name": "Menam Residences Condominium",
        "completedYear": 2016,
        "completedYearSourceUrl": PROPERTYHUB_PROJECT,
        "fee": {
            "rate": 60,
            "note": "PropertyHub 專案頁標示每平方米每月 60 泰銖；實際收費請向管委會核實。",
            "source": PROPERTYHUB_PROJECT,
            "status": "published_indicative",
        },
        "sale": {
            "count": len(sale_samples),
            "observedCount": len(sale_samples),
            "countKind": "manual_verified_listing",
            "average": purchase_price,
            "minimum": purchase_price,
            "minimumArea": purchase_area,
            "minimumSampleUpdated": "2026-10-16",
            "averageSqm": sale_rate,
            "minimumSqm": round(purchase_price / purchase_area),
            "minimumSqmSampleUpdated": "2026-10-16",
            "asOf": AS_OF,
            "sourceName": "PropertyHub 個別掛牌",
            "source": PROPERTYHUB_PROJECT,
            "minimumSourceUrl": SALE_SOURCE,
            "minimumSqmSourceUrl": SALE_SOURCE,
            "samples": sale_samples,
            "byBedroom": {
                "2": {
                    "count": 1,
                    "minimum": purchase_price,
                    "area": purchase_area,
                    "minimumArea": purchase_area,
                    "priceSqm": round(purchase_price / purchase_area),
                    "minimumSqm": round(purchase_price / purchase_area),
                    "minimumSourceUrl": SALE_SOURCE,
                    "sourceUrl": SALE_SOURCE,
                }
            },
        },
        "rent": {
            "count": len(rent_samples),
            "observedCount": len(rent_samples),
            "countKind": "manual_verified_listing",
            "average": round(sum(row["price"] for row in rent_samples) / len(rent_samples)),
            "minimum": min(row["price"] for row in rent_samples),
            "minimumArea": rent_samples[0]["area"],
            "minimumSampleUpdated": "2026-10-10",
            "averageSqm": round(sum(row["priceSqm"] for row in rent_samples) / len(rent_samples)),
            "minimumSqm": round(rent_rate),
            "minimumSqmSampleUpdated": "2026-10-16",
            "asOf": AS_OF,
            "sourceName": "PropertyHub 個別掛牌",
            "source": PROPERTYHUB_PROJECT,
            "minimumSourceUrl": RENT_38K_SOURCE,
            "minimumSqmSourceUrl": RENT_42K_SOURCE,
            "samples": rent_samples,
            "byBedroom": {
                "2": {
                    "count": len(rent_samples),
                    "minimum": rent_samples[0]["price"],
                    "area": rent_samples[0]["area"],
                    "minimumArea": rent_samples[0]["area"],
                    "minimumSqm": rent_rate,
                    "minimumSourceUrl": RENT_38K_SOURCE,
                    "minimumSqmSourceUrl": RENT_42K_SOURCE,
                    "sourceUrl": RENT_38K_SOURCE,
                }
            },
        },
    }
)
manual_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

crosschecks = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", 0)) != PROJECT_ID]
crosschecks.append(
    {
        "hipflatId": PROJECT_ID,
        "projectName": "Menam Residences Condominium",
        "asOf": AS_OF,
        "sourceName": "PropertyHub",
        "projectSourceUrl": PROPERTYHUB_PROJECT,
        "sale": {
            "activeListingCount": 1,
            "sourceUrl": PROPERTYHUB_PROJECT,
            "listings": [
                {
                    "id": "3940968",
                    "bedrooms": 2,
                    "price": 11_000_000,
                    "area": 69,
                    "priceSqm": 159_420,
                    "listedAt": "2026-10-16",
                    "url": SALE_SOURCE,
                }
            ],
        },
        "rent": {
            "activeListingCount": 2,
            "sourceUrl": PROPERTYHUB_PROJECT,
            "listings": [
                {
                    "id": "4752692",
                    "bedrooms": 2,
                    "price": 38_000,
                    "area": 65,
                    "priceSqm": 585,
                    "updatedAt": "2026-10-10",
                    "url": RENT_38K_SOURCE,
                },
                {
                    "id": "6208130",
                    "bedrooms": 2,
                    "price": 42_000,
                    "area": 77,
                    "priceSqm": 545,
                    "updatedAt": "2026-10-16",
                    "url": RENT_42K_SOURCE,
                },
            ],
        },
        "availabilitySources": [
            {
                "sourceName": "Hipflat 專案頁",
                "url": HIPFLAT_PROJECT,
                "statusLabel": "專案名稱、所在 Bang Kho Laem 區與 2108 Charoenkrung 地址相符。",
            },
            {
                "sourceName": "PropertyHub 專案頁",
                "url": PROPERTYHUB_PROJECT,
                "statusLabel": "2016 完工、54 樓、294 戶；公布管理費 60 泰銖/㎡/月。出售 2 房最低可見掛牌 ฿11,000,000 / 69㎡；出租掛牌 ฿38,000 / 65㎡ 與 ฿42,000 / 77㎡。",
            },
            {
                "sourceName": "售出單筆掛牌",
                "url": SALE_SOURCE,
                "statusLabel": "PropertyHub 單筆頁列出 Menam Residences、2 房、69㎡、17 樓及售價 ฿11,000,000；專案頁搜索結果顯示 2026-10-16 更新。",
            },
            {
                "sourceName": "租出單筆掛牌",
                "url": RENT_38K_SOURCE,
                "statusLabel": "PropertyHub 單筆頁列出 2 房、65㎡、฿38,000/月，更新於 2026-10-10。",
            },
            {
                "sourceName": "租出單筆掛牌",
                "url": RENT_42K_SOURCE,
                "statusLabel": "PropertyHub 單筆頁列出 2 房、77㎡、฿42,000/月；專案頁搜索結果顯示 2026-10-16 更新。",
            },
            {
                "sourceName": "座標來源",
                "url": COORDINATE_SOURCE,
                "statusLabel": "Thaiger Property 的 Menam Residences 專案頁提供建物點位，已與 Hipflat 專案名稱及所在行政區核對。",
            },
        ],
    }
)
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

index_path = DIST / "index.html"
index_html = index_path.read_text(encoding="utf-8")
index_html = index_html.replace(
    "bangkok-manual-market-samples.js?v=20261019-ussakan-bam-asset",
    "bangkok-manual-market-samples.js?v=20261019-menam-residences-samples",
)
index_html = index_html.replace(
    "bangkok-market-crosschecks.js?v=20261019-picha-rent-availability",
    "bangkok-market-crosschecks.js?v=20261019-menam-residences-samples",
)
index_path.write_text(index_html, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "projectName": "Menam Residences Condominium",
    "asOf": AS_OF,
    "location": {
        "verified": True,
        "sourceUrl": COORDINATE_SOURCE,
        "coordinates": [13.7064371, 100.5059248],
    },
    "completedYear": 2016,
    "managementFeeThbPerSqmPerMonth": 60,
    "saleSample": {
        "priceThb": purchase_price,
        "areaSqm": purchase_area,
        "bedrooms": 2,
        "priceThbPerSqm": round(purchase_price / purchase_area),
        "sourceUrl": SALE_SOURCE,
    },
    "rentSamples": [
        {"priceThbPerMonth": row["price"], "areaSqm": row["area"], "bedrooms": 2, "sourceUrl": row["url"]}
        for row in rent_samples
    ],
    "yieldCalculation": {
        "purchasePriceThb": purchase_price,
        "pairedSaleAreaSqm": purchase_area,
        "lowestObservedTwoBedroomRentThbPerSqmPerMonth": round(rent_rate, 2),
        "impliedMonthlyRentThb": monthly_comparable_rent,
        "annualYieldBeforeDeductionsPercent": round(monthly_comparable_rent * 12 / purchase_price * 100, 2),
        "annualYieldAfterOneAgentMonthPercent": round(monthly_comparable_rent * 11 / purchase_price * 100, 2),
        "annualNetYieldAfterFeeAndOneAgentMonthPercent": round(annual_net_after_fee_and_one_agent_month, 2),
        "formula": "(monthly rent × 11 − 60 × 69 × 12) ÷ 11,000,000 × 100",
    },
    "note": "Listings are public portal offers observed on 2026-10-19; availability and final agreed prices require direct confirmation with the advertiser.",
}
(ROOT / "reports/menam-residences-market-enrichment-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report["yieldCalculation"], ensure_ascii=True))
