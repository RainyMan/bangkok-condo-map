"""Verify a small set of high-confidence PropertyHub title spelling variants."""
from __future__ import annotations

import json
import argparse
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
    {"hipflatProjectId": 5964, "hipflatName": "Baan Sukhothai Ramkhamhaeng", "district": "Bang Kapi", "propertyHubProjectId": "1263", "propertyHubListingProjectId": "19292", "propertyHubName": "Baan Sukhothai Ramkhamhaeng 1-2", "slug": "baan-sukhothai-ramkhamhaeng-1-2", "listingNameAliasEvidenceUrl": "https://propertyhub.in.th/en/listings/a033373-baan-sukhothai-ramkhamhaeng--b12409b8---6003860", "identityEvidenceUrl": "https://www.livinginsider.com/project/baan-sukhothai-ramkhamhaeng-condo-buysell"},
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
    {"hipflatProjectId": 3206, "hipflatName": "NUE Epic Asok-Rama9", "district": "Din Daeng", "propertyHubProjectId": "21922", "propertyHubListingProjectId": "21678", "propertyHubName": "NUE Epic Asok - Rama 9", "slug": "nue-epic-asok-rama-9"},
    {"hipflatProjectId": 5233, "hipflatName": "Baan Sri Nawamin 2", "district": "Bang Kapi", "propertyHubProjectId": "9322", "propertyHubName": "Baan Sri Nawamin 2 By NHA", "slug": "baan-sri-nawamin-2-by-nha"},
    {"hipflatProjectId": 5069, "hipflatName": "Chateau in Town Sukhumvit 64 Sky Moon", "district": "Phra Khanong", "propertyHubProjectId": "1455", "propertyHubName": "Chateau in Town Sukhumvit 64 Skymoon", "slug": "chateau-in-town-sukhumvit-64-skymoon"},
    {"hipflatProjectId": 4960, "hipflatName": "Vela De Condo UTCC - Vipawadee 2", "district": "Din Daeng", "propertyHubProjectId": "3257", "propertyHubName": "Vela De Condo Vipawadee 2", "slug": "vela-de-condo-vipawadee-2"},
    {"hipflatProjectId": 5113, "hipflatName": "Supalai Premier Narathiwas - Sathorn", "district": "Yan Nawa", "propertyHubProjectId": "1554", "propertyHubName": "Supalai Premier Ratchada - Narathiwas - Sathorn", "slug": "supalai-premier-ratchada-narathiwas-sathorn"},
    {"hipflatProjectId": 4615, "hipflatName": "Metro Luxe Phaholyothin-Sutthisan", "district": "Phaya Thai", "propertyHubProjectId": "1285", "propertyHubName": "Metro Luxe Pahol - Sutthisan", "slug": "metro-luxe-pahol-sutthisan"},
    {"hipflatProjectId": 6416, "hipflatName": "D Condo Ramkhamhaeng 64", "district": "Bang Kapi", "propertyHubProjectId": "367", "propertyHubName": "dcondo Ramkhamhaeng 64", "slug": "dcondo-ramkhamhaeng-64"},
    {"hipflatProjectId": 3450, "hipflatName": "The Complete Ratchaprarop", "district": "Ratchathewi", "propertyHubProjectId": "38", "propertyHubName": "The Complete Rajprarop", "slug": "the-complete-rajprarop"},
    {"hipflatProjectId": 3721, "hipflatName": "Watermark Chaophraya River", "district": "Khlong San", "propertyHubProjectId": "782", "propertyHubName": "Watermark Chaophraya", "slug": "watermark-chaophraya"},
    {"hipflatProjectId": 5556, "hipflatName": "Charktip Court", "district": "Watthana", "propertyHubProjectId": "20624", "propertyHubName": "Chakrathip Court", "slug": "chakrathip-court---20624"},
    {"hipflatProjectId": 3213, "hipflatName": "Aspire Srinakarin", "district": "Prawet", "propertyHubProjectId": "184", "propertyHubListingProjectId": "21395", "propertyHubName": "Aspire Srinakarin", "slug": "aspire-srinakarin"},
    {"hipflatProjectId": 4491, "hipflatName": "Ruensap Condominium", "district": "Thung Khru", "propertyHubProjectId": "1942", "propertyHubName": "Ruansap Condo", "slug": "ruansap-condo"},
    {"hipflatProjectId": 6082, "hipflatName": "185 Rajadamri", "district": "Pathum Wan", "propertyHubProjectId": "1", "propertyHubName": "185 Ratchadamri", "slug": "185-ratchadamri"},
    {"hipflatProjectId": 3339, "hipflatName": "Library Houze Suk Sawat - Prachauthit", "district": "Thung Khru", "propertyHubProjectId": "2953", "propertyHubName": "Library Houze Pracha Uthit-Suk Sawat", "slug": "library-houze-pracha-uthit-suk-sawat"},
    {"hipflatProjectId": 3113, "hipflatName": "Noble ReD", "district": "Phaya Thai", "propertyHubProjectId": "529", "propertyHubName": "Noble RE D", "slug": "noble-re-d"},
    {"hipflatProjectId": 4938, "hipflatName": "JRY RAMA9 CONDOMINIUM", "district": "Huai Khwang", "propertyHubProjectId": "3199", "propertyHubName": "JRY Rama 9", "slug": "jry-rama-9"},
    {"hipflatProjectId": 4878, "hipflatName": "Fuse Mobius Ramkhamhaeng Station", "district": "Suan Luang", "propertyHubProjectId": "624", "propertyHubName": "Fuse Mobius Ramkhamhaeng - Klongton", "slug": "fuse-mobius-ramkhamhaeng-klongton", "listingNameAliasEvidenceUrl": "https://propertyhub.in.th/en/listings/a033862-fuse-mobius-ramkhamhaeng-station---6005426"},
    {"hipflatProjectId": 3011, "hipflatName": "Focus at Ploenchit", "district": "Khlong Toei", "propertyHubProjectId": "1283", "propertyHubListingProjectId": "13771", "propertyHubName": "Focus Ploenchit", "slug": "focus-ploenchit"},
    {"hipflatProjectId": 6426, "hipflatName": "Ideo Q Phahol - Saphan Khwhai", "district": "Phaya Thai", "propertyHubProjectId": "3982", "propertyHubName": "IDEO Q Phahol - Saphankhwai", "slug": "ideo-q-phahol-saphankhwai"},
    {"hipflatProjectId": 4866, "hipflatName": "Grene Prime Don Mueang-Song Prapha", "district": "Don Mueang", "propertyHubProjectId": "14829", "propertyHubName": "Grene Prime Don Mueang - Songprapa", "slug": "grene-prime-don-mueang-songprapa"},
    {"hipflatProjectId": 4690, "hipflatName": "Wongsawang Place Condominium", "district": "Bang Sue", "propertyHubProjectId": "2162", "propertyHubName": "Wong Sawang Place Condominium", "slug": "wong-sawang-place-condominium"},
    {"hipflatProjectId": 4297, "hipflatName": "Baan Ua-Athon Panya Ramintra", "district": "Khlong Sam Wa", "propertyHubProjectId": "2558", "propertyHubName": "Baan Eua Arthorn Panya Ramintha", "slug": "baan-eua-arthorn-panya-ramintha"},
    {"hipflatProjectId": 6147, "hipflatName": "The Key Chaloem Phra Kiat Rama9", "district": "Prawet", "propertyHubProjectId": "1207", "propertyHubName": "The Key Udomsuk Chaloemphrakiat Rama 9", "propertyHubProjectAlias": "The Key Chaloem Phra Kiat Rama9", "slug": "the-key-udomsuk-chaloemphrakiat-rama-9"},
    {"hipflatProjectId": 5099, "hipflatName": "Pesidence Place", "district": "Pathum Wan", "propertyHubProjectId": "1909", "propertyHubName": "President Place", "slug": "president-place"},
    {"hipflatProjectId": 4798, "hipflatName": "Klongjan Place", "district": "Bang Kapi", "propertyHubProjectId": "262", "propertyHubName": "Klongchan Place", "propertyHubProjectAlias": "Klongjan Place", "slug": "klongchan-place"},
    {"hipflatProjectId": 5641, "hipflatName": "Piamrak Residence Condo", "district": "Thon Buri", "propertyHubProjectId": "1275", "propertyHubName": "Piamrak Residence", "slug": "piamrak-residence--a64008fa"},
    {"hipflatProjectId": 5427, "hipflatName": "Rachvipa Place", "district": "Chatuchak", "propertyHubProjectId": "2862", "propertyHubName": "Ratchawipa Place", "slug": "ratchawipa-place"},
    {"hipflatProjectId": 4817, "hipflatName": "Taopoon Mansion", "district": "Bang Sue", "propertyHubProjectId": "2040", "propertyHubName": "Tao Pun Mansion", "propertyHubProjectAlias": "Taopoon Mansion", "slug": "tao-pun-mansion"},
    {"hipflatProjectId": 4760, "hipflatName": "Roong Condo", "district": "Min Buri", "propertyHubProjectId": "2906", "propertyHubName": "Roong Condominium", "propertyHubProjectAlias": "Roong Condo", "slug": "roong-condominium"},
    {"hipflatProjectId": 3186, "hipflatName": "Suwansawat Condo", "district": "Sathon", "propertyHubProjectId": "2989", "propertyHubName": "Suwansawat", "slug": "suwansawat"},
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only-hipflat-ids", nargs="+", type=int, help="Verify only these Hipflat catalogue IDs")
    args = parser.parse_args()
    candidates = [row for row in CANDIDATES if not args.only_hipflat_ids or row["hipflatProjectId"] in args.only_hipflat_ids]
    pages = RESEARCH / "propertyhub-bangkok-pages.jsonl"
    listing_stats: dict[str, Counter] = {str(row.get("propertyHubListingProjectId") or row["propertyHubProjectId"]): Counter() for row in candidates}
    names_seen: dict[str, Counter] = {str(row.get("propertyHubListingProjectId") or row["propertyHubProjectId"]): Counter() for row in candidates}
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
    for candidate in candidates:
        pid = candidate["propertyHubProjectId"]
        listing_pid = str(candidate.get("propertyHubListingProjectId") or pid)
        cards = listing_stats[listing_pid]
        total = sum(cards.values())
        target_district = district(candidate["district"])
        district_share = cards.get(target_district, 0) / total if total else 0
        listing_name = names_seen[listing_pid].most_common(1)[0][0] if names_seen[listing_pid] else ""
        url = f"https://propertyhub.in.th/en/projects/{candidate['slug']}"
        status = "verified"
        record = {"hipflatProjectId": candidate["hipflatProjectId"], "name": candidate["hipflatName"], "propertyHubProjectId": pid, "propertyHubListingProjectId": listing_pid, "sourceUrl": url, "listingCards": total, "listingDistrictShare": round(district_share, 4), "listingName": listing_name}
        if not total or district_share < 0.95 or not listing_name:
            report.append({**record, "status": "listing_district_not_confirmed"})
            continue
        if not re.findall(r"\d+", norm(candidate["hipflatName"])) == re.findall(r"\d+", norm(listing_name)):
            report.append({**record, "status": "phase_or_number_conflict"})
            continue
        normalized_score = SequenceMatcher(None, norm(candidate["hipflatName"]), norm(listing_name)).ratio()
        token_score = SequenceMatcher(None, name_key(candidate["hipflatName"]), name_key(listing_name)).ratio()
        if max(normalized_score, token_score) < 0.84 and not candidate.get("listingNameAliasEvidenceUrl") and not candidate.get("propertyHubProjectAlias"):
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
            project_aliases = (project.get("projectInfo") or {}).get("possibleProjectNames") or []
            alias_match = bool(candidate.get("propertyHubProjectAlias")) and any(
                norm(candidate["propertyHubProjectAlias"]) == norm(alias) for alias in project_aliases
            )
            if candidate.get("propertyHubProjectAlias") and not alias_match:
                report.append({**record, "status": "project_alias_mismatch", "possibleProjectNames": project_aliases})
                continue
            found = project.get("nameEnglish") or project.get("name") or ""
            page_district = district(project.get("address") or "")
            if norm(found) != norm(candidate["propertyHubName"]):
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
                "identityMatchMethod": "verified_propertyhub_id_page_with_listing_title_alias_evidence" if candidate.get("listingNameAliasEvidenceUrl") else "verified_propertyhub_id_page_with_project_alias" if alias_match else "exact_propertyhub_id_plus_high_confidence_name_and_listing_district",
                "identityMatchScore": round(100 * max(normalized_score, token_score), 2),
                "listingDistrictShare": round(district_share, 4),
                "listingCards": total,
                "locationSourceName": "PropertyHub 專案頁（專案 ID＋樓盤名＋行政區核對）",
                "locationSourceUrl": url, "completedYearSourceUrl": url,
                "asOf": date.today().isoformat(),
            }
            if listing_pid != pid:
                detail["propertyHubListingProjectId"] = listing_pid
            if candidate.get("listingNameAliasEvidenceUrl"):
                detail["identityEvidenceUrl"] = candidate["listingNameAliasEvidenceUrl"]
            if candidate.get("identityEvidenceUrl"):
                detail["identityEvidenceUrl"] = candidate["identityEvidenceUrl"]
            if alias_match:
                detail["identityEvidenceUrl"] = url
                detail["verifiedHipflatProjectNameAlias"] = candidate["hipflatName"]
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
    print(json.dumps({"candidateCount": len(candidates), "verifiedAdded": len(rows), "results": report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
