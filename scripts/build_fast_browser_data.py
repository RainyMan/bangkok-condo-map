"""Build a small first-load overview and on-demand condo detail shards."""

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SHARDS = DIST / "detail-shards"


def load_array(filename, symbol):
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Cannot parse {filename}:{symbol}")
    return json.loads(match.group(1))


def indexed(rows, key):
    return {str(row.get(key)): row for row in rows if row.get(key) is not None}


def sample_beds(sample):
    value = sample.get("beds", sample.get("bedrooms"))
    try:
        number = int(value)
        if number > 0:
            return number
    except (TypeError, ValueError):
        pass
    label = f"{sample.get('roomType') or ''} {sample.get('title') or ''}".lower()
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    match = re.search(r"\b(one|two|three|four|five)\s+bed(?:\s*room)?s?\b", label)
    if match:
        return words[match.group(1)]
    match = re.search(r"(?:^|\D)(\d+)\s*(?:br\b|bed(?:\s*room)?s?\b|房)", label, re.I)
    return int(match.group(1)) if match else None


def current_sample(sample):
    return sample.get("specialAsset") is not True and not re.search(
        r"confirmed_unavailable|future_availability|update_over|over_(?:30d|1y|year)|stale",
        str(sample.get("listingStatus") or ""), re.I)


def slim_market(market, manual):
    market = dict(market or manual or {})
    by_bedroom = {str(k): dict(v) for k, v in (market.get("byBedroom") or {}).items()}
    samples = [sample for sample in (manual or {}).get("samples", []) if current_sample(sample) and sample.get("url")]
    for sample in samples:
        price, area, beds = float(sample.get("price") or 0), float(sample.get("area") or 0), sample_beds(sample)
        if not beds or price <= 0 or area <= 0:
            continue
        key = str(beds)
        current = by_bedroom.get(key, {})
        if not float(current.get("minimum") or 0) or price <= float(current.get("minimum") or 0):
            rate = price / area
            by_bedroom[key] = {**current, "beds": beds, "minimum": price, "area": area,
                               "minimumArea": area, "priceSqm": rate, "minimumSqm": rate,
                               "sourceUrl": sample["url"], "minimumSourceUrl": sample["url"],
                               "minimumSqmSourceUrl": sample["url"]}
    if samples:
        cheapest = min(samples, key=lambda row: float(row.get("price") or math.inf))
        lowest_rate = min(samples, key=lambda row: float(row.get("price") or math.inf) / max(float(row.get("area") or 0), 1e-10))
        if not float(market.get("minimum") or 0) or float(cheapest.get("price") or math.inf) <= float(market.get("minimum") or math.inf):
            market.update(minimum=float(cheapest["price"]), minimumArea=float(cheapest["area"]),
                          minimumSourceUrl=cheapest["url"], minimumSampleUpdated=cheapest.get("updated"))
        if not float(market.get("minimumSqm") or 0) or float(lowest_rate["price"]) / float(lowest_rate["area"]) <= float(market.get("minimumSqm") or math.inf):
            market.update(minimumSqm=round(float(lowest_rate["price"]) / float(lowest_rate["area"]), 2),
                          minimumSqmSourceUrl=lowest_rate["url"], minimumSqmSampleUpdated=lowest_rate.get("updated"))
    market["byBedroom"] = by_bedroom
    keep = ("count", "observedCount", "countKind", "average", "minimum", "minimumArea",
            "minimumSampleUpdated", "averageSqm", "minimumSqm", "minimumSqmSampleUpdated",
            "asOf", "source", "sourceName", "marketSummary", "minimumSourceUrl",
            "minimumSqmSourceUrl", "byBedroom")
    return {key: market[key] for key in keep if key in market}


def dist_km(a, b):
    rad = math.pi / 180
    dlat, dlng = (b[0] - a[0]) * rad, (b[1] - a[1]) * rad
    h = math.sin(dlat / 2) ** 2 + math.cos(a[0] * rad) * math.cos(b[0] * rad) * math.sin(dlng / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def write_js(path, symbol, value):
    path.write_text(f"window.{symbol}=" + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


catalogue = load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
propertyhub = indexed(load_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"), "id")
hub_details = indexed(load_array("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS"), "propertyHubProjectId")
guessed = indexed(load_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS"), "hipflatProjectId")
verified = indexed(load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"), "hipflatId")
osm = indexed(load_array("bangkok-osm.js", "BANGKOK_OSM_LOCATIONS"), "id")
scout = indexed(load_array("bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS"), "hipflatId")
scout_market = indexed(load_array("bangkok-propertyscout-markets.js", "BANGKOK_PROPERTYSCOUT_MARKETS"), "hipflatId")
manual = indexed(load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"), "hipflatId")
routes = indexed(load_array("bangkok-walk-routes.js", "BANGKOK_WALK_ROUTES"), "id")
crosschecks = indexed(load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"), "hipflatId")
local = indexed(load_array("bangkok-local-listings.js", "BANGKOK_LOCAL_LISTINGS"), "projectId")
stations = load_array("stations.js", "MRT_STATIONS")
legacy = load_array("data.js", "CONDO_DATA") + load_array("catalogue.js", "CATALOGUE_PROJECTS") + load_array("huai-khwang.js", "HUAI_KHWANG_PROJECTS")
legacy_by_name = {}
for row in legacy:
    key = re.sub(r"[^a-z0-9]+", " ", str(row.get("name") or "").lower()).strip()
    legacy_by_name.setdefault(key, []).append(row)
station_by_id = {str(s.get("id")): s for s in stations}
overview, detail_rows = [], {}

for index, project in enumerate(catalogue):
    pid = str(project["id"])
    base = propertyhub.get(pid, {})
    prop = {**base, **guessed.get(pid, {}), **hub_details.get(str(base.get("propertyHubProjectId") or ""), {})}
    scout_row, scout_m = scout.get(pid, {}), scout_market.get(pid, {})
    manual_row, verified_row, osm_row = manual.get(pid, {}), verified.get(pid, {}), osm.get(pid, {})
    name_key = re.sub(r"[^a-z0-9]+", " ", str(project.get("name") or "").lower()).strip()
    legacy_row = legacy_by_name.get(name_key, [{}])
    legacy_row = legacy_row[0] if len(legacy_row) == 1 else {}

    prop_coords = prop.get("locationVerified") and isinstance(prop.get("lat"), (int, float)) and isinstance(prop.get("lng"), (int, float))
    proj_coords = not prop_coords and project.get("locationVerified") and isinstance(project.get("lat"), (int, float)) and isinstance(project.get("lng"), (int, float))
    osm_coords = not prop_coords and not proj_coords and osm_row.get("lat") is not None and osm_row.get("lng") is not None
    verified_coords = not prop_coords and not proj_coords and not osm_coords and verified_row.get("locationVerified") and verified_row.get("lat") is not None and verified_row.get("lng") is not None
    scout_coords = not prop_coords and not proj_coords and not osm_coords and not verified_coords and scout_row.get("locationVerified") and scout_row.get("lat") is not None and scout_row.get("lng") is not None
    lat = prop.get("lat") if prop_coords else project.get("lat") if proj_coords else osm_row.get("lat") if osm_coords else verified_row.get("lat") if verified_coords else scout_row.get("lat") if scout_coords else legacy_row.get("lat")
    lng = prop.get("lng") if prop_coords else project.get("lng") if proj_coords else osm_row.get("lng") if osm_coords else verified_row.get("lng") if verified_coords else scout_row.get("lng") if scout_coords else legacy_row.get("lng")
    located = bool(prop_coords or proj_coords or osm_coords or verified_coords or scout_coords or legacy_row.get("locationVerified"))

    nearest = routes.get(pid)
    if nearest and nearest.get("stationId"):
        nearest = {k: nearest[k] for k in ("stationId", "distanceKm", "straightDistanceKm", "minutes", "source", "sourceUrl", "asOf") if k in nearest}
    else:
        nearest = prop.get("nearestMrt") or project.get("nearestMrt") or legacy_row.get("nearestMrt")
        if not nearest and isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            closest = min(stations, key=lambda s: dist_km((lat, lng), (s["lat"], s["lng"])))
            distance = dist_km((lat, lng), (closest["lat"], closest["lng"]))
            nearest = {"stationId": closest["id"], "straightDistanceKm": round(distance, 2)}

    sale = prop.get("sale")
    rent = prop.get("rent")
    if not sale and scout_m.get("sale"):
        sale = scout_m["sale"]
    if not rent and scout_m.get("rent"):
        rent = scout_m["rent"]
    if manual_row.get("replaceSale") is True and manual_row.get("sale"):
        sale = manual_row["sale"]
    elif not sale and manual_row.get("sale"):
        sale = manual_row["sale"]
    if manual_row.get("replaceRent") is True and manual_row.get("rent"):
        rent = manual_row["rent"]
    elif not rent and manual_row.get("rent"):
        rent = manual_row["rent"]
    sale, rent = slim_market(sale, manual_row.get("sale")), slim_market(rent, manual_row.get("rent"))
    route = routes.get(pid)
    source_url = prop.get("locationSourceUrl") if prop_coords else project.get("locationSourceUrl") if proj_coords else osm_row.get("sourceUrl") if osm_coords else verified_row.get("sourceUrl") if verified_coords else scout_row.get("locationSourceUrl") if scout_coords else project.get("locationSourceUrl") or legacy_row.get("locationSourceUrl")
    source_name = prop.get("locationSourceName") if prop_coords else "OpenStreetMap 建物／地址" if osm_coords else verified_row.get("sourceName") if verified_coords else scout_row.get("locationSourceName") if scout_coords else project.get("locationSourceName") or legacy_row.get("locationSourceName")
    verification_url = (verified_row.get("corroborationSourceUrl") or verified_row.get("verificationSourceUrl")) if verified_coords else (scout_row.get("locationVerificationSourceUrl") or scout_m.get("locationVerificationSourceUrl")) if scout_coords else prop.get("locationVerificationSourceUrl") if prop_coords else (scout_row.get("locationVerificationSourceUrl") or scout_m.get("locationVerificationSourceUrl")) if osm_coords else None
    completion = (scout_m.get("completedYear") if scout_m.get("locationVerificationSourceUrl") else None) or prop.get("completedYear") or project.get("completedYear") or scout_m.get("completedYear") or manual_row.get("completedYear") or legacy_row.get("completedYear")
    if isinstance(completion, (int, float)) and 2400 <= completion <= 2700:
        completion -= 543
    fee = prop.get("fee") or project.get("fee") or manual_row.get("fee")
    if not fee and (scout_m.get("fee") or 0) > 0:
        fee = {"rate": scout_m["fee"], "status": "public", "note": "PropertyScout 專案頁公開管理費，請向管委會確認。", "source": scout_m.get("sourceUrl")}
    if isinstance(fee, (int, float)):
        fee = {"rate": fee}
    elif fee:
        fee = {k: fee[k] for k in ("rate", "status", "note", "source") if k in fee}

    area = prop.get("area") or project.get("area") or {}
    area_min = area.get("min") if isinstance(area, dict) else area
    area_max = area.get("max") if isinstance(area, dict) else area
    sale_rooms = (sale or {}).get("byBedroom") or {}
    rent_rooms = (rent or {}).get("byBedroom") or {}
    bed_prices = [sale_rooms.get(str(b), {}).get("minimum") for b in range(1, 5)]
    bed_areas = [sale_rooms.get(str(b), {}).get("minimumArea", sale_rooms.get(str(b), {}).get("area")) for b in range(1, 5)]
    bed_rents = [rent_rooms.get(str(b), {}).get("minimumSqm", rent_rooms.get(str(b), {}).get("averageSqm")) for b in range(1, 5)]
    default_sale, default_area, default_rent_rate = sale_rooms.get("2", {}), None, rent_rooms.get("2", {})
    sale_url = default_sale.get("minimumSourceUrl") or default_sale.get("sourceUrl")
    direct_url = bool(sale_url and re.search(r"/(?:ads|listings|property|property-for-sale|property-for-rent|property-rent|livingdetail_en)/", sale_url, re.I))
    if not direct_url and sale_url and "livinginsider.com/detail/condo-" in sale_url:
        direct_url = True
    if not direct_url and sale_url and "rentcondobkk.com/index.php/" in sale_url:
        direct_url = True
    if direct_url:
        default_area = default_sale.get("minimumArea") or default_sale.get("area")
    rent_rate = default_rent_rate.get("minimumSqm") or default_rent_rate.get("averageSqm") or 0
    fee_rate = (fee or {}).get("rate") or 0
    if not (float(default_sale.get("minimum") or 0) > 0 and float(default_area or 0) > 0 and float(rent_rate or 0) > 0):
        core_yield = None
    else:
        core_yield = round((float(rent_rate) * float(default_area) * 11 - float(fee_rate) * float(default_area) * 12) / float(default_sale["minimum"]) * 100, 5)
    overview.append([
        int(project["id"]), project.get("name"), lat if located else None, lng if located else None,
        bool(located), completion, prop.get("floors") or project.get("floors"), prop.get("units") or project.get("units"),
        area_min, area_max, (nearest or {}).get("stationId"), (nearest or {}).get("distanceKm"),
        (nearest or {}).get("straightDistanceKm"), (nearest or {}).get("minutes"),
        (sale or {}).get("minimum"), (sale or {}).get("minimumSqm"),
        (rent or {}).get("minimum"), (rent or {}).get("minimumSqm"), fee_rate,
        bed_prices, bed_areas, bed_rents, core_yield,
        bool((sale or {}).get("marketSummary") or (sale or {}).get("countKind") in ("propertyscout_market_summary", "matched_city_index")),
        bool((rent or {}).get("marketSummary") or (rent or {}).get("countKind") in ("propertyscout_market_summary", "matched_city_index")),
        index // 100,
    ])
    extras = {
        "sale": sale, "rent": rent, "fee": fee,
        "address": prop.get("address") or project.get("address"),
        "locationSourceUrl": source_url, "locationSourceName": source_name,
        "locationVerificationSourceUrl": verification_url,
        "completedYearSourceUrl": prop.get("completedYearSourceUrl") or (scout_m.get("sourceUrl") if scout_m.get("completedYear") else manual_row.get("completedYearSourceUrl") or project.get("completedYearSourceUrl") or legacy_row.get("completedYearSourceUrl")),
        "startedYear": prop.get("startedYear") or project.get("startedYear") or scout_m.get("startedYear") or legacy_row.get("startedYear"),
        "station": project.get("station") or prop.get("station") or legacy_row.get("station"),
        "hipflatSummary": prop.get("hipflatSummary") or project.get("hipflatSummary"),
        "hipflatProjectUrl": project.get("hipflatProjectUrl") or prop.get("hipflatProjectUrl"),
        "discoveryUrl": project.get("discoveryUrl"),
        "propertyHubProjectUrl": prop.get("propertyHubProjectUrl"),
        "propertyHubProjectId": prop.get("propertyHubProjectId"),
        "propertyHubSaleUrl": prop.get("propertyHubSaleUrl"), "propertyHubRentUrl": prop.get("propertyHubRentUrl"),
        "completedYear": completion, "floors": prop.get("floors") or project.get("floors"),
        "units": prop.get("units") or project.get("units"), "beds": prop.get("beds") or project.get("beds"),
        "area": area, "address": prop.get("address") or project.get("address"),
    }
    if manual_row:
        extras["manualMarket"] = manual_row
    if route:
        extras["walkRoute"] = route
    if crosschecks.get(pid):
        extras["marketCrosscheck"] = crosschecks[pid]
    if local.get(pid):
        extras["localListings"] = local[pid].get("listings", [])
    detail_rows.setdefault(str(index // 100), {})[pid] = extras

SHARDS.mkdir(parents=True, exist_ok=True)
for old in SHARDS.glob("*.json"):
    old.unlink()
for shard, rows in detail_rows.items():
    (SHARDS / f"{shard}.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
write_js(DIST / "bangkok-overview.js", "BANGKOK_CONDO_OVERVIEW", overview)
print(f"overview: {len(overview):,} rows, {(DIST / 'bangkok-overview.js').stat().st_size:,} bytes")
print(f"detail shards: {len(detail_rows):,}, {sum(p.stat().st_size for p in SHARDS.glob('*.json')):,} bytes")
