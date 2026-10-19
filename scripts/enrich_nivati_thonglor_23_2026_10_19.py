from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
ID = 4239
NAME = "Nivati Thonglor 23"
CHECKED = "2026-10-19"
PH_PROJECT = "https://propertyhub.in.th/en/projects/nivati-residence"
PH_SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-nivati-residence"
PH_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-nivati-residence"
SALE_URL = "https://propertyhub.in.th/en/listings/nivati-residence-2-bedrooms-for-sale--a5eb08dc---5041991"
RENT_URL = "https://propertyhub.in.th/en/listings/2-bed-3-bath-139-sq-m-nivati-residence--a59f0917---5055276"
HIPFLAT = "https://www.hipflat.co.th/en/projects/nivati-thonglor-23-mnpgio"
COORDINATE_SOURCE = "https://propertyscout.co.th/en/bangkok/condo/nivati-thonglor-23/"


def read_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.DOTALL)
    if not match:
        raise ValueError(f"Cannot find {symbol}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )

sale_price, sale_area = 19_000_000, 104.17
rent_price, rent_area = 120_000, 139
sale_rate = round(sale_price / sale_area)
rent_rate = rent_price / rent_area
scaled_rent = round(rent_rate * sale_area)
net_yield_after_agent = round(scaled_rent * 11 / sale_price * 100, 2)

def sample(kind: str, listing_id: str, price: int, area: float, beds: int, url: str, title: str, updated: str) -> dict:
    return {
        "id": listing_id,
        "price": price,
        "area": area,
        "priceSqm": round(price / area),
        "beds": beds,
        "roomType": "2 Bedroom",
        "url": url,
        "title": title,
        "sourceName": "PropertyHub",
        "projectName": "Nivati Residence / Nivati Thonglor 23",
        "updated": updated,
        "checkedAt": CHECKED,
        "matchedBy": "exact_project_alias_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }

sale_sample = sample(
    "sale", "5041991", sale_price, sale_area, 2, SALE_URL,
    "Nivati Residence · 2 房 2 衛 · 104.17 ㎡ · ฿19,000,000",
    "2026-10-18",
)
rent_sample = sample(
    "rent", "5055276", rent_price, rent_area, 2, RENT_URL,
    "Nivati Residence · 2 房 3 衛 · 139 ㎡ · ฿120,000/月",
    "2026-10-16",
)

markets = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
entry = next((row for row in markets if int(row.get("hipflatId", -1)) == ID), None)
if entry is None:
    entry = {"hipflatId": ID, "name": NAME}
entry.update({"asOf": CHECKED, "sale": {"samples": [sale_sample]}})
entry["rent"] = {
    "count": 9,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": rent_price,
    "minimum": rent_price,
    "minimumArea": rent_area,
    "minimumSampleUpdated": rent_sample["updated"],
    "averageSqm": round(rent_rate),
    "minimumSqm": rent_rate,
    "minimumSqmSampleUpdated": rent_sample["updated"],
    "asOf": CHECKED,
    "sourceName": "PropertyHub 個別出租掛牌",
    "source": PH_RENT_PROJECT,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": rent_price,
            "area": rent_area,
            "minimumArea": rent_area,
            "minimumSqm": rent_rate,
            "sourceUrl": RENT_URL,
            "minimumSourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
        }
    },
    "samples": [rent_sample],
}
entry["availabilitySources"] = [
    {"sourceName": "PropertyHub 專案資料", "url": PH_PROJECT, "statusLabel": "顯示 Nivati Residence／Nivati Thonglor 23 為同一 Condo；刊載 52 戶、7 層。專案頁顯示 23 售、9 租；管理費欄未提供。"},
    {"sourceName": "PropertyHub 出售專案頁", "url": PH_SALE_PROJECT, "statusLabel": "兩房最低總價掛牌 ฿19,000,000／104.17㎡；專案頁標示最近更新 2026-10-18。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": PH_RENT_PROJECT, "statusLabel": "兩房低租金單價樣本 ฿120,000/月／139㎡，專案頁標示最近更新 2026-10-16；非獨立確認空置。"},
    {"sourceName": "PropertyScout 座標及專案頁", "url": COORDINATE_SOURCE, "statusLabel": "與 Hipflat Nivati Thonglor 23 同名專案核對；現有地圖座標已驗證。"},
    {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "以 Hipflat 專案識別頁核對名稱及地址。"},
]
markets = [row for row in markets if int(row.get("hipflatId", -1)) != ID] + [entry]
markets.sort(key=lambda row: int(row.get("hipflatId", 0)))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

crosschecks = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": ID,
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "PropertyHub",
    "projectSourceUrl": PH_PROJECT,
    "sale": {"activeListingCount": 23, "listings": [sale_sample], "sourceUrl": PH_SALE_PROJECT},
    "rent": {"activeListingCount": 9, "sourceUrl": PH_RENT_PROJECT, "listings": [rent_sample]},
    "availabilitySources": entry["availabilitySources"],
    "roi": {
        "status": "estimated_from_direct_same_bedroom_listings",
        "purchasePriceTHB": sale_price,
        "purchaseAreaSqm": sale_area,
        "purchasePriceTHBPerSqm": round(sale_price / sale_area),
        "monthlyRentPerSqmTHB": round(rent_rate, 2),
        "estimatedMonthlyRentForPurchaseAreaTHB": scaled_rent,
        "netAnnualYieldAfterOneAgentMonthPercent": net_yield_after_agent,
        "managementFeeDeducted": False,
        "assumptions": "Two-bedroom lowest total sale price and its own floor area; lowest same-bedroom rent per sqm scaled to the purchase area; deduct one agent month; no management fee deducted because no verified rate is published.",
        "saleSourceUrl": SALE_URL,
        "rentSourceUrl": RENT_URL,
    },
}
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != ID] + [crosscheck]
crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "identity": {"hipflatProject": HIPFLAT, "propertyHubProject": PH_PROJECT, "matchedAliases": ["Nivati Residence", "Nivati Thonglor 23"]},
    "coordinates": {"status": "previously_verified", "latitude": 13.73887535767737, "longitude": 100.58037554956708, "source": COORDINATE_SOURCE, "method": "exact_project_name_and_district"},
    "sale": {"status": "direct_individual_listing", "listingId": "5041991", "bedrooms": 2, "priceTHB": sale_price, "areaSqm": sale_area, "priceTHBPerSqm": round(sale_price / sale_area), "projectPageUpdatedAt": sale_sample["updated"], "source": SALE_URL, "projectSource": PH_SALE_PROJECT},
    "rent": {"status": "direct_individual_listing_availability_unconfirmed", "listingId": "5055276", "bedrooms": 2, "monthlyRentTHB": rent_price, "areaSqm": rent_area, "rentTHBPerSqmPerMonth": round(rent_rate, 2), "projectPageUpdatedAt": rent_sample["updated"], "source": RENT_URL, "projectSource": PH_RENT_PROJECT},
    "fee": {"status": "not_published", "source": PH_PROJECT, "note": "PropertyHub 專案頁的 Common Fee 欄未提供費率；投報試算未扣管理費。"},
    "yield": {"status": "estimated", "netAnnualYieldAfterOneAgentMonthPercent": net_yield_after_agent, "purchasePriceTHB": sale_price, "purchaseAreaSqm": sale_area, "rentRateTHBPerSqmPerMonth": round(rent_rate, 2), "imputedMonthlyRentTHB": scaled_rent, "formula": "(月租 × 11) ÷ 購入總價", "grossBeforeAgentPercent": round(scaled_rent * 12 / sale_price * 100, 2), "sourceSale": SALE_URL, "sourceRent": RENT_URL},
    "limitations": "PropertyHub displays listing refresh dates, but current availability is not independently confirmed. No public management-fee rate was found, so none was deducted.",
}
(REPORTS / "nivati-thonglor-23-market-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html, a = re.subn(r"bangkok-manual-market-samples\.js\?v=[^\"']+", "bangkok-manual-market-samples.js?v=20261019-nivati-thonglor-23-market", html, count=1)
html, b = re.subn(r"bangkok-market-crosschecks\.js\?v=[^\"']+", "bangkok-market-crosschecks.js?v=20261019-nivati-thonglor-23-market", html, count=1)
if a != 1 or b != 1:
    raise ValueError("Could not bump source data cache revisions")
index_path.write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": ID, "saleListing": sale_sample["id"], "rentListing": rent_sample["id"], "lowestTwoBedroomPrice": sale_price, "pairedArea": sale_area, "scaledMonthlyRent": scaled_rent, "netYieldAfterOneAgentMonthPercent": net_yield_after_agent}, ensure_ascii=False))
