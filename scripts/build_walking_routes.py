"""Calculate walking-network distance to the nearest rapid-transit station."""
from __future__ import annotations

import json
import argparse
import pathlib
import re
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
CATALOGUE = ROOT / "dist/bangkok-catalogue.js"
OSM = ROOT / "dist/bangkok-osm.js"
PROPERTYHUB = ROOT / "dist/bangkok-propertyhub.js"
PROPERTYHUB_DETAILS = ROOT / "dist/bangkok-propertyhub-details.js"
PROPERTYHUB_GUESSED_DETAILS = ROOT / "dist/bangkok-propertyhub-guessed-details.js"
STATIONS = ROOT / "dist/stations.js"
CACHE = RESEARCH / "walking-route-matrix.jsonl"
OUTPUT = ROOT / "dist/bangkok-walk-routes.js"
API = "https://valhalla1.openstreetmap.de/sources_to_targets"


def js_array(path: pathlib.Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def write_output(rows: dict[int, dict]) -> None:
    OUTPUT.write_text("window.BANGKOK_WALK_ROUTES = " + json.dumps(list(rows.values()), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-ids", help="Optional UTF-8 text file containing project IDs that must be recalculated")
    args = parser.parse_args()
    projects = js_array(CATALOGUE, "BANGKOK_HIPFLAT_PROJECTS")
    osm = {int(x["id"]): x for x in js_array(OSM, "BANGKOK_OSM_LOCATIONS")}
    propertyhub = {int(x["id"]): x for x in js_array(PROPERTYHUB, "BANGKOK_PROPERTYHUB_PROJECTS")}
    detail_rows = js_array(PROPERTYHUB_DETAILS, "BANGKOK_PROPERTYHUB_DETAILS") if PROPERTYHUB_DETAILS.exists() else []
    details = {str(x["propertyHubProjectId"]): x for x in detail_rows if x.get("propertyHubProjectId")}
    guessed_rows = js_array(PROPERTYHUB_GUESSED_DETAILS, "BANGKOK_PROPERTYHUB_GUESSED_DETAILS") if PROPERTYHUB_GUESSED_DETAILS.exists() else []
    guessed = {int(x["hipflatProjectId"]): x for x in guessed_rows if x.get("hipflatProjectId") and x.get("locationVerified")}
    stations = js_array(STATIONS, "MRT_STATIONS")
    cache: dict[int, dict] = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                cache[int(item["id"])] = item
            except (ValueError, KeyError, TypeError):
                continue
    ph_cache = RESEARCH / "propertyhub-enrichment.jsonl"
    ph: dict[int, dict] = {}
    if ph_cache.exists():
        for line in ph_cache.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                ph[int(item["id"])] = item
            except (ValueError, KeyError, TypeError):
                continue
    refresh_ids = set()
    if args.refresh_ids:
        refresh_ids = {int(value) for value in pathlib.Path(args.refresh_ids).read_text(encoding="utf-8").split() if value.isdigit()}
    coords = []
    for project in projects:
        pid = int(project["id"])
        enriched = ph.get(pid) or {}
        market = propertyhub.get(pid) or {}
        project_detail = details.get(str(market.get("propertyHubProjectId") or "")) or {}
        point = enriched if enriched.get("locationVerified") else project_detail if project_detail.get("locationVerified") else guessed.get(pid) if guessed.get(pid) else project if project.get("locationVerified") else osm.get(pid)
        if not point:
            continue
        lat, lon = point.get("lat"), point.get("lng")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            coords.append({"id": pid, "name": project["name"], "lat": lat, "lon": lon})
    todo = [point for point in coords if point["id"] not in cache or point["id"] in refresh_ids]
    print(f"Verified coordinates: {len(coords)}; routes cached: {len(cache)}; forced refresh: {len(refresh_ids)}; pending: {len(todo)}", flush=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "BangkokCondoMapResearch/1.0 (OSM walking distance research)"})
    with CACHE.open("a", encoding="utf-8") as out:
        # Valhalla limits the combined number of source and target locations to 100.
        batch_start = 0
        while batch_start < len(todo):
            batch = todo[batch_start:batch_start + 2]
            nearby_by_project = [sorted(
                stations,
                key=lambda station: (station["lat"] - project["lat"]) ** 2 * 12300 + (station["lng"] - project["lon"]) ** 2 * 9000,
            )[:30] for project in batch]
            target_by_id = {station["id"]: station for nearby in nearby_by_project for station in nearby}
            # Valhalla limits a matrix response to 100 source-target pairs.
            if len(batch) * len(target_by_id) > 100:
                batch = batch[:1]
                nearby_by_project = nearby_by_project[:1]
                target_by_id = {station["id"]: station for station in nearby_by_project[0]}
            targets = list(target_by_id.values())
            body = {
                "sources": [{"lat": project["lat"], "lon": project["lon"]} for project in batch],
                "targets": [{"lat": station["lat"], "lon": station["lng"]} for station in targets],
                "costing": "pedestrian",
                "units": "kilometers",
            }
            response = None
            for attempt in range(3):
                try:
                    response = session.post(API, json=body, timeout=(10, 45))
                    if response.status_code == 429 or response.status_code >= 500:
                        time.sleep(3 * (attempt + 1))
                        continue
                    response.raise_for_status()
                    break
                except requests.RequestException:
                    time.sleep(2 * (attempt + 1))
            matrix = response.json().get("sources_to_targets", []) if response and response.ok else []
            if matrix:
                for source_index, project in enumerate(batch):
                    candidate_ids = {station["id"] for station in nearby_by_project[source_index]}
                    distances = matrix[source_index] if source_index < len(matrix) else []
                    options = [
                        {"distanceKm": result.get("distance"), "minutes": max(1, round(result.get("time", 0) / 60)), "stationId": targets[i]["id"]}
                        for i, result in enumerate(distances)
                        if targets[i]["id"] in candidate_ids and result and isinstance(result.get("distance"), (int, float))
                    ]
                    if options:
                        route = min(options, key=lambda x: x["distanceKm"])
                        row = {"id": project["id"], "name": project["name"], "originLat": project["lat"], "originLng": project["lon"], **route, "source": "Valhalla pedestrian routing (30 nearest stations checked)", "sourceUrl": "https://valhalla1.openstreetmap.de/", "networkSourceUrl": "https://www.openstreetmap.org/copyright", "asOf": time.strftime("%Y-%m-%d")}
                        cache[project["id"]] = row
                        out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            elif response is not None:
                print(f"Route batch failed ({response.status_code}); {len(batch)} origins remain pending", flush=True)
            out.flush()
            batch_start += len(batch)
            offset = min(batch_start, len(todo))
            if offset % 50 < 2 or offset == len(todo):
                write_output(cache)
                print(f"{offset}/{len(todo)} route origins; completed {len(cache)}", flush=True)
            time.sleep(1.05)
    write_output(cache)
    print(f"Wrote {OUTPUT}; {len(cache)} route records", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

