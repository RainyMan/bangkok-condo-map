"""Keep only OSM project matches supported by the mapped object's name."""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
STOP = {
    "condo", "condominium", "residence", "residences", "apartment", "apartments",
    "tower", "building", "bangkok", "the", "at", "by", "and", "park", "place",
    "project", "a",
}


def array(path: pathlib.Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def tokens(value: str) -> set[str]:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    parts = re.sub(r"[^a-z0-9]+", " ", text).split()
    return {part for part in parts if part not in STOP and (len(part) > 1 or part.isdigit() or part in {"q", "i", "m", "s"})}


def address_tokens(value: str) -> set[str]:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    parts = re.sub(r"[^a-z0-9]+", " ", text).split()
    admin = {word for item in ("Pom Prap Sattru Phai", "Thawi Watthana", "Khlong Sam Wa", "Bang Khun Thian", "Bang Kho Laem", "Saphan Sung", "Bangkok Yai", "Bangkok Noi", "Phaya Thai", "Phra Khanong", "Ratchathewi", "Samphanthawong", "Wang Thonglang", "Huai Khwang", "Khan Na Yao", "Lat Krabang", "Bueng Kum", "Chom Thong", "Don Mueang", "Nong Chok", "Nong Khaem", "Pathum Wan", "Phasi Charoen", "Phra Nakhon", "Rat Burana", "Taling Chan", "Thung Khru", "Bang Kapi", "Bang Khae", "Bang Khen", "Bang Na", "Bang Phlat", "Bang Rak", "Bang Sue", "Chatuchak", "Din Daeng", "Dusit", "Khlong San", "Khlong Toei", "Lak Si", "Lat Phrao", "Min Buri", "Prawet", "Sai Mai", "Sathon", "Suan Luang", "Thon Buri", "Yan Nawa", "Bang Bon", "Watthana") for word in item.lower().split()}
    stop = {"soi", "road", "rd", "street", "st", "bangkok", "thailand", "province", "district", "subdistrict", "tambon", "khet", "kwaeng", "khwaeng", "postcode", "moo", "baan"} | admin
    return {part for part in parts if (len(part) > 1 or part.isdigit()) and part not in stop}


def localized_address_match(row: dict, project: dict) -> bool:
    """Allow a transliterated/local-language name only with exact address evidence."""
    evidence = row.get("matchEvidence") or {}
    project_text = re.sub(r"\s+", "", str(project.get("sourceDescription", "")))
    localized_name = re.sub(r"\s+", "", str(evidence.get("projectLocalizedName", "")))
    osm_localized_name = re.sub(r"\s+", "", str(evidence.get("osmLocalizedName", "")))
    project_address = address_tokens(str(project.get("address", "")))
    house_number_match = str(evidence.get("houseNumber", "")) in project_address
    street_tokens = tokens(str(evidence.get("street", "")))
    street_match = bool(street_tokens & project_address)
    postcode_match = str(evidence.get("postcode", "")) in project_address
    return bool(
        localized_name
        and osm_localized_name
        and localized_name in project_text
        and localized_name in osm_localized_name
        and house_number_match
        and street_match
        and postcode_match
    )


def main() -> int:
    path = DIST / "bangkok-osm.js"
    projects = {int(row["id"]): row for row in array(DIST / "bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")}
    original = array(path, "BANGKOK_OSM_LOCATIONS")
    scored = []
    for row in original:
        project_name = tokens(row.get("name", ""))
        object_name = tokens(row.get("osmName", ""))
        overlap = project_name & object_name
        score = len(overlap) / max(1, len(project_name | object_name))
        # Require two project-specific name tokens. Same-street address matches
        # cannot prove that a shop, hotel, or neighboring building is the condo.
        project = projects.get(int(row["id"]))
        project_address = address_tokens((project or {}).get("address", ""))
        object_address = address_tokens(row.get("osmAddress", ""))
        address_overlap = project_address & object_address
        address_supported = len(address_overlap) >= 2 and len(address_overlap) / max(1, len(project_address)) >= 0.5
        evidenced_score = float(row.get("nameMatchScore", score))
        if ((evidenced_score >= 0.8 and len(overlap) >= 2)
                or (evidenced_score >= 0.6 and len(overlap) >= 2 and address_supported)
                or localized_address_match(row, project or {})):
            scored.append((row, evidenced_score, project_name == object_name))

    by_object: dict[tuple[str, int], list[tuple[dict, float, bool]]] = defaultdict(list)
    for row, score, exact in scored:
        by_object[(row["osmType"], int(row["osmId"]))].append((row, score, exact))

    kept = []
    conflicts = []
    for candidates in by_object.values():
        if len(candidates) == 1:
            kept.append(candidates[0][0])
            continue
        exact = [item for item in candidates if item[2]]
        if len(exact) == 1:
            kept.append(exact[0][0])
        else:
            conflicts.extend(item[0] for item in candidates)

    kept.sort(key=lambda row: int(row["id"]))
    path.write_text(
        "window.BANGKOK_OSM_LOCATIONS = "
        + json.dumps(kept, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "before": len(original), "nameMatched": len(scored), "after": len(kept),
        "removedUnverifiedOrConflicting": len(original) - len(kept),
        "unresolvedConflicts": [
            {"id": r.get("id"), "name": r.get("name"), "osmName": r.get("osmName"), "osmUrl": r.get("sourceUrl")}
            for r in conflicts
        ],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
