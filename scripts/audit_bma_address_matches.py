"""Suggest conservative links from Hipflat projects to BMA residential buildings."""
from __future__ import annotations

import json
import pathlib
import re
import sys
import unicodedata

from pythainlp.transliterate import romanize
from rapidfuzz import fuzz

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
BUILDINGS = RESEARCH / "bma-type6-addresses.jsonl"
OUTPUT = RESEARCH / "bma-address-candidates.json"
PROJECT_DISTRICTS = (
    "Pom Prap Sattru Phai", "Thawi Watthana", "Khlong Sam Wa", "Bang Khun Thian", "Bang Kho Laem", "Saphan Sung",
    "Bangkok Yai", "Bangkok Noi", "Phaya Thai", "Phra Khanong", "Ratchathewi", "Samphanthawong", "Wang Thonglang",
    "Huai Khwang", "Khan Na Yao", "Lat Krabang", "Bueng Kum", "Chom Thong", "Don Mueang", "Nong Chok", "Nong Khaem",
    "Pathum Wan", "Phasi Charoen", "Phra Nakhon", "Rat Burana", "Taling Chan", "Thung Khru", "Bang Kapi", "Bang Khae",
    "Bang Khen", "Bang Na", "Bang Phlat", "Bang Rak", "Bang Sue", "Chatuchak", "Din Daeng", "Dusit", "Khlong San",
    "Khlong Toei", "Lak Si", "Lat Phrao", "Min Buri", "Prawet", "Sai Mai", "Sathon", "Suan Luang", "Thon Buri",
    "Yan Nawa", "Bang Bon",
)
DISTRICT_TH = {
    "Pom Prap Sattru Phai": "ป้อมปราบศัตรูพ่าย", "Thawi Watthana": "ทวีวัฒนา", "Khlong Sam Wa": "คลองสามวา",
    "Bang Khun Thian": "บางขุนเทียน", "Bang Kho Laem": "บางคอแหลม", "Saphan Sung": "สะพานสูง",
    "Bangkok Yai": "บางกอกใหญ่", "Bangkok Noi": "บางกอกน้อย", "Phaya Thai": "พญาไท", "Phra Khanong": "พระโขนง",
    "Ratchathewi": "ราชเทวี", "Samphanthawong": "สัมพันธวงศ์", "Wang Thonglang": "วังทองหลาง",
    "Huai Khwang": "ห้วยขวาง", "Khan Na Yao": "คันนายาว", "Lat Krabang": "ลาดกระบัง", "Bueng Kum": "บึงกุ่ม",
    "Chom Thong": "จอมทอง", "Don Mueang": "ดอนเมือง", "Nong Chok": "หนองจอก", "Nong Khaem": "หนองแขม",
    "Pathum Wan": "ปทุมวัน", "Phasi Charoen": "ภาษีเจริญ", "Phra Nakhon": "พระนคร", "Rat Burana": "ราษฎร์บูรณะ",
    "Taling Chan": "ตลิ่งชัน", "Thung Khru": "ทุ่งครุ", "Bang Kapi": "บางกะปิ", "Bang Khae": "บางแค",
    "Bang Khen": "บางเขน", "Bang Na": "บางนา", "Bang Phlat": "บางพลัด", "Bang Rak": "บางรัก", "Bang Sue": "บางซื่อ",
    "Chatuchak": "จตุจักร", "Din Daeng": "ดินแดง", "Dusit": "ดุสิต", "Khlong San": "คลองสาน", "Khlong Toei": "คลองเตย",
    "Lak Si": "หลักสี่", "Lat Phrao": "ลาดพร้าว", "Min Buri": "มีนบุรี", "Prawet": "ประเวศ", "Sai Mai": "สายไหม",
    "Sathon": "สาทร", "Suan Luang": "สวนหลวง", "Thon Buri": "ธนบุรี", "Yan Nawa": "ยานนาวา", "Bang Bon": "บางบอน",
    "Watthana": "วัฒนา",
}
STOP = {"soi", "road", "rd", "street", "thanon", "thanom", "yaek", "khwaeng", "khet", "bangkok", "thailand", "bkk", "at"}


def arr(file: str, symbol: str) -> list[dict]:
    import re
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", (DIST / file).read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {file}")
    return json.loads(match.group(1))


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def toks(value: str) -> set[str]:
    return {x for x in norm(value).split() if x not in STOP and (len(x) > 1 or x.isdigit())}


def get_district(address: str) -> str | None:
    for label in sorted(PROJECT_DISTRICTS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(label.lower())}\b", address.lower()):
            return label
    if re.search(r"\b(vadhana|watthana)\b", address.lower()):
        return "Watthana"
    return None


def project_house(address: str) -> str | None:
    # House numbers normally precede the street clause. Exclude numbers that
    # begin after a Soi marker, since those belong to the lane, not the house.
    for match in re.finditer(r"(?<![a-z0-9])(\d+[a-z]?(?:/\d+[a-z]?)?)(?![a-z0-9])", address.lower()):
        before = address[:match.start()].lower()
        if re.search(r"\b(soi|yaek|road|rd|street)\b", before):
            continue
        if match.group(1).isdigit() and len(match.group(1)) > 4:
            continue
        return match.group(1)
    return None


def project_streets(address: str) -> tuple[set[str], set[str]]:
    low = address.lower()
    soi = set()
    road = set()
    for match in re.finditer(r"\bsoi\b\s*([^,]+)", low):
        clause = re.split(r"\b(?:yaek|khwaeng|khet|district|subdistrict)\b", match.group(1))[0]
        soi |= toks(clause)
    for match in re.finditer(r"\b(?:road|rd|street)\b", low):
        start = max(low.rfind(",", 0, match.start()), low.rfind(";", 0, match.start())) + 1
        clause = low[start:match.end()]
        # Include the road name immediately before the suffix.
        words = toks(clause)
        road |= words
    return soi, road


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    projects = arr("bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    ph = {int(x["id"]): x for x in arr("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")}
    details = {str(x.get("propertyHubProjectId")): x for x in arr("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")}
    guessed = {int(x["hipflatProjectId"]): x for x in arr("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS") if x.get("locationVerified")}
    located = {int(x["id"]) for x in arr("bangkok-osm.js", "BANGKOK_OSM_LOCATIONS")}
    for p in projects:
        pid = int(p["id"])
        base = ph.get(pid) or {}
        detail = details.get(str(base.get("propertyHubProjectId") or ""))
        if p.get("locationVerified") or base.get("locationVerified") or (detail and detail.get("locationVerified")) or pid in guessed:
            located.add(pid)
    missing = [p for p in projects if int(p["id"]) not in located]
    building_file = BUILDINGS if BUILDINGS.exists() else RESEARCH / "bma-type6-named-buildings.jsonl"
    buildings = [json.loads(line) for line in building_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    by_key: dict[tuple[str, str, str], list[dict]] = {}
    by_house_district: dict[tuple[str, str], list[dict]] = {}
    for b in buildings:
        house = re.sub(r"\s+", "", str(b.get("BL_HOUSENUM") or "")).lower()
        postcode = re.sub(r"\D", "", str(b.get("BL_POSTCODE") or ""))
        district = str(b.get("BL_DISTRICT") or "").strip()
        if house:
            by_key.setdefault((house, postcode, district), []).append(b)
            by_house_district.setdefault((house, district), []).append(b)

    candidates = []
    for p in missing:
        address = str(p.get("address") or "")
        house = project_house(address)
        district = get_district(address)
        if not house or not district:
            continue
        bma_district = DISTRICT_TH[district]
        post = re.search(r"\b(\d{5})\b", address)
        postcode = post.group(1) if post else ""
        soi_tokens, road_tokens = project_streets(address)
        if not soi_tokens and not road_tokens:
            continue
        key_rows = by_key.get((house, postcode, bma_district), []) if postcode else []
        if not key_rows:
            key_rows = by_house_district.get((house, bma_district), [])
        for b in key_rows:
            bma_postcode = re.sub(r"\D", "", str(b.get("BL_POSTCODE") or ""))
            if postcode and bma_postcode and postcode != bma_postcode:
                continue
            thai_street = " ".join(str(b.get(k) or "") for k in ("BL_ROAD", "BL_SOI"))
            roman_street = romanize(thai_street) if re.search(r"[\u0e00-\u0e7f]", thai_street) else thai_street
            bma_tokens = toks(roman_street)
            soi_overlap = soi_tokens & toks(romanize(str(b.get("BL_SOI") or "")))
            road_overlap = road_tokens & toks(romanize(str(b.get("BL_ROAD") or "")))
            # Require a meaningful alphabetic road/soi name match; numeric
            # lane fragments alone (for example "1") cannot verify an address.
            alpha_overlap = {token for token in (soi_overlap | road_overlap) if any(ch.isalpha() for ch in token)}
            if not alpha_overlap:
                continue
            if soi_tokens and not soi_overlap:
                continue
            if not soi_tokens and road_tokens and not road_overlap:
                continue
            project_numbers = {x for x in soi_tokens if x.isdigit()}
            bma_soi_numbers = {x for x in toks(romanize(str(b.get("BL_SOI") or ""))) if x.isdigit()}
            if project_numbers and bma_soi_numbers and not (project_numbers & bma_soi_numbers):
                continue
            source_name = str(b.get("BL_NAME") or "").strip()
            latin_name = romanize(source_name) if re.search(r"[\u0e00-\u0e7f]", source_name) else source_name
            name_score = fuzz.token_set_ratio(norm(p["name"]), norm(latin_name)) if latin_name else 0
            candidates.append({
                "id": int(p["id"]), "name": p["name"], "lat": None, "lng": None,
                "bmaObjectId": int(b["OBJECTID"]), "bmaBuildingId": b.get("BLDG_ID"),
                "bmaName": source_name, "bmaNameRomanized": latin_name,
                "bmaAddress": b.get("BL_ADDRESS"), "houseNumber": house,
                "postcodeMatch": bool(postcode and postcode == re.sub(r"\D", "", str(b.get("BL_POSTCODE") or ""))),
                "district": district, "streetOverlap": sorted(soi_overlap or road_overlap),
                "nameScore": name_score, "bmaUpdateYear": b.get("UPDATE_YEAR"),
                "sourceUrl": f"http://3d-cpd.bangkok.go.th/ArcGIS/rest/services/BMA3D_3DService/MapServer/25/query?objectIds={b['OBJECTID']}&outFields=OBJECTID%2CBL_NAME%2CBL_ADDRESS%2CBL_HOUSENUM%2CBL_ROAD%2CBL_SOI%2CBL_DISTRICT%2CBL_POSTCODE&returnGeometry=true&outSR=4326&f=pjson",
            })
    # Keep all candidate records: downstream review checks whether one exact
    # building remains for each project before any point enters the live map.
    candidates.sort(key=lambda r: (r["id"], -r["nameScore"]))
    by_project: dict[int, list[dict]] = {}
    for row in candidates:
        by_project.setdefault(row["id"], []).append(row)
    report = {
        "matchedProjects": len(by_project), "candidateRecords": len(candidates),
        "uniqueProjectCandidates": sum(len(rows) == 1 for rows in by_project.values()),
        "projects": [{"id": pid, "name": rows[0]["name"], "candidates": rows} for pid, rows in by_project.items()],
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    examples = [{key: row.get(key) for key in ("id", "name", "bmaObjectId", "bmaName", "bmaAddress", "houseNumber", "postcodeMatch", "district", "streetOverlap", "nameScore", "bmaUpdateYear")} for row in candidates[:15]]
    print(json.dumps({"matchedProjects": report["matchedProjects"], "candidateRecords": len(candidates), "uniqueProjectCandidates": report["uniqueProjectCandidates"], "examples": examples}, ensure_ascii=False))


if __name__ == "__main__":
    main()
