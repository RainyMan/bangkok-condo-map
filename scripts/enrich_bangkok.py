"""Enrich the Hipflat Bangkok condo directory with PropertyHub project/listing data.

The Hipflat directory is the source of project identity and its own displayed
from-prices. PropertyHub contributes independently linked listing samples and
project coordinates when a project-name match is clear.
"""
from __future__ import annotations

import concurrent.futures
import html
import json
import math
import pathlib
import re
import sys
import threading
import time
from typing import Any

import requests


ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
CACHE = RESEARCH / "propertyhub-enrichment.jsonl"
OUTPUT = DIST / "bangkok-propertyhub.js"
BASE = "https://propertyhub.in.th"
HEADERS = {
    "User-Agent": "BangkokCondoMapResearch/1.0 (public listing research; contact: site owner)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en,th;q=0.8",
}
LOCK = threading.Lock()


def read_projects() -> list[dict[str, Any]]:
    source = (DIST / "bangkok-catalogue.js").read_text(encoding="utf-8")
    match = re.search(r"window\.BANGKOK_HIPFLAT_PROJECTS\s*=\s*(\[.*\]);", source, re.S)
    if not match:
        raise RuntimeError("Bangkok Hipflat catalogue array was not found")
    return json.loads(match.group(1))


def slugify(value: str) -> str:
    value = html.unescape(value).lower().replace("&", " and ")
    value = value.replace("@", " ").replace("’", "").replace("'", "")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value)).strip("-")


def load_cache() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if row.get("marketDataStatus") != "lookup_error":
                    rows[int(row["id"])] = row
            except (ValueError, KeyError, TypeError):
                continue
    return rows


def fetch_page(session: requests.Session, url: str) -> dict[str, Any] | None:
    for attempt in range(2):
        try:
            response = session.get(url, timeout=(5, 15), headers=HEADERS)
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(2 ** attempt, 10))
                continue
            if response.status_code != 200:
                return None
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.S)
            if not match:
                return None
            return json.loads(match.group(1)).get("props", {}).get("pageProps")
        except (requests.RequestException, json.JSONDecodeError):
            time.sleep(min(2 ** attempt, 10))
    return None


def name_score(a: str, b: str, aliases: list[str] | None = None) -> float:
    def tokens(s: str) -> set[str]:
        raw = slugify(s).split("-")
        ignored = {"condo", "condominium", "apartment", "project", "bangkok", "the"}
        return {t for t in raw if t not in ignored and len(t) > 1}

    left = tokens(a)
    options = [b, *(aliases or [])]
    return max((len(left & tokens(x)) / max(len(left | tokens(x)), 1) for x in options), default=0)


def number(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None


def parse_listing(ad: dict[str, Any], kind: str, expected_project_id: str) -> dict[str, Any] | None:
    if str((ad.get("project") or {}).get("id", "")) != str(expected_project_id):
        return None
    price_data = ad.get("price") or {}
    if kind == "sale":
        amount = number(((price_data.get("forSale") or {}).get("price")))
    else:
        amount = number((((price_data.get("forRent") or {}).get("monthly") or {}).get("price")))
    room = ad.get("roomInformation") or {}
    area = number(room.get("roomArea"))
    if not amount or not area or not 15 <= area <= 1000:
        return None
    rate = amount / area
    title = str(ad.get("title") or "")
    if kind == "sale":
        if not 300_000 <= amount <= 500_000_000 or not 10_000 <= rate <= 1_500_000:
            return None
        if re.search(r"deposit|down.?payment|transfer|booking|assignment|reservation", title, re.I):
            return None
    elif not 3_000 <= amount <= 2_000_000 or not 100 <= rate <= 15_000:
        return None
    listing_id = str(ad.get("id") or "")
    listing_slug = str(ad.get("slug") or "")
    if not listing_id or not listing_slug:
        return None
    return {
        "id": listing_id,
        "price": amount,
        "area": area,
        "beds": room.get("numberOfBed"),
        "type": room.get("roomType"),
        "priceSqm": round(rate),
        "title": title,
        "url": f"{BASE}/en/listings/{listing_slug}---{listing_id}",
        "updated": ad.get("updatedAt"),
    }


def market_summary(items: list[dict[str, Any]], page_props: dict[str, Any], kind: str, source: str) -> dict[str, Any] | None:
    listings = page_props.get("listings") or {}
    pagination = listings.get("pagination") or {}
    valid = [x for ad in listings.get("listings", []) if (x := parse_listing(ad, kind, str((page_props.get("project") or {}).get("id", ""))))]
    # Extra pages are gathered by crawl_project and passed in as parsed observations.
    valid.extend(items)
    unique = {x["id"]: x for x in valid}
    valid = list(unique.values())
    if not valid:
        return None
    by_price = sorted(valid, key=lambda x: x["price"])
    by_rate = sorted(valid, key=lambda x: x["priceSqm"])
    return {
        "count": int(pagination.get("totalCount") or len(valid)),
        "observedCount": len(valid),
        "average": round(sum(x["price"] for x in valid) / len(valid)),
        "minimum": by_price[0]["price"],
        "averageSqm": round(sum(x["priceSqm"] for x in valid) / len(valid)),
        "minimumSqm": by_rate[0]["priceSqm"],
        "asOf": "2026-10-17",
        "snapshotMethod": "propertyhub_project_page_listing_cards_validated",
        "source": source,
        "minimumSourceUrl": by_price[0]["url"],
        "minimumSqmSourceUrl": by_rate[0]["url"],
        "samples": by_price[:12],
    }


def crawl_project(row: dict[str, Any]) -> dict[str, Any]:
    session = requests.Session()
    slug = slugify(row["name"])
    result = dict(row)
    project_info: dict[str, Any] | None = None
    sales: list[dict[str, Any]] = []
    rents: list[dict[str, Any]] = []
    market_sources: dict[str, str] = {}
    market_page_props: dict[str, dict[str, Any]] = {}
    fail: list[str] = []

    for kind, bucket in (("sale", sales), ("rent", rents)):
        project_url = f"{BASE}/en/condo-for-{kind}/project-{slug}"
        page = fetch_page(session, project_url)
        if not page or not page.get("project") or not isinstance(page.get("listings"), dict):
            fail.append(kind)
            continue
        project = page["project"]
        aliases = project.get("possibleProjectNames") or []
        score = name_score(row["name"], project.get("nameEnglish") or project.get("name") or "", aliases)
        if score < 0.5:
            fail.append(kind + "_name_mismatch")
            continue
        if not project_info or (project.get("location") and not project_info.get("location")):
            project_info = project
        market_sources[kind] = project_url
        market_page_props[kind] = page
        expected_id = str(project.get("id", ""))
        listing_data = page.get("listings") or {}
        pagination = listing_data.get("pagination") or {}
        for ad in listing_data.get("listings", []):
            parsed = parse_listing(ad, kind, expected_id)
            if parsed:
                bucket.append(parsed)
        # First page is the publicly visible sample snapshot. Pagination can
        # contain hundreds of cards per project and is not required to provide
        # a source-linked price sample for the map.

    if project_info:
        info = project_info.get("projectInfo") or {}
        location = project_info.get("location") or {}
        lat, lng = number(location.get("lat")), number(location.get("lng"))
        if lat is not None and lng is not None and 13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0:
            result.update({
                "lat": lat,
                "lng": lng,
                "completedYear": int(info["completedYear"]) if str(info.get("completedYear", "")).isdigit() else result.get("completedYear"),
                "units": int(info["totalUnits"]) if str(info.get("totalUnits", "")).isdigit() else result.get("units"),
                "floors": int(info["buildingsFloors"]) if str(info.get("buildingsFloors", "")).isdigit() else result.get("floors"),
                "locationVerified": True,
                "locationSourceUrl": f"{BASE}/en/projects/{project_info.get('slug', slug)}",
                "locationSourceName": "PropertyHub 專案頁",
                "propertyHubProjectUrl": f"{BASE}/en/projects/{project_info.get('slug', slug)}",
            })
        fee = str(info.get("utilityFee") or "")
        fee_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:baht|thb|฿)?\s*(?:/\s*(?:sq\.?\s*m|sqm|㎡)|per\s+(?:sq\.?\s*m|sqm))", fee, re.I)
        if fee_match:
            result["fee"] = {"rate": float(fee_match.group(1)), "note": "PropertyHub 專案頁刊載費率；現行實收仍待管委會核實。", "source": f"{BASE}/en/projects/{project_info.get('slug', slug)}", "status": "published_indicative"}

    for kind, bucket in (("sale", sales), ("rent", rents)):
        if kind in market_page_props:
            market = market_summary(bucket, market_page_props[kind], kind, market_sources[kind])
            if market:
                result[kind] = market
                result[kind + "SourceUrl"] = market_sources[kind]
    sale_data = result.get("sale") or {}
    rent_data = result.get("rent") or {}
    result["marketDataStatus"] = "propertyhub_listing_card_snapshot_validated" if sale_data and rent_data else "propertyhub_sale_only" if sale_data else "propertyhub_rent_only" if rent_data else "hipflat_project_summary_only" if result.get("hipflatSummary", {}).get("saleFrom") or result.get("hipflatSummary", {}).get("rentFrom") else "pending"
    result["lastListingRefresh"] = "2026-10-17" if result.get("sale") or result.get("rent") else None
    result["dataCompleteness"] = {
        "coordinates": bool(result.get("locationVerified") and number(result.get("lat")) is not None and number(result.get("lng")) is not None),
        "saleSample": bool(sale_data.get("minimumSqm")),
        "rentSample": bool(rent_data.get("minimumSqm")),
        "yield": bool(sale_data.get("minimumSqm") and rent_data.get("minimumSqm")),
    }
    if fail:
        result["propertyHubLookupNotes"] = fail
    session.close()
    return result


def write_output(rows: list[dict[str, Any]]) -> None:
    OUTPUT.write_text("window.BANGKOK_PROPERTYHUB_PROJECTS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> int:
    RESEARCH.mkdir(parents=True, exist_ok=True)
    projects = read_projects()
    cached = load_cache()
    completed = set(cached)
    pending = [x for x in projects if int(x["id"]) not in completed]
    print(f"Projects {len(projects)}, cached {len(completed)}, pending {len(pending)}", flush=True)
    write_output([cached.get(int(row["id"]), row) for row in projects])
    # Keep workers modest to limit load on the public listing source.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool, CACHE.open("a", encoding="utf-8") as out:
        futures = {pool.submit(crawl_project, row): row for row in pending}
        done = len(completed)
        for future in concurrent.futures.as_completed(futures):
            row = futures[future]
            try:
                result = future.result()
            except Exception as error:
                result = dict(row)
                result["marketDataStatus"] = "lookup_error"
                result["propertyHubLookupNotes"] = [str(error)[:300]]
            with LOCK:
                out.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                out.flush()
            cached[int(row["id"])] = result
            done += 1
            print(f"Fetched {done}/{len(projects)} {row['name']} · {result.get('marketDataStatus')}", flush=True)
            if done % 25 == 0 or done == len(projects):
                write_output([cached.get(int(item["id"]), item) for item in projects])
                counts = {
                    "coords": sum(bool(x.get("locationVerified")) for x in cached.values()),
                    "sale": sum(bool(x.get("sale", {}).get("minimumSqm")) for x in cached.values()),
                    "rent": sum(bool(x.get("rent", {}).get("minimumSqm")) for x in cached.values()),
                    "both": sum(bool(x.get("sale", {}).get("minimumSqm") and x.get("rent", {}).get("minimumSqm")) for x in cached.values()),
                }
                print(f"{done}/{len(projects)} {row['name']} | {counts}", flush=True)
    final_rows = [cached.get(int(row["id"]), row) for row in projects]
    write_output(final_rows)
    print(f"Wrote {OUTPUT}; {len(final_rows)} rows", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
