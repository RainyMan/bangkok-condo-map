"""Add the directly linked PropertyScout rental to Origin Place Taopoon Interchange."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3585
NAME = "Origin Place Taopoon Interchange"
CHECKED = "2026-10-18"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/origin-place-taopoon-interchange-uanal8981a1e883aa9ce973lalttl33u"
PROJECT_RENT_URL = "https://propertyscout.co.th/en/bangkok/condo/origin-place-taopoon-interchange/"
RENT_URL = "https://propertyscout.co.th/en/1-br-condo-origin-place-taopoon-interchange-near-mrt-tao-poon-2328041/"


def read_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = DIST / filename
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.S,
    )
    if not match:
        raise ValueError(f"Cannot parse {symbol} from {path}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    rent_price, rent_area, rent_beds = 25_000, 28, 1
    rent_rate = rent_price / rent_area
    sample = {
        "id": "PS-2328041",
        "price": rent_price,
        "area": rent_area,
        "priceSqm": round(rent_rate),
        "beds": rent_beds,
        "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 28 ㎡ · ฿25,000/月",
        "url": RENT_URL,
        "sourceName": "PropertyScout",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "exact project name and direct PropertyScout condo listing detail",
        "availability": "AVAILABILITY UPON REQUEST",
        "listingStatus": "availability_unconfirmed_update_over_30d",
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": rent_price,
        "minimum": rent_price,
        "minimumArea": rent_area,
        "averageSqm": round(rent_rate),
        "minimumSqm": round(rent_rate),
        "asOf": CHECKED,
        "snapshotMethod": "Exact PropertyScout project page reports one rental unit; direct listing detail identifies the same project and unit metrics.",
        "sourceName": "PropertyScout 個別租賃掛牌（可用狀態待確認）",
        "source": PROJECT_RENT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": rent_price,
                "area": rent_area,
                "priceSqm": round(rent_rate),
                "minimumSqm": rent_rate,
                "sourceUrl": RENT_URL,
                "minimumSqmSourceUrl": RENT_URL,
            }
        },
        "samples": [sample],
    }

    manual_path, rows = read_array(
        "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
    )
    project = next(
        (row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None
    )
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(project)
    project["name"] = NAME
    existing = project.get("rent", {}).get("samples", [])
    unique = {row.get("url"): row for row in existing if row.get("url")}
    unique[RENT_URL] = sample
    # Preserve any previously added exact-project rent samples and recalculate
    # all summary minima from the individual linked records.
    samples = list(unique.values())
    lowest_total = min(samples, key=lambda row: float(row["price"]))
    lowest_rate = min(samples, key=lambda row: float(row["price"]) / float(row["area"]))
    project["rent"] = {
        **rent,
        "count": len(samples),
        "observedCount": len(samples),
        "average": round(sum(float(row["price"]) for row in samples) / len(samples)),
        "minimum": float(lowest_total["price"]),
        "minimumArea": float(lowest_total["area"]),
        "averageSqm": round(sum(float(row["price"]) / float(row["area"]) for row in samples) / len(samples)),
        "minimumSqm": round(float(lowest_rate["price"]) / float(lowest_rate["area"])),
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "samples": samples,
    }
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    report = {
        "hipflatId": PROJECT_ID,
        "projectName": NAME,
        "checkedAt": CHECKED,
        "hipflatProjectUrl": HIPFLAT_URL,
        "coordinate": {
            "status": "Existing map coordinate retained; this enrichment adds no coordinate override.",
            "sourceUrl": "https://propertyhub.in.th/en/projects/origin-place-taopoon-interchange",
        },
        "saleMarket": {
            "sourceUrl": "https://asset-direct-next.propertyhub.in.th/en/projects/origin-place-taopoon-interchange",
            "twoBedroomMinimumPriceTHB": 5_190_000,
            "twoBedroomAreaSqm": 51,
            "twoBedroomListingUrl": "https://propertyhub.in.th/en/listings/2-br-condo-at-origin-place-taopoon-interchange-near-mrt-tao-poon-id-1792243---5821883",
            "listingUpdated": "2026-10-18",
        },
        "rentListing": sample,
        "rentEvidence": {
            "projectPageUrl": PROJECT_RENT_URL,
            "projectPageReportsOneRental": True,
            "directListingDetails": "1 bedroom, 1 bathroom, 28 sqm, ฿25,000/month (฿892.86/sqm/month), 440m to MRT Tao Poon.",
            "availability": "PropertyScout labels it AVAILABILITY UPON REQUEST. The detail page says it was updated about two months before this check. It is included as an individual price sample, but its current availability is unconfirmed and marked so in the app.",
        },
        "yieldNote": "The available rent listing is one bedroom while the lowest linked sale listing is two bedrooms. The app therefore labels the default two-bedroom calculation as a cross-bedroom estimate until a two-bedroom rental source is found.",
    }
    (REPORTS / "origin-place-taopoon-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    coverage_path = REPORTS / "bangkok-coverage-2026-10-18.csv"
    with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
        headers = list(coverage[0])
    row = next(item for item in coverage if item["hipflat_id"] == str(PROJECT_ID))
    row.update(
        {
            "rent_sample": "yes",
            "rent_individual_listing_link": "yes",
            "rent_source": RENT_URL,
            "rent_sample_updated": CHECKED,
            "missing": "",
        }
    )
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(coverage)

    print(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "rentTHBMonth": rent_price,
                "areaSqm": rent_area,
                "rentTHBPerSqmMonth": round(rent_rate, 2),
                "availability": "unconfirmed; direct listing updated over 30 days ago",
                "source": RENT_URL,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
