"""Verify Horkarnkah Condo Town coordinates and document listing availability."""

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3026
PROJECT = "Horkarnkah Condo Town"
AS_OF = "2026-10-18"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/horkarnkah-condo-town-nmdevf"
PH_PROJECT_URL = "https://propertyhub.in.th/en/projects/horkarnkah-condo-town"
PH_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-horkarnkah-condo-town"
PH_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-horkarnkah-condo-town"
ZMYHOME_LISTING_URL = "https://zmyhome.com/property/V52657"
THAICOZY_URL = "https://thaicozy.com/en/residence/horkarnkah-condo-town"
GMAPS_URL = "https://www.google.com/maps/search/?api=1&query=13.7806739807%2C100.5630645752"
LAT = 13.7806739807
LNG = 100.5630645752


def read_array(path, symbol):
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError(f"Unexpected asset format: {path.name}")
    return json.loads(match.group(1))


def write_array(path, symbol, rows, compact=False):
    body = json.dumps(rows, ensure_ascii=False, separators=(",", ":") if compact else None,
                      indent=None if compact else 2)
    path.write_text(f"window.{symbol} = {body};\n", encoding="utf-8")


def update_project_coordinate():
    path = DIST / "bangkok-propertyhub-map.js"
    rows = read_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    row = next(row for row in rows if int(row["id"]) == PROJECT_ID)
    row.update({
        "lat": LAT,
        "lng": LNG,
        "address": "Soi Inthamara 40, Vibhavadi Rangsit Road, Ratchadaphisek, Din Daeng, Bangkok 10400, Thailand",
        "locationVerified": True,
        "locationSourceUrl": GMAPS_URL,
        "locationSourceName": "Google Maps 同案物件地圖點位",
        "locationVerificationSourceUrl": ZMYHOME_LISTING_URL,
        "locationVerificationMethod": "ZmyHome 個別歷史出售物件明列 Horkarnkah Condotown 與 Soi Inthamara 40，並連至 Google Maps 點位；與 Hipflat/PropertyHub 專案名稱、樓層及完工年核對。Google Maps 點位與原 PropertyHub 專案圖釘相差約 18 公尺。",
    })
    write_array(path, "BANGKOK_PROPERTYHUB_PROJECTS", rows, compact=True)

    path = DIST / "bangkok-propertyhub-guessed-details.js"
    rows = read_array(path, "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
    row = next(row for row in rows if int(row["hipflatProjectId"]) == PROJECT_ID)
    row.update({
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "locationSourceName": "Google Maps 同案物件地圖點位",
        "locationSourceUrl": GMAPS_URL,
        "locationVerificationSourceUrl": ZMYHOME_LISTING_URL,
        "locationVerificationMethod": "ZmyHome 個別歷史出售物件明列 Horkarnkah Condotown 與 Soi Inthamara 40，並連至 Google Maps 點位；與 Hipflat/PropertyHub 專案名稱、樓層及完工年核對。Google Maps 點位與原 PropertyHub 專案圖釘相差約 18 公尺。",
    })
    write_array(path, "BANGKOK_PROPERTYHUB_GUESSED_DETAILS", rows, compact=True)

    path = DIST / "bangkok-verified-coordinates.js"
    rows = read_array(path, "BANGKOK_VERIFIED_COORDINATES")
    rows = [row for row in rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
    rows.append({
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "sourceName": "Google Maps 同案物件地圖點位",
        "sourceUrl": GMAPS_URL,
        "verificationSourceUrl": ZMYHOME_LISTING_URL,
        "verificationMethod": "Exact project name and Inthamara 40 address on the directly linked ZmyHome sale page; Google Maps pin is about 17 m from the PropertyHub project pin.",
        "asOf": AS_OF,
    })
    rows.sort(key=lambda item: int(item.get("hipflatId", 0)))
    write_array(path, "BANGKOK_VERIFIED_COORDINATES", rows, compact=True)


def update_availability_crosscheck():
    path = DIST / "bangkok-market-crosschecks.js"
    rows = read_array(path, "BANGKOK_MARKET_CROSSCHECKS")
    rows = [row for row in rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
    rows.append({
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "asOf": AS_OF,
        "sourceName": "PropertyHub",
        "projectSourceUrl": PH_SALE_URL,
        "sale": {"activeListingCount": 0, "sourceUrl": PH_SALE_URL},
        "rent": {"activeListingCount": 0, "sourceUrl": PH_RENT_URL},
        "availabilitySources": [
            {"sourceName": "Hipflat", "url": HIPFLAT_URL, "statusLabel": "目前無可用房源"},
            {"sourceName": "ThaiCozy", "url": THAICOZY_URL, "statusLabel": "專案頁顯示目前 0 筆出售、0 筆出租"},
            {"sourceName": "ZmyHome 歷史出售物件", "url": ZMYHOME_LISTING_URL,
             "statusLabel": "฿750,000 · 26㎡ · 1 房；2018-02 已售，不列現行行情或投報"},
        ],
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows)


def update_availability_csv():
    path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "sale",
            "status": "no_current_matching_listing",
            "verification_note": "PropertyHub exact-project sale page and Hipflat project page show no currently available matching property. ZmyHome direct item V52657 confirms an exact-project 1BR, 26 sqm, ฿750,000 sale, but the item states it sold in February 2018; retained as historical context and excluded from current price and ROI.",
            "source_1": PH_SALE_URL, "source_2": HIPFLAT_URL, "source_3": ZMYHOME_LISTING_URL,
        },
        {
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "rent",
            "status": "no_current_matching_listing",
            "verification_note": "PropertyHub exact-project rent page and Hipflat project page show no currently available matching property. ThaiCozy's exact-project page also reports 0 rental listings. No nearby-project listings are substituted.",
            "source_1": PH_RENT_URL, "source_2": HIPFLAT_URL, "source_3": THAICOZY_URL,
        },
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (int(row["hipflat_id"]), row["market"])))


def write_report():
    route_rows = read_array(DIST / "bangkok-walk-routes.js", "BANGKOK_WALK_ROUTES")
    walking_route = next((row for row in route_rows if int(row.get("id", -1)) == PROJECT_ID), None)
    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "location": {
            "latitude": LAT,
            "longitude": LNG,
            "verified": True,
            "coordinateSource": GMAPS_URL,
            "sourceListing": ZMYHOME_LISTING_URL,
            "projectIdentityCrosschecks": [HIPFLAT_URL, PH_PROJECT_URL],
            "method": "ZmyHome item V52657 identifies Horkarnkah Condotown, Soi Inthamara 40, Din Daeng and links to this Google Maps pin. The pin is approximately 18 m from the existing PropertyHub project pin.",
        },
        "projectFacts": {"completedYear": 2000, "floors": 9, "identitySource": HIPFLAT_URL},
        "nearestStationWalkingRoute": walking_route,
        "marketAvailability": {
            "sale": {"status": "no_current_matching_listing", "sampleCount": 0,
                     "sources": [PH_SALE_URL, HIPFLAT_URL],
                     "historicalListing": {"url": ZMYHOME_LISTING_URL, "listingId": "V52657", "price": 750000,
                                           "areaSqm": 26, "bedrooms": 1, "soldAt": "2018-02", "excludedFromCurrentMarket": True}},
            "rent": {"status": "no_current_matching_listing", "sampleCount": 0,
                     "sources": [PH_RENT_URL, HIPFLAT_URL, THAICOZY_URL]},
            "roi": {"status": "not_calculable", "reason": "No current exact-project sale listing or current rental listing; the only linked sale object is marked sold in February 2018."},
        },
        "excludedComparables": "Nearby Din Daeng and Huai Khwang listings with different project names were not assigned to this condo.",
    }
    (REPORTS / "horkarnkah-condo-town-availability-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_cache_keys():
    path = DIST / "index.html"
    text = path.read_text(encoding="utf-8")
    replacements = {
        r"bangkok-propertyhub-map\.js\?v=[^\"']+": "bangkok-propertyhub-map.js?v=20261018m-horkarnkah-google-map-pin",
        r"bangkok-propertyhub-guessed-details\.js\?v=[^\"']+": "bangkok-propertyhub-guessed-details.js?v=20261018d-horkarnkah-google-pin-override",
        r"bangkok-verified-coordinates\.js\?v=[^\"']+": "bangkok-verified-coordinates.js?v=20261018u-horkarnkah-exact-address-pin",
        r"bangkok-market-crosschecks\.js\?v=[^\"']+": "bangkok-market-crosschecks.js?v=20261018c-horkarnkah-availability",
        r"bangkok-walk-routes\.js\?v=[^\"']+": "bangkok-walk-routes.js?v=20261018u-horkarnkah-verified-pin-route",
    }
    for pattern, replacement in replacements.items():
        text, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            raise ValueError(f"Could not update cache key: {replacement}")
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    update_project_coordinate()
    update_availability_crosscheck()
    update_availability_csv()
    write_report()
    update_cache_keys()
    print(json.dumps({"project": PROJECT, "hipflatId": PROJECT_ID, "coordinates": [LAT, LNG],
                      "currentSaleSamples": 0, "currentRentSamples": 0,
                      "historicalSaleExcluded": {"price": 750000, "areaSqm": 26, "soldAt": "2018-02"},
                      "roi": "not calculable"}, ensure_ascii=False, indent=2))
