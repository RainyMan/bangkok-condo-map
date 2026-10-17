"""Fetch source-linked PropertyHub coordinates and project facts for matched projects."""
from __future__ import annotations

import concurrent.futures
import json
import pathlib
import re
import threading
import time
from datetime import date
from typing import Any

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
SOURCE = DIST / "bangkok-propertyhub.js"
DETAIL_OUTPUT = DIST / "bangkok-propertyhub-details.js"
CACHE = RESEARCH / "propertyhub-project-details.jsonl"
DIRECT_CACHE = RESEARCH / "propertyhub-enrichment.jsonl"
LOG = RESEARCH / "propertyhub-project-details.log"
BASE = "https://propertyhub.in.th"
HEADERS = {"User-Agent": "BangkokCondoMapResearch/1.0 (public listing research)", "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en,th;q=0.8"}
LOCK = threading.Lock()


def read_projects() -> list[dict[str, Any]]:
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(r"window\.BANGKOK_PROPERTYHUB_PROJECTS\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError("PropertyHub project output was not found")
    return json.loads(match.group(1))


def load_cache() -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if row.get("propertyHubProjectId"):
                    cache[str(row["propertyHubProjectId"])] = row
            except (ValueError, TypeError):
                continue
    return cache


def fetch(row: dict[str, Any]) -> dict[str, Any] | None:
    project_id = str(row.get("propertyHubProjectId") or "")
    url = row.get("propertyHubProjectUrl") or ""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    if not project_id or not slug:
        return None
    page_url = f"{BASE}/en/condo-for-sale/project-{slug}"
    for attempt in range(3):
        try:
            response = requests.get(page_url, headers=HEADERS, timeout=(8, 25))
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            response.raise_for_status()
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.S)
            if not match:
                return None
            props = json.loads(match.group(1)).get("props", {}).get("pageProps", {})
            project = props.get("project") or {}
            if str(project.get("id") or "") != project_id:
                return None
            info = project.get("projectInfo") or {}
            point = project.get("location") or {}
            try:
                lat, lng = float(point.get("lat")), float(point.get("lng"))
            except (TypeError, ValueError):
                lat = lng = None
            result: dict[str, Any] = {"propertyHubProjectId": project_id, "name": row.get("name"),
                                      "sourceUrl": page_url, "projectName": project.get("nameEnglish") or project.get("name"),
                                      "projectAddress": project.get("address"), "asOf": date.today().isoformat()}
            if lat is not None and lng is not None and 13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0:
                result.update({"lat": lat, "lng": lng, "locationVerified": True,
                               "locationSourceUrl": page_url, "locationSourceName": "PropertyHub 專案頁"})
            if str(info.get("completedYear", "")).isdigit():
                result["completedYear"] = int(info["completedYear"])
                result["completedYearSourceUrl"] = page_url
            if str(info.get("totalUnits", "")).isdigit():
                result["units"] = int(info["totalUnits"])
            if str(info.get("buildingsFloors", "")).isdigit():
                result["floors"] = int(info["buildingsFloors"])
            fee_raw = info.get("utilityFee")
            fee_match = re.search(r"(\d+(?:\.\d+)?)", str(fee_raw or ""))
            if fee_match:
                rate = float(fee_match.group(1))
                if 1 <= rate <= 1000:
                    result["fee"] = {"rate": rate, "note": "PropertyHub 專案頁公布的管理費數值；以泰國公寓常見單位解讀，現行費率請向管委會確認。",
                                     "source": page_url, "status": "published_indicative"}
            return result
        except (requests.RequestException, json.JSONDecodeError):
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    return None


def write_output(details: list[dict[str, Any]]) -> None:
    target = DETAIL_OUTPUT.with_suffix(".js.tmp")
    target.write_text("window.BANGKOK_PROPERTYHUB_DETAILS = " + json.dumps(details, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    target.replace(DETAIL_OUTPUT)


def main() -> int:
    RESEARCH.mkdir(parents=True, exist_ok=True)
    rows = read_projects()
    cache = load_cache()
    rows_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("propertyHubProjectId"):
            rows_by_id.setdefault(str(row["propertyHubProjectId"]), []).append(row)
    for project_id, project_rows in rows_by_id.items():
        if project_id in cache:
            for row in project_rows:
                row.update(cache[project_id])
    direct_by_slug: dict[str, dict[str, Any]] = {}
    if DIRECT_CACHE.exists():
        for line in DIRECT_CACHE.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                slug = str(item.get("propertyHubProjectUrl", "")).rstrip("/").rsplit("/", 1)[-1]
                if slug and item.get("locationVerified"):
                    direct_by_slug[slug] = item
            except (ValueError, TypeError):
                continue
    prefilled: list[dict[str, Any]] = []
    for project_id, project_rows in rows_by_id.items():
        if project_id in cache:
            continue
        slug = str(project_rows[0].get("propertyHubProjectUrl", "")).rstrip("/").rsplit("/", 1)[-1]
        direct = direct_by_slug.get(slug)
        if direct:
            item = {"propertyHubProjectId": project_id, "name": project_rows[0].get("name"),
                    "sourceUrl": direct.get("locationSourceUrl") or direct.get("propertyHubProjectUrl"),
                    "locationSourceUrl": direct.get("locationSourceUrl"), "locationSourceName": direct.get("locationSourceName"),
                    "lat": direct.get("lat"), "lng": direct.get("lng"), "locationVerified": True,
                    "completedYear": direct.get("completedYear"), "units": direct.get("units"), "floors": direct.get("floors"),
                    "fee": direct.get("fee"), "asOf": date.today().isoformat()}
            item = {k: v for k, v in item.items() if v is not None}
            cache[project_id] = item
            prefilled.append(item)
            for row in project_rows:
                row.update(item)
    if prefilled:
        with CACHE.open("a", encoding="utf-8") as out:
            for item in prefilled:
                out.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    targets = [project_rows[0] for project_id, project_rows in rows_by_id.items() if project_id not in cache]
    log = LOG.open("a", encoding="utf-8")
    def report(message: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
        print(line, flush=True); log.write(line + "\n"); log.flush()
    report(f"Matched projects {len(rows)}; cached detail pages {len(cache)}; pending {len(targets)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool, CACHE.open("a", encoding="utf-8") as out:
        futures = {pool.submit(fetch, row): row for row in targets}
        for future in concurrent.futures.as_completed(futures):
            item = future.result()
            if item:
                with LOCK:
                    out.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"); out.flush()
                cache[str(item["propertyHubProjectId"])] = item
                for row in rows_by_id.get(str(item["propertyHubProjectId"]), []):
                    row.update(item)
            if len(cache) % 25 == 0:
                write_output(list(cache.values()))
                report(f"Verified project details {len(cache)}")
    write_output(list(cache.values()))
    report(f"Finished: {len(cache)} PropertyHub project detail pages"); log.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
