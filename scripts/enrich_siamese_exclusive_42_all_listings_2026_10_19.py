from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from enrich_propertyhub_exact_project_pages import parse_market

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3538
PROJECT_NAME = "Siamese Exclusive Sukhumvit 42"
PROPERTYHUB_PROJECT_ID = "3592"
SLUG = "siamese-exclusive-sukhumvit-42"
AS_OF = date.today()
PROJECT_URL = f"https://propertyhub.in.th/en/projects/{SLUG}"
SALE_URL = f"https://propertyhub.in.th/en/condo-for-sale/project-{SLUG}"
RENT_URL = f"https://propertyhub.in.th/en/condo-for-rent/project-{SLUG}"
REPORT = ROOT / "reports" / f"siamese-exclusive-42-listings-{AS_OF.isoformat()}.json"


def load_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot read {symbol} from {filename}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"window.{symbol} = ")
        for chunk in encoder.iterencode(rows):
            stream.write(chunk)
        stream.write(";\n")
    temporary.replace(target)


def verified_market(kind: str, excluded_ids: set[str]) -> tuple[dict, dict]:
    result = parse_market(PROJECT_ID, kind, SLUG, PROPERTYHUB_PROJECT_ID)
    if result.get("error"):
        raise RuntimeError(f"PropertyHub {kind} page failed validation: {result['error']}")
    project = result.get("project") or {}
    if str(project.get("id")) != PROPERTYHUB_PROJECT_ID:
        raise RuntimeError(f"PropertyHub project ID mismatch for {kind}: {project.get('id')}")
    project_name = str(project.get("nameEnglish") or project.get("name") or "")
    if project_name != PROJECT_NAME:
        raise RuntimeError(f"PropertyHub project name mismatch: {project_name}")

    cutoff = AS_OF - timedelta(days=30)
    samples = []
    excluded = []
    for card in result.get("cards", []):
        listing_id = str(card.get("id") or "")
        if listing_id in excluded_ids:
            excluded.append({"id": listing_id, "reason": "Listing title conflicts with the exact project (Sukhumvit 31 listing was attached to the Sukhumvit 42 project feed)."})
            continue
        updated = str(card.get("updated") or "")[:10]
        try:
            updated_date = date.fromisoformat(updated)
        except ValueError:
            updated_date = None
        status = (
            "active_as_listed" if updated_date and updated_date >= cutoff
            else "availability_unconfirmed_update_over_30d" if updated_date
            else "availability_unconfirmed_date_unknown"
        )
        sample = {
            **card,
            "sourceName": "PropertyHub",
            "projectName": PROJECT_NAME,
            "checkedAt": AS_OF.isoformat(),
            "matchedBy": f"exact PropertyHub project ID {PROPERTYHUB_PROJECT_ID} and direct listing card",
            "listingStatus": status,
        }
        samples.append(sample)

    current = [sample for sample in samples if sample["listingStatus"] == "active_as_listed"]
    if not current:
        raise RuntimeError(f"No current verified PropertyHub {kind} listings remain")
    source_url = SALE_URL if kind == "sale" else RENT_URL

    def rate(sample: dict) -> float:
        return float(sample["price"]) / float(sample["area"])

    lowest_total = min(current, key=lambda sample: float(sample["price"]))
    lowest_rate = min(current, key=rate)
    bedrooms = sorted({int(sample["beds"]) for sample in current if sample.get("beds")})
    by_bedroom = {}
    for beds in bedrooms:
        group = [sample for sample in current if int(sample.get("beds") or 0) == beds]
        low_total = min(group, key=lambda sample: float(sample["price"]))
        low_rate = min(group, key=rate)
        by_bedroom[str(beds)] = {
            "count": len(group),
            "minimum": float(low_total["price"]),
            "area": float(low_total["area"]),
            "minimumArea": float(low_total["area"]),
            "priceSqm": round(rate(low_total)),
            "minimumSqm": round(rate(low_rate), 2),
            "minimumSourceUrl": low_total["url"],
            "sourceUrl": low_total["url"],
            "minimumSqmSourceUrl": low_rate["url"],
        }
    current_rates = [rate(sample) for sample in current]
    market = {
        "count": len(current),
        "observedCount": len(samples),
        "platformCount": int(result.get("totalCount") or 0),
        "countKind": "manual_verified_listing",
        "average": round(sum(float(sample["price"]) for sample in current) / len(current)),
        "minimum": float(lowest_total["price"]),
        "minimumArea": float(lowest_total["area"]),
        "averageSqm": round(sum(current_rates) / len(current_rates)),
        "minimumSqm": round(rate(lowest_rate), 2),
        "minimumSampleUpdated": lowest_total.get("updated"),
        "minimumSqmSampleUpdated": lowest_rate.get("updated"),
        "asOf": AS_OF.isoformat(),
        "snapshotMethod": "PropertyHub exact project ID 3592; all available project-feed pages fetched, room and price fields read from each direct listing card; listings over 30 days marked unconfirmed.",
        "sourceName": "PropertyHub 個別掛牌",
        "source": source_url,
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "byBedroom": by_bedroom,
        "samples": samples,
    }
    result_report = {
        "projectId": PROJECT_ID,
        "projectName": PROJECT_NAME,
        "kind": kind,
        "propertyHubProjectId": PROPERTYHUB_PROJECT_ID,
        "projectNameOnSource": project_name,
        "platformCount": int(result.get("totalCount") or 0),
        "validIndividualListings": len(samples),
        "currentListingsWithin30Days": len(current),
        "olderOrUndatedListings": len(samples) - len(current),
        "byBedroom": by_bedroom,
        "excludedListings": excluded,
        "sourceUrl": source_url,
        "checkedAt": AS_OF.isoformat(),
    }
    return market, result_report


sale, sale_report = verified_market("sale", {"6206486"})
rent, rent_report = verified_market("rent", set())

manual = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
rows = {int(row["hipflatId"]): row for row in manual}
entry = rows.get(PROJECT_ID, {"hipflatId": PROJECT_ID, "name": PROJECT_NAME})
entry.update({
    "name": PROJECT_NAME,
    "asOf": AS_OF.isoformat(),
    "fee": {
        "rate": 75,
        "status": "published_indicative",
        "note": "PropertyHub 專案頁列示 Common Fee 為 75 THB/sqm；請向管委會確認現行費率。",
        "source": PROJECT_URL,
    },
    "sale": sale,
    "rent": rent,
    "replaceSale": True,
    "replaceRent": True,
})
rows[PROJECT_ID] = entry
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", [rows[key] for key in sorted(rows)])

REPORT.write_text(json.dumps({"projectId": PROJECT_ID, "projectName": PROJECT_NAME, "asOf": AS_OF.isoformat(), "propertyHubProjectId": PROPERTYHUB_PROJECT_ID, "projectUrl": PROJECT_URL, "sale": sale_report, "rent": rent_report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"projectId": PROJECT_ID, "sale": {"sourceSamples": sale["observedCount"], "current": sale["count"], "twoBedroom": sale["byBedroom"].get("2")}, "rent": {"sourceSamples": rent["observedCount"], "current": rent["count"], "twoBedroom": rent["byBedroom"].get("2")}, "report": str(REPORT)}, ensure_ascii=False, indent=2))
