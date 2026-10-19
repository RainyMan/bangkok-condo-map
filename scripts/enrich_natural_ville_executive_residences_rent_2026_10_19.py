from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"natural-ville-executive-residences-rent-{date.today().isoformat()}.json"
PROJECT_ID = 3103
PROJECT_NAME = "Natural Ville Executive Residences"
AS_OF = date.today().isoformat()
PROJECT_URL = "https://www.hipflat.co.th/en/projects/natural-ville-executive-residences-jegmqe"
LISTING_URL = "https://www.hipflat.co.th/en/ads/97c40c728nue2c9019439tln3u0c1u2u"
PRICE_REFERENCE_URL = "https://www.dotproperty.co.th/en/ads/1-bedroom-apartment-for-rent-in-natural-ville-executive-residences-lumphini-bangkok_e90e681b9270-f630-8892-f7ba-c345b089"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format: {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    path = DIST / filename
    temporary = path.with_suffix(path.suffix + ".tmp")
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"window.{symbol} = ")
        for chunk in encoder.iterencode(rows):
            stream.write(chunk)
        stream.write(";\n")
    temporary.replace(path)


catalogue = next(row for row in read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE") if int(row["id"]) == PROJECT_ID)
if catalogue["name"] != PROJECT_NAME or catalogue.get("hipflatProjectUrl") != PROJECT_URL:
    raise RuntimeError("Hipflat catalogue identity does not match the reviewed project page")

sample = {
    "id": "438120TP2",
    "price": 60000,
    "area": 59,
    "priceSqm": round(60000 / 59),
    "beds": 1,
    "roomType": "1BR",
    "title": f"{PROJECT_NAME} · 1 房 · 59 ㎡ · ฿60,000/月",
    "url": LISTING_URL,
    "sourceName": "Hipflat / PropertyScout",
    "projectName": PROJECT_NAME,
    "checkedAt": AS_OF,
    "updated": "2026-09-09",
    "listingStatus": "active_as_listed",
    "matchedBy": "Hipflat project page currently lists this single available unit; linked unit page matches the Thai project name and 1BR/59sqm; Dot Property confirms THB asking rent and PropertyScout ID 438120.",
    "priceReferenceUrl": PRICE_REFERENCE_URL,
}
market = {
    "count": 1,
    "observedCount": 1,
    "platformCount": 1,
    "countKind": "manual_verified_listing",
    "average": sample["price"],
    "minimum": sample["price"],
    "minimumArea": sample["area"],
    "averageSqm": round(sample["price"] / sample["area"]),
    "minimumSqm": round(sample["price"] / sample["area"], 2),
    "minimumSampleUpdated": sample["updated"],
    "minimumSqmSampleUpdated": sample["updated"],
    "asOf": AS_OF,
    "snapshotMethod": "Hipflat project page shows one available rental unit and links the direct listing; listing details were cross-checked against the project name and PropertyScout ID, while Dot Property confirms THB rent.",
    "sourceName": "Hipflat 專案可用租盤",
    "source": PROJECT_URL,
    "minimumSourceUrl": LISTING_URL,
    "minimumSqmSourceUrl": LISTING_URL,
    "samples": [sample],
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
rows = {int(row["hipflatId"]): row for row in manual}
entry = rows.get(PROJECT_ID, {"hipflatId": PROJECT_ID, "name": PROJECT_NAME})
entry.update({"name": PROJECT_NAME, "asOf": AS_OF, "rent": market, "replaceRent": True})
rows[PROJECT_ID] = entry
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", [rows[key] for key in sorted(rows)])
REPORT.write_text(json.dumps({"hipflatId": PROJECT_ID, "projectName": PROJECT_NAME, "checkedAt": AS_OF, "rent": market, "sale": {"status": "no verified current sample"}, "yield": {"status": "not calculated", "reason": "No verified sale listing for this project."}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": PROJECT_NAME, "rentPrice": sample["price"], "rentArea": sample["area"], "rentRatePerSqm": market["minimumSqm"], "directListing": LISTING_URL, "report": str(REPORT)}, ensure_ascii=False, indent=2))
