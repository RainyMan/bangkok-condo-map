"""Add a directly verified current rental listing for Niche Mono Itsaraphap."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3369
PROJECT = "Niche Mono Itsaraphap"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-niche-mono-itsaraphap"
LISTING_URL = "https://propertyhub.in.th/en/listings/1bed-1bath-mrt-itsaraphap-30sqm-thb-13-000-mo-fl-4-niche-mono-itsaraphap-bangkok---6368947"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise RuntimeError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    checked = "2026-10-18"
    updated = "2026-10-03"
    sample = {
        "id": "6368947",
        "price": 13000,
        "area": 30,
        "priceSqm": round(13000 / 30, 2),
        "beds": 1,
        "roomType": "1BR",
        "title": "Niche Mono Itsaraphap，1 房，30 ㎡，4 樓，฿13,000/月",
        "url": LISTING_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "checkedAt": checked,
        "updated": updated,
        "availableFrom": "2026-09-03",
        "matchedBy": "exact_propertyhub_project_and_listing_page",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    record = {
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "rent": {
            "count": 1,
            "observedCount": 1,
            "countKind": "manual_verified_listing",
            "average": 13000,
            "minimum": 13000,
            "minimumArea": 30,
            "minimumSampleUpdated": updated,
            "averageSqm": 433,
            "minimumSqm": round(13000 / 30),
            "minimumSqmSampleUpdated": updated,
            "asOf": checked,
            "sourceName": "PropertyHub 個別掛牌",
            "source": PROJECT_URL,
            "minimumSourceUrl": LISTING_URL,
            "minimumSqmSourceUrl": LISTING_URL,
            "samples": [sample],
        },
    }
    market_path = DIST / "bangkok-manual-market-samples.js"
    rows = read_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    existing = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if existing:
        existing.update(record)
    else:
        rows.append(record)
        rows.sort(key=lambda row: int(row["hipflatId"]))
    market_path.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    report = {
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "checkedAt": checked,
        "projectSource": PROJECT_URL,
        "listing": sample,
        "notes": [
            "PropertyHub's exact project rent page showed three rental listings when checked on 2026-10-18; the listing page opened directly and identifies the project, one bedroom, 30 sqm, THB 13,000/month and floor 4.",
            "The project result card was refreshed 2026-10-03. The direct listing states available from 2026-09-03, a date already passed at verification; the listing remains visible, but current vacancy is unconfirmed and is labeled in the UI.",
            "The listing's rent per square metre is THB 433.33/month. The manually verified sample set contains only this directly inspected rental, not all three result cards.",
        ],
    }
    (ROOT / "reports" / "niche-mono-itsaraphap-rent-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added one exact PropertyHub rental sample for Hipflat condo {PROJECT_ID}.")


if __name__ == "__main__":
    main()
