"""Add My Villa Bang Na's PropertyHub project map coordinates and details."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "my-villa-bang-na-coordinate-2026-10-18.json"


def load_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Could not parse {symbol} from {path.name}")
    return json.loads(match.group(1))


def main() -> None:
    project_id = 3090
    propertyhub_id = "16716"
    project_url = "https://propertyhub.in.th/en/projects/my-villa-bangna---16716"
    hipflat_url = "https://www.hipflat.co.th/en/projects/my-villa-bang-na-ofsmjs"
    lat, lng = 13.672199118675103, 100.59919231480234

    path = DIST / "bangkok-propertyhub-map.js"
    rows = load_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    existing = next((row for row in rows if int(row["id"]) == project_id), None)
    if not existing:
        raise ValueError(f"Hipflat project {project_id} is missing from the PropertyHub map data")
    existing.update({
        "propertyHubProjectId": propertyhub_id,
        "propertyHubProjectUrl": project_url,
        "lat": lat,
        "lng": lng,
        "locationVerified": True,
        "locationSourceUrl": project_url,
        "locationSourceName": "PropertyHub 專案頁地圖座標",
        "completedYear": 2018,
        "completedYearSourceUrl": project_url,
        "units": 365,
        "floors": 12,
        "asOf": "2026-10-18",
    })
    path.write_text(
        "window.BANGKOK_PROPERTYHUB_PROJECTS = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    html_path = DIST / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html = re.sub(
        r"bangkok-propertyhub-map\.js\?v=[^\"']+",
        "bangkok-propertyhub-map.js?v=20261018g-my-villa-bang-na-verified-project",
        html,
        count=1,
    )
    html_path.write_text(html, encoding="utf-8")

    report = {
        "hipflatId": project_id,
        "project": "My villa Bang Na",
        "coordinates": {"lat": lat, "lng": lng},
        "coordinateSource": project_url,
        "projectIdentityCrosscheck": hipflat_url,
        "identityEvidence": "PropertyHub gives the same project name, 365 units and 12 floors; Hipflat names My villa Bang Na at 32 Soi Rom Pho, Bang Na Tai, Bang Na.",
        "mapEvidence": "PropertyHub project page embedded project location object with these latitude/longitude values.",
        "completionYear": 2018,
        "currentListings": {"sale": 0, "rent": 0, "evidence": project_url},
        "checkedAt": "2026-10-18",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": project_id, "coordinates": {"lat": lat, "lng": lng}, "verified": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
