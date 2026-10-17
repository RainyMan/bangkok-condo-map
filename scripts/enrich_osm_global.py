"""Conservatively identify more Bangkok OSM building points using global name matches."""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from collections import defaultdict

import osmium

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
PBF = RESEARCH / "bangkok-latest.osm.pbf"
OUTPUT = DIST / "bangkok-osm.js"
BBOX = (13.4, 100.2, 14.1, 101.0)
STOP = {"condo", "condominium", "residence", "residences", "apartment", "apartments", "tower", "building", "bangkok", "the", "at", "by", "and", "park", "place", "project"}
ADDR_STOP = {"soi", "road", "rd", "street", "bangkok", "thailand", "province", "district", "subdistrict", "tambon", "khet", "kwaeng"}


def array(path: pathlib.Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def tokens(value: str, stop: set[str] = STOP) -> set[str]:
    return {part for part in norm(value).split() if (len(part) > 1 or part.isdigit()) and part not in stop}


def names(tags: osmium.osm.TagList) -> list[str]:
    return [tags.get(key) for key in ("name:en", "official_name:en", "name", "official_name", "alt_name", "short_name") if tags.get(key)]


def address(tags: osmium.osm.TagList) -> str:
    return " ".join(str(tags.get(key) or "") for key in (
        "addr:housenumber", "addr:unit", "addr:place", "addr:street", "addr:suburb",
        "addr:street:en", "addr:soi", "addr:housename", "addr:housename:en",
        "addr:quarter", "addr:subdistrict", "addr:subdistrict:en", "addr:district", "addr:district:en",
        "addr:city", "addr:province", "addr:province:en", "addr:postcode",
    ))


class NamedBangkokObjects(osmium.SimpleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict] = []

    def node(self, obj: osmium.osm.Node) -> None:
        self.add("node", obj.id, obj.location.lat, obj.location.lon, obj.tags)

    def way(self, obj: osmium.osm.Way) -> None:
        points = [(node.location.lat, node.location.lon) for node in obj.nodes if node.location.valid()]
        if points:
            self.add("way", obj.id, sum(x[0] for x in points) / len(points), sum(x[1] for x in points) / len(points), obj.tags)

    def add(self, kind: str, object_id: int, lat: float, lng: float, tags: osmium.osm.TagList) -> None:
        if not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lng <= BBOX[3]):
            return
        found_names = names(tags)
        found_address = address(tags)
        if found_names or len(tokens(found_address, ADDR_STOP)) >= 3:
            self.items.append({"type": kind, "id": object_id, "lat": lat, "lng": lng, "names": found_names, "address": found_address})


def main() -> int:
    projects = array(DIST / "bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    current = {int(row["id"]): row for row in array(OUTPUT, "BANGKOK_OSM_LOCATIONS")}
    used_objects = {(row.get("osmType"), int(row["osmId"])) for row in current.values() if row.get("osmType") and row.get("osmId")}
    known = set(current)
    hipflat_by_propertyhub: dict[str, set[int]] = defaultdict(set)
    for row in array(DIST / "bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS"):
        phid = row.get("propertyHubProjectId")
        if phid:
            hipflat_by_propertyhub[str(phid)].add(int(row["id"]))
    for filename, symbol in (
        ("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS"),
        ("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS"),
        ("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS"),
    ):
        for row in array(DIST / filename, symbol):
            pid = row.get("id") if filename == "bangkok-propertyhub.js" else row.get("hipflatProjectId")
            if pid and row.get("locationVerified"):
                known.add(int(pid))
            if filename == "bangkok-propertyhub-guessed-details.js" and row.get("locationVerified"):
                hipflat_by_propertyhub[str(row.get("propertyHubProjectId"))].add(int(row["hipflatProjectId"]))
    details = array(DIST / "bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")
    for row in details:
        if row.get("locationVerified"):
            known.update(hipflat_by_propertyhub.get(str(row.get("propertyHubProjectId")), set()))
    enrichment = RESEARCH / "propertyhub-enrichment.jsonl"
    if enrichment.exists():
        with enrichment.open(encoding="utf-8") as source:
            for line in source:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                pid = row.get("hipflatProjectId") or row.get("projectId") or row.get("id")
                if pid and row.get("locationVerified"):
                    known.add(int(pid))
    for filename, symbol in (("data.js", "CONDO_DATA"), ("catalogue.js", "CATALOGUE_PROJECTS"), ("huai-khwang.js", "HUAI_KHWANG_PROJECTS")):
        for row in array(DIST / filename, symbol):
            if row.get("locationVerified") and row.get("name"):
                legacy_names = {norm(row["name"])}
                known.update(int(p["id"]) for p in projects if norm(p["name"]) in legacy_names)
    targets = [p for p in projects if int(p["id"]) not in known]
    print(f"Unlocated candidate projects: {len(targets)}; reading Bangkok OSM extract", flush=True)
    handler = NamedBangkokObjects()
    handler.apply_file(str(PBF), locations=True)
    print(f"Named OSM objects: {len(handler.items)}", flush=True)

    by_token: dict[str, list[int]] = defaultdict(list)
    by_address_token: dict[str, list[int]] = defaultdict(list)
    object_sets = []
    for index, obj in enumerate(handler.items):
        obj["nameSets"] = [tokens(name) for name in obj["names"]]
        obj["addrTokens"] = tokens(obj["address"], ADDR_STOP)
        object_sets.append(set().union(*obj["nameSets"]))
        for token in object_sets[-1]:
            by_token[token].append(index)
        for token in obj["addrTokens"]:
            by_address_token[token].append(index)

    proposals: dict[int, list[tuple[float, int, float, float]]] = {}
    for project in targets:
        wanted = tokens(project["name"])
        if len(wanted) < 2:
            continue
        project_address = tokens(project.get("address", ""), ADDR_STOP)
        candidate_ids = {i for token in wanted for i in by_token.get(token, [])}
        scored = []
        for i in candidate_ids:
            obj = handler.items[i]
            if (obj["type"], int(obj["id"])) in used_objects:
                continue
            name_score = max((len(wanted & named) / max(len(wanted | named), 1) for named in obj["nameSets"]), default=0)
            if name_score < 0.62:
                continue
            shared = project_address & obj["addrTokens"]
            address_score = len(shared) / max(len(project_address), 1)
            if name_score < 0.82 and address_score < 0.25:
                continue
            score = name_score * 0.78 + address_score * 0.22
            scored.append((score, i, name_score, address_score))
        scored.sort(reverse=True)
        if not scored:
            continue
        top = scored[0]
        if len(scored) > 1 and top[0] - scored[1][0] < 0.12:
            continue
        if top[2] < 0.82 and top[3] < 0.4:
            continue
        proposals[int(project["id"])] = scored[:2]

    by_object: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for pid, scored in proposals.items():
        by_object[scored[0][1]].append((pid, scored[0][0]))
    accepted: dict[int, int] = {}
    for pid, scored in proposals.items():
        obj_index = scored[0][1]
        competing = sorted(by_object[obj_index], key=lambda pair: pair[1], reverse=True)
        if len(competing) > 1 and competing[0][0] == pid and competing[0][1] - competing[1][1] < 0.12:
            continue
        if len(competing) > 1 and competing[0][0] != pid:
            continue
        accepted[pid] = obj_index

    project_by_id = {int(p["id"]): p for p in projects}
    for pid, obj_index in accepted.items():
        obj = handler.items[obj_index]
        project = project_by_id[pid]
        wanted = tokens(project["name"])
        label = next((name for name in obj["names"] if tokens(name) == wanted or wanted <= tokens(name)), obj["names"][0] if obj["names"] else obj["address"] or "OSM address")
        matched = next(item for item in proposals[pid] if item[1] == obj_index)
        current[pid] = {"id": pid, "name": project["name"], "lat": obj["lat"], "lng": obj["lng"], "osmType": obj["type"], "osmId": obj["id"], "osmName": label, "osmAddress": obj["address"], "nameMatchScore": round(matched[2], 4), "addressMatchScore": round(matched[3], 4), "sourceUrl": f"https://www.openstreetmap.org/{obj['type']}/{obj['id']}"}
        used_objects.add((obj["type"], int(obj["id"])))
    OUTPUT.write_text("window.BANGKOK_OSM_LOCATIONS = " + json.dumps(list(current.values()), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"High-confidence global matches added: {len(accepted)}; OSM coordinates now {len(current)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
