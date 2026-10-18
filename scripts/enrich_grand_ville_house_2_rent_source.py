from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PID = 4211
URL = "https://www.ddproperty.com/en/property/grand-ville-house-2-bangkok-for-rent-500566084"
PROJECT_URL = "https://www.ddproperty.com/en/project/6468-grand-ville-house-2"
PRICE, AREA, BEDS, UPDATED = 100_000, 250.0, 3, "2026-09-18"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temp = target.with_suffix(target.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as out:
        out.write(f"window.{symbol} = ")
        for chunk in json.JSONEncoder(ensure_ascii=False, separators=(",", ":")).iterencode(rows):
            out.write(chunk)
        out.write(";\n")
    temp.replace(target)


def main() -> None:
    project = next(x for x in read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE") if int(x["id"]) == PID)
    if project["name"] != "Grand Ville House 2" or not any(x in project.get("address", "") for x in ("Watthana", "Vadhana")):
        raise RuntimeError("Grand Ville House 2 project identity did not match")
    manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    row = next((x for x in manual if int(x["hipflatId"]) == PID), None)
    if row is None:
        row = {"hipflatId": PID, "name": "Grand Ville House 2"}
        manual.append(row)
    sample = {
        "id": "500566084", "price": PRICE, "area": AREA, "priceSqm": round(PRICE / AREA),
        "beds": BEDS, "roomType": "3BR",
        "title": "Pet-Friendly 3-BR 250 Sqm At Grand Ville House 2 Near MRT Sukhumvit",
        "url": URL, "sourceName": "DDproperty", "projectName": "Grand Ville House 2",
        "updated": UPDATED, "checkedAt": date.today().isoformat(),
        "matchedBy": "exact_project_name_address_and_listing_id_2857453",
        "listingStatus": "availability_unconfirmed_update_over_30d",
    }
    rent = {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_individual_listing",
        "average": PRICE, "minimum": PRICE, "minimumArea": AREA,
        "averageSqm": round(PRICE / AREA), "minimumSqm": round(PRICE / AREA),
        "minimumSampleUpdated": UPDATED, "minimumSqmSampleUpdated": UPDATED,
        "asOf": date.today().isoformat(), "snapshotMethod": "DDproperty exact project and direct listing page",
        "sourceName": "DDproperty 個別掛牌", "source": PROJECT_URL,
        "minimumSourceUrl": URL, "minimumSqmSourceUrl": URL,
        "byBedroom": {"3": {"count": 1, "minimum": PRICE, "area": AREA,
                              "priceSqm": round(PRICE / AREA), "minimumSqm": round(PRICE / AREA), "sourceUrl": URL}},
        "samples": [sample],
    }
    row["rent"] = rent
    row["asOf"] = date.today().isoformat()
    manual.sort(key=lambda x: int(x["hipflatId"]))
    write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)
    report = {
        "hipflatId": PID, "projectName": project["name"], "checkedAt": date.today().isoformat(),
        "rentListing": {"id": sample["id"], "propertyScoutId": "2857453", "priceThbPerMonth": PRICE,
                        "areaSqm": AREA, "bedrooms": BEDS, "rentThbPerSqmMonth": round(PRICE / AREA, 2),
                        "updated": UPDATED, "url": URL},
        "sources": [
            {"url": URL, "finding": "Direct listing page identifies Grand Ville House 2, 3 bedrooms, 250 sqm, THB 100,000/month, PropertyScout ID 2857453."},
            {"url": PROJECT_URL, "finding": "DDproperty project page identifies Grand Ville House 2 at Sukhumvit 19, Watthana."},
        ],
        "limitations": [
            "Listing update date is over 30 days old; current availability is unconfirmed.",
            "This is a 3-bedroom sample and does not supply the missing direct 2-bedroom rent basis for investment yield.",
        ],
    }
    output = ROOT / "reports" / f"grand-ville-house-2-rent-source-{date.today().isoformat()}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": PID, "price": PRICE, "areaSqm": AREA, "beds": BEDS,
                      "rentPerSqm": round(PRICE / AREA, 2), "report": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
