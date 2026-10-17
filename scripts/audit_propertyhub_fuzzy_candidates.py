"""Find cautious Hipflat matches for uncatalogued PropertyHub project IDs."""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import audit_propertyhub_city_listings as audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RESEARCH = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok")
PAGES = RESEARCH / "propertyhub-bangkok-pages.jsonl"
OUTPUT = RESEARCH / "propertyhub-fuzzy-project-targets-next.json"


def arr(filename: str, symbol: str) -> list[dict]:
    return audit.arr(filename, symbol)


def name_tokens(value: str) -> list[str]:
    return [token for token in audit.norm(value).split() if token not in {"the", "at", "by", "condo", "condominium", "project", "residence", "tower"} and len(token) > 2]


def typo_compatible(left: str, right: str) -> bool:
    left_tokens, right_tokens = name_tokens(left), name_tokens(right)
    if sorted(re.findall(r"\d+", audit.norm(left))) != sorted(re.findall(r"\d+", audit.norm(right))):
        return False
    remaining_left = list(left_tokens)
    remaining_right = list(right_tokens)
    for token in list(remaining_left):
        if token in remaining_right:
            remaining_left.remove(token)
            remaining_right.remove(token)
    # Allow spelling and transliteration variants (including a word joined or
    # split differently), while rejecting unrelated name substitutions.
    return bool(remaining_left or remaining_right) and SequenceMatcher(
        None, "".join(remaining_left), "".join(remaining_right)
    ).ratio() >= 0.68 or not remaining_left and not remaining_right


def main() -> None:
    projects = arr("bangkok-catalogue.js", "BANGKOK_HIPFLAT_PROJECTS")
    ph = arr("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    details = arr("bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS")
    known = {str(row["propertyHubProjectId"]) for row in ph if row.get("propertyHubProjectId")}
    known.update(str(row["propertyHubProjectId"]) for row in details if row.get("propertyHubProjectId"))
    known.update(str(row["propertyHubListingProjectId"]) for row in details if row.get("propertyHubListingProjectId"))
    catalogue_by_district: dict[str, list[dict]] = defaultdict(list)
    for row in projects:
        d = audit.district(row.get("address", ""))
        if d:
            catalogue_by_district[d].append(row)

    groups: dict[str, dict] = {}
    with PAGES.open(encoding="utf-8") as pages:
        for line in pages:
            page = json.loads(line)
            for item in page.get("listings", []):
                pid = str(item.get("projectId") or "")
                if not pid or pid in known:
                    continue
                group = groups.setdefault(pid, {"cards": 0, "districts": Counter(), "names": Counter(), "slug": ""})
                group["cards"] += 1
                d = audit.district(item.get("address", ""))
                if d:
                    group["districts"][d] += 1
                name = item.get("projectName") or ""
                if name:
                    group["names"][name] += 1
                group["slug"] = group["slug"] or item.get("projectSlug") or ""

    candidates = []
    for ph_id, group in groups.items():
        if group["cards"] < 4 or not group["districts"] or not group["names"]:
            continue
        d, district_count = group["districts"].most_common(1)[0]
        district_share = district_count / sum(group["districts"].values())
        if district_share < 0.95:
            continue
        ph_name = group["names"].most_common(1)[0][0]
        ranked = sorted(
            ((SequenceMatcher(None, audit.norm(ph_name), audit.norm(project.get("name", ""))).ratio() * 100, project)
             for project in catalogue_by_district[d]),
            key=lambda pair: pair[0], reverse=True,
        )
        if not ranked:
            continue
        score, project = ranked[0]
        margin = score - (ranked[1][0] if len(ranked) > 1 else 0)
        if audit.norm(ph_name) == audit.norm(project.get("name", "")):
            continue
        # Names that share a brand but refer to different numbered phases,
        # streets, or towers must never collapse to one catalogue entry.
        ph_numbers = re.findall(r"\d+", audit.norm(ph_name))
        hipflat_numbers = re.findall(r"\d+", audit.norm(project.get("name", "")))
        if ph_numbers != hipflat_numbers:
            continue
        if not typo_compatible(ph_name, project.get("name", "")):
            continue
        # A modestly relaxed name threshold is still backed by a unique winner,
        # a strong district majority, and exact PropertyHub project-page checks.
        if score < 90 or margin < 12:
            continue
        candidates.append({
            "propertyHubProjectId": ph_id,
            "propertyHubName": ph_name,
            "projectSlug": group["slug"],
            "hipflatProjectId": int(project["id"]),
            "hipflatName": project["name"],
            "district": d,
            "listingCards": group["cards"],
            "districtShare": round(district_share, 4),
            "nameScore": round(score, 2),
            "scoreMargin": round(margin, 2),
            "candidateSourceUrl": f"https://propertyhub.in.th/en/projects/{group['slug']}",
        })
    OUTPUT.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "knownPropertyHubProjectIds": len(known),
        "unmappedCandidates": len(candidates),
        "listingCards": sum(row["listingCards"] for row in candidates),
        "targetsFile": str(OUTPUT),
        "top": [{key: row[key] for key in ("propertyHubName", "hipflatName", "nameScore", "scoreMargin", "listingCards", "districtShare")} for row in candidates[:15]],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
