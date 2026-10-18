"""Add verified location and direct market listings for Pinklao Pavilion."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3794
NAME = "Pinklao Pavilion"
CHECKED = "2026-10-18"
LAT, LNG = 13.7842597961, 100.4760437012
SALE_PRICE, SALE_AREA = 1_890_000, 55.13
RENT_PRICE, RENT_AREA = 7_000, 54.0
SALE_URL = "https://propertyhub.in.th/en/listings/condo-for-sale-pinkrao-pavilion-property-code-lnp-c14638---6369727"
RENT_URL = "https://zmyhome.com/property/V122685"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/pinklao-pavilion-aawhlz"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/pinkrao-pavilion"
ZMYHOME_RENT_PROJECT_URL = "https://zmyhome.com/rent/condo/project-list/13599/owner"
GOOGLE_MAPS_URL = f"https://www.google.com/maps/search/?api=1&query={LAT}%2C{LNG}"


def read_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = DIST / filename
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.S,
    )
    if not match:
        raise ValueError(f"Cannot parse {symbol} from {path}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


sale = {
    "id": "6369727",
    "price": SALE_PRICE,
    "area": SALE_AREA,
    "priceSqm": round(SALE_PRICE / SALE_AREA),
    "beds": 1,
    "roomType": "ONE_BED_ROOM",
    "title": "Pinkrao Pavilion · 1BR · 55.13 sqm · ฿1,890,000",
    "url": SALE_URL,
    "sourceName": "PropertyHub",
    "projectName": NAME,
    "updated": "2026-10-16",
    "checkedAt": CHECKED,
    "matchedBy": "PropertyHub exact project page links listing 6369727; direct page confirms Pinkrao Pavilion, 1 bedroom, 55.13 sqm and ฿1,890,000. Project identity cross-checked against Hipflat name/address and 234 units / 8 floors / 2008 completion.",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "V122685",
    "price": RENT_PRICE,
    "area": RENT_AREA,
    "priceSqm": round(RENT_PRICE / RENT_AREA),
    "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Pinklao Pavilion · 2BR · 54 sqm · ฿7,000/month",
    "url": RENT_URL,
    "sourceName": "ZmyHome",
    "projectName": NAME,
    "updated": "2026-09-20",
    "checkedAt": CHECKED,
    "matchedBy": "Direct ZmyHome listing V122685 states Pinklao Pavilion, Soi Borommaratchachonnani 6, Building B, 2 bedrooms, 54 sqm and ฿7,000/month. The project comparison table showed the listing refreshed 28 days before the 2026-10-18 check; stored date is approximate.",
    "availability": "Listed on the source as a live rental and refreshed 28 days before the check; vacancy has not been independently confirmed.",
    "listingStatus": "availability_unconfirmed_update_under_30d",
}

manual_path, rows = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
project = next(
    (row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None
)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": NAME}
    rows.append(project)
project["name"] = NAME
project["asOf"] = CHECKED
sale_rows = project.setdefault("sale", {})
sale_samples = {sample.get("url"): sample for sample in sale_rows.get("samples", []) if sample.get("url")}
sale_samples[SALE_URL] = sale
sale_rows["samples"] = list(sale_samples.values())

# Retain the older direct Connex record for audit history, while market minimums
# and the two-bedroom rate point to the recently refreshed ZmyHome listing.
rent_rows = project.setdefault("rent", {})
old_samples = {sample.get("url"): sample for sample in rent_rows.get("samples", []) if sample.get("url")}
old_samples[RENT_URL] = rent
rent_rows.update({
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": RENT_PRICE,
    "minimum": RENT_PRICE,
    "minimumArea": RENT_AREA,
    "averageSqm": round(RENT_PRICE / RENT_AREA),
    "minimumSqm": RENT_PRICE / RENT_AREA,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "minimumSampleUpdated": "2026-09-20",
    "minimumSqmSampleUpdated": "2026-09-20",
    "asOf": CHECKED,
    "sourceName": "ZmyHome 個別出租掛牌（更新未滿 30 日，現況待確認）",
    "source": RENT_URL,
    "snapshotMethod": "Direct ZmyHome listing V122685; the project comparison table reported this listing refreshed 28 days before the 2026-10-18 check. Its 2-bedroom details are preserved as a direct unit sample.",
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": RENT_PRICE,
            "area": RENT_AREA,
            "minimumSqm": RENT_PRICE / RENT_AREA,
            "minimumSqmSourceUrl": RENT_URL,
            "sourceUrl": RENT_URL,
        }
    },
    "samples": list(old_samples.values()),
})
rows.sort(key=lambda row: int(row["hipflatId"]))
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

coordinate_path, coordinates = read_array(
    "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"
)
coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
coordinates.append({
    "hipflatId": PROJECT_ID,
    "name": NAME,
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "ZmyHome 物件頁 Google Maps 點位",
    "sourceUrl": GOOGLE_MAPS_URL,
    "verificationSourceUrl": HIPFLAT_URL,
    "corroborationSourceUrl": RENT_URL,
    "verificationMethod": "Google Maps coordinates linked from the exact ZmyHome listing for Pinklao Pavilion; exact project name and Soi Borommaratchachonnani 6 address match Hipflat. ZmyHome and PropertyHub identify the project as 234 units, 8 floors, completed 2008.",
    "asOf": CHECKED,
})
coordinates.sort(key=lambda row: int(row["hipflatId"]))
write_array(coordinate_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

# This exact-name PropertyHub map pin has higher source precedence than the
# coordinate cache in app.js, so keep the verified Google Maps point aligned.
guessed_path, guessed_rows = read_array(
    "bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS"
)
guessed = next(
    (row for row in guessed_rows if int(row.get("hipflatProjectId", -1)) == PROJECT_ID),
    None,
)
if guessed is None:
    raise ValueError("Expected exact-project PropertyHub identity match is missing")
guessed.update({
    "lat": LAT,
    "lng": LNG,
    "locationSourceName": "ZmyHome 物件頁 Google Maps 點位（Hipflat 地址交叉核實）",
    "locationSourceUrl": GOOGLE_MAPS_URL,
    "coordinateSourceVerified": True,
    "coordinateVerificationSourceUrl": RENT_URL,
    "coordinateVerificationMethod": "Google Maps coordinates linked from direct ZmyHome Pinklao Pavilion listing V122685; exact project name and Soi Borommaratchachonnani 6 address match Hipflat.",
    "asOf": CHECKED,
})
write_array(guessed_path, "BANGKOK_PROPERTYHUB_GUESSED_DETAILS", guessed_rows)

route = {
    "id": PROJECT_ID,
    "name": NAME,
    "originLat": LAT,
    "originLng": LNG,
    "distanceKm": 2.694,
    "minutes": 33,
    "stationId": "BL05",
    "source": "Valhalla pedestrian routing (30 nearest stations checked)",
    "sourceUrl": "https://valhalla1.openstreetmap.de/",
    "networkSourceUrl": "https://www.openstreetmap.org/copyright",
    "asOf": CHECKED,
}
route_path, route_rows = read_array("bangkok-walk-routes.js", "BANGKOK_WALK_ROUTES")
route_rows = [row for row in route_rows if int(row.get("id", -1)) != PROJECT_ID]
route_rows.append(route)
route_rows.sort(key=lambda row: int(row["id"]))
write_array(route_path, "BANGKOK_WALK_ROUTES", route_rows)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": NAME,
    "checkedAt": CHECKED,
    "identity": {
        "hipflatProject": HIPFLAT_URL,
        "propertyHubProject": PROPERTYHUB_PROJECT_URL,
        "crossCheck": "Both project pages identify the Bang Phlat condo; Hipflat gives 119 Soi Borommaratchachonnani 6, 234 units, 8 floors, completed 2008. The PropertyHub project spelling is Pinkrao Pavilion.",
    },
    "coordinates": {"lat": LAT, "lng": LNG, "source": GOOGLE_MAPS_URL},
    "walkingRoute": {
        "station": "MRT Blue Line Bang Yi Khan (BL05)",
        "distanceKm": 2.694,
        "minutes": 33,
        "method": route["source"],
    },
    "saleSample": sale,
    "rentSample": rent,
    "availabilityCrossCheck": {
        "propertyHubRentProject": PROPERTYHUB_PROJECT_URL,
        "finding": "PropertyHub showed 0 rental listings when checked. ZmyHome supplied an exact-project individual listing refreshed 28 days before the check; current vacancy remains unconfirmed.",
        "zmyHomeProjectRentPage": ZMYHOME_RENT_PROJECT_URL,
    },
    "managementFee": {
        "publishedValue": 648,
        "unit": "THB/month",
        "source": RENT_URL,
        "note": "ZmyHome direct page lists 648 THB/month but does not make clear whether this is a per-unit amount or a project-wide rate. It is not converted to THB/sqm and is not deducted in ROI.",
    },
    "roi": {
        "status": "not calculated",
        "reason": "No same-bedroom sale listing was found: the lowest current PropertyHub sale sample is one bedroom, while the recent ZmyHome rental is two bedrooms. Do not mix room types for the default yield.",
    },
}
(REPORTS / "pinklao-pavilion-rent-enrichment-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

coverage_path = REPORTS / "bangkok-coverage-2026-10-18.csv"
with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
    coverage = list(csv.DictReader(handle))
    headers = list(coverage[0])
target = next(item for item in coverage if item["hipflat_id"] == str(PROJECT_ID))
target.update({
    "coordinates": "yes",
    "coordinate_source": GOOGLE_MAPS_URL,
    "sale_sample": "yes",
    "sale_individual_listing_link": "yes",
    "sale_source": SALE_URL,
    "sale_sample_updated": sale["updated"],
    "rent_sample": "yes",
    "rent_individual_listing_link": "yes",
    "rent_source": RENT_URL,
    "rent_sample_updated": "2026-09-20 (approx.; source said 28 days before check)",
    "missing": "同房型出售樣本（投報暫不可估）",
})
with coverage_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=headers)
    writer.writeheader()
    writer.writerows(coverage)

print(json.dumps({
    "hipflatId": PROJECT_ID,
    "coordinates": [LAT, LNG],
    "walkToMrtKm": route["distanceKm"],
    "sale": [SALE_PRICE, SALE_AREA, round(SALE_PRICE / SALE_AREA)],
    "rent": [RENT_PRICE, RENT_AREA, round(RENT_PRICE / RENT_AREA, 2)],
    "roi": report["roi"]["status"],
}, ensure_ascii=False))
