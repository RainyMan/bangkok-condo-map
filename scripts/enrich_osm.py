"""Match named OpenStreetMap condo/building objects to Hipflat project names."""
from __future__ import annotations

import difflib
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
SOURCE = json.loads((ROOT / "dist/bangkok-catalogue.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
OSM = json.loads((RESEARCH / "osm-condo-objects.json").read_text(encoding="utf-8"))
STOP = {"condo", "condominium", "residence", "residences", "apartment", "apartments", "tower", "building", "bangkok", "the", "at", "by", "and", "park", "place", "project"}


def norm(value: str) -> str:
    s = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def tokens(value: str) -> set[str]:
    return {x for x in norm(value).split() if x not in STOP and len(x) > 1}


projects = SOURCE
objects = []
for e in OSM.get("elements", []):
    tags = e.get("tags", {})
    names = [tags.get(k) for k in ("name:en", "official_name:en", "name", "official_name", "alt_name", "short_name") if tags.get(k)]
    if not names:
        continue
    lat = e.get("lat", (e.get("center") or {}).get("lat"))
    lon = e.get("lon", (e.get("center") or {}).get("lon"))
    if not isinstance(lat, (float, int)) or not isinstance(lon, (float, int)):
        continue
    address = " ".join(str(tags.get(k, "")) for k in (
        "addr:street", "addr:place", "addr:suburb", "addr:district", "addr:city", "addr:province"
    ))
    objects.append({"type": e["type"], "id": e["id"], "lat": lat, "lng": lon, "names": names, "address": address})

by_token: dict[str, list[dict]] = {}
for obj in objects:
    obj["tokenSets"] = [tokens(name) for name in obj["names"]]
    for token in set.union(*obj["tokenSets"]):
        by_token.setdefault(token, []).append(obj)

locations = {}
ambiguous = 0
address_resolved = 0
for project in projects:
    project_tokens = tokens(project["name"])
    if len(project_tokens) < 2:
        continue
    pool = {id(obj): obj for token in project_tokens for obj in by_token.get(token, [])}
    candidates = []
    for obj in pool.values():
        matched_name = any(
            (project_tokens <= name_tokens and len(name_tokens - project_tokens) <= 2)
            or (name_tokens <= project_tokens and len(project_tokens - name_tokens) <= 1)
            for name_tokens in obj["tokenSets"]
        )
        if matched_name:
            candidates.append(obj)
    if len(candidates) == 1:
        locations[str(project["id"])] = candidates[0]
    elif len(candidates) > 1:
        project_address = tokens(project.get("address", "")) - {"soi", "road", "rd", "street", "bangkok", "thailand", "province", "district", "subdistrict", "tambon", "khet", "kwaeng"}
        ranked = sorted(
            ((len(project_address & (tokens(obj.get("address", "")) - {"soi", "road", "rd", "street", "bangkok", "thailand", "province", "district", "subdistrict", "tambon", "khet", "kwaeng"})), obj)
             for obj in candidates),
            key=lambda item: item[0], reverse=True,
        )
        if ranked[0][0] > 0 and (len(ranked) == 1 or ranked[0][0] > ranked[1][0]):
            locations[str(project["id"])] = ranked[0][1]
            address_resolved += 1
        else:
            ambiguous += 1

rows = []
for project in projects:
    obj = locations.get(str(project["id"]))
    if not obj:
        continue
    label = next((n for n in obj["names"] if tokens(n) == tokens(project["name"]) or tokens(project["name"]) <= tokens(n)), obj["names"][0])
    rows.append({"id": project["id"], "name": project["name"], "lat": obj["lat"], "lng": obj["lng"], "osmType": obj["type"], "osmId": obj["id"], "osmName": label, "sourceUrl": f"https://www.openstreetmap.org/{obj['type']}/{obj['id']}"})

out = ROOT / "dist/bangkok-osm.js"
out.write_text("window.BANGKOK_OSM_LOCATIONS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(json.dumps({"objects": len(objects), "matchedProjects": len(rows), "addressResolved": address_resolved, "ambiguous": ambiguous, "output": str(out)}, ensure_ascii=False))
