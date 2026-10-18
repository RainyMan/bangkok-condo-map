"""Add verified Longdo Map coordinates for Varrzon Residence Sukhumvit 36."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3139
PROJECT_NAME = "Varrzon Residence Sukhumvit 36"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/varrzon-residence-sukhumvit-36-zlyrxc"
LONGDO_URL = "https://map.longdo.com/p/A10174793"


def load_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not find {symbol} in {path.name}")
    return json.loads(match.group(1))


coordinate_path = DIST / "bangkok-verified-coordinates.js"
coordinates = load_array(coordinate_path, "BANGKOK_VERIFIED_COORDINATES")
row = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.722641799133,
    "lng": 100.57552233338,
    "locationVerified": True,
    "sourceName": "Longdo Map 已核准地點座標",
    "sourceUrl": LONGDO_URL,
    "verificationSourceUrl": HIPFLAT_URL,
    "verificationMethod": "approved_longdo_poi_exact_name_and_thai_address_cross_checked_with_hipflat_project",
}
coordinates = [item for item in coordinates if int(item.get("hipflatId", 0)) != PROJECT_ID]
coordinates.append(row)
coordinate_path.write_text(
    "window.BANGKOK_VERIFIED_COORDINATES = "
    + json.dumps(coordinates, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html = re.sub(
    r'bangkok-verified-coordinates\.js\?v=[^" ]+',
    "bangkok-verified-coordinates.js?v=20261018r-varrzon-sukhumvit36-longdo",
    html,
)
index_path.write_text(html, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "checkedAt": date.today().isoformat(),
    "location": {
        "status": "verified_project_poi",
        "lat": row["lat"],
        "lng": row["lng"],
        "sourceUrl": LONGDO_URL,
        "corroboratingProjectUrl": HIPFLAT_URL,
        "method": row["verificationMethod"],
        "evidence": "Longdo approved POI A10174793 has the exact Thai/English project name and Soi Naphasap 2 address; its canonical map page embeds coordinates 13.722641799133, 100.57552233338. Hipflat's exact project page has the same project name and address.",
    },
    "walkingRoute": next(
        item
        for item in load_array(DIST / "bangkok-walk-routes.js", "BANGKOK_WALK_ROUTES")
        if int(item.get("id", 0)) == PROJECT_ID
    ),
    "market": {
        "sale": {
            "status": "no_current_individual_listing_verified",
            "sources": [
                {
                    "url": "https://www.ddproperty.com/en/project/13621-%E0%B8%A7%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%8B%E0%B8%AD%E0%B8%93-%E0%B9%80%E0%B8%A3%E0%B8%AA%E0%B8%8B%E0%B8%B4%E0%B9%80%E0%B8%94%E0%B9%89%E0%B8%99%E0%B8%97%E0%B9%8C-%E0%B8%AA%E0%B8%B8%E0%B8%82%E0%B8%B8%E0%B8%A1%E0%B8%A7%E0%B8%B4%E0%B8%97-36-varrzon-residence-sukhumvit-36/",
                    "finding": "DDproperty project page search result reports 0 sale listings; individual unit-level listing not found.",
                }
            ],
        },
        "rent": {
            "status": "summary_present_individual_active_listing_not_verified",
            "sources": [
                {
                    "url": HIPFLAT_URL,
                    "finding": "Hipflat project result reports 6 rentals and shows two-bedroom cards at ฿38,000–50,000/month for 50 sqm, but the 38,000 individual ad resolves to Rhythm Sukhumvit 36-38, a different project. Do not import that card as a Varrzon sample.",
                },
                {
                    "url": "https://www.thailand-property.com/ads/2-bedroom-apartment-for-rent-in-varrzon-residence-sukhumvit-36-khlong-tan-bangkok-near-bts-thong-lo_9886b13066a1-3900-c642-ce0b-6a4cc089",
                    "finding": "Exact Varrzon 2-bedroom, 50 sqm, ฿50,000/month apartment page was indexed about five months ago; current availability cannot be confirmed, so it is excluded from current rent statistics and ROI.",
                },
                {
                    "url": "https://www.renthub.in.th/en/varrzon-residence-sukhumvit-36",
                    "finding": "Building rental page lists studio and one-bedroom rates with rooms available, but it identifies serviced apartment rooms and does not provide a current individually linked Varrzon two-bedroom condo listing.",
                },
            ],
        },
        "yield": "not calculated: no current verified sale sample and no current individual rent sample that can be safely matched to the project",
    },
}
(ROOT / "reports" / "varrzon-sukhumvit-36-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": [row["lat"], row["lng"]], "verifiedCoordinates": len(coordinates), "sale": report["market"]["sale"]["status"], "rent": report["market"]["rent"]["status"]}, ensure_ascii=False))
