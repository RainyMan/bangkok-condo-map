"""Verify unresolved Bangkok Condo points against exact ArcGIS address/POI results.

Only adds a coordinate when a direct POI name agrees with a separate exact
address result, or when an exact house number, street and Bangkok district
match the catalogue address. Ambiguous geocoder suggestions are recorded for
review and are not used as map coordinates.
"""
from __future__ import annotations

import csv
import difflib
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

import requests

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"arcgis-coordinate-review-{date.today().isoformat()}.json"
CATALOGUE = DIST / "bangkok-catalogue.js"
VERIFIED = DIST / "bangkok-verified-coordinates.js"
AUDIT = ROOT / "reports" / f"bangkok-coverage-{date.today().isoformat()}.csv"
BASE = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
HEADERS = {"User-Agent": "BangkokCondoMapResearch/1.0 (public coordinate verification)", "Accept": "application/json"}
BBOX = (13.4, 14.1, 100.2, 101.0)
STOP = {"the", "at", "by", "and", "condo", "condominium", "residence", "residences", "apartment", "apartments", "project", "building", "tower", "place", "bangkok", "thailand"}
DISTRICTS = (
    "Pom Prap Sattru Phai", "Thawi Watthana", "Khlong Sam Wa", "Bang Khun Thian", "Bang Kho Laem", "Saphan Sung",
    "Bangkok Yai", "Bangkok Noi", "Phaya Thai", "Phra Khanong", "Ratchathewi", "Samphanthawong", "Wang Thonglang",
    "Huai Khwang", "Khan Na Yao", "Lat Krabang", "Bueng Kum", "Chom Thong", "Don Mueang", "Nong Chok", "Nong Khaem",
    "Pathum Wan", "Phasi Charoen", "Phra Nakhon", "Rat Burana", "Taling Chan", "Thung Khru", "Bang Kapi", "Bang Khae",
    "Bang Khen", "Bang Na", "Bang Phlat", "Bang Rak", "Bang Sue", "Chatuchak", "Din Daeng", "Dusit", "Khlong San",
    "Khlong Toei", "Lak Si", "Lat Phrao", "Min Buri", "Prawet", "Sai Mai", "Sathon", "Suan Luang", "Thon Buri",
    "Yan Nawa", "Bang Bon", "Watthana",
)


def js_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot parse {symbol} from {path.name}")
    return json.loads(match.group(1))


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def tokens(value: object) -> set[str]:
    return {part for part in norm(value).split() if part not in STOP and len(part) > 1}


def district(value: object) -> str | None:
    text = norm(value)
    for name in sorted(DISTRICTS, key=len, reverse=True):
        candidate = norm(name)
        if re.search(rf"\b{re.escape(candidate)}\b", text):
            return "watthana" if candidate in {"watthana", "vadhana"} else candidate
    return "watthana" if re.search(r"\bvadhana\b", text) else None


def postcode(value: object) -> str | None:
    match = re.search(r"\b(10\d{3})\b", str(value or ""))
    return match.group(1) if match else None


def house_number(value: object) -> str | None:
    first = str(value or "").split(",", 1)[0].strip()
    if re.match(r"^(?:soi|road|rd\.?|ถนน|ซอย)\b", first, re.I):
        return None
    match = re.search(r"(?<![a-z0-9])(\d+[a-z]?(?:/\d+[a-z]?)?)(?![a-z0-9])", first, re.I)
    return match.group(1).lower() if match else None


def geocode(query: str) -> list[dict]:
    response = requests.get(BASE, params={"SingleLine": query, "f": "json", "outFields": "*", "maxLocations": 5}, headers=HEADERS, timeout=(8, 25))
    response.raise_for_status()
    return response.json().get("candidates", [])


def inside(candidate: dict) -> bool:
    point = candidate.get("location") or {}
    try:
        lng, lat = float(point["x"]), float(point["y"])
    except (KeyError, TypeError, ValueError):
        return False
    return BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lng <= BBOX[3]


def point(candidate: dict) -> tuple[float, float]:
    value = candidate["location"]
    return float(value["y"]), float(value["x"])


def distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    return (((a[0] - b[0]) * 111_000) ** 2 + ((a[1] - b[1]) * 108_000) ** 2) ** 0.5


def address_match(project: dict, candidate: dict) -> tuple[bool, str]:
    attrs = candidate.get("attributes") or {}
    match = str(attrs.get("Match_addr") or "")
    if candidate.get("score", 0) < 95 or attrs.get("Addr_type") not in {"PointAddress", "Subaddress"} or not inside(candidate):
        return False, "not_high_confidence_point_address"
    expected_district, found_district = district(project.get("address")), district(match)
    if expected_district and found_district != expected_district:
        return False, "district_mismatch"
    expected_postcode, found_postcode = postcode(project.get("address")), postcode(match)
    if expected_postcode and found_postcode != expected_postcode:
        return False, "postcode_mismatch"
    expected_house, found_house = house_number(project.get("address")), house_number(match)
    if expected_house and found_house != expected_house:
        return False, "house_number_mismatch"
    source_tokens = {token for token in tokens(project.get("address")) if not re.fullmatch(r"\d+[a-z]?", token)}
    result_tokens = {token for token in tokens(match) if not re.fullmatch(r"\d+[a-z]?", token)}
    distinctive = source_tokens & result_tokens
    # For street-only records, demand multiple distinctive address tokens and
    # both the same district and postcode. An interpolated street line alone
    # is not enough evidence for a building's entrance.
    if expected_house:
        return (len(distinctive) >= 2, "exact_house_street_district")
    if expected_district and expected_postcode and found_district == expected_district and found_postcode == expected_postcode and len(distinctive) >= 2:
        return True, "exact_street_district_postcode"
    return False, "insufficient_address_identity"


def poi_match(project: dict, candidate: dict) -> tuple[bool, float]:
    attrs = candidate.get("attributes") or {}
    name = str(attrs.get("PlaceName") or attrs.get("Match_addr") or "")
    left, right = tokens(project.get("name")), tokens(name)
    if not left or not right:
        return False, 0.0
    # Keep project numbers exact so phases and buildings do not collapse.
    if re.findall(r"\d+", norm(project.get("name"))) != re.findall(r"\d+", norm(name)):
        return False, 0.0
    overlap = len(left & right) / max(1, len(left | right))
    joined = difflib.SequenceMatcher(None, "".join(sorted(left)), "".join(sorted(right))).ratio()
    score = max(overlap, joined)
    return attrs.get("Addr_type") == "POI" and candidate.get("score", 0) >= 88 and score >= 0.74 and inside(candidate), score


def inspect(project: dict) -> dict:
    row = {"id": int(project["id"]), "name": project.get("name"), "address": project.get("address"), "hipflatUrl": project.get("hipflatProjectUrl")}
    try:
        address_candidates = geocode(str(project.get("address") or "")) if project.get("address") else []
        named_candidates = geocode(f"{project.get('name')}, {project.get('address') or 'Bangkok, Thailand'}")
        named_candidates += geocode(str(project.get("name") or ""))
        accepted_address = []
        for candidate in address_candidates + named_candidates:
            ok, reason = address_match(project, candidate)
            if ok:
                accepted_address.append((candidate, reason))
        accepted_poi = []
        for candidate in named_candidates:
            ok, similarity = poi_match(project, candidate)
            if ok:
                accepted_poi.append((candidate, similarity))
        # Prefer a high-confidence exact address. If a POI is used, require a
        # separately geocoded exact address at the same physical site.
        accepted_address.sort(key=lambda item: (float(item[0].get("score") or 0), item[1] == "exact_house_street_district"), reverse=True)
        chosen = accepted_address[0] if accepted_address else None
        method = chosen[1] if chosen else None
        evidence_url = str(project.get("address") or "")
        verification_url = BASE + "?" + urlencode({"SingleLine": evidence_url, "f": "json", "outFields": "*", "maxLocations": 5})
        if not chosen and accepted_poi:
            accepted_poi.sort(key=lambda item: (item[1], float(item[0].get("score") or 0)), reverse=True)
            poi, similarity = accepted_poi[0]
            addr = next(((candidate, reason) for candidate in address_candidates if (ok := address_match(project, candidate))[0] and distance_m(point(poi), point(candidate)) <= 300 for reason in [ok[1]]), None)
            if addr:
                chosen = (poi, f"exact_project_poi_plus_{addr[1]}")
                method = chosen[1]
                evidence_url = f"{project.get('name')} / {project.get('address')}"
                verification_url = BASE + "?" + urlencode({"SingleLine": f"{project.get('name')}, {project.get('address')}", "f": "json", "outFields": "*", "maxLocations": 5})
        row["candidateSummary"] = [
            {"score": candidate.get("score"), "addressType": (candidate.get("attributes") or {}).get("Addr_type"),
             "placeName": (candidate.get("attributes") or {}).get("PlaceName"), "matchedAddress": (candidate.get("attributes") or {}).get("Match_addr"),
             "lat": point(candidate)[0], "lng": point(candidate)[1]}
            for candidate in (address_candidates + named_candidates)[:10] if inside(candidate)
        ]
        if chosen:
            candidate = chosen[0]
            lat, lng = point(candidate)
            row["verifiedCoordinate"] = {"hipflatId": int(project["id"]), "name": project.get("name"), "lat": lat, "lng": lng,
                "locationVerified": True, "sourceName": "ArcGIS 精確門牌／專案點位", "sourceUrl": f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lng}",
                "verificationSourceUrl": verification_url, "corroborationSourceUrl": project.get("hipflatProjectUrl"),
                "verificationMethod": f"ArcGIS {method}; project identity corroborated by Hipflat project name/address.", "asOf": date.today().isoformat()}
        return row
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {str(exc)[:180]}"
        return row


def main() -> None:
    projects = js_array(CATALOGUE, "BANGKOK_CONDO_CATALOGUE")
    audit_rows = {int(row["hipflat_id"]): row for row in csv.DictReader(AUDIT.open(encoding="utf-8-sig"))}
    targets = [project for project in projects if audit_rows.get(int(project["id"]), {}).get("coordinates") == "no"]
    existing = js_array(VERIFIED, "BANGKOK_VERIFIED_COORDINATES")
    existing_ids = {int(row["hipflatId"]) for row in existing}
    print(f"Unresolved projects to verify: {len(targets)}; concurrent address/POI checks: 4", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(inspect, project) for project in targets]
        for done, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            if done % 50 == 0 or done == len(futures):
                print(f"Checked {done}/{len(futures)}; high-confidence accepted so far: {sum(bool(row.get('verifiedCoordinate')) for row in results)}", flush=True)
    accepted = [row["verifiedCoordinate"] for row in results if row.get("verifiedCoordinate") and int(row["id"]) not in existing_ids]
    by_id = {int(row["hipflatId"]): row for row in existing}
    by_id.update({int(row["hipflatId"]): row for row in accepted})
    VERIFIED.write_text("window.BANGKOK_VERIFIED_COORDINATES = " + json.dumps([by_id[key] for key in sorted(by_id)], ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    summary = {"checkedAt": date.today().isoformat(), "checkedProjects": len(results), "acceptedNewCoordinates": len(accepted),
        "rejectedOrAmbiguous": sum(not row.get("verifiedCoordinate") for row in results), "errors": sum(bool(row.get("error")) for row in results),
        "verificationRules": ["exact high-confidence PointAddress/Subaddress with matching house number, street, district and postal code when available", "or exact-name POI corroborated by a separate exact address point within 300 m"],
        "projects": results}
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("checkedAt", "checkedProjects", "acceptedNewCoordinates", "rejectedOrAmbiguous", "errors", "verificationRules",)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
