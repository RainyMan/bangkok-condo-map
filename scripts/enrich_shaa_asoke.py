"""Add PropertyHub-verified location and project metadata for SHAA Asoke."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3147
PROJECT_NAME = "SHAA Asoke"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/shaa-asoke-hsnrho"
PROPERTYHUB_URL = "https://propertyhub.in.th/en/condo-for-sale/project-shaa-asoke---20338"
PROPERTYHUB_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-shaa-asoke---20338"
SCANCONDO_URL = "https://www.scancondo.com/เช่าคอนโด/คอนโด-ฌา-อโศก"


def load_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not find {symbol} in {path.name}")
    return json.loads(match.group(1))


project = None
for filename in ("bangkok-propertyhub-map.js", "bangkok-propertyhub.js"):
    path = DIST / filename
    projects = load_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    project = next(item for item in projects if int(item.get("id", 0)) == PROJECT_ID)
    project.update(
        {
            "lat": 13.7399539,
            "lng": 100.55991130000007,
            "locationVerified": True,
            "locationSourceName": "PropertyHub 專案頁原生地圖座標",
            "locationSourceUrl": PROPERTYHUB_URL,
            "locationVerificationSourceUrl": HIPFLAT_URL,
            "completedYearSourceUrl": PROPERTYHUB_URL,
            "propertyHubProjectUrl": "https://propertyhub.in.th/en/projects/shaa-asoke---20338",
        }
    )
    path.write_text(
        "window.BANGKOK_PROPERTYHUB_PROJECTS = "
        + json.dumps(projects, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
html = re.sub(
    r'bangkok-propertyhub-map\.js\?v=[^" ]+',
    "bangkok-propertyhub-map.js?v=20261018j-shaa-asoke-verified-map-coordinates",
    html,
)
html = re.sub(
    r'bangkok-walk-routes\.js\?v=[^" ]+',
    "bangkok-walk-routes.js?v=20261018i-shaa-asoke-walk-route",
    html,
)
html_path.write_text(html, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "checkedAt": date.today().isoformat(),
    "identity": {
        "hipflatProjectUrl": HIPFLAT_URL,
        "propertyHubProjectUrl": "https://propertyhub.in.th/en/projects/shaa-asoke---20338",
        "addressMatch": "Hipflat lists 29-31 Soi Sukhumvit 19; PropertyHub identifies the same SHAA Asoke project in Watthana. The PropertyHub map point is taken from its exact project page's embedded project-location data.",
    },
    "location": {
        "status": "verified_exact_project_map_point",
        "lat": project["lat"],
        "lng": project["lng"],
        "sourceUrl": PROPERTYHUB_URL,
        "corroboratingProjectUrl": HIPFLAT_URL,
        "verificationMethod": "exact_propertyhub_project_page_map_coordinates_and_hipflat_project_identity",
    },
    "projectDetails": {
        "completedYear": 2023,
        "units": 143,
        "floors": 24,
        "sourceUrl": PROPERTYHUB_URL,
        "crosscheckUrl": SCANCONDO_URL,
        "note": "PropertyHub specifies completed 2566 BE, 143 units and 24 floors; Scancondo project details also specify 143 units and 24 floors. Scancondo's descriptive paragraph later says 40 floors, conflicting with its own structured details and the PropertyHub page, so that isolated discrepancy was not used.",
    },
    "walkingRoute": next(
        item
        for item in load_array(DIST / "bangkok-walk-routes.js", "BANGKOK_WALK_ROUTES")
        if int(item.get("id", 0)) == PROJECT_ID
    ),
    "market": {
        "sale": {
            "status": "no_current_individual_sale_listing_found",
            "sourceUrl": PROPERTYHUB_URL,
            "finding": "The exact PropertyHub project sale page, checked 2026-10-18, reports no matched properties for sale.",
        },
        "rent": {
            "status": "no_current_individual_rent_listing_found",
            "sourceUrl": PROPERTYHUB_RENT_URL,
            "crosscheckUrl": SCANCONDO_URL,
            "finding": "The exact PropertyHub project rent page, checked 2026-10-18, reports no matched properties for rent. Scancondo project search also shows no rental listings.",
        },
        "yield": "not calculated because no direct sale or rent listing sample was available",
    },
}
(ROOT / "reports" / "shaa-asoke-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(
    json.dumps(
        {
            "hipflatId": PROJECT_ID,
            "coordinate": [project["lat"], project["lng"]],
            "completedYear": project["completedYear"],
            "sale": report["market"]["sale"]["status"],
            "rent": report["market"]["rent"]["status"],
        },
        ensure_ascii=False,
    )
)
