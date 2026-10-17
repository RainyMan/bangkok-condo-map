"""Add clearly labelled PropertyScout project market summaries where PropertyHub has no samples."""
from __future__ import annotations

import concurrent.futures
import html
import json
import re
import urllib.request
from pathlib import Path

from rapidfuzz import fuzz, process

import enrich_propertyscout_coordinates as locations

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = DIST / "bangkok-propertyscout-markets.js"
AUDIT = locations.RESEARCH / "propertyscout-market-audit.json"


def number(value: str) -> float | None:
    text = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    match = re.search(r"\d[\d,]*(?:\.\d+)?", text)
    return float(match.group(0).replace(",", "")) if match else None


def cell_text(value: object) -> str:
    if isinstance(value, list):
        return " ".join(cell_text(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("en", ""))
    return str(value or "")


def parse_table(table: dict | None, source: str, listing_count: int) -> dict | None:
    rows = table.get("rows") if isinstance(table, dict) else None
    parsed = []
    for row in rows or []:
        if not isinstance(row, list) or len(row) < 5:
            continue
        count = number(cell_text(row[1])) or 0
        average = number(cell_text(row[3]))
        average_sqm = number(cell_text(row[4]))
        beds_text = cell_text(row[0]).strip()
        beds = number(beds_text)
        if count > 0 and average is not None and average_sqm is not None:
            parsed.append({"beds": beds, "count": int(count), "average": average, "averageSqm": average_sqm})
    if not parsed:
        return None
    total_units = sum(row["count"] for row in parsed)
    weighted_average = sum(row["average"] * row["count"] for row in parsed) / total_units
    weighted_sqm = sum(row["averageSqm"] * row["count"] for row in parsed) / total_units
    start_price = number(cell_text(table.get("startText", "")))
    return {
        "average": round(weighted_average),
        "minimum": round(start_price) if start_price is not None else round(min(row["average"] for row in parsed)),
        "averageSqm": round(weighted_sqm),
        "minimumSqm": round(min(row["averageSqm"] for row in parsed)),
        "count": listing_count,
        "observedCount": total_units,
        "countKind": "propertyscout_market_summary",
        "marketSummary": True,
        "sourceName": "PropertyScout 樓盤行情摘要",
        "source": source,
        "minimumSourceUrl": source,
        "minimumSqmSourceUrl": source,
        "bedroomRates": parsed,
    }


def fetch(candidate: dict) -> dict:
    row = dict(candidate)
    try:
        req = urllib.request.Request(row["sourceUrl"], headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=25) as response:
            page = response.read().decode("utf-8")
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', page, re.S)
        if not match:
            raise ValueError("No project detail data")
        props = json.loads(match.group(1)).get("props", {}).get("pageProps", {})
        building, content, basic = props.get("building", {}), props.get("content", {}), props.get("basicInfo", {})
        ps_name = building.get("name", {}).get("en", "")
        ps_district = building.get("district_ps", {}).get("en", "")
        row.update({
            "propertyScoutName": ps_name,
            "propertyScoutDistrict": ps_district,
            "nameScore": round(fuzz.ratio(locations.norm(row["hipflatName"]), locations.norm(ps_name)), 1),
            "basicInfo": {key: basic.get(key) for key in (
                "completion_year", "started_year", "commonarea_management_fee", "total_units", "number_of_floors",
            )},
            "sale": None,
            "rent": None,
        })
        for kind in ("sale", "rent"):
            table = content.get(f"{kind}_pricing")
            if table:
                table = dict(table)
                table["startText"] = content.get(f"{kind}_type_content", {}).get("en", "")
                listed_count = number(cell_text(content.get(f"count_{kind}_content", {}).get("en", ""))) or 0
                row[kind] = parse_table(table, row["sourceUrl"], int(listed_count))
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
    return row


def main() -> int:
    catalogue = locations.arr("bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    summaries = {int(row["id"]): row for row in locations.arr("bangkok-propertyhub-city-summaries.js", "BANGKOK_PROPERTYHUB_CITY_SUMMARIES")}
    xml = locations.SITEMAP.read_text(encoding="utf-8")
    slug_map: dict[str, list[str]] = {}
    for url in re.findall(r"<loc>(.*?)</loc>", xml):
        match = re.search(r"/en/bangkok/condo/([^/]+)/?$", url)
        if match:
            slug_map.setdefault(match.group(1), []).append(url)

    candidates = []
    known_slugs = list(slug_map)
    for project in catalogue:
        project_id = int(project["id"])
        market = summaries.get(project_id, {})
        if market.get("sale") and market.get("rent"):
            continue
        expected = locations.slug(project.get("name", ""))
        urls = slug_map.get(expected) or slug_map.get(re.sub(r"-(?:condo|minium|residence)$", "", expected), [])
        match_score = 100
        if not urls:
            ranked = process.extract(expected, known_slugs, scorer=fuzz.ratio, limit=2)
            if not ranked or ranked[0][1] < 80 or (len(ranked) > 1 and ranked[0][1] - ranked[1][1] < 8):
                continue
            urls = slug_map[ranked[0][0]]
            match_score = float(ranked[0][1])
        candidates.append({
            "hipflatId": project_id,
            "hipflatName": project["name"],
            "expectedDistrict": locations.district_from_address(project.get("address")),
            "sourceUrl": urls[0],
            "slugMatchScore": match_score,
            "existingSale": bool(market.get("sale")),
            "existingRent": bool(market.get("rent")),
        })

    cached = {}
    if AUDIT.exists():
        try:
            cached = {int(row["hipflatId"]): row for row in json.loads(AUDIT.read_text(encoding="utf-8"))}
        except (ValueError, KeyError):
            cached = {}
    pending = [row for row in candidates if row["hipflatId"] not in cached]
    print(f"Missing listing side(s): {len(candidates)} name-matched projects; fetching {len(pending)}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for i, row in enumerate(pool.map(fetch, pending), 1):
            cached[int(row["hipflatId"])] = row
            if i % 20 == 0 or i == len(pending):
                AUDIT.parent.mkdir(parents=True, exist_ok=True)
                AUDIT.write_text(json.dumps(list(cached.values()), ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"Fetched {i}/{len(pending)}", flush=True)

    verified = []
    for row in cached.values():
        district = locations.norm(row.get("propertyScoutDistrict"))
        expected_district = locations.norm(row.get("expectedDistrict"))
        aliases = {"vadhana": "watthana", "sathorn": "sathon"}
        district, expected_district = aliases.get(district, district), aliases.get(expected_district, expected_district)
        cross_check = locations.CROSS_DISTRICT_VERIFIED.get(int(row["hipflatId"]))
        min_name_score = 95 if row.get("slugMatchScore", 100) < 100 else 90
        if row.get("error") or row.get("nameScore", 0) < min_name_score or (expected_district and district != expected_district and not cross_check):
            continue
        sale = None if row.get("existingSale") else row.get("sale")
        rent = None if row.get("existingRent") else row.get("rent")
        basic = row.get("basicInfo", {})
        if not sale and not rent and not basic.get("completion_year") and not basic.get("commonarea_management_fee"):
            continue
        verified.append({
            "hipflatId": row["hipflatId"],
            "name": row["hipflatName"],
            "sourceUrl": row["sourceUrl"],
            "locationSourceName": "PropertyScout 專案頁",
            "locationVerificationSourceUrl": cross_check,
            "sale": sale,
            "rent": rent,
            "completedYear": basic.get("completion_year"),
            "startedYear": basic.get("started_year"),
            "fee": basic.get("commonarea_management_fee"),
            "units": basic.get("total_units"),
            "floors": basic.get("number_of_floors"),
        })

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(list(cached.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT.write_text(
        "window.BANGKOK_PROPERTYSCOUT_MARKETS = " + json.dumps(verified, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Verified supplemental market summaries: {len(verified)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
