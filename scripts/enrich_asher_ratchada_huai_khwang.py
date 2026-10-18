from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 6184
PROJECT = "ASHER Ratchada - Huai Khwang"
CHECKED = "2026-10-18"
PROJECT_URL = "https://propertyhub.in.th/en/projects/asher-ratchada-huai-khwang"
SALE_URL = "https://propertyhub.in.th/en/listings/a033620-asher-ratchada-huai-khwang--9f3408cd---6005497"
SALE_OLDER_URL = "https://propertyhub.in.th/en/listings/1-br-condo-at-asher-ratchada-huai-khwang-near-mrt-sutthisan-id-1345612---5110456"
RENT_URL = (
    "https://propertyhub.in.th/en/listings/%EF%B8%8Fp-10067-asher-ratchada-"
    "huai-khwang-modern-design-1-bed-near-mrt-sutthisan-13-000-thb-line-"
    "id-easycondoplus-099-229-6397--aa9e091b---6332874"
)


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


sale_sample = {
    "id": "6005497",
    "price": 1_899_000,
    "area": 28,
    "priceSqm": round(1_899_000 / 28),
    "beds": 1,
    "roomType": "ONE_BED_ROOM",
    "title": "ASHER Ratchada - Huai Khwang，1 房，28 ㎡，฿1,899,000",
    "url": SALE_URL,
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_date_unknown",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
sale_older_sample = {
    "id": "5110456",
    "price": 3_050_000,
    "area": 31.2,
    "priceSqm": round(3_050_000 / 31.2),
    "beds": 1,
    "roomType": "ONE_BED_ROOM",
    "title": "ASHER Ratchada - Huai Khwang，1 房，31.2 ㎡，฿3,050,000",
    "url": SALE_OLDER_URL,
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "updated": "2026-03-28",
    "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_over_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
rent_sample = {
    "id": "6332874",
    "price": 13_000,
    "area": 30,
    "priceSqm": round(13_000 / 30, 2),
    "beds": 1,
    "roomType": "ONE_BED_ROOM",
    "title": "ASHER Ratchada - Huai Khwang，1 房，30 ㎡，฿13,000/月",
    "url": RENT_URL,
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "updated": "2026-10-17T14:34:00+07:00",
    "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
rent_other_sample = {
    "id": "5033907",
    "price": 14_000,
    "area": 30.63,
    "priceSqm": round(14_000 / 30.63, 2),
    "beds": 1,
    "roomType": "ONE_BED_ROOM",
    "title": "ASHER Ratchada - Huai Khwang，1 房，30.63 ㎡，฿14,000/月",
    "url": "https://propertyhub.in.th/en/listings/r3365-for-rent-asher-ratchada-huaikhwang---5033907",
    "sourceName": "PropertyHub",
    "projectName": PROJECT,
    "updated": "2026-10-17T07:45:00+07:00",
    "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
sale_samples = [sale_sample, sale_older_sample]
rent_samples = [rent_sample, rent_other_sample]
sale_average_sqm = round(sum(row["priceSqm"] for row in sale_samples) / len(sale_samples))
rent_average_sqm = round(sum(row["priceSqm"] for row in rent_samples) / len(rent_samples))
sale_market = {
    "count": len(sale_samples),
    "observedCount": len(sale_samples),
    "countKind": "manual_verified_listing",
    "average": round(sum(row["price"] for row in sale_samples) / len(sale_samples)),
    "minimum": sale_sample["price"],
    "minimumArea": sale_sample["area"],
    "minimumSampleUpdated": None,
    "averageSqm": sale_average_sqm,
    "minimumSqm": sale_sample["priceSqm"],
    "minimumSqmSampleUpdated": None,
    "asOf": CHECKED,
    "sourceName": "PropertyHub 個別出售掛牌",
    "source": PROJECT_URL,
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "byBedroom": {
        "1": {
            "beds": 1,
            "count": len(sale_samples),
            "minimum": sale_sample["price"],
            "minimumArea": sale_sample["area"],
            "area": sale_sample["area"],
            "minimumSqm": sale_sample["priceSqm"],
            "priceSqm": sale_sample["priceSqm"],
            "minimumSourceUrl": SALE_URL,
            "sourceUrl": SALE_URL,
        }
    },
    "samples": sale_samples,
}
rent_market = {
    "count": len(rent_samples),
    "observedCount": len(rent_samples),
    "countKind": "manual_verified_listing",
    "average": round(sum(row["price"] for row in rent_samples) / len(rent_samples)),
    "minimum": rent_sample["price"],
    "minimumArea": rent_sample["area"],
    "minimumSampleUpdated": rent_sample["updated"],
    "averageSqm": rent_average_sqm,
    "minimumSqm": rent_sample["priceSqm"],
    "minimumSqmSampleUpdated": rent_sample["updated"],
    "asOf": CHECKED,
    "sourceName": "PropertyHub 個別出租掛牌",
    "source": "https://propertyhub.in.th/en/condo-for-rent/project-asher-ratchada-huai-khwang",
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "byBedroom": {
        "1": {
            "beds": 1,
            "count": len(rent_samples),
            "minimum": rent_sample["price"],
            "minimumArea": rent_sample["area"],
            "area": rent_sample["area"],
            "minimumSqm": rent_sample["priceSqm"],
            "minimumSourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
            "sourceUrl": RENT_URL,
        }
    },
    "samples": rent_samples,
}

manual_path, manual_rows = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
manual.update(
    {
        "name": PROJECT,
        "replaceSale": True,
        "replaceRent": True,
        "sale": sale_market,
        "rent": rent_market,
        "fee": {
            "rate": 49,
            "status": "published_indicative",
            "note": "PropertyHub 專案頁公布管理費 ฿49/㎡/月；現行費率請向管委會確認。",
            "source": PROJECT_URL,
        },
    }
)
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

# Replace the old near-name PropertyHub match with facts from this exact project.
for filename, symbol in (
    ("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"),
    ("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS"),
):
    path, rows = read_array(filename, symbol)
    row = next(item for item in rows if int(item.get("id", -1)) == PROJECT_ID)
    row.update(
        {
            "name": PROJECT,
            "completedYear": 2021,
            "units": 121,
            "floors": 8,
            "fee": {
                "rate": 49,
                "note": "PropertyHub 專案頁公布管理費 ฿49/㎡/月；現行費率請向管委會確認。",
                "source": PROJECT_URL,
                "status": "published_indicative",
            },
            "locationSourceUrl": PROJECT_URL,
            "propertyHubProjectUrl": PROJECT_URL,
            "propertyHubRentUrl": "https://propertyhub.in.th/en/condo-for-rent/project-asher-ratchada-huai-khwang",
            "propertyHubSaleUrl": "https://propertyhub.in.th/en/condo-for-sale/project-asher-ratchada-huai-khwang",
        }
    )
    # This was the ID of a similarly named, different PropertyHub project;
    # leave exact-page details embedded on this row instead of joining that record.
    row.pop("propertyHubProjectId", None)
    write_array(path, symbol, rows)

# Calculate the selectable one-bedroom estimate. There is no two-bedroom unit
# type listed by the project's own PropertyHub page, so no two-bedroom yield is inferred.
purchase_price = sale_sample["price"]
sale_area = sale_sample["area"]
monthly_rent = round(rent_sample["priceSqm"] * sale_area)
annual_rent_after_agent = monthly_rent * 11
annual_management_fee = 49 * sale_area * 12
net_yield = (annual_rent_after_agent - annual_management_fee) / purchase_price * 100
REPORTS.mkdir(exist_ok=True)
(REPORTS / "asher-ratchada-huai-khwang-market-2026-10-18.json").write_text(
    json.dumps(
        {
            "hipflatId": PROJECT_ID,
            "project": PROJECT,
            "checkedAt": CHECKED,
            "projectSource": PROJECT_URL,
            "projectFacts": {
                "completedYear": 2021,
                "floors": 8,
                "units": 121,
                "commonFeePerSqmPerMonth": 49,
                "unitTypes": "PropertyHub lists 1-bedroom units, 25–33 sqm; no 2-bedroom type shown.",
            },
            "saleSamples": sale_samples,
            "rentSamples": rent_samples,
            "yieldScenario": {
                "bedrooms": 1,
                "purchasePriceTHB": purchase_price,
                "saleAreaSqm": sale_area,
                "roomRentLowTHBPerSqmPerMonth": rent_sample["priceSqm"],
                "estimatedMonthlyRentOnSaleAreaTHB": monthly_rent,
                "deductAgentMonths": 1,
                "annualCommonFeeTHB": annual_management_fee,
                "estimatedNetAnnualYieldPercent": round(net_yield, 2),
                "availabilityCaveat": "Rental listing page has no individual update date; the exact-project listing index showed a refresh on 2026-10-17. Confirm current availability before relying on the estimate.",
            },
            "twoBedroomYield": None,
            "coordinateNote": "Existing verified coordinate retained; this update corrects the PropertyHub project match and market samples.",
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(json.dumps({"project": PROJECT, "projectId": PROJECT_ID, "oneBedroomNetYield": round(net_yield, 2)}, ensure_ascii=False))
