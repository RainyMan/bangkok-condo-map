from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "yong-charoen-complex-rent-roi-2026-10-19.json"
HIPFLAT_ID = 4055
NAME = "Yong Charoen Complex"
CHECKED = "2026-10-19"
RENT_URL = "https://zmyhome.com/property/V56241"
SALE_URL = "https://propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%A2%E0%B8%87%E0%B9%80%E0%B8%88%E0%B8%A3%E0%B8%B4%E0%B8%8D-%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%B4%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B9%8C40---6350516"
PROJECT_URL = "https://propertyhub.in.th/en/projects/yong-charoen-complex"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/yong-charoen-complex-bqjeur"


def read_array(filename: str, symbol: str):
    path = DIST / filename
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows):
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


# The ZmyHome listing is an exact individual unit page, identifies Yong Charoen
# Complex by name and Soi Suphapong 3, and was shown as updated six days before
# the 19 Oct 2026 check. Both this and the sale record are studios; PropertyHub
# normalizes studio records to beds=1, so preserve that same matching convention.
monthly_rent = 3200
rent_area = 27
rent_rate = monthly_rent / rent_area
rent_sample = {
    "id": "V56241",
    "price": monthly_rent,
    "area": rent_area,
    "priceSqm": round(rent_rate),
    "beds": 1,
    "roomType": "Studio",
    "title": "Yong Charoen Complex · Studio · 27 ㎡ · ฿3,200/月",
    "url": RENT_URL,
    "sourceName": "ZmyHome",
    "projectName": NAME,
    "updated": "2026-10-13",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_and_Soi_Suphapong_3_address_on_individual_unit_page",
    "listingStatus": "active_as_listed",
}
rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": monthly_rent,
    "minimum": monthly_rent,
    "minimumArea": rent_area,
    "minimumSampleUpdated": rent_sample["updated"],
    "averageSqm": round(rent_rate),
    "minimumSqm": round(rent_rate, 2),
    "minimumSqmSampleUpdated": rent_sample["updated"],
    "asOf": CHECKED,
    "snapshotMethod": "ZmyHome exact project-name and address match; direct individual rental listing",
    "sourceName": "ZmyHome 個別出租掛牌",
    "source": RENT_URL,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": monthly_rent,
            "area": rent_area,
            "minimumSqm": round(rent_rate, 2),
            "averageSqm": round(rent_rate, 2),
            "sourceUrl": RENT_URL,
            "minimumSourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
        }
    },
    "samples": [rent_sample],
}

manual_path, manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
entry = next((row for row in manual if int(row.get("hipflatId", 0)) == HIPFLAT_ID), None)
if entry is None:
    entry = {"hipflatId": HIPFLAT_ID, "name": NAME}
    manual.append(entry)
entry.update({"asOf": CHECKED, "rent": rent, "replaceRent": True})

# PropertyHub's direct sale listing states a unit management fee of ฿325/month
# for its 25 sqm studio. Normalize the same unit's published fee to ฿13/sqm/mo.
entry["fee"] = {
    "rate": 13,
    "status": "public",
    "source": SALE_URL,
    "note": "PropertyHub 個別出售頁列出此 25 ㎡ Studio 管理費 ฿325/月，折算 ฿13/㎡/月；其他戶型費額仍需向管委會確認。",
}
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

# The current lowest linked studio sale in the project sample is ฿520,000 / 25
# sqm. Pair it with the exact studio rent rate, then deduct one agent month and
# the published fee for the matched 25 sqm sale unit.
sale_price, sale_area = 520000, 25
estimated_monthly_rent = rent_rate * sale_area
annual_rent_after_agent = estimated_monthly_rent * 11
annual_common_fee = 13 * sale_area * 12
net_roi = (annual_rent_after_agent - annual_common_fee) / sale_price * 100

# Bust the browser cache for the changed manual sample file.
index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html, count = re.subn(
    r"bangkok-manual-market-samples\.js\?v=[^\"']+",
    "bangkok-manual-market-samples.js?v=20261019-yong-charoen-zmyhome-studio-rent",
    html,
    count=1,
)
if count != 1:
    raise RuntimeError("Could not update manual market sample cache key")
index_path.write_text(html, encoding="utf-8")

report = {
    "hipflatId": HIPFLAT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "hipflatProject": HIPFLAT_URL,
    "projectVerificationSource": PROJECT_URL,
    "sale": {
        "priceThb": sale_price,
        "areaSqm": sale_area,
        "pricePerSqmThb": sale_price / sale_area,
        "sourceUrl": SALE_URL,
        "note": "PropertyHub individual project listing states studio, 25 sqm, 1 bedroom, ฿520,000; unit page lists common fee ฿325/month. Project page count showed one sale listing and zero rent listings.",
    },
    "rent": {
        "priceThbPerMonth": monthly_rent,
        "areaSqm": rent_area,
        "pricePerSqmThbPerMonth": rent_rate,
        "sourceUrl": RENT_URL,
        "updated": rent_sample["updated"],
        "roomType": "Studio",
        "note": "ZmyHome's individual listing page matches project name and Soi Suphapong 3, shows Studio, 27 sqm, ฿3,200/month; listing table reported it updated six days before the check.",
    },
    "yield": {
        "matchedRoomType": "Studio (normalized to the source data's 1-bedroom convention)",
        "purchasePriceThb": sale_price,
        "purchaseAreaSqm": sale_area,
        "rentRateThbPerSqmMonth": round(rent_rate, 2),
        "estimatedMonthlyRentAtPurchaseAreaThb": round(estimated_monthly_rent),
        "annualRentAfterOneAgentMonthThb": round(annual_rent_after_agent),
        "annualCommonFeeThb": round(annual_common_fee),
        "netAnnualYieldPercent": round(net_roi, 2),
        "saleSourceUrl": SALE_URL,
        "rentSourceUrl": RENT_URL,
        "note": "Estimate deducts one month's rent for agent management and ฿325/month common fee reported for the selected 25 sqm unit. Excludes vacancy, taxes, repairs, and transaction costs; confirm listing availability and fee with the publisher/juristic office.",
    },
    "coordinate": {
        "lat": 13.69322717614331,
        "lng": 100.63930675959591,
        "sourceUrl": PROJECT_URL,
        "crossCheckUrl": HIPFLAT_URL,
        "status": "existing verified project coordinate; corroborated against Hipflat project identity/address",
    },
}
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": HIPFLAT_ID, "rentSampleAdded": 1, "rentThb": monthly_rent, "rentSqm": rent_area, "feeRate": 13, "netYieldPercent": round(net_roi, 2)}, ensure_ascii=False))
