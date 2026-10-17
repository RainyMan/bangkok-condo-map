"""Add uniquely name-matched Bangkok condo points from the local OSM extract.

This deliberately accepts exact normalized project-name matches only. Fuzzy
matches belong in a separate review queue and must not become map coordinates.
"""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
SOURCE = RESEARCH / "osm-condo-objects.json"
OUTPUT = DIST / "bangkok-osm.js"
GENERIC = {"condo", "condominium", "residence", "residences", "apartment", "apartments", "the", "at", "by", "project", "building"}


def array(path: pathlib.Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def tokens(value: str) -> tuple[str, ...]:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return tuple(sorted(token for token in re.sub(r"[^a-z0-9]+", " ", value).split() if len(token) > 1 and token not in GENERIC))


def district(value: str) -> str | None:
    normalized = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    districts = (
        "huai khwang", "watthana", "vadhana", "khlong toei", "ratchathewi", "sathon", "bang na",
        "lat phrao", "chatuchak", "din daeng", "phaya thai", "bang kapi", "suan luang", "phra khanong",
        "bang rak", "pathum wan", "prawet", "min buri", "nonthaburi",
    )
    for name in sorted(districts, key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}\b", normalized):
            return "watthana" if name == "vadhana" else name
    return None


def has_verified_coords(row: dict | None) -> bool:
    return bool(row and row.get("locationVerified") and isinstance(row.get("lat"), (int, float)) and isinstance(row.get("lng"), (int, float)))


def main() -> None:
    projects = array(DIST / "bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    current = {int(row["id"]): row for row in array(OUTPUT, "BANGKOK_OSM_LOCATIONS")}
    propertyhub = {int(row["id"]): row for row in array(DIST / "bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")}
    details = {str(row.get("propertyHubProjectId")): row for row in array(DIST / "bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")}
    guessed = {int(row["hipflatProjectId"]): row for row in array(DIST / "bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")}
    legacy_rows = (
        array(DIST / "data.js", "CONDO_DATA")
        + array(DIST / "catalogue.js", "CATALOGUE_PROJECTS")
        + array(DIST / "huai-khwang.js", "HUAI_KHWANG_PROJECTS")
    )
    legacy_by_name: dict[str, list[dict]] = defaultdict(list)
    for row in legacy_rows:
        normalized_name = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(row.get("name", "")).lower())).strip()
        legacy_by_name[normalized_name].append(row)

    located: set[int] = set(current)
    for project in projects:
        project_id = int(project["id"])
        base = propertyhub.get(project_id, {})
        detail = details.get(str(base.get("propertyHubProjectId") or ""), {})
        normalized_name = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(project.get("name", "")).lower())).strip()
        legacy_matches = legacy_by_name.get(normalized_name, [])
        legacy = legacy_matches[0] if len(legacy_matches) == 1 else {}
        if (has_verified_coords(project) or has_verified_coords(base) or has_verified_coords(detail)
                or has_verified_coords(guessed.get(project_id)) or has_verified_coords(legacy)):
            located.add(project_id)

    osm = json.loads(SOURCE.read_text(encoding="utf-8"))
    objects: list[dict] = []
    by_name: dict[tuple[str, ...], dict[tuple[str, int], dict]] = defaultdict(dict)
    for element in osm.get("elements", []):
        tags = element.get("tags", {})
        names = [tags.get(key) for key in ("name:en", "official_name:en", "name", "official_name", "alt_name", "short_name") if tags.get(key)]
        lat = element.get("lat", (element.get("center") or {}).get("lat"))
        lng = element.get("lon", (element.get("center") or {}).get("lon"))
        if not names or not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            continue
        obj = {"type": element["type"], "id": int(element["id"]), "lat": lat, "lng": lng, "names": names, "tags": tags}
        objects.append(obj)
        for name in names:
            key = tokens(name)
            if len(key) >= 2:
                by_name[key][(obj["type"], obj["id"])] = obj

    used_objects = {(row.get("osmType"), int(row["osmId"])) for row in current.values() if row.get("osmType") and row.get("osmId")}
    project_by_name: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for project in projects:
        project_id = int(project["id"])
        key = tokens(project.get("name", ""))
        if project_id not in located and len(key) >= 2:
            project_by_name[key].append(project)

    added = []
    ambiguous = 0
    district_conflicts = 0
    for key, matching_projects in project_by_name.items():
        if len(matching_projects) != 1:
            ambiguous += len(matching_projects)
            continue
        candidates = [obj for obj_key, obj in by_name.get(key, {}).items() if obj_key not in used_objects]
        if len(candidates) != 1:
            if candidates:
                ambiguous += 1
            continue
        project = matching_projects[0]
        obj = candidates[0]
        project_district = district(project.get("address", ""))
        object_address = " ".join(str(obj["tags"].get(tag, "")) for tag in ("addr:district", "addr:suburb", "addr:city", "addr:street", "addr:place"))
        object_district = district(object_address)
        if project_district and object_district and project_district != object_district:
            district_conflicts += 1
            continue
        name = next((name for name in obj["names"] if tokens(name) == key), obj["names"][0])
        row = {
            "id": int(project["id"]), "name": project["name"], "lat": obj["lat"], "lng": obj["lng"],
            "osmType": obj["type"], "osmId": obj["id"], "osmName": name,
            "sourceUrl": f"https://www.openstreetmap.org/{obj['type']}/{obj['id']}",
            "sourceExtractUrl": "https://download.bbbike.org/osm/bbbike/Bangkok/Bangkok.osm.pbf",
        }
        current[int(project["id"])] = row
        used_objects.add((obj["type"], obj["id"]))
        added.append(row)

    rows = sorted(current.values(), key=lambda row: int(row["id"]))
    OUTPUT.write_text("window.BANGKOK_OSM_LOCATIONS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(json.dumps({"namedOsmObjects": len(objects), "verifiedOsmLocations": len(rows), "newlyAdded": len(added), "ambiguousHeld": ambiguous, "districtConflictsHeld": district_conflicts, "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
