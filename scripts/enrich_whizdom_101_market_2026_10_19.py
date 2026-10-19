"""Add direct sale/rent listing evidence for Whizdom 101 (Hipflat ID 6477)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 6477
AS_OF = "2026-10-19"
PROJECT_URL = "https://www.dotproperty.co.th/en/condo/10002/whizdom-101"
SALE_URL = "https://www.108siam.com/en/property-sales/2-bedroom-condo-for-sale-at-whizdom-101-in-bang-chak-bangkok-u6794249"
RENT_1BR_URL = "https://www.dotproperty.co.th/en/ads/1-bedroom-condo-for-rent-in-whizdom-101-bang-chak-bangkok_39323d681d90-a2df-e792-9413-6502d089"
RENT_2BR_URL = "https://www.dotproperty.co.th/en/ads/2-bedroom-condo-for-rent-in-whizdom-101-bang-chak-bangkok_78f290ddcd00-9500-5d62-7371-3734e089"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/whizdom-101-xprnok"


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
        "id": "U6794249",
        "price": 5_200_000,
        "area": 40,
        "priceSqm": 130_000,
        "beds": 2,
        "roomType": "2BR",
        "url": SALE_URL,
        "title": "Whizdom 101 · 2 房 · 40 ㎡ · 30 樓 · ฿5,200,000",
        "sourceName": "108Siam / Dot Property",
        "projectName": "Whizdom 101",
        "checkedAt": AS_OF,
        "updated": "2026-10-18",
        "matchedBy": "exact_project_name_unit_id_and_matching_address",
        "listingStatus": "active_as_listed",
    }
]
rent_samples = [
    {
        "id": "dotproperty-whizdom101-rent-1br",
        "price": 15_000,
        "area": 29,
        "priceSqm": 517,
        "beds": 1,
        "roomType": "1BR",
        "url": RENT_1BR_URL,
        "title": "Whizdom 101 · 1 房 · 29 ㎡ · ฿15,000/月",
        "sourceName": "Dot Property",
        "projectName": "Whizdom 101",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_card_and_listing_url",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "dotproperty-whizdom101-rent-2br",
        "price": 22_000,
        "area": 40,
        "priceSqm": 550,
        "beds": 2,
        "roomType": "2BR",
        "url": RENT_2BR_URL,
        "title": "Whizdom 101 · 2 房 · 40 ㎡ · ฿22,000/月",
        "sourceName": "Dot Property",
        "projectName": "Whizdom 101",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_card_and_listing_url",
        "listingStatus": "active_as_listed",
    },
]

manual_rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [row for row in manual_rows if int(row.get("hipflatId", 0)) != PROJECT_ID]
manual_rows.append(
    {
        "hipflatId": PROJECT_ID,
        "name": "Whizdom 101",
        "completedYear": 2020,
        "completedYearSourceUrl": PROJECT_URL,
        "sale": {
            "count": 1,
            "observedCount": 1,
            "countKind": "manual_verified_listing",
            "average": 5_200_000,
            "minimum": 5_200_000,
            "minimumArea": 40,
            "minimumSampleUpdated": "2026-10-18",
            "averageSqm": 130_000,
            "minimumSqm": 130_000,
            "minimumSqmSampleUpdated": "2026-10-18",
            "asOf": AS_OF,
            "sourceName": "Dot Property / 108Siam 單筆掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": SALE_URL,
            "minimumSqmSourceUrl": SALE_URL,
            "samples": sale_samples,
            "byBedroom": {
                "2": {
                    "count": 1,
                    "minimum": 5_200_000,
                    "area": 40,
                    "minimumArea": 40,
                    "priceSqm": 130_000,
                    "minimumSqm": 130_000,
                    "minimumSourceUrl": SALE_URL,
                    "sourceUrl": SALE_URL,
                }
            },
        },
        "rent": {
            "count": 2,
            "observedCount": 2,
            "countKind": "manual_verified_listing",
            "average": 18_500,
            "minimum": 15_000,
            "minimumArea": 29,
            "minimumSampleUpdated": None,
            "averageSqm": 534,
            "minimumSqm": 517,
            "minimumSqmSampleUpdated": None,
            "asOf": AS_OF,
            "sourceName": "Dot Property 個別掛牌",
            "source": "https://www.dotproperty.co.th/en/condos-for-rent/whizdom-101_p10002",
            "minimumSourceUrl": RENT_1BR_URL,
            "minimumSqmSourceUrl": RENT_1BR_URL,
            "samples": rent_samples,
            "byBedroom": {
                "1": {
                    "count": 1,
                    "minimum": 15_000,
                    "area": 29,
                    "minimumArea": 29,
                    "minimumSqm": 15_000 / 29,
                    "minimumSourceUrl": RENT_1BR_URL,
                    "sourceUrl": RENT_1BR_URL,
                },
                "2": {
                    "count": 1,
                    "minimum": 22_000,
                    "area": 40,
                    "minimumArea": 40,
                    "minimumSqm": 550,
                    "minimumSourceUrl": RENT_2BR_URL,
                    "minimumSqmSourceUrl": RENT_2BR_URL,
                    "sourceUrl": RENT_2BR_URL,
                },
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
        "projectName": "Whizdom 101",
        "asOf": AS_OF,
        "sourceName": "Dot Property / 108Siam",
        "projectSourceUrl": PROJECT_URL,
        "sale": {
            "activeListingCount": 1,
            "sourceUrl": PROJECT_URL,
            "listings": [
                {
                    "id": "U6794249",
                    "bedrooms": 2,
                    "price": 5_200_000,
                    "area": 40,
                    "priceSqm": 130_000,
                    "listedAt": "2026-09-29",
                    "url": SALE_URL,
                }
            ],
        },
        "rent": {
            "activeListingCount": 2,
            "sourceUrl": "https://www.dotproperty.co.th/en/condos-for-rent/whizdom-101_p10002",
            "listings": [
                {"bedrooms": 1, "price": 15_000, "area": 29, "priceSqm": 517, "url": RENT_1BR_URL},
                {"bedrooms": 2, "price": 22_000, "area": 40, "priceSqm": 550, "url": RENT_2BR_URL},
            ],
        },
        "availabilitySources": [
            {
                "sourceName": "Hipflat 專案頁",
                "url": HIPFLAT_URL,
                "statusLabel": "專案名稱 Whizdom 101，地址 3079/7 Sukhumvit Road，位於 Bang Chak、Phra Khanong。",
            },
            {
                "sourceName": "Dot Property 專案頁",
                "url": PROJECT_URL,
                "statusLabel": "頁面列出出售 2 筆、出租 2–3 筆；最低可見出售單價 ฿5,200,000 / 40㎡，出租 ฿15,000 / 29㎡ 與 ฿22,000 / 40㎡。專案資訊列出 2020 完工、554 戶。",
            },
            {
                "sourceName": "出售物件頁",
                "url": SALE_URL,
                "statusLabel": "108Siam 物件頁列出 Whizdom 101 單位 U6794249：2 房、40㎡、30 樓、售價 ฿5,200,000；2026-09-29 刊登，頁面在核對日前一天更新。",
            },
            {
                "sourceName": "出租物件頁（2 房）",
                "url": RENT_2BR_URL,
                "statusLabel": "Dot Property 專案出租頁列出 2 房、40㎡、฿22,000/月；同頁提供此單筆物件連結。",
            },
            {
                "sourceName": "出租物件頁（1 房）",
                "url": RENT_1BR_URL,
                "statusLabel": "Dot Property 專案出租頁列出 1 房、29㎡、฿15,000/月；同頁提供此單筆物件連結。",
            },
        ],
    }
)
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

index_path = DIST / "index.html"
index_html = index_path.read_text(encoding="utf-8")
index_html = index_html.replace(
    "bangkok-manual-market-samples.js?v=20261019-menam-residences-samples",
    "bangkok-manual-market-samples.js?v=20261019-whizdom-101-market",
)
index_html = index_html.replace(
    "bangkok-market-crosschecks.js?v=20261019-menam-residences-samples",
    "bangkok-market-crosschecks.js?v=20261019-whizdom-101-market",
)
index_path.write_text(index_html, encoding="utf-8")

two_bed_rent = 22_000
two_bed_sale = 5_200_000
report = {
    "hipflatId": PROJECT_ID,
    "projectName": "Whizdom 101",
    "asOf": AS_OF,
    "location": {
        "verified": True,
        "sourceUrl": "https://www.thaigerproperty.com/projects/thailand/bangkok/phra-khanong/bang-chak/whizdom-101",
        "coordinates": [13.6856974, 100.6107152],
    },
    "completedYear": 2020,
    "saleSample": {
        "priceThb": two_bed_sale,
        "areaSqm": 40,
        "bedrooms": 2,
        "priceThbPerSqm": 130_000,
        "sourceUrl": SALE_URL,
    },
    "rentSamples": [
        {"priceThbPerMonth": row["price"], "areaSqm": row["area"], "bedrooms": row["beds"], "sourceUrl": row["url"]}
        for row in rent_samples
    ],
    "yieldCalculation": {
        "purchasePriceThb": two_bed_sale,
        "pairedSaleAreaSqm": 40,
        "twoBedroomRentThbPerSqmPerMonth": 550,
        "impliedMonthlyRentThb": two_bed_rent,
        "annualYieldBeforeDeductionsPercent": round(two_bed_rent * 12 / two_bed_sale * 100, 2),
        "annualYieldAfterOneAgentMonthPercent": round(two_bed_rent * 11 / two_bed_sale * 100, 2),
        "formula": "(22,000 × 11) ÷ 5,200,000 × 100; no management fee deducted because no reliable project fee was found.",
    },
    "note": "Public listing offers observed on 2026-10-19; the sale record says the unit is tenant-occupied through 2027-07-03. Advertiser must confirm availability and final terms.",
}
(ROOT / "reports/whizdom-101-market-enrichment-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report["yieldCalculation"], ensure_ascii=True))
