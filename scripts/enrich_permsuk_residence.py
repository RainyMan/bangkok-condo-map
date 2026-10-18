"""Add verified location and linked market samples for Permsuk Residence."""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3152
NAME = "Permsuk Residence"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/permsuk-residence-vhhnxs"
ZMY_PROJECT_URL = "https://zmyhome.com/project/V17766"
ZMY_COORDINATE_SEARCH_URL = "https://zmyhome.com/search/result?id=17766&keyword=%E0%B9%80%E0%B8%9E%E0%B8%B4%E0%B9%88%E0%B8%A1%E0%B8%AA%E0%B8%B8%E0%B8%82%E0%B9%80%E0%B8%A3%E0%B8%AA%E0%B8%8B%E0%B8%B4%E0%B9%80%E0%B8%94%E0%B8%99%E0%B8%8B%E0%B9%8C+2&lat=13.7853612000&lng=100.5959766000&type=Project&typePost%5B0%5D=1&typeProperty%5B0%5D=1"
ENN_PROJECT_URL = "https://www.ennxo.com/condo/for-sale/project/permsuk-residence"
ENN_LISTING_URL = "https://www.ennxo.com/product/1163761"
ZMY_SALE_URL = "https://zmyhome.com/property/V179457"
ZMY_RENT_URL = "https://zmyhome.com/property/V179458"
ZMY_UPDATED_SALE_URL = "https://zmyhome.com/property/V208989"
LAT, LNG = 13.7853612, 100.5959766
CHECKED = date.today().isoformat()

SALE_SAMPLES = [
    {
        "id": "1163761", "price": 490_000, "area": 32, "beds": 1,
        "roomType": "1 Bedroom", "title": "Permsuk Residence 2，1 房，32㎡",
        "url": ENN_LISTING_URL, "sourceName": "ENNXO",
        "projectName": "Permsuk Residence 2", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_address_and_project_listing",
        "listingStatus": "availability_unconfirmed_date_unknown",
    },
    {
        "id": "V208989", "price": 560_000, "area": 31.57,
        "title": "Permsuk Residence 2，31.57㎡，機構出售",
        "url": ZMY_UPDATED_SALE_URL, "sourceName": "ZmyHome",
        "projectName": "Permsuk Residence 2", "updated": "2026-09-02",
        "checkedAt": CHECKED, "matchedBy": "exact_project_name_and_address",
        "listingStatus": "availability_unconfirmed_update_over_30d",
    },
    {
        "id": "V179457", "price": 990_000, "area": 64, "beds": 2,
        "roomType": "2 Bedroom", "title": "Permsuk Residence 2，2 房，64㎡",
        "url": ZMY_SALE_URL, "sourceName": "ZmyHome",
        "projectName": "Permsuk Residence 2", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_address",
        "listingStatus": "availability_unconfirmed_date_unknown",
    },
]
RENT_SAMPLES = [
    {
        "id": "V179458", "price": 7_000, "area": 64, "beds": 2,
        "roomType": "2 Bedroom", "title": "Permsuk Residence 2，2 房，64㎡",
        "url": ZMY_RENT_URL, "sourceName": "ZmyHome",
        "projectName": "Permsuk Residence 2", "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_address",
        "listingStatus": "availability_unconfirmed_date_unknown",
    },
]


def read_js_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Cannot read {symbol} from {path}")
    return json.loads(match.group(1))


def write_js_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def market(samples: list[dict], kind: str) -> dict:
    rows = [{**row, "priceSqm": row["price"] / row["area"]} for row in samples]
    low_total = min(rows, key=lambda row: row["price"])
    low_sqm = min(rows, key=lambda row: row["priceSqm"])
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        if int(row.get("beds") or 0) > 0:
            grouped.setdefault(str(row["beds"]), []).append(row)
    by_bedroom = {}
    for beds, group in grouped.items():
        cheapest = min(group, key=lambda row: row["price"])
        lowest_rate = min(group, key=lambda row: row["priceSqm"])
        by_bedroom[beds] = {
            "count": len(group), "minimum": cheapest["price"], "area": cheapest["area"],
            "priceSqm": round(cheapest["priceSqm"]), "minimumSqm": round(lowest_rate["priceSqm"], 2),
            "sourceUrl": cheapest["url"], "minimumSqmSourceUrl": lowest_rate["url"],
        }
    return {
        "count": len(rows), "observedCount": len(rows), "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in rows) / len(rows)),
        "minimum": low_total["price"], "minimumArea": low_total["area"],
        "averageSqm": round(sum(row["priceSqm"] for row in rows) / len(rows)),
        "minimumSqm": round(low_sqm["priceSqm"], 2), "asOf": CHECKED,
        "sourceName": "可核對的個別掛牌樣本",
        "source": ENN_PROJECT_URL if kind == "sale" else ZMY_RENT_URL,
        "minimumSourceUrl": low_total["url"], "minimumSqmSourceUrl": low_sqm["url"],
        "samples": sorted(rows, key=lambda row: row["price"]), "byBedroom": by_bedroom,
    }


def update_manual_samples() -> dict:
    path = DIST / "bangkok-manual-market-samples.js"
    rows = read_js_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(project)
    project["sale"] = market(SALE_SAMPLES, "sale")
    project["rent"] = market(RENT_SAMPLES, "rent")
    project["sourceNote"] = "Exact-project individual ads from ENNXO and ZmyHome. Listing availability is unconfirmed where the source page gives no current status/update date."
    write_js_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)
    return project


def update_coordinate() -> None:
    path = DIST / "bangkok-verified-coordinates.js"
    rows = read_js_array(path, "BANGKOK_VERIFIED_COORDINATES")
    project = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(project)
    project.update({
        "lat": LAT, "lng": LNG, "locationVerified": True,
        "sourceName": "ZmyHome 專案地圖座標",
        "sourceUrl": ZMY_PROJECT_URL,
        "corroborationSourceUrl": ZMY_COORDINATE_SEARCH_URL,
        "verificationMethod": "Exact project page and project-centered listing search resolve to the same pin at 13.7853612, 100.5959766.",
        "asOf": CHECKED,
    })
    write_js_array(path, "BANGKOK_VERIFIED_COORDINATES", rows)


def update_walk_route() -> dict:
    route = {
        "id": PROJECT_ID, "name": NAME, "originLat": LAT, "originLng": LNG,
        "distanceKm": 1.668, "minutes": 20, "stationId": "YL04",
        "source": "Valhalla pedestrian routing (30 nearest stations checked)",
        "sourceUrl": "https://valhalla1.openstreetmap.de/",
        "networkSourceUrl": "https://www.openstreetmap.org/copyright", "asOf": CHECKED,
    }
    path = DIST / "bangkok-walk-routes.js"
    rows = read_js_array(path, "BANGKOK_WALK_ROUTES")
    rows = [row for row in rows if int(row.get("id", 0)) != PROJECT_ID]
    rows.append(route)
    write_js_array(path, "BANGKOK_WALK_ROUTES", rows)
    return route


def update_cache_busters() -> None:
    path = DIST / "index.html"
    text = path.read_text(encoding="utf-8")
    version = "20261018s-permsuk-residence-data"
    for filename, old in (
        ("bangkok-verified-coordinates.js", r'bangkok-verified-coordinates\.js\?v=[^\"]+'),
        ("bangkok-manual-market-samples.js", r'bangkok-manual-market-samples\.js\?v=[^\"]+'),
        ("bangkok-walk-routes.js", r'bangkok-walk-routes\.js\?v=[^\"]+'),
    ):
        text, count = re.subn(old, f"{filename}?v={version}", text, count=1)
        if count != 1:
            raise ValueError(f"Could not update cache version for {filename}")
    path.write_text(text, encoding="utf-8")


def update_reports(sale: dict, rent: dict, route: dict) -> dict:
    two_bed_sale = sale["byBedroom"]["2"]
    two_bed_rent = rent["byBedroom"]["2"]
    estimated_monthly_rent = round(two_bed_rent["minimumSqm"] * two_bed_sale["area"])
    annual_rent_after_agent = estimated_monthly_rent * 11
    net_yield = annual_rent_after_agent / two_bed_sale["minimum"] * 100
    report = {
        "hipflatId": PROJECT_ID, "name": NAME, "checkedAt": CHECKED,
        "projectIdentity": {
            "hipflatProjectUrl": HIPFLAT_URL, "hipflatAddress": "Phoem Suk Residence, 661/22 Soi Lat Phrao 64, Wang Thonglang",
            "matchEvidence": "The Hipflat page gives 297 units and 8 floors. PropertyHub and ZmyHome label the same 661/22 Lat Phrao 64 address as Permsuk Residence 2 and also give 297 units.",
            "projectSourceUrl": "https://propertyhub.in.th/projects/permsuk-residence-2",
        },
        "location": {
            "status": "verified_exact_project_pin", "lat": LAT, "lng": LNG,
            "sourceUrl": ZMY_PROJECT_URL, "corroborationSourceUrl": ZMY_COORDINATE_SEARCH_URL,
            "method": "ZmyHome's exact-project location and project-centered search link resolve to the project pin.",
        },
        "projectDetails": {
            "completedYear": 1995, "units": 297, "floors": 8,
            "sourceUrl": HIPFLAT_URL,
            "conflict": "PropertyHub's page for Permsuk Residence 2 gives 1998 and 9 floors (2 buildings). Hipflat's exact-address page gives Jan 1995 and 8 floors, and the catalogue count of 297 units matches both. UI follows the Hipflat primary project record; record both differences for later onsite/source verification.",
            "secondarySourceUrl": "https://propertyhub.in.th/projects/permsuk-residence-2",
            "commonFee": {"status": "not_verified", "sourceUrl": "https://propertyhub.in.th/projects/permsuk-residence-2"},
        },
        "marketSamples": {
            "sale": {
                "sourceUrl": ENN_PROJECT_URL, "directLinkedSamples": len(SALE_SAMPLES),
                "lowestOverall": {"priceThb": sale["minimum"], "areaSqm": sale["minimumArea"], "priceThbPerSqm": sale["minimumSqm"], "url": sale["minimumSourceUrl"]},
                "lowestTwoBedroom": {"priceThb": two_bed_sale["minimum"], "areaSqm": two_bed_sale["area"], "url": two_bed_sale["sourceUrl"]},
                "samples": SALE_SAMPLES,
            },
            "rent": {
                "sourceUrl": ZMY_RENT_URL, "directLinkedSamples": len(RENT_SAMPLES),
                "lowestTwoBedroom": {"monthlyRentThb": rent["minimum"], "areaSqm": rent["minimumArea"], "rentThbPerSqmMonth": rent["minimumSqm"], "url": rent["minimumSourceUrl"]},
                "samples": RENT_SAMPLES,
            },
        },
        "yieldEstimate": {
            "bedrooms": 2, "purchasePriceThb": two_bed_sale["minimum"],
            "saleAreaSqm": two_bed_sale["area"], "monthlyRentThbPerSqm": two_bed_rent["minimumSqm"],
            "estimatedMonthlyRentAtSaleAreaThb": estimated_monthly_rent,
            "agentMonthsDeducted": 1, "commonFeeDeducted": False,
            "netAnnualYieldPercentBeforeUnverifiedFee": round(net_yield, 2),
            "formula": "(monthly rent × 11 − verified annual common fee) / lowest linked two-bedroom sale total × 100",
            "caveat": "Both two-bedroom source pages identify the exact project and unit details, but show no current availability confirmation or update date. The common fee is not verified; yield excludes it and is an indicative estimate.",
        },
        "walkingRoute": route,
        "sourceChecks": {
            "propertyHubExactProjectPage": "0 sales and 0 rentals listed; used as project-detail cross-check only.",
            "saleAvailability": "ENNXO project index and linked object; ZmyHome pages do not provide a confirmed current availability date.",
            "rentAvailability": "ZmyHome direct 2-bedroom listing; page states ownership is unverified and provides no update date.",
        },
    }
    report_path = ROOT / "reports" / "permsuk-residence-enrichment-2026-10-18.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with availability_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    rows = [row for row in rows if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    sale_note = "Three linked exact-project sale pages checked; lowest overall ENNXO listing has no verified availability date, and the lowest linked two-bedroom ZmyHome page has no update date."
    rent_note = "One exact-project two-bedroom rent page checked; source page says owner has not been verified and provides no update date."
    rows.extend([
        {"hipflat_id": str(PROJECT_ID), "condo": NAME, "checked_at": CHECKED, "market": "sale", "status": "direct_project_listing_availability_unconfirmed", "verification_note": sale_note, "source_1": ENN_PROJECT_URL, "source_2": ENN_LISTING_URL, "source_3": ZMY_SALE_URL},
        {"hipflat_id": str(PROJECT_ID), "condo": NAME, "checked_at": CHECKED, "market": "rent", "status": "direct_project_listing_availability_unconfirmed", "verification_note": rent_note, "source_1": ZMY_RENT_URL, "source_2": "https://propertyhub.in.th/en/condo-for-rent/project-permsuk-residence-2", "source_3": "https://www.hipflat.co.th/en/projects/permsuk-residence-vhhnxs"},
    ])
    with availability_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    coverage_path = ROOT / "reports" / "bangkok-coverage-2026-10-18.csv"
    with coverage_path.open(encoding="utf-8-sig", newline="") as stream:
        coverage = list(csv.DictReader(stream))
        coverage_fields = list(coverage[0])
    row = next(item for item in coverage if item["hipflat_id"] == str(PROJECT_ID))
    row.update({
        "coordinates": "yes", "coordinate_source": ZMY_PROJECT_URL,
        "sale_sample": "yes", "sale_market_value": "yes", "sale_individual_listing_link": "yes",
        "sale_source": ENN_LISTING_URL,
        "sale_sample_updated": "",
        "rent_sample": "yes", "rent_individual_listing_link": "yes",
        "rent_source": ZMY_RENT_URL, "rent_sample_updated": "",
        "missing": "",
    })
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=coverage_fields)
        writer.writeheader()
        writer.writerows(coverage)

    return {"report": str(report_path), "netYield": round(net_yield, 2), "monthlyRent": estimated_monthly_rent}


def main() -> None:
    manual = update_manual_samples()
    update_coordinate()
    route = update_walk_route()
    update_cache_busters()
    result = update_reports(manual["sale"], manual["rent"], route)
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [LAT, LNG], "saleSamples": len(SALE_SAMPLES), "rentSamples": len(RENT_SAMPLES), "lowestTwoBedroomSale": [manual["sale"]["byBedroom"]["2"]["minimum"], manual["sale"]["byBedroom"]["2"]["area"]], "twoBedroomRentPerSqm": manual["rent"]["byBedroom"]["2"]["minimumSqm"], "netYieldPercentBeforeUnverifiedFee": result["netYield"], "walkingRoute": route, "report": result["report"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
