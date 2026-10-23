"""Backfill direct DDproperty unit links for Bangkok projects with market samples but no linked unit page."""
from __future__ import annotations

import csv
import argparse
import json
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

from enrich_arcgis_unlocated_coordinates_2026_10_23 import district
from enrich_arcgis_exact_poi_coordinates import js_array

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
TODAY = date.today()
AUDIT = ROOT / "reports" / f"bangkok-coverage-{TODAY.isoformat()}.csv"
REPORT = ROOT / "reports" / f"ddproperty-direct-listing-backfill-{TODAY.isoformat()}.json"
CATALOGUE = DIST / "bangkok-catalogue.js"
MANUAL = DIST / "bangkok-manual-market-samples.js"
BASE = "https://www.ddproperty.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
NAME_STOP = {"a", "an", "at", "by", "in", "of", "on", "the", "and", "condo", "condotown", "condominium", "apartment", "apartments", "residence", "residences", "tower", "building", "bangkok", "project"}


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def name_tokens(value: object) -> set[str]:
    return {token for token in norm(value).split() if token not in NAME_STOP and len(token) > 1}


def name_match(target: str, candidate: str) -> bool:
    left, right = name_tokens(target), name_tokens(candidate)
    if not left or not right or re.findall(r"\d+", norm(target)) != re.findall(r"\d+", norm(candidate)):
        return False
    coverage = len(left & right) / len(left)
    return coverage >= 0.85 and bool(left & right)


def parse_json_data(page: str) -> dict | None:
    match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def request_json(url: str, params: dict | None = None) -> tuple[dict | None, str | None]:
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=(8, 35))
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep((attempt + 1) * 1.5)
                continue
            response.raise_for_status()
            data = parse_json_data(response.text)
            return data, None if data else f"missing_next_data_http_{response.status_code}"
        except Exception as error:
            if attempt == 2:
                return None, f"{type(error).__name__}: {str(error)[:140]}"
            time.sleep((attempt + 1) * 1.0)
    return None, "request_retries_exhausted"


def page_data(payload: dict) -> dict:
    return (((payload.get("props") or {}).get("pageProps") or {}).get("pageData") or {}).get("data") or {}


def listing_rows(payload: dict) -> list[dict]:
    return [row.get("listingData") or {} for row in page_data(payload).get("listingsData", []) if isinstance(row, dict)]


def search_project_id(project: dict, kind: str) -> dict:
    result = {"hipflatId": int(project["id"]), "name": project.get("name"), "kind": kind}
    page_url = f"{BASE}/en/property-for-{kind}"
    payload, error = request_json(page_url, {"keyword": str(project.get("name") or "")})
    result["keywordPage"] = page_url + "?keyword=" + quote(str(project.get("name") or ""))
    if error:
        result["status"] = "keyword_search_failed"
        result["error"] = error
        return result
    catalogue_district = district(project.get("address"))
    candidates: dict[int, dict] = {}
    expected_name = str(project.get("name") or "")
    for item in listing_rows(payload or {}):
        prop = item.get("property") or {}
        try:
            dd_id = int(prop.get("id"))
        except (TypeError, ValueError):
            continue
        title = str(item.get("localizedTitle") or "").rsplit(",", 1)[0]
        if not name_match(expected_name, title):
            continue
        found_district = district(item.get("fullAddress") or item.get("shortAddress"))
        if not catalogue_district or found_district != catalogue_district:
            continue
        price_obj = item.get("price") or {}
        try:
            price = float(price_obj.get("value"))
            area = float(item.get("floorArea") or 0)
        except (TypeError, ValueError):
            continue
        beds = item.get("bedrooms")
        if not (price > 0 and 15 <= area <= 1000 and (beds is None or isinstance(beds, (int, float)))):
            continue
        if item.get("statusCode") != "ACT" or item.get("typeCode") != ("SALE" if kind == "sale" else "RENT"):
            continue
        posted = (item.get("postedOn") or {}).get("unix")
        try:
            listed = datetime.fromtimestamp(int(posted), tz=timezone.utc).date() if posted else None
        except (TypeError, ValueError, OSError):
            listed = None
        age_days = (TODAY - listed).days if listed else None
        candidate = {"ddPropertyProjectId": dd_id, "title": title, "address": item.get("fullAddress") or item.get("shortAddress"),
                    "district": found_district, "projectPage": item.get("project"), "ageDays": age_days}
        candidates.setdefault(dd_id, candidate)
    if not candidates:
        result["status"] = "no_exact_current_candidate_in_keyword_results"
        return result
    if len(candidates) > 1:
        result["status"] = "multiple_ddproperty_project_ids"
        result["candidates"] = list(candidates.values())
        return result
    candidate = next(iter(candidates.values()))
    dd_id = candidate["ddPropertyProjectId"]
    project_slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", norm(candidate["title"]))).strip("-")
    dd_project_url = f"{BASE}/en/project/{dd_id}-{project_slug}"
    project_payload, project_error = request_json(dd_project_url)
    if project_error:
        result.update(status="ddproperty_project_page_failed", candidate=candidate, error=project_error)
        return result
    source_project = page_data(project_payload or {}).get("projectData") or {}
    source_name = str(source_project.get("projectName") or "")
    source_district = str(source_project.get("districtName") or "")
    if int(source_project.get("projectId") or -1) != dd_id or not name_match(expected_name, source_name) or district(source_district) != catalogue_district:
        result.update(status="ddproperty_project_identity_mismatch", candidate=candidate,
                      ddProject={"id": source_project.get("projectId"), "name": source_name, "district": source_district})
        return result

    project_path_slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", norm(source_name))).strip("-")
    srp_url = f"{BASE}/en/property-for-{kind}/at-{project_path_slug}-{dd_id}"
    first_payload, first_error = request_json(srp_url)
    if first_error:
        result.update(status="project_listing_page_failed", candidate=candidate, ddProjectUrl=dd_project_url, error=first_error)
        return result
    data = page_data(first_payload or {})
    pagination = data.get("paginationData") or {}
    try:
        pages = min(max(1, int(pagination.get("totalPages") or 1)), 10)
    except (TypeError, ValueError):
        pages = 1
    all_cards = list(listing_rows(first_payload or {}))
    for page_no in range(2, pages + 1):
        next_payload, next_error = request_json(srp_url, {"page": page_no})
        if next_error:
            result.setdefault("pageErrors", []).append({"page": page_no, "error": next_error})
            continue
        all_cards.extend(listing_rows(next_payload or {}))

    samples = []
    seen = set()
    for item in all_cards:
        try:
            listing_id = str(item.get("id"))
            price = float((item.get("price") or {}).get("value"))
            area = float(item.get("floorArea") or 0)
        except (TypeError, ValueError):
            continue
        if not listing_id.isdigit() or listing_id in seen or not (price > 0 and 15 <= area <= 1000):
            continue
        if item.get("statusCode") != "ACT" or item.get("typeCode") != ("SALE" if kind == "sale" else "RENT"):
            continue
        prop = item.get("property") or {}
        if int(prop.get("id") or -1) != dd_id:
            continue
        title = str(item.get("localizedTitle") or "").rsplit(",", 1)[0]
        if not name_match(expected_name, title):
            continue
        found_district = district(item.get("fullAddress") or item.get("shortAddress"))
        if found_district != catalogue_district:
            continue
        url = str(item.get("url") or "")
        if not url.startswith(f"{BASE}/en/property/"):
            continue
        posted = (item.get("postedOn") or {}).get("unix")
        try:
            updated = datetime.fromtimestamp(int(posted), tz=timezone.utc).date().isoformat() if posted else None
        except (TypeError, ValueError, OSError):
            updated = None
        age = (TODAY - date.fromisoformat(updated)).days if updated else None
        beds = item.get("bedrooms")
        sample = {"id": listing_id, "price": price, "area": area,
                  "beds": int(beds) if isinstance(beds, (int, float)) and int(beds) > 0 else None,
                  "roomType": f"{int(beds)}BR" if isinstance(beds, (int, float)) and int(beds) > 0 else None,
                  "title": str(item.get("localizedTitle") or item.get("typeText") or "")[:240],
                  "url": url, "updated": updated, "sourceName": "DDproperty",
                  "listingStatus": "active" if age is None or age <= 30 else "update_over_30d",
                  "matchedBy": "DDproperty project ID + exact name tokens + matching district"}
        samples.append(sample)
        seen.add(listing_id)
    current = [row for row in samples if row["listingStatus"] == "active"]
    if not current:
        result.update(status="project_verified_but_no_recent_active_sample", candidate=candidate,
                      ddProjectUrl=dd_project_url, srpUrl=srp_url, observedListings=len(samples), samples=samples)
        return result
    minimum = min(current, key=lambda row: row["price"])
    minimum_rate = min(current, key=lambda row: row["price"] / row["area"])
    by_bedroom = {}
    for beds in sorted({row["beds"] for row in current if row.get("beds")}):
        group = [row for row in current if row.get("beds") == beds]
        cheapest = min(group, key=lambda row: row["price"])
        cheapest_rate = min(group, key=lambda row: row["price"] / row["area"])
        by_bedroom[str(beds)] = {"count": len(group), "minimum": cheapest["price"], "area": cheapest["area"],
            "minimumArea": cheapest["area"], "priceSqm": round(cheapest["price"] / cheapest["area"], 2),
            "minimumSqm": round(cheapest_rate["price"] / cheapest_rate["area"], 2),
            "sourceUrl": cheapest["url"], "minimumSourceUrl": cheapest["url"], "minimumSqmSourceUrl": cheapest_rate["url"]}
    market = {"count": len(current), "observedCount": len(current), "countKind": "ddproperty_current_individual_listings",
        "average": round(sum(row["price"] for row in current) / len(current)), "minimum": minimum["price"],
        "minimumArea": minimum["area"], "averageSqm": round(sum(row["price"] / row["area"] for row in current) / len(current)),
        "minimumSqm": round(minimum_rate["price"] / minimum_rate["area"], 2), "asOf": TODAY.isoformat(),
        "sourceName": "DDproperty 專案單筆掛牌", "source": srp_url,
        "minimumSourceUrl": minimum["url"], "minimumSqmSourceUrl": minimum_rate["url"],
        "byBedroom": by_bedroom, "samples": samples}
    result.update(status="verified_active_ddproperty_listings", candidate=candidate,
                  ddProjectUrl=dd_project_url, srpUrl=srp_url, sampleCount=len(current), market=market)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-no-sample", action="store_true", help="Search markets that currently have no sale/rent sample")
    parser.add_argument("--limit", type=int, default=0, help="Limit the target market batch (0 means all)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many target markets before processing")
    args = parser.parse_args()
    global REPORT
    if args.include_no_sample:
        REPORT = ROOT / "reports" / f"ddproperty-no-sample-backfill-{TODAY.isoformat()}-offset-{args.offset}.json"
    projects = js_array(CATALOGUE, "BANGKOK_CONDO_CATALOGUE")
    project_by_id = {int(project["id"]): project for project in projects}
    coverage = {int(row["hipflat_id"]): row for row in csv.DictReader(AUDIT.open(encoding="utf-8-sig"))}
    targets = []
    for project_id, row in coverage.items():
        for kind, sample_key, link_key in (("sale", "sale_sample", "sale_individual_listing_link"),
                                             ("rent", "rent_sample", "rent_individual_listing_link")):
            if ((row.get(sample_key) == "yes" and row.get(link_key) != "yes")
                    or (args.include_no_sample and row.get(sample_key) != "yes")):
                targets.append((project_by_id[project_id], kind))
    targets = targets[args.offset:]
    if args.limit:
        targets = targets[:args.limit]
    print(f"DDproperty project markets to backfill with clickable unit listings: {len(targets)}; workers: 4", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(search_project_id, project, kind) for project, kind in targets]
        for done, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            if done % 10 == 0 or done == len(futures):
                print(f"Searched {done}/{len(futures)} markets; verified active DDproperty project pages: {sum(row.get('status') == 'verified_active_ddproperty_listings' for row in results)}", flush=True)

    manual_rows = js_array(MANUAL, "BANGKOK_MANUAL_MARKET_SAMPLES")
    manual_by_id = {int(row["hipflatId"]): row for row in manual_rows}
    accepted = 0
    for result in results:
        if result.get("status") != "verified_active_ddproperty_listings":
            continue
        project_id, kind = result["hipflatId"], result["kind"]
        record = manual_by_id.get(project_id) or {"hipflatId": project_id, "name": result["name"]}
        record[kind] = result["market"]
        record["replace" + kind.title()] = True
        record["ddpropertyProjectUrl"] = result["ddProjectUrl"]
        manual_by_id[project_id] = record
        accepted += 1
    MANUAL.write_text("window.BANGKOK_MANUAL_MARKET_SAMPLES = " + json.dumps([manual_by_id[key] for key in sorted(manual_by_id)], ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    statuses = {}
    for result in results:
        status = result.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1
    REPORT.write_text(json.dumps({"checkedAt": TODAY.isoformat(), "targetMarkets": len(targets), "backfilledMarkets": accepted,
        "statuses": statuses, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checkedAt": TODAY.isoformat(), "targetMarkets": len(targets), "backfilledMarkets": accepted,
        "statuses": statuses, "report": str(REPORT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
