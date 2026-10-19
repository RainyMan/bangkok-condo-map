import csv
import json
import re
import runpy
from datetime import date
from pathlib import Path


if __name__ == "__main__":
    # Superseded: the prior script mistranslated a rental start date as expiry.
    # Keep legacy invocations aligned with the corrected, source-linked record.
    runpy.run_path(str(Path(__file__).with_name("enrich_chatuchak_condominium_rent_2026_10_19.py")), run_name="__main__")
    raise SystemExit(0)


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3005
PROJECT = "Chatuchak Condominium"
AS_OF = date(2026, 10, 18).isoformat()
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/chatuchak-condominium-cpdwry"
PH_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-chatuchak-condominium"
PH_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-chatuchak-condominium"
PH_LISTING_URL = "https://propertyhub.in.th/en/listings/%EF%B8%8F-64-2-sq-m-condo-for-rent-high-floor-stunning-chatuchak-park-view-fully-furnished-move-in-ready---6242213"
LISTING_ID = "6242213"


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


def update_exclusion():
    path = ROOT / "scripts" / "propertyhub_listing_exclusions.json"
    rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    rows = [row for row in rows if not (str(row.get("listingId")) == LISTING_ID and row.get("kind") == "rent")]
    rows.append({
        "listingId": LISTING_ID,
        "hipflatProjectId": PROJECT_ID,
        "kind": "rent",
        "sourceUrl": PH_LISTING_URL,
        "reason": "Exact-project listing identifies Chatuchak Condominium and 2BR/64 sqm/฿33,000 per month, but its stated availability date is 2026-06-30, before the 2026-10-18 check. Exclude it from current rent and ROI; retain the source in the availability cross-check.",
    })
    rows.sort(key=lambda row: (int(row.get("hipflatProjectId", 0)), row.get("kind", ""), str(row.get("listingId", ""))))
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_summaries():
    path = DIST / "bangkok-propertyhub-city-summaries.js"
    rows = read_array(path, "BANGKOK_PROPERTYHUB_CITY_SUMMARIES")
    for row in rows:
        if int(row.get("id", -1)) == PROJECT_ID:
            row.pop("rent", None)
    rows = [row for row in rows if row.get("sale") or row.get("rent")]
    write_array(path, "BANGKOK_PROPERTYHUB_CITY_SUMMARIES", rows, compact=True)


def update_crosschecks():
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
            {"sourceName": "PropertyHub 過期租盤", "url": PH_LISTING_URL, "statusLabel": "頁面標示可租至 2026-06-30；不列現租樣本"},
        ],
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows)


def update_availability_csv():
    path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "sale",
            "status": "no_current_matching_listing",
            "verification_note": "PropertyHub exact-project sale page shows no matched properties; Hipflat says the project currently has no available properties. Search results for nearby Phaya Thai/Chatuchak condos name other projects and are excluded.",
            "source_1": PH_SALE_URL, "source_2": HIPFLAT_URL, "source_3": "",
        },
        {
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "rent",
            "status": "historical_listing_expired",
            "verification_note": "Exact-project PropertyHub item 6242213 shows 2BR, 64 sqm, ฿33,000/month but its stated availability date is 2026-06-30 and the current exact-project rent page shows no matched properties. Removed from current rent samples and ROI; retained as a linked historical source.",
            "source_1": PH_LISTING_URL, "source_2": PH_RENT_URL, "source_3": HIPFLAT_URL,
        },
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (int(row["hipflat_id"]), row["market"])))


def write_report():
    project_rows = read_array(DIST / "bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    project = next(row for row in project_rows if int(row["id"]) == PROJECT_ID)
    route_rows = read_array(DIST / "bangkok-walk-routes.js", "BANGKOK_WALK_ROUTES")
    route = next((row for row in route_rows if int(row["id"]) == PROJECT_ID), None)
    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "asOf": AS_OF,
        "location": {
            "latitude": project["lat"], "longitude": project["lng"], "verified": True,
            "coordinateSource": project.get("locationSourceUrl"),
            "identitySource": HIPFLAT_URL,
            "method": "PropertyHub project coordinate and exact Phaya Thai project page cross-checked against Hipflat name/address; no nearby listings used as coordinates or samples.",
        },
        "projectFacts": {"completedYear": 1983, "floors": 4, "units": 45, "source": HIPFLAT_URL},
        "nearestStationWalkingRoute": route,
        "marketAvailability": {
            "sale": {"status": "no_current_matching_listing", "sampleCount": 0, "sources": [PH_SALE_URL, HIPFLAT_URL]},
            "rent": {"status": "historical_listing_expired", "sampleCount": 0, "sources": [PH_RENT_URL, HIPFLAT_URL],
                     "historicalListing": {"url": PH_LISTING_URL, "listingId": LISTING_ID, "price": 33000, "areaSqm": 64,
                                            "bedrooms": 2, "availableUntil": "2026-06-30", "excludedFromCurrentMarket": True}},
            "roi": {"status": "not_calculable", "reason": "No current exact-project sale listing and no current exact-project rental listing."},
        },
        "excludedComparables": "Nearby Phaya Thai and Chatuchak listings with different project names, including IDEO and other Pradiphat projects, were not assigned to this condo.",
    }
    (REPORTS / "chatuchak-condominium-availability-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_asset_version():
    path = DIST / "index.html"
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r"bangkok-propertyhub-city-summaries\.js\?v=[^\"']+",
                     "bangkok-propertyhub-city-summaries.js?v=20261018d-chatuchak-stale-rent-excluded", text)
    if updated == text and "bangkok-propertyhub-city-summaries.js?v=20261018d-chatuchak-stale-rent-excluded" not in text:
        raise ValueError("Could not update city-summary cache key")
    path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    update_exclusion()
    update_summaries()
    update_crosschecks()
    update_availability_csv()
    write_report()
    update_asset_version()
    print(json.dumps({"project": PROJECT, "hipflatId": PROJECT_ID, "asOf": AS_OF,
                      "currentSaleSamples": 0, "currentRentSamples": 0, "roi": "not calculable"}, ensure_ascii=False, indent=2))
