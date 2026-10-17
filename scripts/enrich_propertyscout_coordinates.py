"""Audit missing Hipflat Bangkok coordinates against public PropertyScout project pages."""
from __future__ import annotations

import concurrent.futures
import html
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

from rapidfuzz import fuzz, process

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
SITEMAP = Path(__import__("tempfile").gettempdir()) / "propertyscout-projects.xml"
AUDIT = RESEARCH / "propertyscout-coordinate-audit.json"
OUTPUT = DIST / "bangkok-propertyscout-details.js"
BBOX = (13.4, 14.1, 100.2, 101.0)
# These exact-name PropertyScout points cross-check against independent listing
# addresses even though the imported Hipflat address assigns a different district.
CROSS_DISTRICT_VERIFIED = {
    3304: "https://www.ddproperty.com/en/property-for-sale/at-metro-sky-bang-son-interchange-prachachuen-4628",
    4149: "https://www.ddproperty.com/en/property-for-sale/at-the-golden-master-ratchada-19-6338",
}


def arr(file: str, symbol: str) -> list[dict]:
    text = (DIST / file).read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {file}")
    return json.loads(match.group(1))


def norm(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", html.unescape(value or ""))
    value = value.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def slug(value: str) -> str:
    return norm(value).replace(" ", "-")


def district_from_address(address: str | None) -> str:
    # Bangkok districts are the penultimate comma-delimited address component.
    parts = [norm(part) for part in (address or "").split(",") if norm(part)]
    known = {norm(name) for name in (
        "Pom Prap Sattru Phai", "Thawi Watthana", "Khlong Sam Wa", "Bang Khun Thian",
        "Bang Kho Laem", "Saphan Sung", "Bangkok Yai", "Bangkok Noi", "Phaya Thai",
        "Phra Khanong", "Ratchathewi", "Samphanthawong", "Wang Thonglang", "Huai Khwang",
        "Khan Na Yao", "Lat Krabang", "Bueng Kum", "Chom Thong", "Don Mueang", "Nong Chok",
        "Nong Khaem", "Pathum Wan", "Phasi Charoen", "Phra Nakhon", "Rat Burana", "Taling Chan",
        "Thung Khru", "Bang Kapi", "Bang Khae", "Bang Khen", "Bang Na", "Bang Phlat", "Bang Rak",
        "Bang Sue", "Chatuchak", "Din Daeng", "Dusit", "Khlong San", "Khlong Toei", "Lak Si",
        "Lat Phrao", "Min Buri", "Prawet", "Sai Mai", "Sathon", "Suan Luang", "Thon Buri",
        "Yan Nawa", "Bang Bon", "Watthana", "Vadhana",
    )}
    district = next((part for part in reversed(parts) if part in known), "")
    return {"vadhana": "watthana", "sathorn": "sathon"}.get(district, district)


def current_coordinate_ids(catalogue: list[dict]) -> set[int]:
    osm = {int(row["id"]): row for row in arr("bangkok-osm.js", "BANGKOK_OSM_LOCATIONS")}
    base = {int(row["id"]): row for row in arr("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")}
    details = {str(row["propertyHubProjectId"]): row for row in arr("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")}
    guessed = {int(row["hipflatProjectId"]): row for row in arr("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")}
    found = set()
    for project in catalogue:
        project_id = int(project["id"])
        property_hub = base.get(project_id, {})
        detail = details.get(str(property_hub.get("propertyHubProjectId", "")), {})
        candidates = (detail, property_hub, guessed.get(project_id, {}), osm.get(project_id, {}))
        if any(row.get("lat") is not None and row.get("lng") is not None and
               (row.get("locationVerified") or row in (osm.get(project_id, {}),)) for row in candidates):
            found.add(project_id)
    return found


def request_page(url: str) -> dict:
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        page = response.read().decode("utf-8")
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', page, re.S)
    if not match:
        raise ValueError("No project data in page")
    payload = json.loads(match.group(1))
    return payload.get("props", {}).get("pageProps", {}).get("building", {})


def main() -> int:
    if not SITEMAP.exists():
        raise RuntimeError(f"Missing sitemap cache: {SITEMAP}")
    catalogue = arr("bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    xml = SITEMAP.read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(.*?)</loc>", xml)
    slug_map: dict[str, list[str]] = {}
    for url in urls:
        match = re.search(r"/en/bangkok/condo/([^/]+)/?$", url)
        if match:
            slug_map.setdefault(match.group(1), []).append(url)
    known_slugs = list(slug_map)
    already_located = current_coordinate_ids(catalogue)
    candidates = []
    for project in catalogue:
        project_id = int(project["id"])
        if project_id in already_located:
            continue
        expected_slug = slug(project.get("name", ""))
        page_urls = slug_map.get(expected_slug) or slug_map.get(
            re.sub(r"-(?:condo|minium|residence)$", "", expected_slug), []
        )
        match_score = 100
        if not page_urls:
            ranked = process.extract(expected_slug, known_slugs, scorer=fuzz.ratio, limit=2)
            if ranked and ranked[0][1] >= 80 and (len(ranked) == 1 or ranked[0][1] - ranked[1][1] >= 8):
                page_urls = slug_map[ranked[0][0]]
                match_score = float(ranked[0][1])
        if page_urls:
            candidates.append({
                "hipflatId": project_id,
                "hipflatName": project["name"],
                "hipflatAddress": project.get("address", ""),
                "expectedDistrict": district_from_address(project.get("address")),
                "slugMatchScore": match_score,
                "sourceUrl": page_urls[0],
            })

    cache = {}
    if AUDIT.exists():
        try:
            cache = {int(row["hipflatId"]): row for row in json.loads(AUDIT.read_text(encoding="utf-8"))}
        except (ValueError, KeyError):
            cache = {}
    pending = [row for row in candidates if row["hipflatId"] not in cache]
    print(f"Candidates: {len(candidates)}; cached: {len(cache)}; fetching: {len(pending)}", flush=True)

    def fetch(candidate: dict) -> dict:
        result = dict(candidate)
        try:
            building = request_page(candidate["sourceUrl"])
            result.update({
                "propertyScoutName": building.get("name", {}).get("en", ""),
                "propertyScoutDistrict": building.get("district_ps", {}).get("en", ""),
                "lat": building.get("lat"),
                "lng": building.get("lng"),
                "buildingType": building.get("building_type"),
            })
            result["pageNameScore"] = round(fuzz.ratio(norm(candidate["hipflatName"]), norm(result["propertyScoutName"])), 1)
        except Exception as exc:  # Keep failures visible and resumable.
            result["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for completed, result in enumerate(pool.map(fetch, pending), start=1):
            cache[int(result["hipflatId"])] = result
            if completed % 20 == 0 or completed == len(pending):
                AUDIT.parent.mkdir(parents=True, exist_ok=True)
                AUDIT.write_text(json.dumps(list(cache.values()), ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"Fetched {completed}/{len(pending)}", flush=True)

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    rows = list(cache.values())
    AUDIT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    verified = []
    for row in rows:
        district = norm(row.get("propertyScoutDistrict"))
        district = {"vadhana": "watthana", "sathorn": "sathon"}.get(district, district)
        expected_district = {"vadhana": "watthana", "sathorn": "sathon"}.get(norm(row.get("expectedDistrict")), norm(row.get("expectedDistrict")))
        name_score = fuzz.ratio(norm(row.get("hipflatName")), norm(row.get("propertyScoutName")))
        lat, lng = row.get("lat"), row.get("lng")
        if row.get("buildingType") != "condo" or name_score < 90:
            continue
        if not (isinstance(lat, (float, int)) and isinstance(lng, (float, int)) and
                BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lng <= BBOX[3]):
            continue
        cross_check = CROSS_DISTRICT_VERIFIED.get(int(row["hipflatId"]))
        if expected_district and district != expected_district and not cross_check:
            continue
        verified.append({
            "hipflatId": row["hipflatId"],
            "name": row["hipflatName"],
            "lat": lat,
            "lng": lng,
            "locationVerified": True,
            "locationSourceName": "PropertyScout 專案頁",
            "locationSourceUrl": row["sourceUrl"],
            "locationVerificationSourceUrl": cross_check,
            "verificationMethod": "exact_project_name_and_independent_address_check" if cross_check else "exact_project_name_and_district",
        })
    OUTPUT.write_text(
        "window.BANGKOK_PROPERTYSCOUT_DETAILS = " + json.dumps(verified, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Verified coordinate points: {len(verified)} / {len(rows)} fetched candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
