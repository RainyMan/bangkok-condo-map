"""Add exact-name, district-matched Thaiger project coordinates to the map."""
from __future__ import annotations

import concurrent.futures
import csv
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"bangkok-coverage-{date.today().isoformat()}.csv"
OUTPUT = DIST / "bangkok-verified-coordinates.js"
SITEMAP_URLS = [
    "https://www.thaigerproperty.com/sitemaps/www.thaigerproperty.com-2.xml",
    "https://www.thaigerproperty.com/sitemaps/www.thaigerproperty.com-3.xml",
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BangkokCondoMapResearch/1.0)"}
BBOX = (13.4, 14.1, 100.2, 101.0)


def array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


DISTRICTS = {
    norm(name): norm(name).replace(" ", "-") for name in (
        "Pom Prap Sattru Phai", "Thawi Watthana", "Khlong Sam Wa", "Bang Khun Thian",
        "Bang Kho Laem", "Saphan Sung", "Bangkok Yai", "Bangkok Noi", "Phaya Thai",
        "Phra Khanong", "Ratchathewi", "Samphanthawong", "Wang Thonglang", "Huai Khwang",
        "Khan Na Yao", "Lat Krabang", "Bueng Kum", "Chom Thong", "Don Mueang", "Nong Chok",
        "Nong Khaem", "Pathum Wan", "Phasi Charoen", "Phra Nakhon", "Rat Burana", "Taling Chan",
        "Thung Khru", "Bang Kapi", "Bang Khae", "Bang Khen", "Bang Na", "Bang Phlat", "Bang Rak",
        "Bang Sue", "Chatuchak", "Din Daeng", "Dusit", "Khlong San", "Khlong Toei", "Lak Si",
        "Lat Phrao", "Min Buri", "Prawet", "Sai Mai", "Sathon", "Suan Luang", "Thon Buri",
        "Yan Nawa", "Bang Bon", "Watthana", "Vadhana",
    )
}
DISTRICTS.update({"vadhana": "watthana", "sathorn": "sathon"})


def district_from_address(value: str) -> str | None:
    text = norm(value)
    for name in sorted(DISTRICTS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}\b", text):
            return DISTRICTS[name]
    return None


def load_schema(value):
    if isinstance(value, list):
        for item in value:
            found = load_schema(item)
            if found:
                return found
    elif isinstance(value, dict):
        if isinstance(value.get("geo"), dict) and (value.get("name") or value.get("@type")):
            return value
        for child in value.values():
            found = load_schema(child)
            if found:
                return found
    return None


def fetch(candidate: dict) -> dict:
    row = dict(candidate)
    try:
        response = requests.get(row["url"], headers=HEADERS, timeout=(8, 25))
        row["httpStatus"] = response.status_code
        if response.status_code != 200:
            row["status"] = f"http_{response.status_code}"
            return row
        schemas = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', response.text, re.S | re.I)
        project = None
        for raw in schemas:
            try:
                project = load_schema(json.loads(raw))
            except (json.JSONDecodeError, TypeError):
                continue
            if project:
                break
        if not project:
            row["status"] = "project_geo_schema_missing"
            return row
        found_name = str(project.get("name") or "")
        point = project.get("geo") or {}
        lat, lng = float(point.get("latitude")), float(point.get("longitude"))
        page_district = row["url"].split("/projects/thailand/bangkok/", 1)[1].split("/", 1)[0]
        if norm(found_name) != norm(row["name"]):
            row["status"] = "project_name_mismatch"
        elif page_district != row["expectedDistrictSlug"]:
            row["status"] = "district_path_mismatch"
        elif not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lng <= BBOX[3]):
            row["status"] = "outside_bangkok"
        else:
            address = project.get("address") or {}
            address_district = norm(address.get("addressLocality") or "")
            # Thaiger's structured addressLocality is usually the subdistrict;
            # require the separately published district path and exact name.
            row.update({"lat": lat, "lng": lng, "pageName": found_name, "pageAddressLocality": address_district, "status": "verified"})
    except Exception as error:
        row["status"] = f"fetch_error:{type(error).__name__}"
    return row


def main() -> None:
    projects = array(DIST / "bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    current = array(OUTPUT, "BANGKOK_VERIFIED_COORDINATES")
    existing = {int(row["hipflatId"]): row for row in current}
    missing = {int(row["hipflat_id"]) for row in csv.DictReader(REPORT.open(encoding="utf-8-sig")) if row["coordinates"] == "no"}
    sitemap_urls = []
    for url in SITEMAP_URLS:
        response = requests.get(url, headers=HEADERS, timeout=35)
        response.raise_for_status()
        sitemap_urls.extend(re.findall(r"<loc>(.*?)</loc>", response.text))
    urls_by_slug: dict[str, set[str]] = {}
    for url in sitemap_urls:
        if "/projects/thailand/bangkok/" not in url:
            continue
        slug = norm(url.rstrip("/").rsplit("/", 1)[-1]).replace(" ", "-")
        urls_by_slug.setdefault(slug, set()).add(url)

    candidates = []
    for project in projects:
        pid = int(project["id"])
        if pid not in missing:
            continue
        slug = norm(project.get("name", "")).replace(" ", "-")
        matches = sorted(urls_by_slug.get(slug, set()))
        expected_district = district_from_address(project.get("address", ""))
        if len(matches) != 1 or not expected_district:
            continue
        page_district = matches[0].split("/projects/thailand/bangkok/", 1)[1].split("/", 1)[0]
        if page_district != expected_district.replace(" ", "-"):
            continue
        candidates.append({"hipflatId": pid, "name": project["name"], "address": project.get("address", ""),
                           "expectedDistrictSlug": expected_district.replace(" ", "-"), "url": matches[0]})
    print(f"Candidates exact name slug + district: {len(candidates)}", flush=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for idx, result in enumerate(pool.map(fetch, candidates), start=1):
            results.append(result)
            if idx % 50 == 0 or idx == len(candidates):
                print(f"Fetched {idx}/{len(candidates)}; verified {sum(x.get('status') == 'verified' for x in results)}", flush=True)

    added = []
    for row in results:
        if row.get("status") != "verified":
            continue
        pid = int(row["hipflatId"])
        added.append({"hipflatId": pid, "name": row["name"], "lat": row["lat"], "lng": row["lng"],
                      "locationVerified": True, "sourceName": "Thaiger Property 專案頁 GeoCoordinates",
                      "sourceUrl": row["url"], "verificationSourceUrl": f"https://www.hipflat.co.th/en/projects/{next(p['hipflatProjectUrl'].split('/projects/')[-1] for p in projects if int(p['id']) == pid)}",
                      "verificationMethod": "exact_project_name_unique_slug_and_matching_bangkok_district"})
        existing[pid] = added[-1]
    if added:
        OUTPUT.write_text("window.BANGKOK_VERIFIED_COORDINATES = " + json.dumps(sorted(existing.values(), key=lambda x: int(x["hipflatId"])), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    summary = {"candidates": len(candidates), "verified": len(added), "statuses": {}, "rows": results}
    for row in results:
        status = row.get("status", "unknown")
        summary["statuses"][status] = summary["statuses"].get(status, 0) + 1
    output_report = ROOT / "reports" / f"thaiger-coordinate-enrichment-{date.today().isoformat()}.json"
    output_report.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
