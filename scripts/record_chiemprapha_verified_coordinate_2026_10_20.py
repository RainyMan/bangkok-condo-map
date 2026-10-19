"""Record Chiemprapha Mansion's exact named POI coordinate from Longdo Map."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dist" / "bangkok-verified-coordinates.js"
REPORT = ROOT / "reports" / "chiemprapha-coordinate-verification-2026-10-20.json"
PROJECT_ID = 3469
LONGDO_URL = "https://map.longdo.com/p/A00313337"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/chiemprapha-mansion-ezrsuj"

text = DATA.read_text(encoding="utf-8")
prefix = "window.BANGKOK_VERIFIED_COORDINATES = "
assert text.startswith(prefix) and text.rstrip().endswith(";")
rows = json.loads(text[len(prefix):].rstrip()[:-1])
existing = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
entry = {
    "hipflatId": PROJECT_ID,
    "name": "Chiemprapha Mansion",
    "lat": 13.730846995662,
    "lng": 100.57237762299,
    "locationVerified": True,
    "sourceName": "Longdo Map approved named POI",
    "sourceUrl": LONGDO_URL,
    "verificationSourceUrl": HIPFLAT_URL,
    "verificationMethod": "Longdo named POI A00313337 (Thai name แจ่มประภา) and exact Soi Sukhumwit 41/Phirom address match the Hipflat project address Soi Phirom, Khlong Tan Nuea, Watthana",
}
if existing:
    rows[rows.index(existing)] = entry
else:
    rows.append(entry)
rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
DATA.write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": "Chiemprapha Mansion",
    "checkedAt": str(date.today()),
    "coordinates": {"lat": entry["lat"], "lng": entry["lng"]},
    "sources": [
        {"url": LONGDO_URL, "evidence": "Approved named POI A00313337; page's embedded map snippet gives lat=13.730846995662, long=100.57237762299 and names Soi Sukhumwit 41 (Phirom)."},
        {"url": HIPFLAT_URL, "evidence": "Bangkok condo project page uses the exact corresponding name Chiemprapha Mansion and address Soi Phirom, Khlong Tan Nuea, Watthana."},
    ],
    "method": entry["verificationMethod"],
}
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": report["coordinates"], "recorded": str(DATA.relative_to(ROOT)), "report": str(REPORT.relative_to(ROOT))}, ensure_ascii=True))
