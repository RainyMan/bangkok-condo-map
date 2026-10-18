import csv
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3004
AS_OF = date(2026, 10, 18).isoformat()
HIPFLAT_URL = "https://www.hipflat.co.th/projects/lk-tower-yvbgnf"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/projects/lk-tower---20199"
PROPERTYHUB_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-lk-tower---20199"
PROPERTYHUB_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-lk-tower---20199"
SCANCONDO_SALE_URL = "https://eng.scancondo.com/buy-sell/condo/Condo-LK-Tower"
SCANCONDO_RENT_URL = "https://eng.scancondo.com/rent-condo/Condo-LK-Tower"
HOME_PROJECT_URL = "https://www.home.co.th/condo/lk-tower-10919"


def read_crosschecks():
    path = ROOT / "dist" / "bangkok-market-crosschecks.js"
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.BANGKOK_MARKET_CROSSCHECKS = (\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError("Unexpected market cross-check asset format")
    rows = json.loads(match.group(1))
    rows = [row for row in rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
    rows.append({
        "hipflatId": PROJECT_ID,
        "projectName": "LK Tower",
        "asOf": AS_OF,
        "sourceName": "PropertyHub",
        "projectSourceUrl": PROPERTYHUB_SALE_URL,
        "sale": {"activeListingCount": 0, "sourceUrl": PROPERTYHUB_SALE_URL},
        "rent": {"activeListingCount": 0, "sourceUrl": PROPERTYHUB_RENT_URL},
        "availabilitySources": [
            {"sourceName": "Hipflat", "url": HIPFLAT_URL, "statusLabel": "目前無可用房源"},
            {"sourceName": "Scancondo 出售", "url": SCANCONDO_SALE_URL, "statusLabel": "目前 0 筆"},
            {"sourceName": "Scancondo 出租", "url": SCANCONDO_RENT_URL, "statusLabel": "目前 0 筆"},
        ],
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    path.write_text("window.BANGKOK_MARKET_CROSSCHECKS = " + json.dumps(rows, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def append_availability_checks():
    path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {
            "hipflat_id": str(PROJECT_ID), "condo": "LK Tower", "checked_at": AS_OF, "market": "sale",
            "status": "no_current_matching_listing",
            "verification_note": "PropertyHub exact-project feed and Scancondo exact-project page both show zero current sale listings. Hipflat reports no currently available properties. ZmyHome results are within a 1 km radius and name other projects, so they are excluded.",
            "source_1": PROPERTYHUB_SALE_URL, "source_2": SCANCONDO_SALE_URL, "source_3": HIPFLAT_URL,
        },
        {
            "hipflat_id": str(PROJECT_ID), "condo": "LK Tower", "checked_at": AS_OF, "market": "rent",
            "status": "no_current_matching_listing",
            "verification_note": "PropertyHub exact-project feed and Scancondo exact-project page both show zero current rental listings. Hipflat reports no currently available properties. No rent value is estimated without a linked listing.",
            "source_1": PROPERTYHUB_RENT_URL, "source_2": SCANCONDO_RENT_URL, "source_3": HIPFLAT_URL,
        },
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_report():
    routes_text = (ROOT / "dist" / "bangkok-walk-routes.js").read_text(encoding="utf-8")
    routes_match = re.fullmatch(r"window\.BANGKOK_WALK_ROUTES = (\[.*\]);\s*", routes_text, re.S)
    if not routes_match:
        raise ValueError("Unexpected walking route asset format")
    walking_route = next((row for row in json.loads(routes_match.group(1)) if int(row.get("id", -1)) == PROJECT_ID), None)
    report = {
        "hipflatId": PROJECT_ID,
        "project": "LK Tower",
        "asOf": AS_OF,
        "location": {
            "latitude": 13.82200134,
            "longitude": 100.6426991,
            "verified": True,
            "coordinateSource": HOME_PROJECT_URL,
            "projectIdentityCrosscheck": HIPFLAT_URL,
            "method": "Home.co.th project-page coordinates matched exact project name, Nuanchan Road address, developer Link Property, and 340-unit project facts; coordinate is within about 4 m of the ZmyHome area-search center (which is not used as a listing sample).",
        },
        "projectFacts": {
            "completedYear": 2021,
            "floors": 8,
            "units": 340,
            "source": HIPFLAT_URL,
            "crosscheckSource": HOME_PROJECT_URL,
        },
        "nearestStationWalkingRoute": walking_route,
        "marketAvailability": {
            "sale": {"status": "no_current_matching_listing", "sampleCount": 0, "sources": [PROPERTYHUB_SALE_URL, SCANCONDO_SALE_URL, HIPFLAT_URL]},
            "rent": {"status": "no_current_matching_listing", "sampleCount": 0, "sources": [PROPERTYHUB_RENT_URL, SCANCONDO_RENT_URL, HIPFLAT_URL]},
            "roi": {"status": "not_calculable", "reason": "No exact-project sale or rental listing is available to form a linked purchase/rent pair."},
            "excludedComparables": "ZmyHome returns nearby 1 km area listings under other project names; none are attributed to LK Tower.",
        },
    }
    path = ROOT / "reports" / "lk-tower-availability-2026-10-18.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_cache_key():
    path = ROOT / "dist" / "index.html"
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r"bangkok-market-crosschecks\.js\?v=[^\"]+",
        "bangkok-market-crosschecks.js?v=20261018b-lk-tower-no-listings",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not update market cross-check cache key")
    text, count = re.subn(
        r"bangkok-walk-routes\.js\?v=[^\"]+",
        "bangkok-walk-routes.js?v=20261018t-lk-tower-route",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not update walking route cache key")
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    read_crosschecks()
    append_availability_checks()
    write_report()
    update_cache_key()
    print("LK Tower availability and source links recorded")
