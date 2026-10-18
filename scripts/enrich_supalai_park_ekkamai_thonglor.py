"""Add verified coordinates and exact two-bedroom PropertyHub samples."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT_ID = 3866
NAME = "Supalai Park Ekkamai - Thonglor"
CHECKED = "2026-10-18"
SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-supalai-park-ekkamai-thonglor"
RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-supalai-park-ekkamai-thonglor"
SALE_URL = "https://propertyhub.in.th/en/listings/30th-floor-2-br-supalai-park-ekamai-thonglor-near-arl-ramkhamhaeng-id-3240351---6341897"
RENT_URL = "https://propertyhub.in.th/en/listings/line-id-habitant-with-%EF%B8%8F-supalai-park-ekkamai-thonglor-fully-furnished-credit-cards-accepted---6244627"
HIPFLAT = "https://www.hipflat.co.th/en/projects/supalai-park-ekamai-thonglor-00cut23717nte07a0l0l4l20nce2lh2h"
ADDRESS_CROSSCHECK = "https://wanderlog.com/place/details/5417666/supalai-park-ekkamai-thonglor"
WALK_ROUTE = {
    "id": PROJECT_ID, "name": NAME,
    "originLat": 13.7435959, "originLng": 100.58939540000006,
    "distanceKm": 2.936, "minutes": 37, "stationId": "E6",
    "source": "Valhalla pedestrian routing (30 nearest stations checked)",
    "sourceUrl": "https://valhalla1.openstreetmap.de/",
    "networkSourceUrl": "https://www.openstreetmap.org/copyright",
    "asOf": CHECKED,
}

SALE_PRICE, SALE_AREA = 4_990_000, 82.0
RENT_PRICE, RENT_AREA = 24_000, 82.27
RENT_RATE = RENT_PRICE / RENT_AREA
ESTIMATED_MONTHLY_RENT = round(RENT_RATE * SALE_AREA)
GROSS_YIELD = ESTIMATED_MONTHLY_RENT * 12 / SALE_PRICE * 100
AFTER_AGENT_YIELD = ESTIMATED_MONTHLY_RENT * 11 / SALE_PRICE * 100


def read_js_array(path: pathlib.Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{symbol} = "
    if not text.startswith(prefix):
        raise RuntimeError(f"Unexpected JavaScript array format: {path}")
    return json.loads(text[len(prefix):].strip().rstrip(";"))


def write_js_array(path: pathlib.Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_sample = {
    "id": "6341897", "price": SALE_PRICE, "area": SALE_AREA,
    "priceSqm": round(SALE_PRICE / SALE_AREA), "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Great Value 2-BR Supalai Park Ekkamai - Thonglor (ID 3240351) · 82 sqm · ฿4,990,000",
    "url": SALE_URL, "sourceName": "PropertyHub",
    "projectName": NAME, "updated": CHECKED, "checkedAt": CHECKED,
    "matchedBy": "Exact PropertyHub project sale pages (all 107 structured listings, 55 two-bedroom); direct listing confirms project, 2 bedrooms, 82 sqm and ฿4,990,000",
    "listingStatus": "active_as_listed",
}
rent_sample = {
    "id": "6244627", "price": RENT_PRICE, "area": RENT_AREA,
    "priceSqm": round(RENT_RATE), "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Supalai Park Ekkamai - Thonglor · 2BR · 82.27 sqm · ฿24,000/month (two-year contract)",
    "url": RENT_URL, "sourceName": "PropertyHub",
    "projectName": NAME, "updated": CHECKED, "checkedAt": CHECKED,
    "matchedBy": "Exact PropertyHub project rent pages (all 158 structured listings, 63 two-bedroom); rent is ฿24,000/month for a two-year contract and ฿25,000/month for one year. Listing summary and project card report 82.27 sqm; one descriptive sentence says 84.27 sqm, so the area discrepancy is flagged.",
    "listingStatus": "active_as_listed",
}

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual = read_js_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = [row for row in manual if int(row.get("hipflatId", -1)) != PROJECT_ID]
manual.append({"hipflatId": PROJECT_ID, "name": NAME, "asOf": CHECKED,
               "sale": {"samples": [sale_sample]}, "rent": {"samples": [rent_sample]}})
write_js_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

coordinate_path = ROOT / "dist/bangkok-verified-coordinates.js"
coordinates = read_js_array(coordinate_path, "BANGKOK_VERIFIED_COORDINATES")
coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
coordinates.append({
    "hipflatId": PROJECT_ID, "name": NAME,
    "lat": 13.7435959, "lng": 100.58939540000006,
    "locationVerified": True,
    "sourceName": "PropertyHub 專案頁結構化座標",
    "sourceUrl": SALE_PROJECT,
    "verificationSourceUrl": HIPFLAT,
    "corroborationSourceUrl": ADDRESS_CROSSCHECK,
    "verificationMethod": "PropertyHub project record gives 13.7435959, 100.5893954 for exact project name; cross-checked against Hipflat project and the matching New Phetchaburi Alley, Bang Kapi address / PHVQ+7H2 public place listing.",
    "asOf": CHECKED,
})
write_js_array(coordinate_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

walking_path = ROOT / "dist/bangkok-walk-routes.js"
walking = read_js_array(walking_path, "BANGKOK_WALK_ROUTES")
walking = [row for row in walking if int(row.get("id", -1)) != PROJECT_ID]
walking.append(WALK_ROUTE)
write_js_array(walking_path, "BANGKOK_WALK_ROUTES", walking)

report = {
    "project": NAME, "hipflatId": PROJECT_ID, "checkedAt": CHECKED,
    "coordinates": {
        "lat": 13.7435959, "lng": 100.58939540000006,
        "source": SALE_PROJECT, "crossCheck": [HIPFLAT, ADDRESS_CROSSCHECK],
    },
    "nearestWalkingTransit": {
        "stationId": WALK_ROUTE["stationId"],
        "distanceKm": WALK_ROUTE["distanceKm"], "minutes": WALK_ROUTE["minutes"],
        "method": WALK_ROUTE["source"], "source": WALK_ROUTE["sourceUrl"],
    },
    "sources": {"saleProject": SALE_PROJECT, "rentProject": RENT_PROJECT,
                "saleListing": SALE_URL, "rentListing": RENT_URL},
    "enumeration": {
        "saleStructuredRows": 107, "twoBedroomSaleRows": 55,
        "rentStructuredRows": 158, "twoBedroomRentRows": 63,
        "discrepancy": "Rendered sale project page says Found 110 properties while structured page pagination totals 107; the selected two-bedroom minimum was compared across all 107 structured rows. The selected rent minimum was compared across all 158 structured rows.",
    },
    "saleMinimumTwoBedroom": {"priceThb": SALE_PRICE, "areaSqm": SALE_AREA,
                               "pricePerSqmThb": round(SALE_PRICE / SALE_AREA),
                               "listingId": sale_sample["id"], "source": SALE_URL,
                               "updated": CHECKED},
    "rentMinimumTwoBedroomRate": {"monthlyThb": RENT_PRICE, "areaSqm": RENT_AREA,
                                  "pricePerSqmMonthThb": round(RENT_RATE, 2),
                                  "listingId": rent_sample["id"], "source": RENT_URL,
                                  "contractTerms": {"oneYearThbPerMonth": 25_000,
                                                    "twoYearThbPerMonth": 24_000},
                                  "areaDiscrepancy": "Page summary, top-level facts and project card report 82.27 sqm; one descriptive sentence states 84.27 sqm. Calculations use the repeated structured/list-card area 82.27 sqm."},
    "yieldEstimate": {
        "bedrooms": 2, "purchasePriceThb": SALE_PRICE,
        "purchaseAreaSqm": SALE_AREA, "rentRateThbPerSqmMonth": round(RENT_RATE, 4),
        "estimatedMonthlyRentAtPurchaseAreaThb": ESTIMATED_MONTHLY_RENT,
        "grossAnnualYieldPercent": round(GROSS_YIELD, 2),
        "afterOneAgentMonthBeforeCommonFeePercent": round(AFTER_AGENT_YIELD, 2),
        "commonFee": "Unverified; excluded.",
        "purchaseSource": SALE_URL, "rentSource": RENT_URL,
        "formula": "((24,000 / 82.27) * 82 * 11) / 4,990,000 * 100",
    },
    "completionYear": {"year": 2015, "source": SALE_PROJECT},
    "managementFee": {"status": "unverified", "projectPageValue": "- THB/sq.m."},
    "notes": [
        "The sale and rent minimums are exact two-bedroom PropertyHub listings, checked across both pages of each current exact-project result set.",
        "PropertyHub structured pagination and rendered total-count labels differ; neither discrepancy changes the selected minimum among structured rows.",
        "The lowest-rent listing shows a two-year contract at THB 24,000/month and a one-year contract at THB 25,000/month.",
        "The rent listing has a 82.27/84.27 sqm text inconsistency; the 82.27 sqm area is repeated in structured listing fields and project result cards.",
        "Common fee is not published as an amount and is not deducted from the estimate.",
    ],
}
(ROOT / "reports/supalai-park-ekkamai-thonglor-listings-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [13.7435959, 100.58939540000006],
                  "sale2br": [SALE_PRICE, SALE_AREA], "rent2br": [RENT_PRICE, RENT_AREA],
                  "rentPerSqm": round(RENT_RATE, 2), "monthlyRentAtSaleArea": ESTIMATED_MONTHLY_RENT,
                  "grossYield": round(GROSS_YIELD, 2),
                  "afterOneAgentMonthBeforeFee": round(AFTER_AGENT_YIELD, 2)}, ensure_ascii=False))
