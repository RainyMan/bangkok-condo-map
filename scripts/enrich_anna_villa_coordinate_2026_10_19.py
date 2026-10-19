"""Add a source-verified project map pin for Anna Villa."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"anna-villa-coordinate-{date.today().isoformat()}.json"
PROJECT_ID = 3273
PROJECT_NAME = "Anna Villa"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/anna-villa-fgxmgy"
KBT_URL = "https://www.kaibaanthai.com/en/projects/thailand/bangkok/khlong-toei/phra-khanong/anna-villa-sukhumvit"
AS_OF = date.today().isoformat()


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format: {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"window.{symbol} = ")
        for chunk in json.JSONEncoder(ensure_ascii=False, separators=(",", ":")).iterencode(rows):
            stream.write(chunk)
        stream.write(";\n")
    temporary.replace(target)


project = next(row for row in read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE") if int(row["id"]) == PROJECT_ID)
if project["name"] != PROJECT_NAME or project.get("hipflatProjectUrl") != HIPFLAT_URL:
    raise RuntimeError("Hipflat catalogue identity does not match the reviewed project page")

coordinates = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
rows = {int(row["hipflatId"]): row for row in coordinates}
rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": PROJECT_NAME,
    "lat": 13.7172609, "lng": 100.5811508,
    "locationVerified": True, "sourceName": "KaiBaanThai 專案地圖",
    "sourceUrl": KBT_URL, "verificationSourceUrl": HIPFLAT_URL,
    "verificationMethod": "KaiBaanThai 專案頁結構化座標；專案名稱、Phra Khanong 區域、1998 完工年與 8 層資料和 Hipflat 相符",
    "checkedAt": AS_OF,
}
write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", [rows[key] for key in sorted(rows)])

REPORT.write_text(json.dumps({
    "hipflatId": PROJECT_ID, "projectName": PROJECT_NAME, "checkedAt": AS_OF,
    "coordinates": {"lat": 13.7172609, "lng": 100.5811508, "source": KBT_URL, "crossCheck": HIPFLAT_URL},
    "completedYear": {"year": 1998, "source": HIPFLAT_URL},
    "sale": {"status": "no current sale listing verified"},
    "rent": {"status": "project pages show a rental unit, but the individual listing is old and current availability cannot be confirmed from its direct page; excluded from sample and ROI"},
    "yield": {"status": "not calculated", "reason": "No current sale sample and no current rental listing detail verified."},
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": PROJECT_NAME, "coordinates": [13.7172609, 100.5811508], "report": str(REPORT)}, ensure_ascii=False, indent=2))
