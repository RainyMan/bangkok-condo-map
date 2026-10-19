"""Attach exact Family Condominium sale and rental listings with freshness."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3859
AS_OF = "2026-10-19"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-family-condominium---18037"
SALE_URL = "https://propertyhub.in.th/en/listings/condo-for-sale-at-family-condominium-bts-saphan-khwai---6350597"
RENT_PROJECT_URL = "https://www.ddproperty.com/en/condo-for-rent/at-family-condominium-1346"
RENT_CURRENT_URL = "https://www.ddproperty.com/en/property/family-condominium-bangkok-for-rent-500584623"
RENT_STALE_URL = "https://www.ddproperty.com/en/property/family-condominium-bangkok-for-rent-500558512"
SALE_DD_URL = "https://www.ddproperty.com/en/condo-for-sale/at-family-condominium-1346"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not read {symbol} from {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    text = f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (DIST / filename).write_text(text, encoding="utf-8")


manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in manual if int(row["hipflatId"]) == PROJECT_ID), None)
if record is None:
    record = {"hipflatId": PROJECT_ID, "name": "Family Condominium"}
    manual.append(record)
record["asOf"] = AS_OF
record["sale"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "direct_propertyhub_listing",
    "average": 950000,
    "minimum": 950000,
    "minimumArea": 27,
    "averageSqm": 35185,
    "minimumSqm": 35185,
    "asOf": AS_OF,
    "sourceName": "PropertyHub 個別出售掛牌",
    "source": SALE_PROJECT_URL,
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "samples": [{
        "id": "6350597", "price": 950000, "area": 27, "priceSqm": 35185,
        "beds": 1, "roomType": "STUDIO", "title": "Family Condominium · Studio / 1 bedroom · ฿950,000",
        "url": SALE_URL, "sourceName": "PropertyHub", "projectName": "Family Condominium",
        "updated": "2026-10-16", "checkedAt": AS_OF, "listingStatus": "active_as_listed",
    }],
    "byBedroom": {"1": {
        "count": 1, "minimum": 950000, "area": 27, "priceSqm": 35185,
        "minimumSqm": 35185, "sourceUrl": SALE_URL, "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL,
    }},
}
record["rent"] = {
    "count": 1,
    "observedCount": 1,
    "countKind": "direct_ddproperty_listings_with_one_current_unique_unit",
    "average": 27000,
    "minimum": 27000,
    "minimumArea": 45,
    "averageSqm": 600,
    "minimumSqm": 600,
    "minimumSampleUpdated": "2026-09-24",
    "minimumSqmSampleUpdated": "2026-09-24",
    "asOf": AS_OF,
    "sourceName": "DDproperty 個別出租掛牌",
    "source": RENT_PROJECT_URL,
    "minimumSourceUrl": RENT_CURRENT_URL,
    "minimumSqmSourceUrl": RENT_CURRENT_URL,
    "samples": [
        {
            "id": "500584623", "price": 27000, "area": 45, "priceSqm": 600,
            "beds": 1, "title": "Family Condominium · 1 bedroom · 45 sqm · ฿27,000/month",
            "url": RENT_CURRENT_URL, "sourceName": "DDproperty", "projectName": "Family Condominium",
            "updated": "2026-09-24", "checkedAt": AS_OF, "listingStatus": "active_as_listed",
        },
        {
            "id": "500558512", "price": 25000, "area": 33, "priceSqm": 758,
            "beds": 1, "title": "Family Condominium · 1 bedroom · 33 sqm · ฿25,000/month",
            "url": RENT_STALE_URL, "sourceName": "DDproperty", "projectName": "Family Condominium",
            "updated": "2026-09-16", "checkedAt": AS_OF,
            "listingStatus": "availability_unconfirmed_update_over_30d",
        },
    ],
    "byBedroom": {"1": {
        "count": 1, "minimum": 27000, "area": 45, "minimumArea": 45,
        "priceSqm": 600, "minimumSqm": 600, "sourceUrl": RENT_CURRENT_URL,
        "minimumSourceUrl": RENT_CURRENT_URL, "minimumSqmSourceUrl": RENT_CURRENT_URL,
    }},
}
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

crosschecks = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next((row for row in crosschecks if int(row["hipflatId"]) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID, "projectName": "Family Condominium"}
    crosschecks.append(cross)
cross.update({
    "asOf": AS_OF,
    "sourceName": "DDproperty",
    "projectSourceUrl": SALE_DD_URL,
    "sale": {"activeListingCount": 5, "sourceUrl": SALE_DD_URL, "listings": []},
    "rent": {
        "activeListingCount": 4,
        "sourceUrl": RENT_PROJECT_URL,
        "listings": [
            {"id": "500584623", "bedrooms": 1, "price": 27000, "area": 45, "priceSqm": 600, "listedAt": "2026-09-24", "url": RENT_CURRENT_URL},
            {"id": "500558512", "bedrooms": 1, "price": 25000, "area": 33, "priceSqm": 758, "listedAt": "2026-09-16", "url": RENT_STALE_URL},
        ],
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 專案出售頁", "url": SALE_PROJECT_URL, "statusLabel": "頁面列出 3 筆出售；直接物件 6350597 為 1 房/Studio、27㎡、฿950,000，專案頁刷新於 2026-10-16。"},
        {"sourceName": "DDproperty 專案出售頁", "url": SALE_DD_URL, "statusLabel": "頁面列出 5 筆出售；未把未逐筆核對的 DD 掛牌併入均價。"},
        {"sourceName": "DDproperty 專案出租頁", "url": RENT_PROJECT_URL, "statusLabel": "頁面顯示 4 筆出租；個別頁核對到兩筆不同房型面積的 1 房掛牌，避免重複樣本。"},
        {"sourceName": "DDproperty 1 房出租物件", "url": RENT_CURRENT_URL, "statusLabel": "1 房/45㎡/฿27,000，Listed on 2026-09-24；約 25 日內，採為目前最低已核對租金單價 ฿600/㎡/月。"},
        {"sourceName": "DDproperty 較舊 1 房出租物件", "url": RENT_STALE_URL, "statusLabel": "1 房/33㎡/฿25,000，Listed on 2026-09-16；超過 30 日，保留來源但不納入目前租金基準與自動投報。"},
        {"sourceName": "Hipflat 專案頁", "url": "https://www.hipflat.co.th/en/projects/family-condominium-u9altatn1nnt1c40ctnet12un299704a", "statusLabel": "Hipflat 與 DDproperty 標示 2002 完工；PropertyHub 專案頁標示 2012，年份有來源衝突，沿用 Hipflat/DDproperty 的 2002 並標記待核。"},
    ],
})
write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

monthly_rent = round(600 * 27)
annual_rent_after_agent = monthly_rent * 11
report = {
    "hipflatId": PROJECT_ID,
    "project": "Family Condominium",
    "checkedAt": AS_OF,
    "sale": {
        "status": "direct_propertyhub_listing",
        "priceTHB": 950000,
        "areaSqm": 27,
        "priceTHBPerSqm": round(950000 / 27),
        "bedroomLabel": "PropertyHub says Studio; listing details and matched feed classify as 1 bedroom.",
        "source": SALE_URL,
    },
    "rent": {
        "currentSample": {"priceTHBPerMonth": 27000, "areaSqm": 45, "bedrooms": 1, "rateTHBPerSqmPerMonth": 600, "listedOn": "2026-09-24", "source": RENT_CURRENT_URL},
        "olderSample": {"priceTHBPerMonth": 25000, "areaSqm": 33, "bedrooms": 1, "listedOn": "2026-09-16", "status": "availability_unconfirmed_update_over_30d", "source": RENT_STALE_URL},
    },
    "yieldScenario": {
        "bedrooms": 1,
        "purchasePriceTHB": 950000,
        "purchaseAreaSqm": 27,
        "referenceMonthlyRentTHB": monthly_rent,
        "rentMethod": "Same-bedroom rent rate (THB 600/sqm/month) multiplied by the selected lowest direct sale sample area (27 sqm).",
        "annualRentAfterOneAgentMonthTHB": annual_rent_after_agent,
        "yieldAfterOneAgentMonthPercent": round(annual_rent_after_agent / 950000 * 100, 2),
        "yieldBeforeAgentMonthPercent": round(monthly_rent * 12 / 950000 * 100, 2),
        "commonFee": "Not found in checked project pages; not deducted.",
        "twoBedroomDefault": "Unavailable: no two-bedroom direct sale listing was verified. The 1-bedroom scenario is selectable in the calculator.",
    },
    "completionYear": {"value": 2002, "sources": ["Hipflat project page", "DDproperty listing/project data"], "conflict": "PropertyHub project details says 2012; unresolved."},
}
(ROOT / "reports" / "family-condominium-market-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "sale": "950000 THB / 27 sqm", "rentPerSqm": 600, "monthlyRentEstimate": monthly_rent, "yieldAfterAgent": round(annual_rent_after_agent / 950000 * 100, 2), "twoBedroomDefault": "unavailable"}))
