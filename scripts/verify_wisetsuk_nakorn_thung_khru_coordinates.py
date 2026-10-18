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
REPORT_PATH = ROOT / "reports" / "wisetsuk-nakorn-coordinate-correction-2026-10-19.json"


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
    "propertyHubProjectId": None,
    "propertyHubProjectUrl": None,
    "propertyHubSaleUrl": None,
    "propertyHubRentUrl": None,
})
save_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", projects)

# Keep the unbundled research feed from restoring the same-name Bang Khae pin
# on the next browser-data rebuild.
source_path = DIST / "bangkok-propertyhub.js"
source_text = source_path.read_text(encoding="utf-8")
source_start = source_text.find('{"id":3054,')
if source_start < 0:
    raise ValueError("Project 3054 not found in the unbundled PropertyHub feed")
source_project, source_end = json.JSONDecoder().raw_decode(source_text, source_start)
if source_project.get("locationSourceUrl") != "https://propertyhub.in.th/en/projects/wisetsuk-nakorn-condo":
    raise ValueError("The unbundled PropertyHub coordinate source differs from the mismatch being corrected")
source_project.update({
    "lat": None,
    "lng": None,
    "locationVerified": False,
    "locationSourceUrl": None,
    "locationSourceName": None,
    "locationVerificationSourceUrl": None,
    "propertyHubProjectId": None,
    "propertyHubProjectUrl": None,
    "coordinateConflictNote": "Same-name PropertyHub record points to Bang Khae, not the Hipflat Thung Khru project; exclude its pin and listings.",
})
source_text = source_text[:source_start] + json.dumps(source_project, ensure_ascii=False, separators=(",", ":")) + source_text[source_end:]
source_path.write_text(source_text, encoding="utf-8")

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
    ("bangkok-propertyhub-map.js", "20261019a-wisetsuk-same-name-mismatch-corrected"),
    ("bangkok-verified-coordinates.js", "20261019a-wisetsuk-longdo-coordinate"),
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
    "checkedAt": "2026-10-19",
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
    "marketCrosscheck": {
        "propertyHubSalePage": "https://propertyhub.in.th/en/condo-for-sale/project-wisetsuk-nakorn-condo",
        "propertyHubRentPage": "https://propertyhub.in.th/en/condo-for-rent/project-wisetsuk-nakorn-condo",
        "finding": "The only linked PropertyHub project is in Bang Khae and its 790,000 THB/51 sqm listing identifies Bang Khae; excluded from the Hipflat Thung Khru project. Hipflat project page reports no available property, and no current Thung Khru sale or rental object could be verified.",
        "excludedListingUrl": "https://propertyhub.in.th/en/listings/condo-for-sale-at-wisetsuk-nakorn-condo-bang-khae-large-corner-unit-51-sq-m-fully-furnished-and-ready-to-move-in---6184765",
    },
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

crosscheck_path = DIST / "bangkok-market-crosschecks.js"
crosschecks_text = crosscheck_path.read_text(encoding="utf-8")
match = re.fullmatch(r"window\.BANGKOK_MARKET_CROSSCHECKS\s*=\s*(\[.*\]);\s*", crosschecks_text, re.S)
if not match:
    raise ValueError("Unexpected market crosscheck format")
crosschecks = json.loads(match.group(1))
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", 0)) != PROJECT_ID]
crosschecks.append({
    "hipflatId": PROJECT_ID,
    "projectName": NAME,
    "asOf": "2026-10-19",
    "sourceName": "Hipflat / PropertyHub",
    "projectSourceUrl": HIPFLAT_URL,
    "sale": {"activeListingCount": 0, "sourceUrl": "https://propertyhub.in.th/en/condo-for-sale/project-wisetsuk-nakorn-condo"},
    "rent": {"activeListingCount": 0, "sourceUrl": "https://propertyhub.in.th/en/condo-for-rent/project-wisetsuk-nakorn-condo"},
    "availabilitySources": [
        {"sourceName": "Hipflat exact project page", "url": HIPFLAT_URL, "statusLabel": "專案頁目前顯示無可用出售或出租物件。"},
        {"sourceName": "PropertyHub same-name project page", "url": "https://propertyhub.in.th/en/projects/wisetsuk-nakorn-condo", "statusLabel": "同名頁面位於 Bang Khae，與 Hipflat 的 Thung Khru 專案不同，不納入。"},
        {"sourceName": "PropertyHub excluded same-name listing", "url": report["marketCrosscheck"]["excludedListingUrl"], "statusLabel": "฿790,000／51㎡ 刊登明確指向 Bang Khae；非 Thung Khru 樣本。"},
    ],
})
crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
crosscheck_path.write_text("window.BANGKOK_MARKET_CROSSCHECKS = " + json.dumps(crosschecks, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
index_text = index_path.read_text(encoding="utf-8")
index_text, n = re.subn(
    r"bangkok-market-crosschecks\.js\?v=[^\"']+",
    "bangkok-market-crosschecks.js?v=20261019a-wisetsuk-no-market-and-name-collision",
    index_text,
    count=1,
)
if n != 1:
    raise ValueError("Could not update market crosschecks cache key")
index_path.write_text(index_text, encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
