"""Match Hipflat condo addresses to exact OSM building/address records.

Only accepts a unique physical location with the same house number, at least
one distinctive street/Soi token, and a matching postcode or district token.
Ambiguous and partial-address candidates are left unresolved.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys
import unicodedata
from collections import defaultdict

import osmium

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PBF = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok\bangkok-latest.osm.pbf")
ADDRESS_CACHE = PBF.with_name("osm-address-objects.jsonl")
REVIEW_OUTPUT = PBF.with_name("osm-address-review.json")
OUTPUT = DIST / "bangkok-osm.js"
STOP = {"road", "rd", "street", "soi", "roadway", "thailand", "thai", "bangkok", "bkk"}


def arr(path: pathlib.Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def tokens(value: str) -> set[str]:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return {part for part in re.sub(r"[^a-z0-9]+", " ", value).split() if part not in STOP and (len(part) > 1 or part.isdigit())}


def normalize_name(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def house_number(value: str) -> str | None:
    match = re.search(r"(?<![a-z0-9])(\d+[a-z]?(?:/\d+[a-z]?)?)(?![a-z0-9])", value.lower())
    return match.group(1) if match else None


def project_addr(project: dict) -> dict:
    raw = str(project.get("address") or "")
    parts = [part.strip() for part in raw.split(",")]
    return {
        "raw": raw,
        "house": house_number(parts[0] if parts else raw),
        "street": tokens(" ".join(parts[:3])),
        "admin": tokens(" ".join(parts[-4:])),
        "postcode": next((m.group(0) for m in re.finditer(r"\b\d{5}\b", raw)), None),
    }


class AddressObjects(osmium.SimpleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict] = []

    def node(self, obj: osmium.osm.Node) -> None:
        if obj.location.valid():
            self.add("node", obj.id, obj.location.lat, obj.location.lon, obj.tags)

    def way(self, obj: osmium.osm.Way) -> None:
        points = [(node.location.lat, node.location.lon) for node in obj.nodes if node.location.valid()]
        if points:
            self.add("way", obj.id, sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points), obj.tags)

    def add(self, kind: str, oid: int, lat: float, lng: float, tags: osmium.osm.TagList) -> None:
        values = {key: str(tags.get(key) or "") for key in (
            "addr:housenumber", "addr:street", "addr:street:en", "addr:soi", "addr:place",
            "addr:district", "addr:district:en", "addr:subdistrict", "addr:subdistrict:en",
            "addr:postcode", "addr:housename", "addr:housename:en", "name", "name:en", "building",
        )}
        if not (values["addr:housenumber"] or values["addr:street"] or values["addr:soi"] or values["addr:place"]):
            return
        self.items.append({"type": kind, "id": int(oid), "lat": lat, "lng": lng, **values})


def main() -> None:
    projects = arr(DIST / "bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    current = {int(row["id"]): row for row in arr(OUTPUT, "BANGKOK_OSM_LOCATIONS")}
    located = set(current)
    verified = {int(row["hipflatId"]): row for row in arr(DIST / "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")}
    propertyscout = {int(row["hipflatId"]): row for row in arr(DIST / "bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS")}
    located.update(pid for pid, row in verified.items() if row.get("locationVerified"))
    located.update(pid for pid, row in propertyscout.items() if row.get("locationVerified") and row.get("lat") is not None and row.get("lng") is not None)
    legacy_rows = []
    for filename, symbol in (("data.js", "CONDO_DATA"), ("catalogue.js", "CATALOGUE_PROJECTS"), ("huai-khwang.js", "HUAI_KHWANG_PROJECTS")):
        legacy_rows.extend(arr(DIST / filename, symbol))
    legacy_verified_names = {normalize_name(row.get("name", "")) for row in legacy_rows
                             if row.get("locationVerified") and row.get("lat") is not None and row.get("lng") is not None}
    ph = {int(row["id"]): row for row in arr(DIST / "bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")}
    details = {str(row.get("propertyHubProjectId")): row for row in arr(DIST / "bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")}
    guessed = {int(row["hipflatProjectId"]): row for row in arr(DIST / "bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS") if row.get("locationVerified")}
    for project in projects:
        pid = int(project["id"])
        base = ph.get(pid) or {}
        detail = details.get(str(base.get("propertyHubProjectId") or "")) or {}
        if (base.get("locationVerified") or detail.get("locationVerified") or pid in guessed or project.get("locationVerified")
                or normalize_name(project.get("name", "")) in legacy_verified_names):
            located.add(pid)

    if ADDRESS_CACHE.exists():
        with ADDRESS_CACHE.open(encoding="utf-8") as source:
            address_items = [json.loads(line) for line in source if line.strip()]
    else:
        handler = AddressObjects()
        handler.apply_file(str(PBF), locations=True)
        address_items = handler.items
        with ADDRESS_CACHE.open("w", encoding="utf-8") as output:
            for row in address_items:
                output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"OSM address objects: {len(address_items)}; unlocated projects: {len(projects) - len(located)}", flush=True)
    by_house: dict[str, list[dict]] = defaultdict(list)
    for obj in address_items:
        number = house_number(obj.get("addr:housenumber", ""))
        if number:
            by_house[number].append(obj)

    accepted = []
    review = []
    for project in projects:
        pid = int(project["id"])
        if pid in located:
            continue
        pa = project_addr(project)
        if not pa["house"] or len(pa["street"]) < 1 or (not pa["postcode"] and not pa["admin"]):
            continue
        candidates = []
        for obj in by_house.get(pa["house"], []):
            osm_street = tokens(" ".join(obj.get(k, "") for k in ("addr:street", "addr:street:en", "addr:soi", "addr:place")))
            street_overlap = pa["street"] & osm_street
            distinctive_street_overlap = {token for token in street_overlap if token.isalpha()}
            if not distinctive_street_overlap:
                continue
            osm_admin = tokens(" ".join(obj.get(k, "") for k in ("addr:district", "addr:district:en", "addr:subdistrict", "addr:subdistrict:en")))
            postcode_match = bool(pa["postcode"] and pa["postcode"] == obj.get("addr:postcode"))
            admin_match = bool(pa["admin"] & osm_admin)
            if not (postcode_match or admin_match):
                continue
            project_name = tokens(project.get("name", ""))
            object_name = tokens(" ".join(obj.get(k, "") for k in ("name", "name:en", "addr:housename", "addr:housename:en")))
            name_overlap = project_name & object_name
            # House number + a citywide road name can still land on a nearby
            # business. Require a distinctive condo-name match as well.
            if not (any(len(token) >= 6 for token in name_overlap) or len(name_overlap) >= 2):
                continue
            candidates.append((obj, len(street_overlap), postcode_match, admin_match))
        # Address points and the building footprint often duplicate a single
        # physical address. Collapse only objects within 20 m, then select a
        # building polygon, otherwise the address point.
        groups: list[list[tuple[dict, int, bool, bool]]] = []
        for candidate in candidates:
            obj = candidate[0]
            group = next((g for g in groups if math.hypot((g[0][0]["lat"] - obj["lat"]) * 111_000, (g[0][0]["lng"] - obj["lng"]) * 108_000) <= 20), None)
            if group is None:
                groups.append([candidate])
            else:
                group.append(candidate)
        if len(groups) != 1:
            if candidates:
                review.append({"id": pid, "name": project["name"], "candidateCount": len(candidates), "siteCount": len(groups)})
            continue
        group = groups[0]
        best = max(group, key=lambda item: (item[2], item[3], item[1], item[0]["type"] == "way" and bool(item[0].get("building"))))
        obj, street_hits, postcode_match, admin_match = best
        street_evidence = sorted(token for token in pa["street"] & tokens(" ".join(obj.get(k, "") for k in ("addr:street", "addr:street:en", "addr:soi", "addr:place"))) if token.isalpha())
        if not street_evidence or not (postcode_match or admin_match):
            continue
        row = {"id": pid, "name": project["name"], "lat": obj["lat"], "lng": obj["lng"], "osmType": obj["type"], "osmId": obj["id"],
               "osmName": obj.get("name:en") or obj.get("name") or obj.get("addr:housename:en") or obj.get("addr:housename") or "Exact address match",
               "sourceUrl": f"https://www.openstreetmap.org/{obj['type']}/{obj['id']}", "sourceExtractUrl": "https://download.bbbike.org/osm/bbbike/Bangkok/Bangkok.osm.pbf",
               "matchEvidence": {"houseNumber": pa["house"], "streetTokens": street_evidence, "postcodeMatch": postcode_match, "administrativeAreaMatch": admin_match}}
        accepted.append(row)

    report = {"addressCandidatesRequireManualConfirmation": len(accepted), "ambiguousCandidates": len(review), "candidates": accepted, "ambiguous": review}
    REVIEW_OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"addressCandidatesRequireManualConfirmation": len(accepted), "ambiguousCandidates": len(review), "examples": accepted[:15], "reviewExamples": review[:10]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
