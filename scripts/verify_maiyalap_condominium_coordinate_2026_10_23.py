"""Record the independently corroborated Maiyalap Condominium location."""

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dist" / "bangkok-verified-coordinates.js"
REPORT = ROOT / "reports" / "maiyalap-condominium-coordinate-verification-2026-10-23.json"
HIPFLAT_ID = 3872
LAT, LNG = 13.85341382, 100.630478413
PROJECT = "https://zmyhome.com/project/V13013"
MAP = "https://zmyhome.com/search/result?id=13013&keyword=%E0%B8%A1%E0%B8%B1%E0%B8%A2%E0%B8%A5%E0%B8%B2%E0%B8%A0%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1&lat=13.8534138200&lng=100.6304784130&type=Project&typePost%5B0%5D=1&typePost%5B1%5D=2&typePost%5B2%5D=8&typePost%5B3%5D=10&typePost%5B4%5D=9&typeProperty%5B0%5D=1"
HIPFLAT = "https://www.hipflat.co.th/en/projects/maiyalap-condominium-bfabxl"


def distance_m(a, b):
    rad = math.pi / 180
    p1, p2 = a[0] * rad, b[0] * rad
    dp, dl = (b[0] - a[0]) * rad, (b[1] - a[1]) * rad
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6_371_000 * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


text = PATH.read_text(encoding="utf-8")
match = re.search(r"window\.BANGKOK_VERIFIED_COORDINATES\s*=\s*(\[.*\]);", text, re.S)
if not match:
    raise ValueError(f"Cannot parse {PATH}")
rows = json.loads(match.group(1))
existing = next((row for row in rows if int(row.get("hipflatId", -1)) == HIPFLAT_ID), None)
record = {
    "hipflatId": HIPFLAT_ID,
    "name": "Maiyalap Condominium",
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "ZmyHome project map coordinates",
    "sourceUrl": MAP,
    "verificationSourceUrl": PROJECT,
    "verificationMethod": "ZmyHome map search coordinates for project V13013; exact project name and Ramintra 14/Tha Raeng address corroborated by the ZmyHome and Hipflat project pages. ArcGIS exact-name Maiyalap Condominium POI is within 6 m.",
}
if existing and (abs(float(existing["lat"]) - LAT) > 0.00001 or abs(float(existing["lng"]) - LNG) > 0.00001):
    raise ValueError(f"Refusing to replace conflicting verified coordinate: {existing}")
if not existing:
    rows.append(record)
rows.sort(key=lambda row: int(row["hipflatId"]))
PATH.write_text("window.BANGKOK_VERIFIED_COORDINATES=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
arcgis = (13.853404975, 100.63052947)
REPORT.write_text(json.dumps({
    "checkedAt": "2026-10-23",
    "hipflatId": HIPFLAT_ID,
    "project": "Maiyalap Condominium",
    "address": "Soi Ramintra 14, Tha Raeng, Bang Khen, Bangkok 10230",
    "coordinate": {"lat": LAT, "lng": LNG, "source": MAP, "sourceType": "ZmyHome project map center"},
    "crossChecks": [
        {"source": "ZmyHome project page", "url": PROJECT, "finding": "Exact Maiyalap Condominium project name, Ramintra 14, Tha Raeng, Bang Khen address; project record V13013."},
        {"source": "Hipflat project page", "url": HIPFLAT, "finding": "Exact Maiyalap Condominium project name and Soi Muban Inthon Phithak address in Tha Raeng/Bang Khen."},
        {"source": "ArcGIS World Geocoding Service", "finding": "POI exact name Maiyalap Condominium at Soi Maiyalap, Tha Raeng, Bang Khen; candidate 13.853404975, 100.63052947.", "distanceFromZmyHomeMapMeters": round(distance_m((LAT, LNG), arcgis), 1)},
    ],
    "decision": "Accepted as verified based on project-specific coordinates and matching exact-name POI within 6 m.",
    "coordinateRecordAdded": not bool(existing),
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": HIPFLAT_ID, "added": not bool(existing), "verifiedCoordinateCount": len(rows), "arcgisOffsetMeters": round(distance_m((LAT, LNG), arcgis), 1)}, ensure_ascii=False))
