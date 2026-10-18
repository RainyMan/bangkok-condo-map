"""Correct the mismatched Bang Khae pin for the Hipflat Thung Khru project."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3054
NAME = "Wisetsuk Nakorn Condo"
LAT = 13.633713110107
LNG = 100.50511835365
LONGDO_URL = "https://map.longdo.com/p/A00316287"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/wisetsuk-nakorn-condo-npkjeq"
REPORT_PATH = ROOT / "reports" / "wisetsuk-nakorn-coordinate-correction-2026-10-18.json"


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


projects = load_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS")
project = next((row for row in projects if int(row.get("id", 0)) == PROJECT_ID), None)
if project is None:
    raise ValueError(f"Project {PROJECT_ID} not found in PropertyHub map overlay")
old = {key: project.get(key) for key in ("lat", "lng", "locationSourceUrl")}
if project.get("locationSourceUrl") != "https://propertyhub.in.th/en/projects/wisetsuk-nakorn-condo":
    raise ValueError("The current coordinate source differs from the mismatch being corrected")
project.update({
    "lat": None,
    "lng": None,
    "locationVerified": False,
    "locationSourceUrl": None,
    "locationSourceName": None,
    "locationVerificationSourceUrl": None,
    "coordinateConflictNote": "PropertyHub project page uses Bang Khae location, which conflicts with Hipflat's 595-unit 1992 Thung Khru project; its pin is not used.",
})
save_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", projects)

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
    "sourceName": "Longdo Map 核准 Condo 地點",
    "sourceUrl": LONGDO_URL,
    "verificationSourceUrl": HIPFLAT_URL,
    "verificationMethod": "Longdo Map approved exact-name Wisetsuk Nakhon Condominium pin at Soi Sap Bunchai 2; Hipflat confirms same project address, completion year 1992, 595 units and 5 floors. Rejected PropertyHub pin because its same-name page identifies Bang Khae instead of Thung Khru.",
})
verified.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", verified)

index_path = DIST / "index.html"
index_text = index_path.read_text(encoding="utf-8")
for asset, version in (
    ("bangkok-propertyhub-map.js", "20261018x-wisetsuk-location-mismatch-corrected"),
    ("bangkok-verified-coordinates.js", "20261018w-wisetsuk-longdo-coordinate"),
):
    index_text, n = re.subn(
        rf"{re.escape(asset)}\?v=[^\"']+",
        f"{asset}?v={version}",
        index_text,
        count=1,
    )
    if n != 1:
        raise ValueError(f"Could not update cache key for {asset}")
index_path.write_text(index_text, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": "2026-10-18",
    "correctedCoordinate": {"lat": LAT, "lng": LNG, "sourceUrl": LONGDO_URL},
    "crossCheck": {
        "hipflatProjectUrl": HIPFLAT_URL,
        "facts": "Soi Muban Wiset Suk Nakhon, Thung Khru; completed Jan 1992; 595 units; 5 floors.",
        "longdoRecord": "Approved Wisetsuk Nakhon Condominium, Soi Sap Bunchai 2, Thung Khru.",
    },
    "rejectedCoordinate": {
        **old,
        "reason": "The same-name PropertyHub project is indexed in Bang Khae. Its area does not match the Hipflat Thung Khru project and is not used as the coordinate source.",
    },
    "marketSamples": {
        "sale": "No active sale listing confirmed for this Thung Khru project in the checked project pages. A same-name PropertyHub 790,000 THB listing is in Bang Khae and is excluded.",
        "rent": "No active rent listing confirmed for this Thung Khru project in the checked project pages.",
    },
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
