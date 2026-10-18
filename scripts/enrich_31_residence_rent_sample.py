import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT = ROOT / "reports" / "31-residence-two-bedroom-rent-sample-2026-10-19.json"
SYMBOL = "BANGKOK_MANUAL_MARKET_SAMPLES"
sample = {
    "id": "6058105", "price": 90000, "area": 241, "priceSqm": 373,
    "beds": 2, "roomType": "TWO_BED_ROOM",
    "title": "Enormous 2 Bedroom Apartment with Large Private Terrace - BR21426AP",
    "url": "https://propertyhub.in.th/en/listings/enormous-2-bedroom-apartment-with-large-private-terrace-br21426ap---6058105",
    "sourceName": "PropertyHub", "projectName": "31 Residence",
    "updated": "2026-09-13", "checkedAt": "2026-10-19",
    "matchedBy": "exact_project_name_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_over_30d",
}
text = TARGET.read_text(encoding="utf-8")
match = re.search(rf"window\.{SYMBOL}\s*=\s*(\[.*\]);", text, re.S)
if not match:
    raise SystemExit(f"Cannot locate {SYMBOL}")
rows = json.loads(match.group(1))
entry = next((row for row in rows if int(row.get("hipflatId", 0)) == 3006), None)
if entry is None:
    entry = {"hipflatId": 3006, "name": "31 Residence"}
    rows.append(entry)
rent = entry.setdefault("rent", {})
samples = rent.setdefault("samples", [])
if not any(row.get("url") == sample["url"] for row in samples):
    samples.append(sample)
TARGET.write_text(f"window.{SYMBOL} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
REPORT.write_text(json.dumps({
    "hipflatId": 3006,
    "projectName": "31 Residence",
    "checkedAt": "2026-10-19",
    "rentListing": sample,
    "yieldEstimate": None,
    "sourceNotes": [
        {"url": sample["url"], "finding": "Direct PropertyHub unit page identifies 31 Residence, 2 bedrooms, 241 sqm, THB 90,000/month."},
        {"url": "https://www.ddproperty.com/en/project/6787-31-residence", "finding": "DDproperty project page shows 0 for-sale listings and current rent listings."},
        {"url": "https://www.propertyhub.in.th/en/condo-for-sale/project-31-residence", "finding": "PropertyHub for-sale project page currently reports no matched sale properties."},
    ],
    "limitations": ["Rental update date is 13 September 2026, so current availability is unconfirmed.", "No direct sale listing was found on PropertyHub or DDproperty; ROI is not calculated without a verified purchase price."],
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": "31 Residence", "rentThbPerMonth": sample["price"], "rentAreaSqm": sample["area"], "report": str(REPORT)}, ensure_ascii=False))
