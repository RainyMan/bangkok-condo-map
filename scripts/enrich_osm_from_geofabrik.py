"""Match named or address-tagged Bangkok OSM objects from a BBBike extract."""
from __future__ import annotations

import concurrent.futures
import json
import pathlib
import re
import time
import unicodedata

import osmium
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
PBF = RESEARCH / "bangkok-latest.osm.pbf"
LOG = RESEARCH / "geofabrik-osm-progress.log"
URL = "https://download.bbbike.org/osm/bbbike/Bangkok/Bangkok.osm.pbf"
BBOX = (13.4, 100.2, 14.1, 101.0)
STOP = {"condo", "condominium", "residence", "residences", "apartment", "apartments", "tower", "building", "bangkok", "the", "at", "by", "and", "park", "place", "project"}


def report(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as log:
        log.write(line + "\n")


def download() -> None:
    if PBF.exists() and PBF.stat().st_size > 30_000_000:
        return
    temporary = PBF.with_suffix(".pbf.part")
    with requests.get(URL, stream=True, timeout=(20, 120), headers={"User-Agent": "BangkokCondoMapResearch/1.0 OSM extract processing"}) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length") or 0)
        done = 0
        with temporary.open("wb") as output:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    output.write(chunk)
                    done += len(chunk)
                    if done // 25_000_000 != (done - len(chunk)) // 25_000_000:
                        report(f"Downloaded {done // 1_000_000} MB of {total // 1_000_000 if total else 'unknown'} MB")
    temporary.replace(PBF)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def tokens(value: str) -> set[str]:
    return {item for item in norm(value).split() if (len(item) > 1 or item.isdigit() or item in {"q", "i", "m", "s"}) and item not in STOP}


def names(tags: osmium.osm.TagList) -> list[str]:
    return [tags.get(key) for key in ("name:en", "official_name:en", "name", "official_name", "alt_name", "short_name") if tags.get(key)]


def address(tags: osmium.osm.TagList) -> str:
    return " ".join(str(tags.get(key) or "") for key in (
        "addr:housenumber", "addr:unit", "addr:place", "addr:street", "addr:suburb",
        "addr:street:en", "addr:soi", "addr:housename", "addr:housename:en",
        "addr:quarter", "addr:subdistrict", "addr:subdistrict:en", "addr:district", "addr:district:en",
        "addr:city", "addr:province", "addr:province:en", "addr:postcode",
    ))


class BangkokObjects(osmium.SimpleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict] = []

    def node(self, obj: osmium.osm.Node) -> None:
        self.add("node", obj.id, obj.location.lat, obj.location.lon, obj.tags)

    def way(self, obj: osmium.osm.Way) -> None:
        points = [(node.location.lat, node.location.lon) for node in obj.nodes if node.location.valid()]
        if not points:
            return
        self.add("way", obj.id, sum(point[0] for point in points) / len(points), sum(point[1] for point in points) / len(points), obj.tags)

    def add(self, kind: str, object_id: int, lat: float, lng: float, tags: osmium.osm.TagList) -> None:
        if not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lng <= BBOX[3]):
            return
        found_names = names(tags)
        found_address = address(tags)
        if not found_names and len(tokens(found_address)) < 3:
            return
        self.items.append({"type": kind, "id": object_id, "lat": lat, "lng": lng, "names": found_names, "address": found_address})


def js_array(path: pathlib.Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def main() -> int:
    RESEARCH.mkdir(parents=True, exist_ok=True)
    download()
    report(f"Downloaded extract ready ({PBF.stat().st_size // 1_000_000} MB); collecting named/address-tagged objects in Bangkok")
    handler = BangkokObjects()
    handler.apply_file(str(PBF), locations=True)
    report(f"Collected {len(handler.items)} named or address-tagged OSM nodes and building ways in Bangkok bounds")

    projects = js_array(DIST / "bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    previous = {int(row["id"]): row for row in js_array(DIST / "bangkok-osm.js", "BANGKOK_OSM_LOCATIONS")}
    used_objects = {(row.get("osmType"), int(row["osmId"])) for row in previous.values() if row.get("osmType") and row.get("osmId")}
    object_tokens = []
    by_token: dict[str, list[int]] = {}
    by_address_token: dict[str, list[int]] = {}
    for index, obj in enumerate(handler.items):
        obj["tokenSets"] = [tokens(name) for name in obj["names"]]
        for token in set().union(*obj["tokenSets"]):
            by_token.setdefault(token, []).append(index)
        obj["addressTokens"] = tokens(obj.get("address", ""))
        for token in obj["addressTokens"]:
            by_address_token.setdefault(token, []).append(index)

    ambiguous = 0
    address_resolved = 0
    added = 0
    ignore_address = {"soi", "road", "rd", "street", "bangkok", "thailand", "province", "district", "subdistrict", "tambon", "khet", "kwaeng"}
    for project in projects:
        project_id = int(project["id"])
        if project_id in previous:
            continue
        wanted = tokens(project["name"])
        if len(wanted) < 2:
            continue
        candidates = set(index for token in wanted for index in by_token.get(token, []))
        matched = []
        for index in candidates:
            obj = handler.items[index]
            if (obj["type"], int(obj["id"])) in used_objects:
                continue
            best_name_score = max((len(wanted & named) / max(1, len(wanted | named)) for named in obj["tokenSets"]), default=0)
            best_overlap = max((len(wanted & named) for named in obj["tokenSets"]), default=0)
            if best_name_score >= 0.8 and best_overlap >= 2:
                matched.append((best_name_score, obj))
        if len(matched) == 1:
            obj = matched[0][1]
        elif len(matched) > 1:
            project_address = tokens(project.get("address", "")) - ignore_address
            ranked = sorted(((len(project_address & (tokens(obj.get("address", "")) - ignore_address)), obj) for _, obj in matched), key=lambda pair: pair[0], reverse=True)
            if ranked[0][0] > 0 and (len(ranked) == 1 or ranked[0][0] > ranked[1][0]):
                obj = ranked[0][1]
                address_resolved += 1
            else:
                obj = None
        else:
            obj = None
        if obj is None:
            ambiguous += 1
            continue
        label = next((name for name in obj["names"] if tokens(name) == wanted or wanted <= tokens(name)), None) or (obj["names"][0] if obj["names"] else obj["address"])
        previous[project_id] = {"id": project_id, "name": project["name"], "lat": obj["lat"], "lng": obj["lng"], "osmType": obj["type"], "osmId": obj["id"], "osmName": label,
                                "sourceUrl": f"https://www.openstreetmap.org/{obj['type']}/{obj['id']}", "sourceExtractUrl": URL}
        used_objects.add((obj["type"], int(obj["id"])))
        added += 1
    output = DIST / "bangkok-osm.js"
    output.write_text("window.BANGKOK_OSM_LOCATIONS = " + json.dumps(list(previous.values()), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    report(f"Added {added} uniquely matched coordinates; address disambiguations {address_resolved}; ambiguous names held back {ambiguous}; total verified OSM matches {len(previous)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
