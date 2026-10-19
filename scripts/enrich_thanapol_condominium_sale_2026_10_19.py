"""Record the directly linked current Thanapol Condominium sale listing."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"thanapol-condominium-sale-{date.today().isoformat()}.json"
PROJECT_ID = 3227
PROJECT_NAME = "Thanapol Condominium"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/thanapon-condominium-wccoki"
LISTING_URL = "https://www.hipflat.co.th/es/ads/e7l9092n88214287h1t37t9l3u0clte9"
PRICE_REFERENCE_URL = "https://www.fazwaz.com/property-sales/studio-condo-for-sale-at-thanapol-condominium-in-nong-khaem-bangkok-u6383026"
COORDINATE_SOURCE_URL = "https://www.kaibaanthai.com/en/projects/thailand/bangkok/nong-khaem/nong-khaem/thanapol-condominium"
AS_OF = date.today().isoformat()


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format: {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    path = DIST / filename
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"window.{symbol} = ")
        for chunk in json.JSONEncoder(ensure_ascii=False, separators=(",", ":")).iterencode(rows):
            stream.write(chunk)
        stream.write(";\n")
    temporary.replace(path)


catalogue = next(row for row in read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE") if int(row["id"]) == PROJECT_ID)
if catalogue["name"] != PROJECT_NAME or catalogue.get("hipflatProjectUrl") != PROJECT_URL:
    raise RuntimeError("Hipflat catalogue identity does not match the reviewed project page")

price = 220_000
area = 27
sample = {
    "id": "U6383026",
    "price": price,
    "area": area,
    "priceSqm": round(price / area, 2),
    "beds": 0,
    "roomType": "STUDIO",
    "title": f"{PROJECT_NAME} · 套房 · {area} ㎡ · ฿{price:,}",
    "url": LISTING_URL,
    "sourceName": "Hipflat（FazWaz 交叉核對）",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": AS_OF,
    "listingStatus": "active_as_listed",
    "matchedBy": "Hipflat direct listing identifies unit U6383026, Thanapol Condominium, studio, 27 sqm and ฿220,000; the project listing card and FazWaz direct unit page corroborate the THB price, unit size and project. Hipflat states listing updated 21 minutes before its indexed check on 2026-10-19.",
    "priceReferenceUrl": PRICE_REFERENCE_URL,
}
market = {
    "count": 1,
    "observedCount": 1,
    "platformCount": 1,
    "countKind": "manual_verified_listing",
    "average": price,
    "minimum": price,
    "minimumArea": area,
    "averageSqm": round(price / area),
    "minimumSqm": round(price / area, 2),
    "minimumSampleUpdated": AS_OF,
    "minimumSqmSampleUpdated": AS_OF,
    "asOf": AS_OF,
    "snapshotMethod": "Hipflat project-level sale availability and direct unit page cross-checked against the matching FazWaz unit page.",
    "sourceName": "Hipflat 個別出售掛牌",
    "source": PROJECT_URL,
    "minimumSourceUrl": LISTING_URL,
    "minimumSqmSourceUrl": LISTING_URL,
    "samples": [sample],
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
rows = {int(row["hipflatId"]): row for row in manual}
entry = rows.get(PROJECT_ID, {"hipflatId": PROJECT_ID, "name": PROJECT_NAME})
if entry.get("name") not in (None, PROJECT_NAME):
    raise RuntimeError("Manual market data name does not match project ID")
entry.update({
    "name": PROJECT_NAME,
    "completedYear": 1992,
    "completedYearSourceUrl": LISTING_URL,
    "asOf": AS_OF,
    "sale": market,
    "replaceSale": True,
})
rows[PROJECT_ID] = entry
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", [rows[key] for key in sorted(rows)])

coordinates = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = {int(row["hipflatId"]): row for row in coordinates}
coordinate_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.6819716,
    "lng": 100.3707816,
    "locationVerified": True,
    "sourceName": "KaiBaanThai 專案地圖",
    "sourceUrl": COORDINATE_SOURCE_URL,
    "verificationSourceUrl": PROJECT_URL,
    "verificationMethod": "KaiBaanThai 專案頁結構化地圖座標；以 Hipflat 同名專案及 Nong Khaem 街址核對",
    "checkedAt": AS_OF,
}
write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", [coordinate_rows[key] for key in sorted(coordinate_rows)])

REPORT.write_text(json.dumps({
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "sale": market,
    "rent": {"status": "not verified; no sample added"},
    "coordinates": {"lat": 13.6819716, "lng": 100.3707816, "source": COORDINATE_SOURCE_URL, "verificationSource": PROJECT_URL},
    "yield": {"status": "not calculated", "reason": "Only a studio sale is verified; no current rental sample is verified, and studio data is not substituted for a bedroom-class yield."},
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": PROJECT_NAME, "salePrice": price, "area": area, "pricePerSqm": market["minimumSqm"], "directListing": LISTING_URL, "report": str(REPORT)}, ensure_ascii=False, indent=2))
