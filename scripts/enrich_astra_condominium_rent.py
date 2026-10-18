from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3868
PROJECT = "Astra Condominium"
CHECKED = "2026-10-18"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-astra-condominium"
RENT_1BR_URL = "https://propertyhub.in.th/en/listings/1-br-condo-at-astra-condominium-in-chan-kasem-id-2874409---6032496"
RENT_2BR_URL = "https://propertyhub.in.th/en/listings/2-br-condo-for-rent-at-astra-condominium-chan-kasem-id-3295603---6392993"
SALE_1BR_URL = "https://propertyhub.in.th/en/listings/a034262-astra-condominium--b55709e9---6003893"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-astra-condominium"
DD_PROJECT_URL = "https://www.ddproperty.com/en/property-for-sale/at-astra-condominium-1389"


def read_array(filename: str, symbol: str):
    path = DIST / filename
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.S,
    )
    if not match:
        raise ValueError(f"Missing {symbol} in {path}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


rent_rows = [
    {
        "id": "2874409",
        "price": 22000,
        "area": 58,
        "priceSqm": round(22000 / 58, 2),
        "beds": 1,
        "roomType": "ONE_BED_ROOM",
        "title": "15th-Floor 1-BR 58 Sqm Condo For Rent, Astra Condominium",
        "url": RENT_1BR_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "updated": "2026-10-18 16:19",
        "checkedAt": CHECKED,
        "listingStatus": "active_as_listed",
        "matchedBy": "Exact Astra Condominium project rent page links this unit; direct listing states 1 bedroom, 58 sqm, THB 22,000/month and 15th floor.",
    },
    {
        "id": "3295603",
        "price": 20000,
        "area": 59,
        "priceSqm": round(20000 / 59, 2),
        "beds": 2,
        "roomType": "TWO_BED_ROOM",
        "title": "2-BR Condo At Astra Condominium In Chan Kasem",
        "url": RENT_2BR_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "updated": "2026-10-18 10:09",
        "checkedAt": CHECKED,
        "listingStatus": "active_as_listed",
        "matchedBy": "Exact Astra Condominium project rent page links listing ID 3295603; direct listing states Astra Condominium, 2 bedrooms, 59 sqm and THB 20,000/month.",
    },
]

rates = [row["priceSqm"] for row in rent_rows]
minimum_total = min(rent_rows, key=lambda row: row["price"])
minimum_rate = min(rent_rows, key=lambda row: row["priceSqm"])
by_bedroom = {
    str(row["beds"]): {
        "beds": row["beds"],
        "count": 1,
        "minimum": row["price"],
        "area": row["area"],
        "minimumArea": row["area"],
        "minimumSqm": row["priceSqm"],
        "minimumSourceUrl": row["url"],
        "minimumSqmSourceUrl": row["url"],
        "sourceUrl": row["url"],
    }
    for row in rent_rows
}
rent_market = {
    "count": len(rent_rows),
    "observedCount": len(rent_rows),
    "average": round(sum(row["price"] for row in rent_rows) / len(rent_rows)),
    "minimum": minimum_total["price"],
    "minimumArea": minimum_total["area"],
    "averageSqm": round(sum(rates) / len(rates)),
    "minimumSqm": minimum_rate["priceSqm"],
    "asOf": CHECKED,
    "source": PROJECT_URL,
    "sourceName": "PropertyHub",
    "minimumSourceUrl": minimum_total["url"],
    "minimumSqmSourceUrl": minimum_rate["url"],
    "byBedroom": by_bedroom,
    "samples": rent_rows,
}

manual_path, manual_rows = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual = next(
    (row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None
)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
manual["replaceRent"] = True
manual["rent"] = rent_market
manual["marketDataStatus"] = "propertyhub_exact_project_current_rent_listings"
manual["availabilitySources"] = [
    {
        "sourceName": "DDproperty",
        "url": DD_PROJECT_URL,
        "statusLabel": "專案出售目前 0 筆；不據過期廣告新增出售樣本",
    },
    {
        "sourceName": "PropertyHub 出售專案頁",
        "url": SALE_PROJECT_URL,
        "statusLabel": "目前無符合出售掛牌；既有出售樣本由獨立直接物件頁支持",
    },
]
manual_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

# The current linked 1BR sale is paired only with the 1BR rent rate and the
# exact sale unit area. Astra currently has no verified two-bedroom sale ad.
sale_price, sale_area = 1_899_000, 33
rent_per_sqm_1br = by_bedroom["1"]["minimumSqm"]
estimated_monthly_rent = rent_per_sqm_1br * sale_area
gross_yield = estimated_monthly_rent * 12 / sale_price * 100
after_agent_yield = estimated_monthly_rent * 11 / sale_price * 100
REPORTS.mkdir(exist_ok=True)
report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED,
    "rentListings": rent_rows,
    "saleBaseline": {
        "bedrooms": 1,
        "priceTHB": sale_price,
        "areaSqm": sale_area,
        "source": SALE_1BR_URL,
        "sourceName": "PropertyHub",
        "crossCheck": "PropertyScout direct listing ID 2838222 reports the same Astra project, 1BR, 33 sqm and ฿1,899,000 and says confirmed available two weeks before 2026-10-18.",
    },
    "yieldEstimate": {
        "bedrooms": 1,
        "purchasePriceTHB": sale_price,
        "purchaseAreaSqm": sale_area,
        "rentRateTHBPerSqmMonth": rent_per_sqm_1br,
        "estimatedMonthlyRentAtSaleAreaTHB": round(estimated_monthly_rent),
        "grossAnnualYieldPercent": round(gross_yield, 2),
        "afterOneAgentMonthPercent": round(after_agent_yield, 2),
        "managementFeeDeducted": False,
        "managementFeeStatus": "unknown",
        "formula": "(1BR rent per sqm × paired 1BR sale area × 12 [or 11 after one agent month]) ÷ linked 1BR sale price.",
    },
    "twoBedroomStatus": {
        "rentListing": RENT_2BR_URL,
        "rentTHBPerMonth": 20000,
        "rentAreaSqm": 59,
        "saleListing": None,
        "note": "No two-bedroom sale listing was verified; PropertyHub and DDproperty project pages currently show no matching sale inventory. Do not substitute a one-bedroom sale into the two-bedroom yield.",
    },
    "projectChecks": {
        "propertyHubProjectRent": PROJECT_URL,
        "propertyHubProjectSale": SALE_PROJECT_URL,
        "ddpropertyProjectSale": DD_PROJECT_URL,
    },
}
(REPORTS / "astra-condominium-rent-enrichment-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(
    json.dumps(
        {
            "hipflatId": PROJECT_ID,
            "rentListings": len(rent_rows),
            "roomRates": {key: round(value["minimumSqm"], 2) for key, value in by_bedroom.items()},
            "oneBedroomGrossYieldPercent": round(gross_yield, 2),
            "oneBedroomAfterAgentMonthPercent": round(after_agent_yield, 2),
            "twoBedroomSaleVerified": False,
        },
        ensure_ascii=False,
    )
)
