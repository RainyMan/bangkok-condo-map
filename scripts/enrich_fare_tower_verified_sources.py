from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PID = 3240
OSM_URL = "https://www.openstreetmap.org/way/387351098"
DD_PROJECT_URL = "https://www.ddproperty.com/en/project/310-fare-tower"
SALE_URL = "https://www.ddproperty.com/property/fare-tower-%E0%B9%81%E0%B8%9F%E0%B8%A3%E0%B9%8C-%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B9%80%E0%B8%A7%E0%B8%AD%E0%B8%A3%E0%B9%8C-%E0%B8%82%E0%B8%B2%E0%B8%A2-500507966"
RENT_URL = "https://www.ddproperty.com/en/property/fare-tower-bangkok-for-rent-500579179"
SALE_PRICE, SALE_AREA, SALE_BEDS = 6_990_000, 75.0, 2
RENT_PRICE, RENT_AREA, RENT_BEDS = 45_000, 86.92, 2
SALE_UPDATED, RENT_UPDATED = "2026-10-17", "2026-09-23"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        output.write(f"window.{symbol} = ")
        for chunk in encoder.iterencode(rows):
            output.write(chunk)
        output.write(";\n")
    temporary.replace(target)


def market(kind: str, price: int, area: float, beds: int, url: str, updated: str, title: str) -> dict:
    rate = price / area
    sample = {
        "id": url.rsplit("-", 1)[-1], "price": price, "area": area,
        "priceSqm": round(rate), "beds": beds, "roomType": "2BR", "title": title,
        "url": url, "sourceName": "DDproperty", "projectName": "Fare Tower",
        "updated": updated, "checkedAt": date.today().isoformat(),
        "matchedBy": "exact_project_name_address_and_unit_details",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }
    return {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_individual_listing",
        "average": price, "minimum": price, "minimumArea": area,
        "averageSqm": round(rate), "minimumSqm": round(rate),
        "minimumSampleUpdated": updated, "minimumSqmSampleUpdated": updated,
        "asOf": date.today().isoformat(), "snapshotMethod": "DDproperty direct 2-bedroom listing page",
        "sourceName": "DDproperty 個別掛牌", "source": DD_PROJECT_URL,
        "minimumSourceUrl": url, "minimumSqmSourceUrl": url,
        "byBedroom": {str(beds): {"count": 1, "minimum": price, "area": area,
                                    "priceSqm": round(rate), "minimumSqm": round(rate), "sourceUrl": url}},
        "samples": [sample],
    }


def main() -> None:
    projects = read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    project = next(row for row in projects if int(row["id"]) == PID)
    if project["name"] != "Fare Tower" or "370/5 Soi Sukhumvit 50" not in project.get("address", ""):
        raise RuntimeError("Fare Tower catalogue identity/address did not match the verified source")

    coordinates = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
    coordinate = {
        "hipflatId": PID, "name": "Fare Tower", "lat": 13.705521582913672,
        "lng": 100.59691215866356, "locationVerified": True,
        "sourceName": "OpenStreetMap 建物輪廓：Fair Tower",
        "sourceUrl": OSM_URL, "verificationSourceUrl": DD_PROJECT_URL,
        "verificationMethod": "exact_building_name_and_Sukhumvit_50_project_address; OSM polygon centroid",
    }
    coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PID]
    coordinates.append(coordinate)
    coordinates.sort(key=lambda row: int(row["hipflatId"]))
    write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinates)

    samples = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    row = next((item for item in samples if int(item["hipflatId"]) == PID), None)
    if row is None:
        row = {"hipflatId": PID, "name": "Fare Tower"}
        samples.append(row)
    row.update({
        "asOf": date.today().isoformat(),
        "sale": market("sale", SALE_PRICE, SALE_AREA, SALE_BEDS, SALE_URL, SALE_UPDATED,
                        "2-bedroom Fair Tower Sukhumvit 50, 75 sqm, THB 6,990,000 · DDproperty ID 500507966"),
        "rent": market("rent", RENT_PRICE, RENT_AREA, RENT_BEDS, RENT_URL, RENT_UPDATED,
                       "2-bedroom Fare Tower, 86.92 sqm, THB 45,000/month · DDproperty ID 500579179"),
        "coordinateSourceUrl": OSM_URL,
        "projectIdentitySourceUrl": DD_PROJECT_URL,
    })
    samples.sort(key=lambda item: int(item["hipflatId"]))
    write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", samples)

    estimated_rent = RENT_PRICE / RENT_AREA * SALE_AREA
    report = {
        "hipflatId": PID, "projectName": "Fare Tower", "checkedAt": date.today().isoformat(),
        "coordinates": coordinate,
        "saleListing": {"id": "500507966", "price": SALE_PRICE, "areaSqm": SALE_AREA,
                        "bedrooms": SALE_BEDS, "priceThbPerSqm": round(SALE_PRICE / SALE_AREA),
                        "updated": SALE_UPDATED, "url": SALE_URL},
        "rentListing": {"id": "500579179", "priceThbPerMonth": RENT_PRICE, "areaSqm": RENT_AREA,
                        "bedrooms": RENT_BEDS, "rentThbPerSqmMonth": round(RENT_PRICE / RENT_AREA, 2),
                        "updated": RENT_UPDATED, "url": RENT_URL},
        "yieldEstimate": {
            "bedrooms": 2, "purchasePriceThb": SALE_PRICE, "purchaseAreaSqm": SALE_AREA,
            "rentRateThbPerSqmMonth": round(RENT_PRICE / RENT_AREA, 2),
            "estimatedMonthlyRentOnSaleAreaThb": round(estimated_rent),
            "grossAnnualYieldPercent": round(estimated_rent * 12 / SALE_PRICE * 100, 2),
            "annualYieldAfterOneAgentMonthPercent": round(estimated_rent * 11 / SALE_PRICE * 100, 2),
            "commonFeeDeducted": False,
            "reason": "Paired direct 2-bedroom sale and rent listings; monthly rent rate is multiplied by the lowest observed two-bedroom sale unit area. No verified common fee available.",
        },
        "sources": [
            {"url": OSM_URL, "finding": "OSM building footprint named Fair Tower, tagged building=yes and 12 levels; map point uses footprint centroid."},
            {"url": DD_PROJECT_URL, "finding": "DDproperty project page identifies Fare Tower at Soi Sukhumvit 50 and describes Fair Tower Condominium."},
            {"url": SALE_URL, "finding": "Direct sale listing: 2 bedrooms, 75 sqm, THB 6,990,000; listed/reposted 17 Oct 2026."},
            {"url": RENT_URL, "finding": "Direct rent listing: 2 bedrooms, 86.92 sqm, THB 45,000/month; listed 23 Sep 2026."},
        ],
        "limitations": [
            "Listing pages show recent posting dates but present availability should be confirmed with advertisers.",
            "Common area fee not verified; yield estimate does not deduct it.",
            "Hipflat completion metadata (1996) and DDproperty descriptions (1991/1992) differ; existing completion year was not overwritten.",
        ],
    }
    output = ROOT / "reports" / f"fare-tower-location-market-yield-{date.today().isoformat()}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": PID, "lat": coordinate["lat"], "lng": coordinate["lng"],
                      "sale": SALE_PRICE, "rent": RENT_PRICE, "estimatedMonthlyRent": round(estimated_rent),
                      "grossYieldPercent": report["yieldEstimate"]["grossAnnualYieldPercent"],
                      "afterOneAgentMonthPercent": report["yieldEstimate"]["annualYieldAfterOneAgentMonthPercent"],
                      "report": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
