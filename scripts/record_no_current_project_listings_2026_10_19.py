from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from enrich_propertyhub_exact_project_pages import arr, parse_market

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"no-current-project-listings-{date.today().isoformat()}.json"
AS_OF = date.today().isoformat()
CASES = {
    3063: {
        "name": "Thong Thai Condominium",
        "propertyHubId": "4327",
        "propertyHubName": "Thong Thai Condominium 3",
        "hipflatUrl": "https://www.hipflat.co.th/en/projects/thong-thai-condominium-zcpcep",
    },
    3093: {
        "name": "The Peace",
        "propertyHubId": "443",
        "propertyHubName": "The Peace",
        "hipflatUrl": "https://www.hipflat.co.th/en/projects/the-peace-bxoyim",
    },
}


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"window.{symbol} = ")
        for chunk in encoder.iterencode(rows):
            stream.write(chunk)
        stream.write(";\n")
    temporary.replace(target)


projects = {int(row["id"]): row for row in arr("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")}
propertyhub = {int(row["id"]): row for row in arr("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS")}
coverage = {
    int(row["hipflat_id"]): row
    for row in csv.DictReader((ROOT / "reports" / f"bangkok-coverage-{AS_OF}.csv").open(encoding="utf-8-sig"))
}
crosschecks = {int(row["hipflatId"]): row for row in arr("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")}
results = []

for project_id, case in CASES.items():
    project = projects[project_id]
    mapped = propertyhub[project_id]
    if project["name"] != case["name"]:
        raise RuntimeError(f"Hipflat catalogue identity changed for {project_id}: {project['name']}")
    slug = urlparse(mapped["propertyHubProjectUrl"]).path.rstrip("/").split("/")[-1]
    if not slug:
        raise RuntimeError(f"Missing exact PropertyHub project URL for {project_id}")
    markets = {}
    for kind in ("sale", "rent"):
        parsed = parse_market(project_id, kind, slug, case["propertyHubId"])
        source_project = parsed.get("project") or {}
        source_name = str(source_project.get("nameEnglish") or source_project.get("name") or "")
        if parsed.get("error"):
            raise RuntimeError(f"PropertyHub {kind} check failed for {project_id}: {parsed['error']}")
        if str(source_project.get("id")) != case["propertyHubId"] or source_name != case["propertyHubName"]:
            raise RuntimeError(f"PropertyHub identity mismatch for {project_id}: {source_project}")
        if parsed.get("cards") or int(parsed.get("totalCount") or 0) != 0:
            raise RuntimeError(f"Current PropertyHub {kind} listings found for {project_id}; do not record zero availability")
        markets[kind] = {
            "activeListingCount": 0,
            "displayedResultCount": 0,
            "sourceUrl": parsed["sourceUrl"],
            "checkedAt": AS_OF,
        }

    hipflat_status = "Hipflat 專案頁顯示目前沒有可用物件。"
    previous = crosschecks.get(project_id, {})
    crosschecks[project_id] = {
        **previous,
        "hipflatId": project_id,
        "projectName": case["name"],
        "asOf": AS_OF,
        "sourceName": "PropertyHub",
        "projectSourceUrl": mapped["propertyHubProjectUrl"],
        "sale": markets["sale"],
        "rent": markets["rent"],
        "availabilitySources": [
            {"sourceName": "Hipflat 專案頁", "url": case["hipflatUrl"], "statusLabel": hipflat_status},
            {"sourceName": "PropertyHub 出售專案頁", "url": markets["sale"]["sourceUrl"], "statusLabel": "查核時 0 筆符合此專案的出售掛牌。"},
            {"sourceName": "PropertyHub 出租專案頁", "url": markets["rent"]["sourceUrl"], "statusLabel": "查核時 0 筆符合此專案的出租掛牌。"},
        ],
        "yieldStatus": "not_calculated",
        "yieldNote": "Hipflat 與 PropertyHub 專案頁均無現行售租掛牌，沒有足夠的同案售租樣本計算投報。",
    }
    results.append({
        "hipflatId": project_id,
        "projectName": case["name"],
        "propertyHubProjectId": case["propertyHubId"],
        "propertyHubProjectName": case["propertyHubName"],
        "propertyHubProjectUrl": mapped["propertyHubProjectUrl"],
        "hipflatProjectUrl": case["hipflatUrl"],
        "sale": markets["sale"],
        "rent": markets["rent"],
        "checkedAt": AS_OF,
    })

write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", [crosschecks[key] for key in sorted(crosschecks)])
REPORT.write_text(json.dumps({"checkedAt": AS_OF, "projects": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"checkedAt": AS_OF, "checkedProjects": len(results), "zeroSaleAndRentSources": 2, "report": str(REPORT)}, ensure_ascii=False, indent=2))
