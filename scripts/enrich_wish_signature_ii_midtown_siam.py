from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 4319
PROJECT_NAME = "WISH Signature II Midtown Siam"
CHECKED = "2026-10-18"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/wish-signature-2-midtown-siam"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-wish-signature-2-midtown-siam"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-wish-signature-2-midtown-siam"
SALE_URL = "https://propertyhub.in.th/en/listings/2-bed-1-bath-47-sq-m-wish-signature-ii-midtown-siam---5890494"
RENT_URL = "https://propertyhub.in.th/en/listings/dl007033-condo-for-rent-wish-signature-2-midtown-siam-near-bts-ratchathewi-ready-to-move-in-call-urgently-0614453194-lineid-952jdxxk---3547164"
COORDINATE_CROSSCHECK = "https://thinkofliving.com/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B8%A3%E0%B8%B5%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B8%95%E0%B8%B6%E0%B8%81%E0%B9%80%E0%B8%AA%E0%B8%A3%E0%B9%87%E0%B8%88-wish-signature-ii-midtown-siam-%E0%B8%A7%E0%B8%B4%E0%B8%8A-%E0%B8%8B%E0%B8%B4%E0%B8%81%E0%B9%80%E0%B8%99%E0%B9%80%E0%B8%88%E0%B8%AD%E0%B8%A3%E0%B9%8C-2-%E0%B8%A1%E0%B8%B4%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C-%E0%B8%AA%E0%B8%A2%E0%B8%B2%E0%B8%A1-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-high-rise-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-bts-%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B9%80%E0%B8%97%E0%B8%A7%E0%B8%B5-%E0%B9%80%E0%B8%94%E0%B8%B4%E0%B8%99%E0%B9%84%E0%B8%9B%E0%B8%AA%E0%B8%A2%E0%B8%B2%E0%B8%A1%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B8%B2%E0%B8%81%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%94%E0%B9%89-%E0%B8%88%E0%B8%B2%E0%B8%81-siamnuwat-433725-%E0%B8%A3%E0%B8%B5%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3/"


def load_array(filename: str, symbol: str):
    path = DIST / filename
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Missing {symbol} in {filename}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


sale = {
    "id": "5890494", "price": 11_391_904, "area": 47, "priceSqm": round(11_391_904 / 47),
    "beds": 2, "roomType": "TWO_BED_ROOM", "title": "2 Bed 1 Bath 47 SQ.M Wish Signature II Midtown Siam",
    "url": SALE_URL, "sourceName": "PropertyHub", "projectName": PROJECT_NAME,
    "updated": "2026-10-15T04:40:00+07:00", "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
rent = {
    "id": "3547164", "price": 39_000, "area": 48, "priceSqm": 812.5,
    "beds": 2, "roomType": "TWO_BED_ROOM", "title": "DL007033 Condo for rent, Wish Signature 2 Midtown Siam, 2 bedrooms, 48 sqm",
    "url": RENT_URL, "sourceName": "PropertyHub", "projectName": PROJECT_NAME,
    "updated": "2026-10-18T19:00:51+07:00", "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}

manual_path, manual_rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    manual_rows.append(manual)
manual["name"] = PROJECT_NAME
for key, samples in (("sale", [sale]), ("rent", [rent])):
    market = manual.setdefault(key, {})
    existing = market.setdefault("samples", [])
    by_url = {row.get("url"): row for row in existing if row.get("url")}
    by_url.update({row["url"]: row for row in samples})
    market["samples"] = list(by_url.values())
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

for filename, symbol in (("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"), ("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")):
    path, rows = load_array(filename, symbol)
    row = next(item for item in rows if int(item.get("id", -1)) == PROJECT_ID)
    row.update({
        "completedYear": 2022,
        "propertyHubProjectUrl": PROPERTYHUB_PROJECT,
        "propertyHubSaleUrl": PROPERTYHUB_SALE,
        "propertyHubRentUrl": PROPERTYHUB_RENT,
    })
    write_array(path, symbol, rows)

scout_path, scout_rows = load_array("bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS")
scout = next(row for row in scout_rows if int(row.get("hipflatId", -1)) == PROJECT_ID)
scout["locationVerificationSourceUrl"] = COORDINATE_CROSSCHECK
scout["coordinateCrosscheckNote"] = "PropertyScout project pin 13.7509466,100.5352635 is within about 60 m of ThinkOfLiving Google Maps coordinates 13.7513372,100.5348561 and about 40 m of its earlier project preview pin 13.751292,100.535072; the exact project name and Ratchathewi location agree."
write_array(scout_path, "BANGKOK_PROPERTYSCOUT_DETAILS", scout_rows)

purchase, area = sale["price"], sale["area"]
rent_rate = rent["price"] / rent["area"]
monthly_rent = rent_rate * area
yield_after_agent_month = monthly_rent * 11 / purchase * 100
gross_yield = monthly_rent * 12 / purchase * 100

def haversine_m(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


property_scout_coord = (13.750946600417045, 100.53526347936435)
think_of_living_coord = (13.751337162701832, 100.53485605423093)
preview_coord = (13.751292, 100.535072)
report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": CHECKED,
    "coordinates": {
        "selected": list(property_scout_coord),
        "source": "https://propertyscout.co.th/en/bangkok/condo/wish-signature-ii-midtown-siam/",
        "crossChecks": [
            {"source": COORDINATE_CROSSCHECK, "coordinates": list(think_of_living_coord), "distanceFromSelectedMeters": round(haversine_m(property_scout_coord, think_of_living_coord), 1)},
            {"source": "https://thinkofliving.com/article/wish-signature-ii-midtown-siam-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-high-rise-%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%87-siam-paragon-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-bts-%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B9%80%E0%B8%97%E0%B8%A7%E0%B8%B5-%E0%B8%88%E0%B8%B2%E0%B8%81%E0%B8%AA%E0%B8%A2%E0%B8%B2%E0%B8%A1%E0%B8%99%E0%B8%B8%E0%B8%A7%E0%B8%B1%E0%B8%95%E0%B8%A3-preview-411782-%E0%B8%9E%E0%B8%A3%E0%B8%B5%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3/", "coordinates": list(preview_coord), "distanceFromSelectedMeters": round(haversine_m(property_scout_coord, preview_coord), 1)},
        ],
    },
    "completionYear": {"year": 2022, "source": PROPERTYHUB_PROJECT},
    "propertyHubProject": PROPERTYHUB_PROJECT,
    "saleListing": sale,
    "rentListing": rent,
    "yieldEstimate": {
        "bedrooms": 2, "purchasePriceThb": purchase, "saleAreaSqm": area,
        "rentListingThbPerMonth": rent["price"], "rentListingAreaSqm": rent["area"],
        "rentRateThbPerSqmMonth": round(rent_rate, 2),
        "estimatedMonthlyRentOnSaleAreaThb": round(monthly_rent, 2),
        "grossAnnualYieldPercent": round(gross_yield, 2),
        "annualYieldAfterOneAgentMonthPercent": round(yield_after_agent_month, 2),
        "commonFeeDeducted": False,
        "reason": "PropertyHub labels 80 THB/sqm as Utility Fee but does not establish that it is the common-area management fee; it is not deducted. The two-bedroom sale price and area come from the same direct listing, and rent is the verified 2BR rate per square metre multiplied by the 47 sqm sale unit area.",
    },
    "sources": [
        {"url": PROPERTYHUB_PROJECT, "finding": "Exact PropertyHub project page identifies 333 units, completion in 2022, and publishes a Utility Fee of 80 THB/sqm. The label does not confirm this as the condominium management fee."},
        {"url": SALE_URL, "finding": "Direct 2BR sale listing: 47 sqm, ฿11,391,904; exact project page shows refresh date 15 October 2026."},
        {"url": RENT_URL, "finding": "Direct 2BR rental listing: 48 sqm, ฿39,000/month, updated 18 October 2026."},
        {"url": COORDINATE_CROSSCHECK, "finding": "ThinkOfLiving publishes the project's Google Maps coordinates, within about 60 m of the selected PropertyScout project pin."},
    ],
    "limitations": ["PropertyHub refresh or update timestamps do not guarantee current availability; confirm with the advertiser.", "The 80 THB/sqm Utility Fee is not treated as a verified management fee."],
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "wish-signature-ii-midtown-siam-market-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "hipflatId": PROJECT_ID,
    "saleListing": SALE_URL,
    "rentListing": RENT_URL,
    "lowestVerifiedTwoBedroomSalePriceThb": purchase,
    "matchingSaleAreaSqm": area,
    "twoBedroomRentRateThbPerSqmMonth": rent_rate,
    "estimatedAnnualYieldAfterOneAgentMonthPercent": round(yield_after_agent_month, 2),
    "coordinateCrosscheckMeters": [report["coordinates"]["crossChecks"][0]["distanceFromSelectedMeters"], report["coordinates"]["crossChecks"][1]["distanceFromSelectedMeters"]],
}, ensure_ascii=False, indent=2))
