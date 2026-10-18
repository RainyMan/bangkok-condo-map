from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 4074
PROJECT_NAME = "Lumpini Place Ratchayotin"
CHECKED = "2026-10-18"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/lumpini-place-ratchayothin"
SALE_URL = "https://propertyhub.in.th/en/listings/for-sell-condo-lumpini-place-ratchayothin-building-b-floor-2-1-bed-room-room-size-28-5-sqm---5999717"
RENT_1BR_URL = "https://propertyhub.in.th/en/listings/for-rent-lumpini-place-ratchayothin-add-line-id-zcondo-with-z5150---6335611"
RENT_2BR_URL = "https://propertyhub.in.th/en/listings/lumpini-place-ratchayothin-for-rent--b43a09c7---6131955"
COORDINATE_CROSSCHECK = "https://thinkofliving.com/project/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/199/"


def load_array(filename: str, symbol: str):
    path = DIST / filename
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Missing {symbol} in {filename}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


sale = {
    "id": "5999717", "price": 2_480_000, "area": 28.5, "priceSqm": round(2_480_000 / 28.5),
    "beds": 1, "roomType": "ONE_BED_ROOM", "title": "For Sell Condo LUMPINI PLACE RATCHAYOTHIN Building B, Floor 2, 1 bedroom, 28.5 sqm",
    "url": SALE_URL, "sourceName": "PropertyHub", "projectName": "Lumpini Place Ratchayothin",
    "updated": "2026-09-15T12:01:00+07:00", "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_over_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
rent_1br = {
    "id": "6335611", "price": 11_000, "area": 28, "priceSqm": round(11_000 / 28, 2),
    "beds": 1, "roomType": "ONE_BED_ROOM", "title": "For Rent Lumpini Place Ratchayothin Z5150, 1 bedroom, 28 sqm",
    "url": RENT_1BR_URL, "sourceName": "PropertyHub", "projectName": "Lumpini Place Ratchayothin",
    "updated": "2026-09-15T12:13:00+07:00", "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_over_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}
rent_2br = {
    "id": "6131955", "price": 23_500, "area": 56, "priceSqm": round(23_500 / 56, 2),
    "beds": 2, "roomType": "TWO_BED_ROOM", "title": "Lumpini Place Ratchayothin for Rent, 2 bedrooms, 56 sqm",
    "url": RENT_2BR_URL, "sourceName": "PropertyHub", "projectName": "Lumpini Place Ratchayothin",
    "updated": "2026-10-11T14:18:00+07:00", "checkedAt": CHECKED,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "exact_project_page_listing_and_direct_unit_page",
}

manual_path, manual_rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    manual_rows.append(manual)
manual["name"] = PROJECT_NAME
for key, samples in (("sale", [sale]), ("rent", [rent_1br, rent_2br])):
    market = manual.setdefault(key, {})
    existing = market.setdefault("samples", [])
    by_url = {row.get("url"): row for row in existing if row.get("url")}
    by_url.update({row["url"]: row for row in samples})
    market["samples"] = list(by_url.values())
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

# Link to the exact PropertyHub project and point the map's coordinate source
# to an independent project profile that publishes coordinates.
for filename, symbol in (("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"), ("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")):
    path, rows = load_array(filename, symbol)
    row = next(item for item in rows if int(item.get("id", -1)) == PROJECT_ID)
    row.update({
        "propertyHubProjectUrl": PROPERTYHUB_PROJECT,
        "propertyHubSaleUrl": "https://propertyhub.in.th/en/condo-for-sale/project-lumpini-place-ratchayothin",
        "propertyHubRentUrl": "https://propertyhub.in.th/en/condo-for-rent/project-lumpini-place-ratchayothin",
    })
    write_array(path, symbol, rows)

scout_path, scout_rows = load_array("bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS")
scout = next(row for row in scout_rows if int(row.get("hipflatId", -1)) == PROJECT_ID)
scout["locationVerificationSourceUrl"] = COORDINATE_CROSSCHECK
scout["coordinateCrosscheckNote"] = "PropertyScout 13.830093,100.571178 is within 30 m of independent ThinkOfLiving coordinates 13.830025,100.570931 and LivingInsider Google Maps pin 13.830353,100.571042; exact project name and Chatuchak district agree."
write_array(scout_path, "BANGKOK_PROPERTYSCOUT_DETAILS", scout_rows)

# 1-bedroom baseline uses the lowest linked 1BR price and matching 28.5 sqm.
# Rent uses the lowest linked 1BR rate; no common fee is published, so only
# one agent month is deducted and a 2BR sale yield remains unavailable.
purchase = sale["price"]
area = sale["area"]
monthly_rent_estimate = rent_1br["price"] / rent_1br["area"] * area
yield_after_agent_month = monthly_rent_estimate * 11 / purchase * 100
property_scout_coord = (13.830093, 100.571178)
think_of_living_coord = (13.8300252843, 100.5709312368)
livinginsider_coord = (13.83035302, 100.57104245)
def haversine_m(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6_371_000 * 2 * math.atan2(math.sqrt(h), math.sqrt(1-h))

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": CHECKED,
    "coordinates": {
        "selected": list(property_scout_coord),
        "source": "https://propertyscout.co.th/en/bangkok/condo/lumpini-place-ratchayothin/",
        "crossChecks": [
            {"source": COORDINATE_CROSSCHECK, "coordinates": list(think_of_living_coord), "distanceFromSelectedMeters": round(haversine_m(property_scout_coord, think_of_living_coord), 1)},
            {"source": "https://www.livinginsider.com/livingdetail_en/2650440/Lumpini-Place-Ratchayothin-Condominium-for-sale-in-Chatuchak-Bangkok.html", "coordinates": list(livinginsider_coord), "distanceFromSelectedMeters": round(haversine_m(property_scout_coord, livinginsider_coord), 1)},
        ],
    },
    "propertyHubProject": PROPERTYHUB_PROJECT,
    "saleListing": sale,
    "rentListings": [rent_1br, rent_2br],
    "yieldEstimate": {
        "bedrooms": 1, "purchasePriceThb": purchase, "saleAreaSqm": area,
        "rentRateThbPerSqmMonth": round(rent_1br["price"] / rent_1br["area"], 2),
        "estimatedMonthlyRentOnSaleAreaThb": round(monthly_rent_estimate),
        "annualYieldAfterOneAgentMonthPercent": round(yield_after_agent_month, 2),
        "commonFeeDeducted": False,
        "reason": "PropertyHub project details show no common-fee amount. A verified two-bedroom sale listing was not found, so a default two-bedroom yield is not inferred; the selected one-bedroom baseline uses a linked 1BR sale and rental sample.",
    },
    "sources": [
        {"url": PROPERTYHUB_PROJECT, "finding": "Exact project page identifies Lumpini Place Ratchayothin, 1,822 units, completed 2011; common fee is not published."},
        {"url": SALE_URL, "finding": "Individual PropertyHub sale listing: 1BR, 28.5 sqm, ฿2,480,000."},
        {"url": RENT_1BR_URL, "finding": "Individual PropertyHub rental listing: 1BR, 28 sqm, ฿11,000/month."},
        {"url": RENT_2BR_URL, "finding": "Individual PropertyHub rental listing: 2BR, 56 sqm, ฿23,500/month."},
    ],
    "limitations": ["Listing page refresh dates do not confirm that the units remain available.", "No current individual two-bedroom sale page was verified; no default two-bedroom yield is displayed."],
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "lumpini-place-ratchayotin-market-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "saleListing": SALE_URL, "rentListings": [RENT_1BR_URL, RENT_2BR_URL], "estimated1BedroomNetYieldAfterAgentMonthPercent": round(yield_after_agent_month, 2), "verifiedCoordinateCrosscheckMeters": [report["coordinates"]["crossChecks"][0]["distanceFromSelectedMeters"], report["coordinates"]["crossChecks"][1]["distanceFromSelectedMeters"]], "twoBedroomYield": "not calculated: no individual two-bedroom sale sample"}, ensure_ascii=False, indent=2))
