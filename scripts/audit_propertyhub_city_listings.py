"""Audit cached PropertyHub Bangkok listing pages against the Hipflat catalogue."""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
PAGES = RESEARCH / "propertyhub-bangkok-pages.jsonl"
OUTPUT = RESEARCH / "propertyhub-city-listing-match-audit.json"
SUMMARY_OUTPUT = DIST / "bangkok-propertyhub-city-summaries.js"
DISTRICTS = (
    "Pom Prap Sattru Phai", "Thawi Watthana", "Khlong Sam Wa", "Bang Khun Thian", "Bang Kho Laem", "Saphan Sung",
    "Bangkok Yai", "Bangkok Noi", "Phaya Thai", "Phra Khanong", "Ratchathewi", "Samphanthawong", "Wang Thonglang",
    "Huai Khwang", "Khan Na Yao", "Lat Krabang", "Bueng Kum", "Chom Thong", "Don Mueang", "Nong Chok", "Nong Khaem",
    "Pathum Wan", "Phasi Charoen", "Phra Nakhon", "Rat Burana", "Taling Chan", "Thung Khru", "Bang Kapi", "Bang Khae",
    "Bang Khen", "Bang Na", "Bang Phlat", "Bang Rak", "Bang Sue", "Chatuchak", "Din Daeng", "Dusit", "Khlong San",
    "Khlong Toei", "Lak Si", "Lat Phrao", "Min Buri", "Prawet", "Sai Mai", "Sathon", "Suan Luang", "Thon Buri",
    "Yan Nawa", "Bang Bon", "Watthana",
)


def arr(file: str, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", (DIST / file).read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {file}")
    return json.loads(match.group(1))


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def catalogue_name_key(value: str) -> str:
    # Treat punctuation and harmless articles/prepositions as formatting;
    # retain all distinguishing project words and numbers.
    stop = {"a", "an", "at", "by", "in", "of", "on", "the"}
    tokens = [token for token in norm(value).split() if token not in stop]
    return " ".join(sorted(tokens))


def district(value: str) -> str | None:
    text = norm(value)
    for item in sorted(DISTRICTS, key=len, reverse=True):
        needle = norm(item)
        if re.search(rf"\b{re.escape(needle)}\b", text):
            return "watthana" if needle in {"watthana", "vadhana"} else needle
    if re.search(r"\b(vadhana|watthana)\b", text):
        return "watthana"
    return None


def main() -> None:
    projects = arr("bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    propertyhub = arr("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    by_ph_id = {str(row["propertyHubProjectId"]): row for row in propertyhub if row.get("propertyHubProjectId")}
    # Link additional PropertyHub projects only where the official project page
    # was fetched and its numeric ID plus exact English name match a unique
    # Hipflat project in the same Bangkok district.
    by_name: dict[str, list[dict]] = defaultdict(list)
    by_name_key: dict[str, list[dict]] = defaultdict(list)
    for row in projects:
        by_name[norm(row.get("name", ""))].append(row)
        by_name_key[catalogue_name_key(row.get("name", ""))].append(row)
    detail_rows = arr("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
    project_detail_by_ph_id = {}
    for detail in detail_rows:
        if not detail.get("locationVerified") or not detail.get("propertyHubProjectId"):
            continue
        matches = by_name.get(norm(detail.get("name", "")), [])
        if len(matches) != 1:
            continue
        target = matches[0]
        if district(target.get("address", "")) != district(detail.get("projectAddress", "")):
            continue
        project_detail_by_ph_id[str(detail.get("propertyHubProjectId"))] = target
    by_id = {int(row["id"]): row for row in projects}
    # Fuzzy catalogue names are accepted only for the explicitly audited
    # candidate set: the PropertyHub project page ID was checked, and its
    # project name and majority listing district were verified before this
    # detail record was written.
    fuzzy_detail_by_ph_id = {}
    for detail in detail_rows:
        if (not detail.get("locationVerified") or not detail.get("propertyHubProjectId")
                or detail.get("identityMatchMethod") != "exact_propertyhub_id_plus_high_confidence_name_and_listing_district"):
            continue
        target = by_id.get(int(detail.get("hipflatProjectId") or 0))
        if not target or district(target.get("address", "")) != district(detail.get("projectAddress", "")):
            continue
        fuzzy_detail_by_ph_id[str(detail.get("propertyHubProjectId"))] = target

    listings: dict[tuple[int, str], dict[str, dict]] = defaultdict(dict)
    match_methods: Counter = Counter()
    unresolved_name: Counter = Counter()
    pages = 0
    raw_cards = 0
    for line in PAGES.open(encoding="utf-8"):
        page = json.loads(line)
        pages += 1
        for item in page.get("listings", []):
            raw_cards += 1
            kind = item.get("kind") or page.get("kind")
            if kind not in {"sale", "rent"}:
                continue
            owner = by_ph_id.get(str(item.get("projectId") or ""))
            method = "propertyhub_project_id"
            if owner is None:
                owner = project_detail_by_ph_id.get(str(item.get("projectId") or ""))
                if owner is not None:
                    method = "verified_propertyhub_project_id_and_name"
            if owner is None:
                owner = fuzzy_detail_by_ph_id.get(str(item.get("projectId") or ""))
                if owner is not None:
                    method = "verified_propertyhub_project_id_fuzzy_name_and_district"
            if owner is None:
                candidates = by_name_key.get(catalogue_name_key(item.get("projectName", "")), [])
                listing_district = district(item.get("address", ""))
                if len(candidates) > 1 and listing_district:
                    candidates = [p for p in candidates if district(p.get("address", "")) == listing_district]
                if len(candidates) == 1:
                    owner = candidates[0]
                    target_district = district(owner.get("address", ""))
                    if listing_district and target_district and listing_district != target_district:
                        owner = None
                    else:
                        method = "normalized_name_and_district"
            if owner is None:
                candidates = by_name.get(norm(item.get("projectName", "")), [])
                listing_district = district(item.get("address", ""))
                if len(candidates) > 1:
                    if listing_district:
                        candidates = [p for p in candidates if district(p.get("address", "")) == listing_district]
                if len(candidates) == 1:
                    owner = candidates[0]
                    target_district = district(owner.get("address", ""))
                    if listing_district and target_district and listing_district != target_district:
                        owner = None
                    else:
                        method = "exact_name_and_district"
                elif item.get("projectName"):
                    reason = "no_exact_name" if not candidates else "ambiguous_exact_name" if len(candidates) > 1 else "district_conflict"
                    unresolved_name[reason] += 1
            if owner is None:
                continue
            price = float(item.get("price") or 0)
            area = float(item.get("area") or 0)
            price_sqm = float(item.get("priceSqm") or (price / area if area > 0 else 0))
            valid_band = (10_000 <= price_sqm <= 2_000_000) if kind == "sale" else (100 <= price_sqm <= 20_000)
            if price <= 0 or area < 8 or not valid_band:
                continue
            key = (int(owner["id"]), kind)
            listing_url = str(item.get("url") or "")
            listing_id = str(item.get("listingId") or listing_url or "")
            if not listing_id or not listing_url.startswith("https://propertyhub.in.th/en/listings/"):
                continue
            existing = listings[key].get(listing_id)
            normalized = {
                "id": listing_id, "price": price, "area": area, "priceSqm": int(round(price_sqm)),
                "beds": item.get("beds"), "roomType": item.get("roomType"), "title": item.get("title"),
                "url": item.get("url"), "updated": item.get("updated"), "projectId": str(item.get("projectId") or ""),
                "projectName": item.get("projectName"), "matchedBy": method,
            }
            if existing is None or str(normalized.get("updated") or "") > str(existing.get("updated") or ""):
                listings[key][listing_id] = normalized
            match_methods[method] += 1

    # Add per-project samples already fetched from the project's own listing
    # page before building the city-wide summaries, deduplicating by listing ID.
    for row in propertyhub:
        pid = int(row["id"])
        for kind in ("sale", "rent"):
            market = row.get(kind) or {}
            for sample in market.get("samples") or []:
                price = float(sample.get("price") or 0)
                area = float(sample.get("area") or 0)
                price_sqm = float(sample.get("priceSqm") or (price / area if area > 0 else 0))
                valid_band = (10_000 <= price_sqm <= 2_000_000) if kind == "sale" else (100 <= price_sqm <= 20_000)
                if price <= 0 or area < 8 or not valid_band:
                    continue
                listing_url = str(sample.get("url") or "")
                listing_id = str(sample.get("id") or listing_url or "")
                if not listing_id or not listing_url.startswith("https://propertyhub.in.th/en/listings/"):
                    continue
                listings[(pid, kind)].setdefault(listing_id, {
                    "id": listing_id, "price": price, "area": area, "priceSqm": int(round(price_sqm)),
                    "beds": sample.get("beds"), "roomType": sample.get("roomType") or sample.get("type"),
                    "title": sample.get("title"), "url": sample.get("url"), "updated": sample.get("updated"),
                    "projectId": str(row.get("propertyHubProjectId") or ""), "projectName": row.get("name"),
                    "matchedBy": "propertyhub_project_page",
                })

    per_kind = {kind: {int(pid): rows for (pid, row_kind), rows in listings.items() if row_kind == kind} for kind in ("sale", "rent")}
    all_ids = {"sale": set(per_kind["sale"]), "rent": set(per_kind["rent"])}
    summaries = []
    for pid in sorted(set(per_kind["sale"]) | set(per_kind["rent"])):
        summary = {"id": pid}
        for kind in ("sale", "rent"):
            rows = list(per_kind[kind].get(pid, {}).values())
            if not rows:
                continue
            lowest_total = min(rows, key=lambda row: row["price"])
            lowest_sqm = min(rows, key=lambda row: row["priceSqm"])
            metric = {
                "count": len(rows), "observedCount": len(rows), "countKind": "matched_city_index",
                "average": int(round(sum(row["price"] for row in rows) / len(rows))),
                "minimum": lowest_total["price"],
                "averageSqm": int(round(sum(row["priceSqm"] for row in rows) / len(rows))),
                "minimumSqm": lowest_sqm["priceSqm"], "asOf": "2026-10-17",
                "source": "https://propertyhub.in.th/en/condo-for-sale/bangkok" if kind == "sale" else "https://propertyhub.in.th/en/condo-for-rent/bangkok",
                "minimumSourceUrl": lowest_total["url"], "minimumSqmSourceUrl": lowest_sqm["url"],
                "samples": sorted(rows, key=lambda row: (row["priceSqm"], row["price"]))[:12],
            }
            if kind == "rent":
                metric["average"] = int(round(metric["average"]))
                metric["averageSqm"] = int(round(metric["averageSqm"]))
            by_bedroom = {}
            for bedroom in (1, 2, 3, 4):
                room_rows = [row for row in rows if int(row.get("beds") or 0) == bedroom]
                if not room_rows:
                    continue
                room_lowest = min(room_rows, key=lambda row: row["price"])
                room_lowest_sqm = min(room_rows, key=lambda row: row["priceSqm"])
                by_bedroom[str(bedroom)] = {
                    "count": len(room_rows), "minimum": room_lowest["price"],
                    "minimumSqm": room_lowest_sqm["priceSqm"], "sourceUrl": room_lowest["url"],
                    "minimumSqmSourceUrl": room_lowest_sqm["url"],
                }
            if by_bedroom:
                metric["byBedroom"] = by_bedroom
            summary[kind] = metric
        summaries.append(summary)
    SUMMARY_OUTPUT.write_text("window.BANGKOK_PROPERTYHUB_CITY_SUMMARIES = " + json.dumps(summaries, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    report = {
        "pages": pages, "rawCards": raw_cards,
        "uniqueProjectCount": {kind: len(all_ids[kind]) for kind in all_ids},
        "projectsWithBothSaleAndRent": len(all_ids["sale"] & all_ids["rent"]),
        "uniqueListingCount": {kind: sum(len(rows) for rows in per_kind[kind].values()) for kind in per_kind},
        "matchMethods": dict(match_methods), "unresolvedNameCards": dict(unresolved_name),
        "summaryFile": str(SUMMARY_OUTPUT), "summaryProjects": len(summaries),
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
