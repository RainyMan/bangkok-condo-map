"""Add Tamarind Tree Residence's project-specific mapped coordinates."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3171
PROJECT = "Tamarind Tree Residence"
LAT = 13.83745
LNG = 100.578812
TOOKTEE = "https://www.tooktee.com/project/2385/?listtype=1"
HIPFLAT = "https://www.hipflat.co.th/en/projects/tamarind-tree-residence-jprzey"
GOOGLE_MAPS = f"https://www.google.com/maps/search/?api=1&query={LAT}%2C{LNG}"


def load_array(filename: str, variable: str) -> tuple[str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise ValueError(f"Unexpected JavaScript array format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


def main() -> None:
    catalogue_prefix, catalogue, catalogue_suffix = load_array(
        "bangkok-catalogue.js", "window.BANGKOK_CONDO_CATALOGUE"
    )
    project = next(row for row in catalogue if int(row["id"]) == PROJECT_ID)
    project.update({
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "locationSourceUrl": GOOGLE_MAPS,
        "addressSourceUrl": TOOKTEE,
        "sourceDescription": (
            "Tamarind Tree Residence 位於 Soi Phahonyothin 34（Soi Sena Nikhom 2），"
            "1 棟 8 層、72 戶、樓型約 36–44 ㎡。Tooktee 同名專案頁的地圖座標為 "
            f"{LAT}, {LNG}，並列明位於 Phahonyothin 34 Yaek 7、鄰近 Mayo Hospital；"
            "座標以該專案頁所載點位核實。售租樣本仍待補。"
        ),
    })
    completeness = dict(project.get("dataCompleteness") or {})
    completeness["coordinates"] = True
    project["dataCompleteness"] = completeness
    save_array("bangkok-catalogue.js", catalogue_prefix, catalogue, catalogue_suffix)

    coordinate_prefix, coordinates, coordinate_suffix = load_array(
        "bangkok-verified-coordinates.js", "window.BANGKOK_VERIFIED_COORDINATES"
    )
    coordinate = {
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "sourceName": "Tooktee 專案頁地圖座標",
        "sourceUrl": GOOGLE_MAPS,
        "verificationSourceUrl": TOOKTEE,
        "corroborationSourceUrl": HIPFLAT,
        "verificationMethod": (
            "Tooktee 的專案頁以隱藏座標欄位與地圖標記提供 13.83745, 100.578812；"
            "其專案名稱為泰文แทมมารีน ทรี เรสซิเดนซ์，頁面列出 Phahonyothin 34 Yaek 7、"
            "Mayo Hospital 附近及 8 層、72 戶，與 Hipflat 的 Tamarind Tree Residence、"
            "Phahonyothin 34 / Sena Nikhom 2、8 層、72 戶相符。"
        ),
        "asOf": "2026-10-19",
    }
    coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
    coordinates.append(coordinate)
    coordinates.sort(key=lambda row: int(row.get("hipflatId", 0)))
    save_array("bangkok-verified-coordinates.js", coordinate_prefix, coordinates, coordinate_suffix)

    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": "2026-10-19",
        "coordinates": {"lat": LAT, "lng": LNG, "status": "verified"},
        "coordinateSource": TOOKTEE,
        "mapPoint": GOOGLE_MAPS,
        "corroboratingProjectSource": HIPFLAT,
        "method": coordinate["verificationMethod"],
        "marketAvailability": {
            "sale": "no_current_matching_listing_as_checked_2026-10-18",
            "rent": "no_current_matching_listing_as_checked_2026-10-18",
            "roi": "not_calculable_without_current_exact-project_sale_and_rent_samples",
        },
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "tamarind-tree-residence-coordinate-verification-2026-10-19.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(
        r"(bangkok-catalogue\.js\?v=)[^\"']+",
        r"\g<1>20261019-tamarind-tree-tooktee-pin",
        html,
        count=1,
    )
    html = re.sub(
        r"(bangkok-verified-coordinates\.js\?v=)[^\"']+",
        r"\g<1>20261019-tamarind-tree-tooktee-pin",
        html,
        count=1,
    )
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
