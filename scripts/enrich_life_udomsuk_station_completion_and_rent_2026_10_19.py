from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
ID = 3468
NAME = "LIFE Udomsuk Station"
CHECKED = "2026-10-19"
PH_PROJECT = "https://propertyhub.in.th/en/projects/life-udomsuk-station"
PH_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-life-udomsuk-station"
PH_RENT = "https://assets3.propertyhub.in.th/EN/projects/life-udomsuk-station/for-rent"
DD_PROJECT = "https://www.ddproperty.com/en/project/14519-life-udomsuk-station"
AP_PROJECT_PDF = "https://www.apthai.com/images/production/1m6p22elnNO7FP5sizUIzczMgf7zDb-metaNXRjRnhwRDE0Q1JLSFZrT2dkclAtMTc2NTc4NDY3MzIyMDE3NjU3ODQ2NzMyMjAucGRm-.pdf"


def load_array(file: str, symbol: str) -> list[dict]:
    path = DIST / file
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Missing {symbol} in {file}")
    return json.loads(match.group(1))


def save_array(file: str, symbol: str, rows: list[dict]) -> None:
    (DIST / file).write_text(f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n", encoding="utf-8")

projects = load_array("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
project = next(row for row in projects if int(row["id"]) == ID)
previous_year = 2026
project["completedYear"] = 2028
project["completedYearSourceUrl"] = AP_PROJECT_PDF
project["completedYearEvidence"] = "AP official project details state commencement in November 2025 and expected completion around June 2028; DDproperty also reports completion in 2028. PropertyHub project overview labels Year Built 2026, which conflicts with the developer schedule."
save_array("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS", projects)
map_projects = load_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS")
map_project = next(row for row in map_projects if int(row["id"]) == ID)
map_project["completedYear"] = 2028
map_project["completedYearSourceUrl"] = AP_PROJECT_PDF
save_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", map_projects)

crosschecks = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
row = {
    "hipflatId": ID,
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "PropertyHub / DDproperty / AP",
    "projectSourceUrl": PH_PROJECT,
    "sale": {"activeListingCount": 11, "sourceUrl": PH_SALE, "listings": []},
    "rent": {"activeListingCount": 0, "sourceUrl": PH_RENT, "listings": []},
    "availabilitySources": [
        {"sourceName": "PropertyHub 出租結果", "url": PH_RENT, "statusLabel": "專案出租頁未匹配到可核對房源；專案概覽的出租筆數與此結果不一致，暫不把沒有個別物件頁的項目當成租盤。"},
        {"sourceName": "DDproperty 專案頁", "url": DD_PROJECT, "statusLabel": "專案頁顯示 For Rent 0；目前未找到可核實的個別出租房源。"},
        {"sourceName": "AP 官方專案資料", "url": AP_PROJECT_PDF, "statusLabel": "官方資料列明 2025 年 11 月動工，預計 2028 年 6 月左右完工；以 2028 作完工年。PropertyHub 概覽顯示 2026，與官方時程不符。"},
    ],
    "roi": {"status": "not_calculable", "reason": "No current exact-project rental listing with a direct unit page was verified; rental market pages were not substituted for a unit sample."},
}
crosschecks = [item for item in crosschecks if int(item.get("hipflatId", -1)) != ID] + [row]
crosschecks.sort(key=lambda item: int(item.get("hipflatId", 0)))
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "completionYear": {"previousValue": previous_year, "verifiedValue": 2028, "source": AP_PROJECT_PDF, "corroboration": DD_PROJECT, "conflictingSource": PH_PROJECT, "decision": "Use the developer's expected completion schedule (June 2028), corroborated by DDproperty; do not treat PropertyHub's 2026 Year Built field as a completed-year value."},
    "sale": {"activeListings": 11, "source": PH_SALE, "individualSamplesAlreadyAvailable": True},
    "rent": {"status": "no_direct_current_unit_listing_verified", "propertyHubResult": PH_RENT, "ddpropertyProject": DD_PROJECT, "evidence": "PropertyHub exact project rent result says no matched properties; DDproperty reports For Rent (0). A PropertyHub overview count differs, but no direct item could be verified."},
    "yield": {"status": "not_calculable", "reason": "No directly verifiable current rent sample."},
}
(REPORTS / "life-udomsuk-station-completion-and-rent-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html, changed = re.subn(r"bangkok-propertyhub-map\.js\?v=[^\"']+", "bangkok-propertyhub-map.js?v=20261019-life-udomsuk-official-completion", html, count=1)
html, changed_crosscheck = re.subn(r"bangkok-market-crosschecks\.js\?v=[^\"']+", "bangkok-market-crosschecks.js?v=20261019-life-udomsuk-official-completion", html, count=1)
if changed != 1 or changed_crosscheck != 1:
    raise ValueError("Could not update data cache versions")
index_path.write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": ID, "previousCompletionYear": previous_year, "verifiedCompletionYear": 2028, "rent": "no direct active unit listing verified", "yield": "not calculated"}))
