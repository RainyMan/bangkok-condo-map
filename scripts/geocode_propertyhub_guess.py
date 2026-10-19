"""Resolve unlinked Hipflat projects through exact PropertyHub project pages."""
from __future__ import annotations

import concurrent.futures
import html
import json
import math
import pathlib
import re
import threading
import time
from datetime import date
from typing import Any

import requests
from audit_propertyhub_city_listings import district as propertyhub_district

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
CATALOGUE = DIST / "bangkok-catalogue.js"
PROPERTYHUB = DIST / "bangkok-propertyhub.js"
DETAILS = DIST / "bangkok-propertyhub-details.js"
OSM = DIST / "bangkok-osm.js"
OUTPUT = DIST / "bangkok-propertyhub-guessed-details.js"
CACHE = RESEARCH / "propertyhub-guessed-project-details.jsonl"
LOG = RESEARCH / "propertyhub-guessed-project-details.log"
BASE = "https://propertyhub.in.th"
HEADERS = {"User-Agent": "BangkokCondoMapResearch/1.0 (public project page research)", "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en,th;q=0.8"}
LOCK = threading.Lock()
STOP = {"condo", "condominium", "apartment", "apartments", "residence", "residences", "project", "bangkok", "the", "at", "by", "and", "tower", "building"}


def read_array(path: pathlib.Path, symbol: str) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def tokens(value: Any) -> set[str]:
    value = html.unescape(str(value or "")).lower().replace("&", " and ")
    return {x for x in re.sub(r"[^a-z0-9]+", " ", value).split() if len(x) > 1 and x not in STOP}


def slugify(value: str) -> str:
    value = html.unescape(value).lower().replace("&", " and ").replace("@", " ").replace("'", "")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value)).strip("-")


def find_project(page: str) -> dict[str, Any] | None:
    for match in re.finditer(r"<script[^>]*>(.*?)</script>", page, re.S):
        body = match.group(1)
        if "projectInfo" not in body or "__next_f.push" not in body:
            continue
        chunk = re.search(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)', body, re.S)
        if not chunk:
            continue
        try:
            decoded = json.loads(chunk.group(1))
            payload = json.loads(decoded.split(":", 1)[1])
        except (ValueError, IndexError):
            continue
        stack = [payload]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if "projectInfo" in item and "location" in item and (item.get("nameEnglish") or item.get("name")):
                    return item
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return None


def exact_name_match(target_id: int, source_name: str, found_name: str, projects: list[dict[str, Any]]) -> bool:
    wanted = tokens(source_name)
    actual = tokens(found_name)
    if len(wanted) < 2 or len(actual) < 2:
        return False
    union = wanted | actual
    score = len(wanted & actual) / len(union)
    if score < 0.80:
        return False
    top = []
    for project in projects:
        project_tokens = tokens(project.get("name"))
        if len(project_tokens) < 2:
            continue
        candidate_score = len(project_tokens & actual) / len(project_tokens | actual)
        if candidate_score >= score - 0.02:
            top.append((candidate_score, int(project["id"])))
    best = max((item[0] for item in top), default=0)
    winners = {project_id for candidate_score, project_id in top if abs(candidate_score - best) < 0.015}
    return target_id in winners and len(winners) == 1


def fetch(row: dict[str, Any], projects: list[dict[str, Any]]) -> dict[str, Any]:
    slug = slugify(row["name"])
    page_url = f"{BASE}/en/projects/{slug}"
    for attempt in range(2):
        try:
            response = requests.get(page_url, headers=HEADERS, timeout=(8, 25))
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            if response.status_code != 200:
                return {"hipflatProjectId": int(row["id"]), "name": row["name"], "status": f"http_{response.status_code}"}
            project = find_project(response.text)
            if not project:
                return {"hipflatProjectId": int(row["id"]), "name": row["name"], "status": "project_data_missing"}
            found_name = project.get("nameEnglish") or project.get("name") or ""
            if not exact_name_match(int(row["id"]), row["name"], found_name, projects):
                return {"hipflatProjectId": int(row["id"]), "name": row["name"], "status": "name_not_unique"}
            point = project.get("location") or {}
            try:
                lat, lng = float(point.get("lat")), float(point.get("lng"))
            except (TypeError, ValueError):
                lat = lng = None
            if lat is None or lng is None or not (math.isfinite(lat) and math.isfinite(lng) and 13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0):
                return {"hipflatProjectId": int(row["id"]), "name": row["name"], "status": "coordinates_outside_bangkok"}
            info = project.get("projectInfo") or {}
            result: dict[str, Any] = {"hipflatProjectId": int(row["id"]), "propertyHubProjectId": str(project.get("id") or ""),
                "name": row["name"], "projectName": found_name, "projectSlug": project.get("slug") or slug,
                "projectAddress": project.get("address"), "lat": lat, "lng": lng, "locationVerified": True,
                "locationSourceName": "PropertyHub 精確樓盤頁", "locationSourceUrl": page_url,
                "completedYearSourceUrl": page_url, "asOf": date.today().isoformat()}
            if str(info.get("completedYear", "")).isdigit():
                result["completedYear"] = int(info["completedYear"])
            if str(info.get("totalUnits", "")).isdigit():
                result["units"] = int(info["totalUnits"])
            if str(info.get("buildingsFloors", "")).isdigit():
                result["floors"] = int(info["buildingsFloors"])
            fee_match = re.search(r"(\d+(?:\.\d+)?)", str(info.get("utilityFee") or ""))
            if fee_match and 1 <= float(fee_match.group(1)) <= 1000:
                result["fee"] = {"rate": float(fee_match.group(1)), "note": "PropertyHub 專案頁公布的管理費數值；以泰國公寓常見單位解讀，現行費率請向管委會確認。",
                                 "source": page_url, "status": "published_indicative"}
            return result
        except (requests.RequestException, json.JSONDecodeError):
            if attempt == 0:
                time.sleep(2)
    return {"hipflatProjectId": int(row["id"]), "name": row["name"], "status": "request_failed"}


def write_output(rows: list[dict[str, Any]]) -> None:
    # Retain coordinates verified by earlier research passes. This runner only
    # checks projects that have no linked PropertyHub project ID, so replacing
    # its output with this run's cache would silently discard other verified
    # project-page matches that are not in the current cache.
    if OUTPUT.exists():
        try:
            previous = read_array(OUTPUT, "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
        except (OSError, ValueError, json.JSONDecodeError):
            previous = []
        by_id = {int(row["hipflatProjectId"]): row for row in previous
                 if row.get("locationVerified") and row.get("lat") is not None and row.get("lng") is not None}
        # Preserve every previously reviewed coordinate. This runner uses a
        # unique project-name match to discover candidates, but that alone can
        # still match a same-name project in a different district. New results
        # fill gaps only; replacing an existing reviewed identity requires a
        # separate, explicit reconciliation.
        for row in rows:
            project_id = int(row["hipflatProjectId"])
            if (project_id not in by_id and row.get("locationVerified")
                    and row.get("lat") is not None and row.get("lng") is not None):
                by_id[project_id] = row
        rows = sorted(by_id.values(), key=lambda row: int(row["hipflatProjectId"]))
    target = OUTPUT.with_suffix(".js.tmp")
    target.write_text("window.BANGKOK_PROPERTYHUB_GUESSED_DETAILS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    target.replace(OUTPUT)


def verified_rows(rows: list[dict[str, Any]], projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projects_by_id = {int(row["id"]): row for row in projects}
    accepted = []
    for row in rows:
        if not row.get("locationVerified") or row.get("lat") is None or row.get("lng") is None:
            continue
        target = projects_by_id.get(int(row["hipflatProjectId"]))
        expected = propertyhub_district((target or {}).get("address", ""))
        actual = propertyhub_district(row.get("projectAddress", ""))
        if expected and actual and expected != actual:
            continue
        accepted.append(row)
    return accepted


def main() -> int:
    RESEARCH.mkdir(parents=True, exist_ok=True)
    projects = read_array(CATALOGUE, "BANGKOK_CONDO_CATALOGUE")
    market = {int(x["id"]): x for x in read_array(PROPERTYHUB, "BANGKOK_PROPERTYHUB_PROJECTS")}
    known_details = {int(x.get("hipflatProjectId")): x for x in read_array(DETAILS, "BANGKOK_PROPERTYHUB_DETAILS") if x.get("hipflatProjectId")} if DETAILS.exists() else {}
    known_osm = {int(x["id"]) for x in read_array(OSM, "BANGKOK_OSM_LOCATIONS")} if OSM.exists() else set()
    cached: dict[int, dict[str, Any]] = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                cached[int(item["hipflatProjectId"])] = item
            except (ValueError, KeyError, TypeError):
                continue
    eligible = [x for x in projects if not market.get(int(x["id"]), {}).get("propertyHubProjectId")
                and not known_details.get(int(x["id"]), {}).get("locationVerified")
                and int(x["id"]) not in known_osm
                and not cached.get(int(x["id"]), {}).get("locationVerified")]
    log = LOG.open("a", encoding="utf-8")
    def report(message: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
        print(line, flush=True); log.write(line + "\n"); log.flush()
    report(f"Projects {len(projects)}; guessed detail pages cached {len(cached)}; pending {len(eligible)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool, CACHE.open("a", encoding="utf-8") as out:
        futures = {pool.submit(fetch, row, projects): row for row in eligible}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            item = future.result(); done += 1
            with LOCK:
                out.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"); out.flush()
            cached[int(item["hipflatProjectId"])] = item
            if done % 25 == 0:
                valid = verified_rows(list(cached.values()), projects)
                write_output(valid)
                report(f"Guessed project pages {done}/{len(eligible)}; verified coordinates {len(valid)}")
    valid = verified_rows(list(cached.values()), projects)
    write_output(valid)
    report(f"Finished; {len(valid)} unique address/name verified coordinates")
    log.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
