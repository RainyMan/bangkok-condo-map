from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_propertyhub_city_listings as audit
import enrich_propertyhub_exact_project_pages as exact
import geocode_propertyhub_guess as propertyhub

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "presidence-place-propertyhub-identity-and-markets-2026-10-19.json"
HIPFLAT_ID = 5099
PROPERTYHUB_ID = "1909"
PROJECT_URL = "https://propertyhub.in.th/en/projects/president-place"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/pesidence-place-xrlrld"
LEASEHOLD_LISTING_ID = "6214384"
LEASEHOLD_URL = "https://propertyhub.in.th/en/listings/president-place-you-won-t-find-a-better-deal-ratchadamri-the-best-location-in-bangkok-leasehold---6214384"


def arr(filename: str, symbol: str) -> list[dict]:
    return audit.arr(filename, symbol)


def save(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    temporary.replace(target)


def build_market(kind: str, result: dict) -> dict:
    cards = result["cards"]
    low_total = min(cards, key=lambda row: row["price"])
    low_rate = min(cards, key=lambda row: row["price"] / row["area"])
    by_bedroom = {}
    bed_counts = sorted({int(row["beds"]) for row in cards if isinstance(row.get("beds"), (int, float)) and row["beds"] > 0})
    for beds in bed_counts:
        group = [row for row in cards if row.get("beds") == beds]
        minimum = min(group, key=lambda row: row["price"])
        minimum_sqm = min(group, key=lambda row: row["price"] / row["area"])
        by_bedroom[str(beds)] = {
            "count": len(group),
            "minimum": minimum["price"],
            "area": minimum["area"],
            "minimumArea": minimum["area"],
            "priceSqm": minimum["priceSqm"],
            "minimumSqm": round(minimum_sqm["price"] / minimum_sqm["area"]),
            "sourceUrl": minimum["url"],
            "minimumSourceUrl": minimum["url"],
            "minimumSqmSourceUrl": minimum_sqm["url"],
        }
    return {
        "count": len(cards),
        "platformCount": result["totalCount"],
        "observedCount": len(cards),
        "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in cards) / len(cards)),
        "minimum": low_total["price"],
        "minimumArea": low_total["area"],
        "averageSqm": round(sum(row["priceSqm"] for row in cards) / len(cards)),
        "minimumSqm": round(low_rate["price"] / low_rate["area"]),
        "minimumSampleUpdated": low_total.get("updated"),
        "minimumSqmSampleUpdated": low_rate.get("updated"),
        "asOf": date.today().isoformat(),
        "snapshotMethod": "PropertyHub exact project page; all available pages with project ID 1909 validated; leasehold sale excluded from standard market and ROI",
        "sourceName": "PropertyHub 專案單筆掛牌",
        "source": result["sourceUrl"],
        "minimumSourceUrl": low_total["url"],
        "minimumSqmSourceUrl": low_rate["url"],
        "byBedroom": by_bedroom,
        "samples": cards,
    }


def main() -> None:
    catalogue = {int(row["id"]): row for row in arr("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")}
    target = catalogue[HIPFLAT_ID]
    if target.get("name") != "Pesidence Place" or audit.district(target.get("address", "")) != "pathum wan":
        raise RuntimeError("Hipflat target name/district changed; re-review identity before proceeding")
    if str(target.get("hipflatProjectUrl") or HIPFLAT_URL) != HIPFLAT_URL:
        raise RuntimeError("Hipflat project URL changed; re-review identity before proceeding")

    response = propertyhub.requests.get(PROJECT_URL, headers=propertyhub.HEADERS, timeout=(10, 35))
    response.raise_for_status()
    project = propertyhub.find_project(response.text)
    if not project or str(project.get("id")) != PROPERTYHUB_ID:
        raise RuntimeError("PropertyHub project page ID did not match 1909")
    project_name = str(project.get("nameEnglish") or project.get("name") or "").strip()
    info = project.get("projectInfo") or {}
    point = project.get("location") or {}
    lat, lng = float(point.get("lat")), float(point.get("lng"))
    if project_name != "President Place" or audit.district(project.get("address", "")) != "pathum wan":
        raise RuntimeError("PropertyHub project name/district mismatch")
    if str(info.get("totalUnits")) != "168" or str(info.get("completedYear")) != "2000":
        raise RuntimeError("PropertyHub unit count/completion no longer corroborates the Hipflat record")
    if not (13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0):
        raise RuntimeError("PropertyHub coordinate outside Bangkok bounds")

    # Require the city listing snapshot to independently link the exact page ID,
    # project name, and target district before wiring those listing cards in.
    snapshot_matches = []
    with Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok\propertyhub-bangkok-pages.jsonl").open(encoding="utf-8") as source:
        for line in source:
            for row in json.loads(line).get("listings", []):
                if str(row.get("projectId")) == PROPERTYHUB_ID:
                    snapshot_matches.append(row)
    if not snapshot_matches or any(audit.norm(row.get("projectName", "")) != audit.norm(project_name) for row in snapshot_matches):
        raise RuntimeError("City listing cards do not consistently identify President Place")
    if any(audit.district(row.get("address", "")) != "pathum wan" for row in snapshot_matches):
        raise RuntimeError("City listing cards do not consistently identify Pathum Wan")

    exclusions_path = ROOT / "scripts" / "propertyhub_listing_exclusions.json"
    exclusions = json.loads(exclusions_path.read_text(encoding="utf-8"))
    if not any(str(row.get("listingId")) == LEASEHOLD_LISTING_ID and int(row.get("hipflatProjectId", -1)) == HIPFLAT_ID for row in exclusions):
        exclusions.append({
            "listingId": LEASEHOLD_LISTING_ID,
            "hipflatProjectId": HIPFLAT_ID,
            "propertyHubProjectId": PROPERTYHUB_ID,
            "kind": "sale",
            "sourceUrl": LEASEHOLD_URL,
            "reason": "The PropertyHub title explicitly marks this unit Leasehold. Keep its direct source in the Condo detail card, but exclude it from freehold market minima and ROI because remaining lease term and transfer terms are not provided.",
        })
        exclusions_path.write_text(json.dumps(exclusions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    exact.EXCLUDED.setdefault((HIPFLAT_ID, "sale"), set()).add(LEASEHOLD_LISTING_ID)

    sale_result = exact.parse_market(HIPFLAT_ID, "sale", "president-place", PROPERTYHUB_ID)
    rent_result = exact.parse_market(HIPFLAT_ID, "rent", "president-place", PROPERTYHUB_ID)
    if sale_result.get("error") or rent_result.get("error") or not sale_result.get("cards") or not rent_result.get("cards"):
        raise RuntimeError(f"Exact project listings could not be verified: {sale_result.get('error')} / {rent_result.get('error')}")
    sale_market = build_market("sale", sale_result)
    rent_market = build_market("rent", rent_result)
    special_leasehold = {
        "id": LEASEHOLD_LISTING_ID,
        "price": 1700000,
        "area": 48,
        "beds": 1,
        "priceSqm": round(1700000 / 48),
        "title": "President Place · Leasehold sale · 48 ㎡",
        "url": LEASEHOLD_URL,
        "updated": "2026-10-16",
        "sourceName": "PropertyHub",
        "specialAsset": True,
        "specialNotice": "此掛牌明確標示為租賃權出售，剩餘租期未提供。保留原始來源供查閱，不納入一般售價與投報試算。",
    }
    sale_market["samples"].append(special_leasehold)
    sale_market["specialSaleNotice"] = special_leasehold["specialNotice"]

    propertyhub_rows = arr("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    ph_by_id = {int(row["id"]): row for row in propertyhub_rows}
    base = ph_by_id[HIPFLAT_ID]
    for row in propertyhub_rows:
        if str(row.get("propertyHubProjectId")) == PROPERTYHUB_ID and int(row["id"]) != HIPFLAT_ID:
            raise RuntimeError("PropertyHub ID 1909 is already linked to another Hipflat project")
    base.update({
        "propertyHubProjectId": PROPERTYHUB_ID,
        "propertyHubProjectUrl": PROJECT_URL,
        "propertyHubSaleUrl": sale_result["sourceUrl"],
        "propertyHubRentUrl": rent_result["sourceUrl"],
        "lat": lat,
        "lng": lng,
        "locationVerified": True,
        "locationSourceName": "PropertyHub 精確專案頁（ID、168 戶、2000 年完工及 Pathum Wan 核對）",
        "locationSourceUrl": PROJECT_URL,
        "locationVerificationSourceUrl": HIPFLAT_URL,
        "completedYear": 2000,
        "completedYearSourceUrl": PROJECT_URL,
        "units": 168,
        # Hipflat exposes the unit count as a floor count for this record;
        # PropertyHub does not publish the actual building floor count.
        "floors": None,
        "sale": sale_market,
        "rent": rent_market,
    })
    save("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS", propertyhub_rows)

    guessed = arr("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
    detail_record = {
        "hipflatProjectId": HIPFLAT_ID,
        "propertyHubProjectId": PROPERTYHUB_ID,
        "name": target["name"],
        "projectName": project_name,
        "propertyHubListingProjectName": project_name,
        "projectSlug": project.get("slug") or "president-place",
        "projectAddress": project.get("address"),
        "lat": lat,
        "lng": lng,
        "locationVerified": True,
        "coordinateSourceVerified": True,
        "identityMatchMethod": "verified_propertyhub_id_page_with_project_alias",
        "identityEvidence": "Hipflat's Pesidence Place record reports 168 and year 2000 in Pathum Wan; PropertyHub's exact President Place page ID 1909 independently reports 168 units and year 2000 in Pathum Wan, with matching 975-series Ploenchit/Gay Sorn address evidence.",
        "locationSourceName": "PropertyHub 精確專案頁（頁面 ID、戶數、年份與行政區交叉核對）",
        "locationSourceUrl": PROJECT_URL,
        "completedYear": 2000,
        "completedYearSourceUrl": PROJECT_URL,
        "units": 168,
        "floorCountStatus": "unknown",
        "asOf": date.today().isoformat(),
    }
    guessed = [row for row in guessed if int(row.get("hipflatProjectId", -1)) != HIPFLAT_ID]
    guessed.append(detail_record)
    guessed.sort(key=lambda row: int(row["hipflatProjectId"]))
    save("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS", guessed)

    details = arr("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")
    details = [row for row in details if str(row.get("propertyHubProjectId")) != PROPERTYHUB_ID]
    details.append({
        "propertyHubProjectId": PROPERTYHUB_ID,
        "name": target["name"],
        "projectName": project_name,
        "sourceUrl": PROJECT_URL,
        "locationSourceUrl": PROJECT_URL,
        "locationSourceName": detail_record["locationSourceName"],
        "projectAddress": project.get("address"),
        "lat": lat,
        "lng": lng,
        "locationVerified": True,
        "completedYear": 2000,
        "completedYearSourceUrl": PROJECT_URL,
        "units": 168,
        "floorCountStatus": "unknown",
        "asOf": date.today().isoformat(),
    })
    details.sort(key=lambda row: str(row.get("propertyHubProjectId", "")))
    save("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS", details)

    manual = arr("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    manual_row = next((row for row in manual if int(row.get("hipflatId", -1)) == HIPFLAT_ID), {"hipflatId": HIPFLAT_ID, "name": target["name"]})
    manual_row.update({"sale": sale_market, "rent": rent_market, "replaceSale": True, "replaceRent": True})
    manual = [row for row in manual if int(row.get("hipflatId", -1)) != HIPFLAT_ID]
    manual.append(manual_row)
    manual.sort(key=lambda row: int(row["hipflatId"]))
    save("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

    report = {
        "date": date.today().isoformat(),
        "hipflat": {"id": HIPFLAT_ID, "name": target["name"], "url": HIPFLAT_URL, "district": "Pathum Wan", "completedYear": 2000, "units": 168},
        "propertyhub": {"id": PROPERTYHUB_ID, "name": project_name, "url": PROJECT_URL, "address": project.get("address"), "district": "Pathum Wan", "completedYear": 2000, "units": 168, "lat": lat, "lng": lng},
        "previousCandidateRejected": {"propertyHubProjectId": "614", "name": "Pesidence Place", "sourceReason": "Separate exact-name page reports one total unit, inconsistent with Hipflat's 168-unit record."},
        "identityChecks": ["Exact PropertyHub project page ID 1909", "Project name alias President/Pesidence corroborated with Hipflat title and matching building metadata", "Same Bangkok district", "Current city snapshot listing IDs consistently identify President Place and Pathum Wan", "Coordinates in Bangkok bounds", "Floor count left unknown: the Hipflat record repeats 168 while the PropertyHub page reports 168 units and has no floor count; listing titles show units on floors 25 and 27."],
        "marketCapture": {"saleCount": sale_market["count"], "salePlatformCount": sale_market["platformCount"], "rentCount": rent_market["count"], "rentPlatformCount": rent_market["platformCount"], "saleMinimum": sale_market["minimum"], "saleMinimumArea": sale_market["minimumArea"], "saleMinimumSourceUrl": sale_market["minimumSourceUrl"], "rentMinimum": rent_market["minimum"], "rentMinimumSourceUrl": rent_market["minimumSourceUrl"], "twoBedroomSale": sale_market.get("byBedroom", {}).get("2"), "twoBedroomRent": rent_market.get("byBedroom", {}).get("2"), "excludedLeasehold": {"id": LEASEHOLD_LISTING_ID, "url": LEASEHOLD_URL, "price": 1700000, "area": 48, "reason": "Separate visible special-sale listing; excluded from freehold baseline and ROI because remaining lease term is unknown."}},
        "cityListingSnapshotCardsForProjectId": len(snapshot_matches),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": HIPFLAT_ID, "propertyHubId": PROPERTYHUB_ID, "lat": lat, "lng": lng, "saleCount": sale_market["count"], "rentCount": rent_market["count"], "saleMinimum": sale_market["minimum"], "twoBedroomSale": bool(sale_market.get("byBedroom", {}).get("2")), "twoBedroomRent": bool(rent_market.get("byBedroom", {}).get("2")), "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
