"""Add the exact PropertyHub map coordinate for Hipflat project 3073."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "apa-place-coordinate-2026-10-18.json"


def load_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Could not parse {symbol} from {path.name}")
    return json.loads(match.group(1))


def main() -> None:
    project_id = 3073
    project_url = "https://propertyhub.in.th/projects/arpa-place"
    hipflat_url = "https://www.hipflat.co.th/en/projects/apa-place-ufwlfe"
    lat, lng = 13.81843758868402, 100.58861314472551
    path = DIST / "bangkok-verified-coordinates.js"
    rows = load_array(path, "BANGKOK_VERIFIED_COORDINATES")
    existing = next((row for row in rows if int(row["hipflatId"]) == project_id), None)
    record = {
        "hipflatId": project_id,
        "name": "A-Pa Place",
        "lat": lat,
        "lng": lng,
        "locationVerified": True,
        "sourceName": "PropertyHub 專案頁地圖座標",
        "sourceUrl": project_url,
        "verificationSourceUrl": hipflat_url,
        "verificationMethod": "exact_Thai_and_English_project_name_and_Chan_Kasem_Chatuchak_address_cross_checked_against_Hipflat",
    }
    if existing:
        rows[rows.index(existing)] = record
    else:
        rows.append(record)
    path.write_text(
        "window.BANGKOK_VERIFIED_COORDINATES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    report = {
        "hipflatId": project_id,
        "project": "A-Pa Place",
        "coordinates": {"lat": lat, "lng": lng},
        "coordinateSource": project_url,
        "projectIdentityCrosscheck": hipflat_url,
        "identityEvidence": "PropertyHub project title Arpa Place and Thai name อาภา เพลส; Hipflat A-Pa Place page carries the same Thai name and Soi Chamchuri, Chan Kasem, Chatuchak address.",
        "mapEvidence": "PropertyHub project page embedded project location object with these latitude/longitude values.",
        "checkedAt": "2026-10-18",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": project_id, "coordinates": record, "verifiedCoordinateCount": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
