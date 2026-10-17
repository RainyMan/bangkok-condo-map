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
        if host.endswith("tperty.com") and re.search(r"/.+-\d{5,}", path):
            return True
        if host.endswith("property-hua-hin.com") and re.search(r"/.+-u\d{5,}", path):
            return True
        if host.endswith("propertyscout.co.th") and re.search(r"/.+-\d{6,}/?$", path):
            return True
        if host.endswith("thaiapartment.com") and "/condo-detail/" in path:
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
    projects = load_array("bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    # This must be the same compiled source file loaded by index.html. The
    # similarly named bangkok-propertyhub.js is an unbundled research artifact.
    propertyhub = index(load_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"), "id")
    propertyhub_research = index(load_array("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS"), "id")
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
        base = propertyhub.get(project_id, {})
        propertyhub_id = str(base.get("propertyHubProjectId", ""))
        # Match app.js source precedence for project and market data.
        market = {**base, **guessed.get(project_id, {}), **details.get(propertyhub_id, {})}
        scout_market = scout_markets.get(project_id, {})
        manual_market = manual_markets.get(project_id, {})
        research_market = propertyhub_research.get(project_id, {})
        sale = market.get("sale") or scout_market.get("sale") or manual_market.get("sale") or {}
        if manual_market.get("replaceSale") and manual_market.get("sale"):
            sale = manual_market["sale"]
        rent = market.get("rent") or scout_market.get("rent") or manual_market.get("rent") or {}
        scout_location = scout_details.get(project_id, {})
        verified_location = verified_coordinates.get(project_id, {})
        project_name_key = re.sub(r"[^a-z0-9]+", " ", str(project.get("name", "")).lower()).strip()
        legacy_matches = legacy_by_name.get(project_name_key, [])
        legacy = legacy_matches[0] if len(legacy_matches) == 1 else {}
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
        # Match the coordinate source actually selected by app.js instead of
        # accidentally reporting a market/search URL as the location source.
        coordinate_source = ""
        for row, source_url in (
            (market, market.get("locationSourceUrl")),
            (project, project.get("locationSourceUrl")),
            (osm.get(project_id, {}), osm.get(project_id, {}).get("sourceUrl")),
            (scout_location, scout_location.get("locationSourceUrl")),
            (verified_location, verified_location.get("sourceUrl")),
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
            "sale_source": str(sale.get("minimumSqmSourceUrl") or sale.get("minimumSourceUrl") or sale.get("source") or ""),
            "sale_sample_updated": listing_updated(sale, research_market.get("sale") or {}),
            "rent_sample": "yes" if has_rent else "no",
            "rent_individual_listing_link": "yes" if rent_linked else "no",
            "rent_source": str(rent.get("minimumSqmSourceUrl") or rent.get("minimumSourceUrl") or rent.get("source") or ""),
            "rent_sample_updated": listing_updated(rent, research_market.get("rent") or {}),
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
