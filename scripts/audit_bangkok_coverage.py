"""Audit the displayed data coverage for the Bangkok Hipflat condo catalogue.

This reads the existing local data only. It does not fetch or crawl websites.
Run with: python scripts/audit_bangkok_coverage.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = ROOT / "reports" / f"bangkok-coverage-{date.today().isoformat()}.csv"


def load_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def index(rows: list[dict], key: str) -> dict[str, dict]:
    return {str(row[key]): row for row in rows if row.get(key) is not None}


def in_range(value: object, low: int, high: int) -> bool:
    try:
        return low <= float(value) <= high
    except (TypeError, ValueError):
        return False


def has_individual_listing(market: dict) -> bool:
    urls = [market.get("minimumSourceUrl"), market.get("minimumSqmSourceUrl")]
    urls.extend(sample.get("url") for sample in market.get("samples", []) if isinstance(sample, dict))
    for url in urls:
        if not isinstance(url, str):
            continue
        parsed = urlsplit(url)
        path = parsed.path.lower()
        host = (parsed.hostname or "").lower()
        if re.search(r"/(?:listings?|ads?|property/|properties?|view/\d+|livingdetail_en/\d+|detail/condo-|property-rent/|property-for-sale/)", path):
            return True
        # RentHub verified building detail pages can be the direct source for
        # an available room even when the route has no numeric listing slug.
        if host.endswith("renthub.in.th") and path == "/en/tomi-place":
            return True
        if host.endswith("thaihometown.com") and re.search(r"^/condo/\d+/?$", path):
            return True
        if host.endswith("tperty.com") and re.search(r"/.+-\d{5,}", path):
            return True
        if host.endswith("property-hua-hin.com") and re.search(r"/.+-u\d{5,}", path):
            return True
        if host.endswith("propertyscout.co.th") and re.search(r"/.+-\d{6,}/?$", path):
            return True
        if host.endswith("sam.or.th") and re.search(r"^/site/index\.php/npa/map_preview/\d+/?$", path):
            return True
        if host.endswith("condothai.co.th") and re.search(r"^/room/\d+/", path):
            return True
        if host.endswith("thaiapartment.com") and "/condo-detail/" in path:
            return True
        if host.endswith("scancondo.com") and re.search(r"/(?:sell|rent)/\d+/[a-z0-9-]+/", path):
            return True
        # Thai-language Scancondo detail routes use a numeric condo ID followed
        # by the rental/sale listing ID, rather than the English /rent/... URL.
        if host.endswith("scancondo.com") and re.search(r"/\d{5,}/[a-z]{2,}\d{2}-\d{4}/", path):
            return True
    return False


def listing_updated(market: dict, research_market: dict | None = None) -> str:
    target_url = market.get("minimumSqmSourceUrl") or market.get("minimumSourceUrl")
    # Compiled display markets retain the freshness of the exact minimum-per-
    # sqm sample even when they omit the full list of observed cards.
    if market.get("minimumSqmSampleUpdated"):
        return str(market["minimumSqmSampleUpdated"])
    for source in (market, research_market or {}):
        for sample in source.get("samples", []):
            if isinstance(sample, dict) and sample.get("url") == target_url:
                return str(sample.get("updated") or "")
    return ""


def main() -> None:
    projects = load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    # This must be the same compiled source file loaded by index.html. The
    # similarly named bangkok-propertyhub.js is an unbundled research artifact.
    propertyhub = index(load_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"), "id")
    # This unbundled research artifact has grown beyond the memory limit of
    # some local Python environments. It is only a fallback for attaching a
    # sample freshness date; the compiled app data below remains authoritative.
    try:
        propertyhub_research = index(load_array("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS"), "id")
    except MemoryError:
        propertyhub_research = {}
    city_summaries = index(load_array("bangkok-propertyhub-city-summaries.js", "BANGKOK_PROPERTYHUB_CITY_SUMMARIES"), "id")
    details = index(load_array("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS"), "propertyHubProjectId")
    guessed = index(load_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS"), "hipflatProjectId")
    osm = index(load_array("bangkok-osm.js", "BANGKOK_OSM_LOCATIONS"), "id")
    scout_details = index(load_array("bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS"), "hipflatId")
    verified_coordinates = index(load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"), "hipflatId")
    scout_markets = index(load_array("bangkok-propertyscout-markets.js", "BANGKOK_PROPERTYSCOUT_MARKETS"), "hipflatId")
    manual_markets = index(load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"), "hipflatId")
    legacy_rows = (
        load_array("data.js", "CONDO_DATA")
        + load_array("catalogue.js", "CATALOGUE_PROJECTS")
        + load_array("huai-khwang.js", "HUAI_KHWANG_PROJECTS")
    )
    legacy_by_name: dict[str, list[dict]] = {}
    for row in legacy_rows:
        key = re.sub(r"[^a-z0-9]+", " ", str(row.get("name", "")).lower()).strip()
        legacy_by_name.setdefault(key, []).append(row)

    counts: Counter[str] = Counter()
    audit_rows: list[dict[str, str]] = []
    for project in projects:
        project_id = str(project["id"])
        project_name_key = re.sub(r"[^a-z0-9]+", " ", str(project.get("name", "")).lower()).strip()
        legacy_matches = legacy_by_name.get(project_name_key, [])
        legacy = legacy_matches[0] if len(legacy_matches) == 1 else {}
        base = propertyhub.get(project_id, {})
        propertyhub_id = str(base.get("propertyHubProjectId", ""))
        # Match app.js source precedence for project and market data.
        market = {**base, **guessed.get(project_id, {}), **details.get(propertyhub_id, {})}
        city_summary = city_summaries.get(project_id, {})
        # app.js uses the matched Bangkok-wide listing summary when present;
        # audit that exact displayed market before falling back to other feeds.
        if city_summary.get("sale"):
            market["sale"] = city_summary["sale"]
        if city_summary.get("rent"):
            market["rent"] = city_summary["rent"]
        scout_market = scout_markets.get(project_id, {})
        manual_market = manual_markets.get(project_id, {})
        research_market = propertyhub_research.get(project_id, {})
        # app.js also falls back to an exact, unique legacy-name match after
        # the Hipflat project and its market enrichments. Include those rows
        # here so the report describes the market data the map actually shows.
        sale = (
            market.get("sale") or scout_market.get("sale") or manual_market.get("sale")
            or project.get("sale") or legacy.get("sale") or {}
        )
        if manual_market.get("replaceSale") and manual_market.get("sale"):
            sale = manual_market["sale"]
        rent = (
            market.get("rent") or scout_market.get("rent") or manual_market.get("rent")
            or project.get("rent") or legacy.get("rent") or {}
        )
        if manual_market.get("replaceRent") and manual_market.get("rent"):
            rent = manual_market["rent"]
        scout_location = scout_details.get(project_id, {})
        verified_location = verified_coordinates.get(project_id, {})
        has_coords = any((row.get("locationVerified") and row.get("lat") is not None and row.get("lng") is not None)
                         for row in (market, project, scout_location, verified_location, legacy)) or (
            osm.get(project_id, {}).get("lat") is not None and osm[project_id].get("lng") is not None
        )
        has_sale = in_range(sale.get("minimumSqm"), 10_000, 2_000_000)
        has_rent = in_range(rent.get("minimumSqm"), 50, 20_000)
        manual_sale_samples = manual_market.get("sale", {}).get("samples", [])
        manual_rent_samples = manual_market.get("rent", {}).get("samples", [])
        has_manual_sale_listing = any(
            sample.get("price") and sample.get("area") and isinstance(sample.get("url"), str)
            and has_individual_listing({"minimumSourceUrl": sample["url"]})
            for sample in manual_sale_samples if isinstance(sample, dict)
        )
        has_manual_rent_listing = any(
            sample.get("price") and sample.get("area") and isinstance(sample.get("url"), str)
            and has_individual_listing({"minimumSourceUrl": sample["url"]})
            for sample in manual_rent_samples if isinstance(sample, dict)
        )
        sale_linked = (has_sale and has_individual_listing(sale)) or has_manual_sale_listing
        rent_linked = (has_rent and has_individual_listing(rent)) or has_manual_rent_listing
        direct_sale_samples = [sample for sample in manual_sale_samples if isinstance(sample, dict)
                               and sample.get("price") and sample.get("area") and sample.get("url")
                               and has_individual_listing({"minimumSourceUrl": sample["url"]})]
        direct_rent_samples = [sample for sample in manual_rent_samples if isinstance(sample, dict)
                               and sample.get("price") and sample.get("area") and sample.get("url")
                               and has_individual_listing({"minimumSourceUrl": sample["url"]})]
        # Prefer a clickable direct property page in the coverage report over a
        # market or project summary URL whenever an independently verified
        # individual listing sample is available.
        manual_sale_source = min(direct_sale_samples, key=lambda sample: float(sample["price"]), default={})
        manual_rent_source = min(direct_rent_samples,
                                 key=lambda sample: float(sample["price"]) / float(sample["area"]), default={})
        sale_source = manual_sale_source.get("url") or sale.get("minimumSqmSourceUrl") or sale.get("minimumSourceUrl") or sale.get("source") or ""
        rent_source = manual_rent_source.get("url") or rent.get("minimumSqmSourceUrl") or rent.get("minimumSourceUrl") or rent.get("source") or ""
        sale_updated = manual_sale_source.get("updated") or manual_sale_source.get("checkedAt") or listing_updated(sale, research_market.get("sale") or {})
        rent_updated = manual_rent_source.get("updated") or manual_rent_source.get("checkedAt") or listing_updated(rent, research_market.get("rent") or {})
        # Match the coordinate source actually selected by app.js instead of
        # accidentally reporting a market/search URL as the location source.
        coordinate_source = ""
        for row, source_url in (
            (market, market.get("locationSourceUrl")),
            (project, project.get("locationSourceUrl")),
            (osm.get(project_id, {}), osm.get(project_id, {}).get("sourceUrl")),
            (verified_location, verified_location.get("sourceUrl")),
            (scout_location, scout_location.get("locationSourceUrl")),
            (legacy, legacy.get("locationSourceUrl")),
        ):
            if row.get("locationVerified") and row.get("lat") is not None and row.get("lng") is not None:
                coordinate_source = str(source_url or "")
                break
        counts.update({
            "coordinates": int(has_coords), "sale": int(has_sale), "rent": int(has_rent),
            "sale_individual_listing": int(sale_linked), "rent_individual_listing": int(rent_linked),
            "both_markets": int(has_sale and has_rent),
        })
        missing = []
        if not has_coords:
            missing.append("座標")
        if not has_sale:
            missing.append("出售行情（僅有特殊資產掛牌）" if has_manual_sale_listing else "出售")
        elif not sale_linked:
            missing.append("出售單筆來源")
        if not has_rent:
            missing.append("出租")
        elif not rent_linked:
            missing.append("出租單筆來源")
        audit_rows.append({
            "hipflat_id": project_id,
            "condo": str(project.get("name", "")),
            "thai_address": str(project.get("address", "")),
            "hipflat_project": str(project.get("hipflatProjectUrl") or ""),
            "coordinates": "yes" if has_coords else "no",
            "coordinate_source": str(coordinate_source),
            "sale_sample": "yes" if has_sale or has_manual_sale_listing else "no",
            "sale_market_value": "yes" if has_sale else "no",
            "sale_individual_listing_link": "yes" if sale_linked else "no",
            "sale_source": str(sale_source),
            "sale_sample_updated": str(sale_updated),
            "rent_sample": "yes" if has_rent else "no",
            "rent_individual_listing_link": "yes" if rent_linked else "no",
            "rent_source": str(rent_source),
            "rent_sample_updated": str(rent_updated),
            "missing": ", ".join(missing),
        })

    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=list(audit_rows[0]))
        writer.writeheader()
        writer.writerows(audit_rows)
    print(json.dumps({"projects": len(projects), **counts, "auditCsv": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
