from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3026
PROJECT_NAME = "Horkarnkah Condo Town"
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/projects/horkarnkah-condo-town-nmdevf"
PH_PROJECT = "https://propertyhub.in.th/en/projects/horkarnkah-condo-town"
PH_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-horkarnkah-condo-town"
PH_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-horkarnkah-condo-town"


def read_js_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not find {symbol} in {path}")
    return json.loads(match.group(1))


def write_js_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        f"{json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


crosschecks_path = DIST / "bangkok-market-crosschecks.js"
crosschecks = read_js_array(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS")
entry = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub",
    "projectSourceUrl": PH_PROJECT,
    "sale": {"activeListingCount": 0, "sourceUrl": PH_SALE},
    "rent": {"activeListingCount": 0, "sourceUrl": PH_RENT},
    "availabilitySources": [
        {
            "sourceName": "PropertyHub 出售專案頁",
            "url": PH_SALE,
            "statusLabel": "目前顯示 0 筆在架出售物件",
        },
        {
            "sourceName": "PropertyHub 出租專案頁",
            "url": PH_RENT,
            "statusLabel": "目前顯示 0 筆在架出租物件",
        },
        {
            "sourceName": "Hipflat 專案頁",
            "url": HIPFLAT,
            "statusLabel": "頁面顯示目前無可用房源；此頁較舊，僅作交叉參考",
        },
    ],
}
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != PROJECT_ID]
crosschecks.append(entry)
crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
write_js_array(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "saleAvailability": {
        "status": "no_current_project_listings_found",
        "count": 0,
        "source": PH_SALE,
        "evidence": "PropertyHub project sale page displays no matched properties.",
    },
    "rentAvailability": {
        "status": "no_current_project_listings_found",
        "count": 0,
        "source": PH_RENT,
        "evidence": "PropertyHub project rent page displays no matched properties.",
    },
    "crossCheck": {
        "source": HIPFLAT,
        "evidence": "Hipflat page reports no currently available properties; its indexed page is older and is treated as secondary confirmation.",
    },
    "roi": {
        "status": "not_calculable",
        "reason": "No current verified sale and rent listing samples were found for this Condo.",
    },
    "note": "Nearby projects and district-level prices were not substituted for Horkarnkah Condo Town listings.",
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "horkarnkah-market-availability-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html, changed = re.subn(
    r"bangkok-market-crosschecks\.js\?v=[^\"']+",
    "bangkok-market-crosschecks.js?v=20261019-horkarnkah-availability-check",
    html,
    count=1,
)
if changed != 1:
    raise ValueError("Could not update the market cross-check cache key")
index_path.write_text(html, encoding="utf-8")

print(
    json.dumps(
        {
            "hipflatId": PROJECT_ID,
            "sale": "0 current listings cross-checked",
            "rent": "0 current listings cross-checked",
            "roi": "not calculable",
        },
        ensure_ascii=False,
    )
)
