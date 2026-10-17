"""Collect Bangkok PropertyHub listing cards by paginated city search."""
from __future__ import annotations

import concurrent.futures
import html
import json
import math
import pathlib
import re
import threading
import time
from collections import defaultdict
from datetime import date
from typing import Any

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
PROJECTS_FILE = DIST / "bangkok-catalogue.js"
ENRICHED_FILE = DIST / "bangkok-propertyhub.js"
DIRECT_CACHE = RESEARCH / "propertyhub-enrichment.jsonl"
PAGE_CACHE = RESEARCH / "propertyhub-bangkok-pages.jsonl"
LOG = RESEARCH / "propertyhub-bulk-progress.log"
BASE = "https://propertyhub.in.th"
HEADERS = {
    "User-Agent": "BangkokCondoMapResearch/1.0 (public listing research)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en,th;q=0.8",
}
LOCK = threading.Lock()
IGNORED = {"condo", "condominium", "apartment", "apartments", "residence", "residences", "project", "bangkok", "the", "at", "by"}


def read_array(path: pathlib.Path, symbol: str) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def tokens(value: Any) -> set[str]:
    value = html.unescape(str(value or "")).lower().replace("&", " and ")
    return {part for part in re.sub(r"[^a-z0-9]+", " ", value).split() if len(part) > 1 and part not in IGNORED}


def parse_ad(ad: dict[str, Any], kind: str) -> dict[str, Any] | None:
    project = ad.get("project") or {}
    room = ad.get("roomInformation") or ad.get("room") or {}
    price = ad.get("price") or {}
    amount = (((price.get("forSale") or {}).get("price")) if kind == "sale" else (((price.get("forRent") or {}).get("monthly") or {}).get("price")))
    area = room.get("roomArea")
    try:
        amount, area = float(amount), float(area)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(amount) or not math.isfinite(area) or not 15 <= area <= 1000:
        return None
    rate = amount / area
    if kind == "sale" and not (10_000 <= amount <= 500_000_000 and 10_000 <= rate <= 2_000_000):
        return None
    if kind == "rent" and not (500 <= amount <= 5_000_000 and 100 <= rate <= 20_000):
        return None
    listing_id = str(ad.get("id") or "")
    slug = str(ad.get("slug") or "")
    if not listing_id or not slug or not project.get("nameEnglish") and not project.get("name"):
        return None
    return {
        "listingId": listing_id,
        "kind": kind,
        "projectName": project.get("nameEnglish") or project.get("name"),
        "projectId": str(project.get("id") or ""),
        "projectSlug": project.get("slug"),
        "address": project.get("address"),
        "price": amount,
        "area": area,
        "priceSqm": round(rate),
        "beds": room.get("numberOfBed"),
        "roomType": room.get("roomType"),
        "title": str(ad.get("title") or "")[:250],
        "url": f"{BASE}/en/listings/{slug}---{listing_id}",
        "updated": ad.get("updatedAt") or ad.get("refreshedAt"),
    }


def fetch_page(kind: str, page_num: int) -> dict[str, Any]:
    url = f"{BASE}/en/condo-for-{kind}/bangkok/{page_num}"
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=(8, 25))
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            response.raise_for_status()
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.S)
            if not match:
                raise ValueError("page JSON was not found")
            page = json.loads(match.group(1)).get("props", {}).get("pageProps", {})
            listing_data = page.get("listings") or {}
            pagination = listing_data.get("pagination") or {}
            ads = [item for ad in listing_data.get("listings", []) if (item := parse_ad(ad, kind))]
            return {"key": f"{kind}:{page_num}", "kind": kind, "page": page_num,
                    "totalPages": int(pagination.get("totalPages") or page_num),
                    "totalCount": int(pagination.get("totalCount") or 0), "listings": ads,
                    "pageUrl": url, "asOf": date.today().isoformat()}
        except (requests.RequestException, json.JSONDecodeError, ValueError) as error:
            if attempt == 2:
                return {"key": f"{kind}:{page_num}", "kind": kind, "page": page_num,
                        "error": str(error)[:240], "listings": [], "pageUrl": url}
            time.sleep(2 * (attempt + 1))
    return {"key": f"{kind}:{page_num}", "kind": kind, "page": page_num, "error": "unreachable", "listings": [], "pageUrl": url}


def load_cache() -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    if PAGE_CACHE.exists():
        for line in PAGE_CACHE.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                if item.get("key") and not item.get("error"):
                    cache[item["key"]] = item
            except (ValueError, TypeError):
                continue
    return cache


def load_direct() -> dict[int, dict[str, Any]]:
    cached: dict[int, dict[str, Any]] = {}
    if DIRECT_CACHE.exists():
        for line in DIRECT_CACHE.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                if item.get("marketDataStatus") != "lookup_error":
                    cached[int(item["id"])] = item
            except (ValueError, KeyError, TypeError):
                continue
    return cached


def project_match(name: str, indexes: list[tuple[int, str, set[str]]], token_index: dict[str, set[int]]) -> int | None:
    source_tokens = tokens(name)
    if len(source_tokens) < 2:
        return None
    candidates: set[int] = set()
    for token in source_tokens:
        candidates.update(token_index.get(token, set()))
    scored = []
    for idx in candidates:
        pid, _, target_tokens = indexes[idx]
        union = source_tokens | target_tokens
        score = len(source_tokens & target_tokens) / len(union) if union else 0
        if score >= 0.84:
            scored.append((score, pid))
    scored.sort(reverse=True)
    if not scored or (len(scored) > 1 and scored[0][0] - scored[1][0] < 0.12):
        return None
    return scored[0][1]


def main() -> int:
    RESEARCH.mkdir(parents=True, exist_ok=True)
    projects = read_array(PROJECTS_FILE, "BANGKOK_HIPFLAT_PROJECTS")
    indexes = [(int(row["id"]), row["name"], tokens(row["name"])) for row in projects]
    token_index: dict[str, set[int]] = defaultdict(set)
    for idx, (_, _, name_tokens) in enumerate(indexes):
        for token in name_tokens:
            token_index[token].add(idx)
    cache = load_cache()
    with LOG.open("a", encoding="utf-8") as log:
        def report(message: str) -> None:
            line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()

        report(f"PropertyHub city scan: {len(projects)} projects; {len(cache)} cached pages")
        # Bootstrap page totals from the first page of each market.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            first_pages = list(pool.map(lambda kind: fetch_page(kind, 1), ("sale", "rent")))
        with PAGE_CACHE.open("a", encoding="utf-8") as out:
            for item in first_pages:
                if not item.get("error"):
                    cache[item["key"]] = item
                    out.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            out.flush()
        pages_by_kind = {item["kind"]: item["totalPages"] for item in first_pages if not item.get("error")}
        for key, item in list(cache.items()):
            if item.get("kind") in pages_by_kind and int(item.get("page") or 0) > pages_by_kind[item["kind"]]:
                cache.pop(key, None)
        pending = [(kind, page_num) for page_num in range(2, max(pages_by_kind.values(), default=1) + 1)
                   for kind, total in pages_by_kind.items()
                   if page_num <= total and f"{kind}:{page_num}" not in cache]
        expected_pages = sum(pages_by_kind.values())
        report(f"Page totals {pages_by_kind}; cached {len(cache)}/{expected_pages}; pending {len(pending)} pages")
        completed = len(cache)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool, PAGE_CACHE.open("a", encoding="utf-8") as out:
            futures = [pool.submit(fetch_page, kind, page_num) for kind, page_num in pending]
            for future in concurrent.futures.as_completed(futures):
                item = future.result()
                with LOCK:
                    if not item.get("error"):
                        out.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
                        out.flush()
                        cache[item["key"]] = item
                completed += 1
                if completed % 25 == 0 or completed == expected_pages:
                    report(f"Pages {completed}/{expected_pages}; errors {sum(bool(x.get('error')) for x in cache.values())}")
                    merged = aggregate(projects, indexes, token_index, cache, load_direct())
                    write_output(merged)
        merged = aggregate(projects, indexes, token_index, cache, load_direct())
        write_output(merged)
        counts = {"matchedSale": sum(bool((x.get("sale") or {}).get("observedCount")) for x in merged),
                  "matchedRent": sum(bool((x.get("rent") or {}).get("observedCount")) for x in merged),
                  "matchedBoth": sum(bool((x.get("sale") or {}).get("observedCount") and (x.get("rent") or {}).get("observedCount")) for x in merged)}
        report(f"Finished; {counts}")
    return 0


def aggregate(projects: list[dict[str, Any]], indexes: list[tuple[int, str, set[str]]], token_index: dict[str, set[int]],
              pages: dict[str, dict[str, Any]], direct: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    by_project: dict[int, dict[str, dict[str, dict[str, Any]]]] = defaultdict(lambda: {"sale": {}, "rent": {}})
    project_meta: dict[int, dict[str, Any]] = {}
    for page in pages.values():
        kind = page.get("kind")
        for ad in page.get("listings", []):
            pid = project_match(ad.get("projectName"), indexes, token_index)
            if pid is not None:
                by_project[pid][kind][ad["listingId"]] = ad
                project_meta.setdefault(pid, {"projectId": ad.get("projectId"), "projectSlug": ad.get("projectSlug"),
                                               "projectAddress": ad.get("address"), "projectName": ad.get("projectName")})
    output = []
    for project in projects:
        pid = int(project["id"])
        row = dict(project)
        row.update(direct.get(pid) or {})
        meta = project_meta.get(pid) or {}
        if meta.get("projectId") and meta.get("projectSlug"):
            row["propertyHubProjectId"] = meta["projectId"]
            row["propertyHubProjectUrl"] = f"{BASE}/en/projects/{meta['projectSlug']}"
            row["propertyHubAddress"] = meta.get("projectAddress")
            row["propertyHubProjectName"] = meta.get("projectName")
        for kind in ("sale", "rent"):
            values = list(by_project[pid][kind].values())
            previous = row.get(kind) or {}
            if not values or len(values) < int(previous.get("observedCount") or 0):
                continue
            by_price = sorted(values, key=lambda item: item["price"])
            by_rate = sorted(values, key=lambda item: item["priceSqm"])
            def by_bedroom(items: list[dict[str, Any]]) -> dict[str, Any]:
                groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for item in items:
                    if isinstance(item.get("beds"), (int, float)):
                        groups[str(int(item["beds"]))].append(item)
                return {bed: {"count": len(group), "minimum": min(x["price"] for x in group),
                              "minimumSqm": min(x["priceSqm"] for x in group),
                              "sourceUrl": min(group, key=lambda x: x["price"])["url"]}
                        for bed, group in groups.items()}
            previous_minimum = float(previous.get("minimum") or math.inf)
            previous_minimum_sqm = float(previous.get("minimumSqm") or math.inf)
            minimum = min(by_price[0]["price"], previous_minimum)
            minimum_sqm = min(by_rate[0]["priceSqm"], previous_minimum_sqm)
            row[kind] = {
                "count": max(int(previous.get("count") or 0), len(values)),
                "countKind": "project_total" if previous.get("count") else "matched_city_index",
                "observedCount": max(len(values), int(previous.get("observedCount") or 0)),
                "average": round(sum(x["price"] for x in values) / len(values)),
                "minimum": minimum,
                "averageSqm": round(sum(x["priceSqm"] for x in values) / len(values)),
                "minimumSqm": minimum_sqm,
                "asOf": date.today().isoformat(),
                "snapshotMethod": "propertyhub_bangkok_paginated_listing_cards_project_name_matched",
                "source": f"{BASE}/en/condo-for-{kind}/bangkok",
                "minimumSourceUrl": previous.get("minimumSourceUrl") if previous_minimum < by_price[0]["price"] else by_price[0]["url"],
                "minimumSqmSourceUrl": previous.get("minimumSqmSourceUrl") if previous_minimum_sqm < by_rate[0]["priceSqm"] else by_rate[0]["url"],
                "samples": by_price[:20],
                "byBedroom": by_bedroom(values),
            }
            row["propertyHub" + kind.title() + "Url"] = previous.get("source") or f"{BASE}/en/condo-for-{kind}/bangkok"
        if row.get("sale") or row.get("rent"):
            row["marketDataStatus"] = "propertyhub_bangkok_listing_cards_name_matched"
            row["lastListingRefresh"] = date.today().isoformat()
        output.append(row)
    return output


def write_output(rows: list[dict[str, Any]]) -> None:
    target = ENRICHED_FILE.with_suffix(".js.tmp")
    target.write_text("window.BANGKOK_PROPERTYHUB_PROJECTS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    target.replace(ENRICHED_FILE)


if __name__ == "__main__":
    raise SystemExit(main())
