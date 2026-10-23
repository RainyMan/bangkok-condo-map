"""Add exact Bangkok project POIs when their published POI address matches Hipflat."""
from __future__ import annotations

import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

import requests

from enrich_arcgis_unlocated_coordinates_2026_10_23 import (
    AUDIT, BBOX, DIST, HEADERS, REPORT as PREVIOUS_REVIEW, VERIFIED,
    address_match, district, house_number, inside, js_array, point, poi_match,
    postcode, tokens,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / f"arcgis-exact-poi-coordinate-review-{date.today().isoformat()}.json"
BASE = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
STOP_ADDRESS = {"soi", "road", "rd", "street", "bangkok", "thailand", "tha", "province", "district", "subdistrict", "tambon", "khet", "kwaeng"}


def geocode(query: str) -> list[dict]:
    response = requests.get(BASE, params={"SingleLine": query, "f": "json", "outFields": "*", "maxLocations": 10}, headers=HEADERS, timeout=(8, 25))
    response.raise_for_status()
    return response.json().get("candidates", [])


def inspect(project: dict, duplicate_names: set[int]) -> dict:
    result = {"id": int(project["id"]), "name": project.get("name"), "address": project.get("address"), "hipflatUrl": project.get("hipflatProjectUrl")}
    try:
        query = f"{project.get('name')}, {project.get('address') or 'Bangkok, Thailand'}"
        candidates = geocode(query)
        accepted = []
        for candidate in candidates:
            attrs = candidate.get("attributes") or {}
            matched, name_similarity = poi_match(project, candidate)
            if not matched or candidate.get("score", 0) < 88:
                continue
            if attrs.get("Region") and district(attrs.get("Region")) not in (None, "bangkok"):
                continue
            if attrs.get("Country") and str(attrs.get("Country")).upper() not in {"THA", "THAILAND"}:
                continue
            place_address = " ".join(str(attrs.get(key) or "") for key in ("Place_addr", "LongLabel", "Nbrhd", "City", "Subregion", "Region", "Postal"))
            wanted_district, found_district = district(project.get("address")), district(place_address)
            if not wanted_district or found_district != wanted_district:
                continue
            wanted_postcode, found_postcode = postcode(project.get("address")), postcode(place_address)
            if wanted_postcode and wanted_postcode != found_postcode:
                continue
            # The POI must return at least one address token beyond generic
            # Bangkok/administrative terms, unless the source provides a full
            # postal code that also matches exactly.
            expected_address = tokens(project.get("address")) - STOP_ADDRESS
            returned_address = tokens(place_address) - STOP_ADDRESS
            if wanted_postcode:
                expected_address.discard(wanted_postcode)
                returned_address.discard(wanted_postcode)
            address_overlap = expected_address & returned_address
            if not address_overlap and not wanted_postcode:
                continue
            if int(project["id"]) in duplicate_names:
                distinctive_overlap = address_overlap - tokens(wanted_district or "")
                if not distinctive_overlap:
                    continue
            if not inside(candidate):
                continue
            accepted.append((candidate, name_similarity, sorted(address_overlap)))
        result["candidateSummary"] = [
            {"score": candidate.get("score"), "type": (candidate.get("attributes") or {}).get("Addr_type"),
             "placeName": (candidate.get("attributes") or {}).get("PlaceName"),
             "placeAddress": (candidate.get("attributes") or {}).get("Place_addr"),
             "lat": point(candidate)[0], "lng": point(candidate)[1]}
            for candidate in candidates if inside(candidate)
        ]
        if accepted:
            accepted.sort(key=lambda row: (row[1], float(row[0].get("score") or 0), len(row[2])), reverse=True)
            candidate, similarity, address_overlap = accepted[0]
            lat, lng = point(candidate)
            query_url = BASE + "?" + urlencode({"SingleLine": query, "f": "json", "outFields": "*", "maxLocations": 10})
            result["verifiedCoordinate"] = {
                "hipflatId": int(project["id"]), "name": project.get("name"), "lat": lat, "lng": lng,
                "locationVerified": True, "sourceName": "ArcGIS 精確樓盤 POI＋地址核對",
                "sourceUrl": f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lng}",
                "verificationSourceUrl": query_url, "corroborationSourceUrl": project.get("hipflatProjectUrl"),
                "verificationMethod": f"ArcGIS exact-name POI ({similarity:.2f}); Hipflat district/postcode/address matched ({','.join(address_overlap) or 'exact postcode'}).",
                "asOf": date.today().isoformat(),
            }
        return result
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {str(error)[:180]}"
        return result


def main() -> None:
    projects = js_array(DIST / "bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    current_audit = {int(row["hipflat_id"]): row for row in __import__("csv").DictReader(AUDIT.open(encoding="utf-8-sig"))}
    targets = [project for project in projects if current_audit.get(int(project["id"]), {}).get("coordinates") == "no"]
    by_normalized: dict[str, list[dict]] = {}
    for project in projects:
        key = re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", str(project.get("name") or "")).encode("ascii", "ignore").decode().lower()).strip()
        by_normalized.setdefault(key, []).append(project)
    duplicate_names = {int(project["id"]) for group in by_normalized.values() if len(group) > 1 for project in group}
    print(f"Missing-coordinate projects to check for address-matched POIs: {len(targets)}; workers: 4", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(inspect, project, duplicate_names) for project in targets]
        for done, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            if done % 50 == 0 or done == len(futures):
                print(f"Checked {done}/{len(futures)}; exact POIs accepted: {sum(bool(row.get('verifiedCoordinate')) for row in results)}", flush=True)
    existing = js_array(VERIFIED, "BANGKOK_VERIFIED_COORDINATES")
    by_id = {int(row["hipflatId"]): row for row in existing}
    accepted = [row["verifiedCoordinate"] for row in results if row.get("verifiedCoordinate")]
    by_id.update({int(row["hipflatId"]): row for row in accepted})
    VERIFIED.write_text("window.BANGKOK_VERIFIED_COORDINATES = " + json.dumps([by_id[key] for key in sorted(by_id)], ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    summary = {"checkedAt": date.today().isoformat(), "checkedProjects": len(results), "acceptedNewCoordinates": len(accepted),
        "ambiguousOrNoMatch": sum(not row.get("verifiedCoordinate") for row in results), "errors": sum(bool(row.get("error")) for row in results),
        "method": "High-confidence ArcGIS POI with exact project-name/phase match and same Bangkok district, plus matching postal code or address token, corroborated by the exact Hipflat project page.", "projects": results}
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "projects"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
