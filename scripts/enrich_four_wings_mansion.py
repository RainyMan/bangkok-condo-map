"""Verify Four Wings Mansion's map point and add one directly linked rent listing."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKED = "2026-10-18"
PROJECT_ID = 3160
NAME = "Four Wings Mansion"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/four-wings-mansion-klbplq"
DD_PROJECT_URL = "https://www.ddproperty.com/en/project/6576-four-wings-mansion"
DD_RENT_URL = "https://www.ddproperty.com/en/property/four-wings-mansion-for-rent-11230056"
HIPFLAT_RENT_URL = "https://www.hipflat.co.th/en/ads/31aht4h881hh80un7hhhne973u09ec8c"
GOOGLE_MAPS_URL = "https://www.google.com/maps/place/?q=place_id:ChIJm_C_iOie4jAR-TOWeEOSgRs"
COORDINATE_LISTING_URL = "https://www.superagent.co/en/listing/3-bed-condo-four-wings-mansion-901386"
SALE_CANDIDATE_URL = "https://www.ddproperty.com/property/four-wings-mansion-%E0%B9%82%E0%B8%9F%E0%B8%A3%E0%B9%8C%E0%B8%A7%E0%B8%B4%E0%B8%87%E0%B8%AA%E0%B9%8C-%E0%B9%81%E0%B8%A1%E0%B8%99%E0%B8%8A%E0%B8%B1%E0%B9%88%E0%B8%99-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B8%82%E0%B8%B2%E0%B8%A2-500645052"
RENT_PRICE = 65_000
RENT_AREA = 220


def load_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Could not parse {symbol} from {path.name}")
    return json.loads(match.group(1))


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


def main() -> None:
    # The Superagent listing embeds Google's place ID and the same building
    # coordinates in its map metadata. Its exact address is 32/1-4 Sukhumvit 3.
    verified = load_array(DIST / "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
    coordinate = next((row for row in verified if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if coordinate is None:
        coordinate = {"hipflatId": PROJECT_ID, "name": NAME}
        verified.append(coordinate)
    coordinate.update({
        "lat": 13.7465183,
        "lng": 100.5552571,
        "locationVerified": True,
        "sourceName": "Google Maps 專案地圖點位（Superagent 個別房源）",
        "sourceUrl": GOOGLE_MAPS_URL,
        "verificationSourceUrl": COORDINATE_LISTING_URL,
        "verificationMethod": "google_place_id_and_exact_building_address_32_1_4_sukhumvit_3",
    })
    verified.sort(key=lambda row: int(row["hipflatId"]))
    save_array(DIST / "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", verified)

    map_path = DIST / "bangkok-propertyhub-map.js"
    map_rows = load_array(map_path, "BANGKOK_PROPERTYHUB_PROJECTS")
    map_project = next((row for row in map_rows if int(row.get("id", 0)) == PROJECT_ID), None)
    if map_project is None:
        raise ValueError(f"Missing Hipflat project {PROJECT_ID} in PropertyHub map data")
    map_project["address"] = "32/1-4 Soi Sukhumvit 3, Khlong Toei Nuea, Watthana, Bangkok 10110"
    map_project["locationVerified"] = True
    map_project["locationSourceUrl"] = GOOGLE_MAPS_URL
    map_project["locationSourceName"] = "Google Maps place pin"
    map_project["locationVerificationSourceUrl"] = COORDINATE_LISTING_URL
    # This Hipflat project-level sale starting price has no linked live item.
    map_project.setdefault("hipflatSummary", {}).pop("saleFrom", None)
    save_array(map_path, "BANGKOK_PROPERTYHUB_PROJECTS", map_rows)

    manual_path = DIST / "bangkok-manual-market-samples.js"
    projects = load_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in projects if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        projects.append(project)
    sample = {
        "id": "11230056",
        "price": RENT_PRICE,
        "area": RENT_AREA,
        "priceSqm": round(RENT_PRICE / RENT_AREA),
        "beds": 3,
        "roomType": "3BR",
        "title": "Four Wings Mansion，3 房，220 ㎡，฿65,000/月",
        "url": DD_RENT_URL,
        "sourceName": "DDproperty",
        "projectName": NAME,
        "updated": "2026-08-30",
        "checkedAt": CHECKED,
        "matchedBy": "exact_project_name_and_listing_description_identifies_four_wings_mansion_sukhumvit_soi_3",
        "listingStatus": "active_as_listed_availability_not_confirmed_with_advertiser",
    }
    rent = project.setdefault("rent", {})
    samples = [row for row in rent.get("samples", []) if row.get("url") != DD_RENT_URL]
    samples.append(sample)
    rent.update({
        "count": len(samples),
        "observedCount": len(samples),
        "countKind": "manual_verified_listing",
        "average": RENT_PRICE,
        "minimum": RENT_PRICE,
        "minimumArea": RENT_AREA,
        "minimumSampleUpdated": "2026-08-30",
        "averageSqm": round(RENT_PRICE / RENT_AREA),
        "minimumSqm": round(RENT_PRICE / RENT_AREA),
        "minimumSqmSampleUpdated": "2026-08-30",
        "asOf": CHECKED,
        "sourceName": "DDproperty 個別租賃掛牌（Hipflat 專案頁交叉核對）",
        "source": DD_RENT_URL,
        "minimumSourceUrl": DD_RENT_URL,
        "minimumSqmSourceUrl": DD_RENT_URL,
        "samples": samples,
        "byBedroom": {
            "3": {
                "count": 1,
                "minimum": RENT_PRICE,
                "area": RENT_AREA,
                "minimumSqm": RENT_PRICE / RENT_AREA,
                "averageSqm": RENT_PRICE / RENT_AREA,
                "sourceUrl": DD_RENT_URL,
                "minimumSqmSourceUrl": DD_RENT_URL,
            }
        },
    })
    # The scraped Hipflat sale/rent starting prices are not tied to verified
    # individual listing pages. Do not expose those summary values as samples.
    project.pop("sale", None)
    project["asOf"] = CHECKED
    projects.sort(key=lambda row: int(row["hipflatId"]))
    save_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", projects)

    availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with availability_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        availability = list(reader)
        columns = list(reader.fieldnames or [])
    availability = [row for row in availability if not (
        row.get("hipflat_id") == str(PROJECT_ID) and row.get("market") in {"sale", "rent"}
    )]
    availability.extend([
        {
            "hipflat_id": str(PROJECT_ID),
            "condo": NAME,
            "checked_at": CHECKED,
            "market": "sale",
            "status": "no_current_linked_sale_listing",
            "verification_note": "DDproperty project page currently reports 0 units to buy. Search surfaced a ฿9,000,000 candidate (ID 500645052), but its item URL currently redirects to the project result page; excluded as a current individual listing. Hipflat's project summary is not an individual item and was not counted.",
            "source_1": DD_PROJECT_URL,
            "source_2": SALE_CANDIDATE_URL,
            "source_3": PROJECT_URL,
        },
        {
            "hipflat_id": str(PROJECT_ID),
            "condo": NAME,
            "checked_at": CHECKED,
            "market": "rent",
            "status": "direct_listing_cross_checked_active_as_listed",
            "verification_note": "DDproperty listing 11230056: 3 bedrooms, 220 sqm, ฿65,000/month; its description identifies Four Wings Mansion on Sukhumvit Soi 3. Hipflat exact project page has current rent listings for 220-240 sqm units; vacancy was not confirmed with the advertiser. A 23 sqm/฿9,900 Hipflat related-listing result was excluded because its title says BTS Bang Na. DDproperty's street-number field conflicts with the exact building address, so the map point is sourced independently from the Google Maps place ID.",
            "source_1": DD_RENT_URL,
            "source_2": HIPFLAT_RENT_URL,
            "source_3": COORDINATE_LISTING_URL,
        },
    ])
    with availability_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(availability)

    report = {
        "hipflatId": PROJECT_ID,
        "projectName": NAME,
        "checkedAt": CHECKED,
        "coordinates": {
            "lat": 13.7465183,
            "lng": 100.5552571,
            "googlePlaceId": "ChIJm_C_iOie4jAR-TOWeEOSgRs",
            "googleMapsUrl": GOOGLE_MAPS_URL,
            "verificationListing": COORDINATE_LISTING_URL,
            "address": "32/1-4 Soi Sukhumvit 3, Khlong Toei Nuea, Watthana, Bangkok 10110",
            "note": "DDproperty project/listing address fields say Soi 11, while listing description, Google place pin, and independent building address source identify Sukhumvit Soi 3. Map coordinates use the Google place pin for the exact building.",
        },
        "completionYear": 1993,
        "rentListing": {
            "status": "listed; vacancy not confirmed",
            "source": DD_RENT_URL,
            "crossCheck": HIPFLAT_RENT_URL,
            "bedrooms": 3,
            "monthlyRentThb": RENT_PRICE,
            "areaSqm": RENT_AREA,
            "rentThbPerSqmMonth": round(RENT_PRICE / RENT_AREA, 2),
            "listedOrRefreshed": "2026-08-30",
        },
        "excludedRentCandidate": {
            "url": "https://www.hipflat.co.th/en/ads/22c20eu98u9luu0nu3l7c8c93ul3n8ln",
            "reason": "Although displayed in the related-project listings, the unit title identifies BTS Bang Na, so it is not counted for Four Wings Mansion.",
        },
        "saleListing": {
            "status": "no linked current individual listing verified",
            "projectPage": DD_PROJECT_URL,
            "candidateUrlExcluded": SALE_CANDIDATE_URL,
            "reason": "Candidate item URL redirects to the project result page, which currently reports 0 units to buy.",
        },
        "managementFee": {"status": "not published", "deducted": False},
        "yieldEstimate": "not calculated because no current linked sale listing is available",
    }
    report_path = ROOT / "reports" / "four-wings-mansion-enrichment-2026-10-18.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Version the scripts loaded by the page and coordinate cache.
    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(
        r"bangkok-verified-coordinates\.js\?v=[^\"']+",
        "bangkok-verified-coordinates.js?v=20261018t-four-wings-mansion-google-pin",
        html,
        count=1,
    )
    html = re.sub(
        r"bangkok-manual-market-samples\.js\?v=[^\"']+",
        "bangkok-manual-market-samples.js?v=20261018u-four-wings-mansion-rent",
        html,
        count=1,
    )
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({
        "hipflatId": PROJECT_ID,
        "coordinates": [13.7465183, 100.5552571],
        "rentThb": RENT_PRICE,
        "rentAreaSqm": RENT_AREA,
        "rentThbPerSqm": round(RENT_PRICE / RENT_AREA),
        "sale": "no current individual listing verified",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
