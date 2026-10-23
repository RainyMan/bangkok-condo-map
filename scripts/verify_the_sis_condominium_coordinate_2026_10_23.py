"""Record the exact, independently corroborated location of The Sis Condominium."""

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDINATES = ROOT / "dist" / "bangkok-verified-coordinates.js"
REPORT = ROOT / "reports" / "the-sis-condominium-coordinate-verification-2026-10-23.json"
HIPFLAT_ID = 3820
LAT, LNG = 13.714320, 100.412723
PRIMARY = "https://www.homenayoo.com/the-sis-condo-bangkhae/"
VERIFICATION = "https://zmyhome.com/project/V13068"
HIPFLAT = "https://www.hipflat.co.th/en/projects/the-sis-condominium-yqeweo"


def distance_m(lat1, lng1, lat2, lng2):
    radius = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


text = COORDINATES.read_text(encoding="utf-8")
match = re.search(r"window\.BANGKOK_VERIFIED_COORDINATES\s*=\s*(\[.*\]);", text, re.S)
if not match:
    raise ValueError(f"Cannot parse {COORDINATES}")
rows = json.loads(match.group(1))
existing = next((row for row in rows if int(row.get("hipflatId", -1)) == HIPFLAT_ID), None)
record = {
    "hipflatId": HIPFLAT_ID,
    "name": "The Sis Condominium",
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "Homenayoo project page Google coordinates",
    "sourceUrl": PRIMARY,
    "verificationSourceUrl": VERIFICATION,
    "verificationMethod": "Exact project name and Soi Phet Kasem 76/1 address confirmed by Hipflat and ZmyHome; Homenayoo Google pin is within 14 m of the ArcGIS POI with the exact project name and matching street address.",
}
if existing and (abs(float(existing["lat"]) - LAT) > 0.00001 or abs(float(existing["lng"]) - LNG) > 0.00001):
    raise ValueError(f"Refusing to replace conflicting verified coordinate: {existing}")
if not existing:
    rows.append(record)
rows.sort(key=lambda row: int(row["hipflatId"]))
COORDINATES.write_text(
    "window.BANGKOK_VERIFIED_COORDINATES=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)

arcgis = {"lat": 13.714338957, "lng": 100.412599482}
REPORT.write_text(json.dumps({
    "checkedAt": "2026-10-23",
    "hipflatId": HIPFLAT_ID,
    "project": "The Sis Condominium",
    "address": "Soi Phet Kasem 76/1, Bang Khae Nuea, Bang Khae, Bangkok 10160",
    "coordinate": {"lat": LAT, "lng": LNG, "source": PRIMARY, "sourceType": "published Google coordinates"},
    "crossChecks": [
        {"source": "Hipflat", "url": HIPFLAT, "finding": "Exact project name and full Soi Phet Kasem 76/1 address."},
        {"source": "ZmyHome", "url": VERIFICATION, "finding": "Exact project name and same street/subdistrict/district."},
        {"source": "ArcGIS World Geocoding Service", "finding": "POI exact name The Sis Condominium at Soi Phet Kasem 76/1; candidate 13.714338957, 100.412599482.", "distanceFromPublishedGooglePinMeters": round(distance_m(LAT, LNG, arcgis["lat"], arcgis["lng"]), 1)},
    ],
    "decision": "Accepted as a verified project coordinate: the published project Google pin matches the exact project address and is independently corroborated by a same-name POI within 14 m.",
    "coordinateRecordAdded": not bool(existing),
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": HIPFLAT_ID, "added": not bool(existing), "verifiedCoordinateCount": len(rows), "arcgisOffsetMeters": round(distance_m(LAT, LNG, arcgis["lat"], arcgis["lng"]), 1)}, ensure_ascii=False))
