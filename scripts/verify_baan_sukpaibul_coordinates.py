"""Verify the Baan Sukpaibul project pin from independent exact-address pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3194
NAME = "Baan Sukpaibul"
LAT = 13.779718
LNG = 100.550462
ONEDAY_URL = "https://www.oneday.co.th/th_TH/สิ่งปลูกสร้าง/บ้านสุขไพบูลย์/"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/baan-sukpaibul-rkmbxf"
DDPROPERTY_URL = "https://www.ddproperty.com/en/project/15255-baan-sukpaibul"
REPORT_PATH = ROOT / "reports" / "baan-sukpaibul-coordinate-verification-2026-10-18.json"


def load_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError(f"Unexpected {symbol} format in {filename}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


verified = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
record = next((row for row in verified if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if record is None:
    record = {"hipflatId": PROJECT_ID, "name": NAME}
    verified.append(record)
record.update({
    "name": NAME,
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "OneDay 精確專案頁地圖座標",
    "sourceUrl": ONEDAY_URL,
    "verificationSourceUrl": HIPFLAT_URL,
    "corroboratingSourceUrl": DDPROPERTY_URL,
    "verificationMethod": "OneDay exact Baan Sukpaibul project page embeds 13.779718,100.550462 and gives address 35 Soi Sai Lom 2. Hipflat and DDproperty independently match the project name and Soi Sai Lom 2, Phaya Thai address; DDproperty also records 8 floors.",
})
verified.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", verified)

index_path = DIST / "index.html"
index_text = index_path.read_text(encoding="utf-8")
index_text, replacements = re.subn(
    r"bangkok-verified-coordinates\.js\?v=[^\"']+",
    "bangkok-verified-coordinates.js?v=20261018x-baan-sukpaibul-oneday-coordinate",
    index_text,
    count=1,
)
if replacements != 1:
    raise ValueError("Could not update verified-coordinate asset cache key")
index_path.write_text(index_text, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": "2026-10-18",
    "coordinates": {"lat": LAT, "lng": LNG},
    "sources": {
        "primaryMapAndAddress": ONEDAY_URL,
        "hipflatProject": HIPFLAT_URL,
        "ddpropertyProject": DDPROPERTY_URL,
    },
    "crossCheckedFacts": "OneDay exact project page: 35 Soi Sai Lom 2, Phaya Thai; page map coordinates 13.779718, 100.550462; 8 floors and 22 apartments. Hipflat project page confirms Baan Sukpaibul and Soi Sai Lom 2, Sam Sen Nai, Phaya Thai; DDproperty confirms Baan Sukpaibul and Soi Sai Lom 2, Phaya Thai.",
    "marketStatus": "Hipflat currently reports no properties available; no expired rent or sale prices were added as active listing samples.",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=True, indent=2))
