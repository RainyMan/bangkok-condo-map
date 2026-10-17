"""Verify a small set of high-confidence PropertyHub title spelling variants."""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import unicodedata
from collections import Counter
from datetime import date
from difflib import SequenceMatcher

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
sys.path.insert(0, str(ROOT / "scripts"))
import geocode_propertyhub_guess as base

CANDIDATES = [
    {"hipflatProjectId": 5033, "hipflatName": "Regent Home 15 Chaengwattana", "district": "Bang Khen", "propertyHubProjectId": "704", "propertyHubName": "Regent Home 15 Chaengwattana", "slug": "regent-home-15-chaengwattana"},
    {"hipflatProjectId": 4796, "hipflatName": "Regent Home 10 Chaengwattana", "district": "Bang Khen", "propertyHubProjectId": "702", "propertyHubName": "Regent Home 10 Chaengwattana", "slug": "regent-home-10-chaengwattana"},
    {"hipflatProjectId": 6281, "hipflatName": "Regal Sathon - Naradhiwas", "district": "Sathon", "propertyHubProjectId": "3986", "propertyHubName": "Regal Sathon - Naradhiwas", "slug": "regal-sathon-naradhiwas"},
    {"hipflatProjectId": 5165, "hipflatName": "Nue Connex Donmueang", "district": "Don Mueang", "propertyHubProjectId": "4252", "propertyHubName": "Nue Connex Donmueang", "slug": "nue-connex-donmueang"},
    {"hipflatProjectId": 4272, "hipflatName": "Formosa Ratchayothin", "district": "Chatuchak", "propertyHubProjectId": "3957", "propertyHubName": "Formosa Ratchayothin", "slug": "formosa-ratchayothin"},
    {"hipflatProjectId": 6011, "hipflatName": "Bang Aor Riverside Tower", "district": "Bang Phlat", "propertyHubProjectId": "2861", "propertyHubName": "Bang Aor Riverside Tower", "slug": "bang-aor-riverside-tower"},
    {"hipflatProjectId": 5880, "hipflatName": "Origin Play Sri Lasalle Station", "district": "Bang Na", "propertyHubProjectId": "4478", "propertyHubName": "Origin Play Sri Lasalle Station", "slug": "origin-play-sri-lasalle-station"},
    {"hipflatProjectId": 5964, "hipflatName": "Baan Sukhothai Ramkhamhaeng", "district": "Bang Kapi", "propertyHubProjectId": "19292", "propertyHubName": "Baan Sukhothai Ramklamhaeng condominium", "slug": "baan-sukhothai-ramkhamhaeng-condominium---19292"},
    {"hipflatProjectId": 4136, "hipflatName": "Lumpini Condo Town Ramindra - Latplakhao", "district": "Bang Khen", "propertyHubProjectId": "1897", "propertyHubName": "Lumpini Condo Town Raminthra - Latplakhao", "slug": "lumpini-condo-town-raminthra-latplakhao"},
    {"hipflatProjectId": 5168, "hipflatName": "Tanyakarn Condominium", "district": "Huai Khwang", "propertyHubProjectId": "2382", "propertyHubName": "Thanyakarn Condominium", "slug": "thanyakarn-condominium"},
    {"hipflatProjectId": 4906, "hipflatName": "39 Suites", "district": "Watthana", "propertyHubProjectId": "244", "propertyHubName": "39 Suite", "slug": "39-suite"},
    {"hipflatProjectId": 4087, "hipflatName": "Baan Boonpitak", "district": "Suan Luang", "propertyHubProjectId": "2635", "propertyHubName": "Baan Boonyapitak", "slug": "baan-boonyapitak"},
    {"hipflatProjectId": 4464, "hipflatName": "Choke Thanachai Condominium", "district": "Min Buri", "propertyHubProjectId": "23115", "propertyHubName": "Chokthanachai Condominium", "slug": "chokthanachai-condominium"},
    {"hipflatProjectId": 6255, "hipflatName": "Metro Luxe Rose Gold Phaholyothin - Sutthisan", "district": "Phaya Thai", "propertyHubProjectId": "3124", "propertyHubName": "Metro Luxe Rose Gold Phahol - Sutthisan", "slug": "metro-luxe-rose-gold-phahol-sutthisan"},
    {"hipflatProjectId": 3443, "hipflatName": "Nirund Residence 9 Udom Suk", "district": "Bang Na", "propertyHubProjectId": "14279", "propertyHubName": "Niran Residence 9 Udom Suk", "slug": "niran-residence-9-udom-suk---14279"},
    {"hipflatProjectId": 3140, "hipflatName": "Baan Nonzee Condominium", "district": "Sathon", "propertyHubProjectId": "1583", "propertyHubName": "Baan Nonsee", "slug": "baan-nonsee--2"},
    {"hipflatProjectId": 4602, "hipflatName": "Yen Akard Garden", "district": "Yan Nawa", "propertyHubProjectId": "4917", "propertyHubName": "Yen Akat Garden", "slug": "yen-akat-garden"},
    {"hipflatProjectId": 5648, "hipflatName": "Lamsalee Mansion", "district": "Bang Kapi", "propertyHubProjectId": "2591", "propertyHubName": "Lamsali Mansion", "slug": "lamsali-mansion"},
    {"hipflatProjectId": 3206, "hipflatName": "NUE Epic Asok-Rama9", "district": "Din Daeng", "propertyHubProjectId": "21678", "propertyHubName": "NUE Epic Asoke - Rama 9", "slug": "nue-epic-asoke-rama-9"},
    {"hipflatProjectId": 5233, "hipflatName": "Baan Sri Nawamin 2", "district": "Bang Kapi", "propertyHubProjectId": "9322", "propertyHubName": "Baan Sri Nawamin 2 By NHA", "slug": "baan-sri-nawamin-2-by-nha"},
]


def norm(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def name_key(value: str) -> str:
    stop = {"a", "an", "at", "by", "in", "of", "on", "the", "condo", "condominium", "residence", "residences", "apartment", "apartments", "tower"}
    return " ".join(sorted(token for token in norm(value).split() if token not in stop))


def district(value: str) -> str | None:
    from audit_propertyhub_city_listings import district as parse_district
    return parse_district(value)


def read_array(file: str, symbol: str) -> list[dict]:
    return base.read_array(DIST / file, symbol)


def main() -> None:
    pages = RESEARCH / "propertyhub-bangkok-pages.jsonl"
    listing_stats: dict[str, Counter] = {row["propertyHubProjectId"]: Counter() for row in CANDIDATES}
    names_seen: dict[str, Counter] = {row["propertyHubProjectId"]: Counter() for row in CANDIDATES}
    needed = set(listing_stats)
    with pages.open(encoding="utf-8") as source:
        for line in source:
            page = json.loads(line)
            for item in page.get("listings", []):
                pid = str(item.get("projectId") or "")
                if pid not in needed:
                    continue
                listing_stats[pid][district(item.get("address", "")) or "unknown"] += 1
                if item.get("projectName"):
                    names_seen[pid][item["projectName"]] += 1

    rows = []
    report = []
    for candidate in CANDIDATES:
        pid = candidate["propertyHubProjectId"]
        cards = listing_stats[pid]
        total = sum(cards.values())
        target_district = district(candidate["district"])
        district_share = cards.get(target_district, 0) / total if total else 0
        listing_name = names_seen[pid].most_common(1)[0][0] if names_seen[pid] else ""
        url = f"https://propertyhub.in.th/en/projects/{candidate['slug']}"
        status = "verified"
        record = {"hipflatProjectId": candidate["hipflatProjectId"], "name": candidate["hipflatName"], "propertyHubProjectId": pid, "sourceUrl": url, "listingCards": total, "listingDistrictShare": round(district_share, 4), "listingName": listing_name}
        if not total or district_share < 0.95 or not listing_name:
            report.append({**record, "status": "listing_district_not_confirmed"})
            continue
        if not re.findall(r"\d+", norm(candidate["hipflatName"])) == re.findall(r"\d+", norm(listing_name)):
            report.append({**record, "status": "phase_or_number_conflict"})
            continue
        if SequenceMatcher(None, name_key(candidate["hipflatName"]), name_key(listing_name)).ratio() < 0.90:
            report.append({**record, "status": "listing_name_too_different"})
            continue
        try:
            response = base.requests.get(url, headers=base.HEADERS, timeout=(8, 25))
            if response.status_code != 200:
                report.append({**record, "status": f"http_{response.status_code}"})
                continue
            project = base.find_project(response.text)
            if not project:
                report.append({**record, "status": "project_data_missing"})
                continue
            if str(project.get("id")) != pid:
                report.append({**record, "status": "project_id_mismatch", "foundId": project.get("id")})
                continue
            found = project.get("nameEnglish") or project.get("name") or ""
            page_district = district(project.get("address") or "")
            if norm(found) != norm(listing_name):
                report.append({**record, "status": "project_title_mismatch", "pageName": found})
                continue
            if page_district != target_district:
                report.append({**record, "status": "project_district_mismatch", "pageName": found, "pageDistrict": page_district})
                continue
            point = project.get("location") or {}
            lat, lng = float(point["lat"]), float(point["lng"])
            if not (13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0):
                report.append({**record, "status": "coordinates_outside_bangkok", "pageName": found})
                continue
            info = project.get("projectInfo") or {}
            detail = {
                "hipflatProjectId": candidate["hipflatProjectId"], "propertyHubProjectId": pid,
                "name": candidate["hipflatName"], "projectName": found,
                "propertyHubListingProjectName": listing_name,
                "projectSlug": project.get("slug") or candidate["slug"],
                "projectAddress": project.get("address"), "lat": lat, "lng": lng,
                "locationVerified": True,
                "identityMatchMethod": "exact_propertyhub_id_plus_high_confidence_name_and_listing_district",
                "identityMatchScore": round(100 * SequenceMatcher(None, name_key(candidate["hipflatName"]), name_key(listing_name)).ratio(), 2),
                "listingDistrictShare": round(district_share, 4),
                "listingCards": total,
                "locationSourceName": "PropertyHub 專案頁（專案 ID＋樓盤名＋行政區核對）",
                "locationSourceUrl": url, "completedYearSourceUrl": url,
                "asOf": date.today().isoformat(),
            }
            for key, target in (("completedYear", "completedYear"), ("totalUnits", "units"), ("buildingsFloors", "floors")):
                if str(info.get(key, "")).isdigit():
                    detail[target] = int(info[key])
            fee = re.search(r"(\d+(?:\.\d+)?)", str(info.get("utilityFee") or ""))
            if fee and 1 <= float(fee.group(1)) <= 1000:
                detail["fee"] = {"rate": float(fee.group(1)), "note": "PropertyHub 專案頁公布數值；現行費率請向管委會確認。", "source": url, "status": "published_indicative"}
            rows.append(detail)
            report.append({**record, "status": status, "pageName": found, "pageDistrict": page_district, "lat": lat, "lng": lng})
            time.sleep(1.1)
        except Exception as error:
            report.append({**record, "status": "fetch_error", "error": type(error).__name__})

    output = read_array("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
    by_project = {int(row["hipflatProjectId"]): row for row in output if row.get("hipflatProjectId")}
    for row in rows:
        by_project[int(row["hipflatProjectId"])] = row
    target = DIST / "bangkok-propertyhub-guessed-details.js"
    temp = target.with_suffix(".js.tmp")
    temp.write_text("window.BANGKOK_PROPERTYHUB_GUESSED_DETAILS = " + json.dumps(sorted(by_project.values(), key=lambda item: int(item["hipflatProjectId"])), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    temp.replace(target)
    (RESEARCH / "propertyhub-extra-fuzzy-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidateCount": len(CANDIDATES), "verifiedAdded": len(rows), "results": report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
