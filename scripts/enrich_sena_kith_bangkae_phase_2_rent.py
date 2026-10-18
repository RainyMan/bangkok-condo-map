"""Add the current direct Scancondo rent listing for Sena Kith Bangkae Phase 2."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 4993
NAME = "Sena Kith MRT - Bangkae Phase 2"
CHECKED = "2026-10-18"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/sena-kith-mrt-bangkae-phase-2-xpkowx"
RENT_URL = "https://www.scancondo.com/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/172443/SK31-0017/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-sena-kith-mrt-bangkae-phase-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%A3%E0%B8%AD%E0%B8%8A%E0%B9%89%E0%B8%B2"


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
    rent_price, rent_area, rent_beds = 8_500, 26.4, 1
    rent_rate = rent_price / rent_area
    sample = {
        "id": "SK31-0017",
        "price": rent_price,
        "area": rent_area,
        "priceSqm": round(rent_rate),
        "beds": rent_beds,
        "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 26.4 ㎡ · ฿8,500/月",
        "url": RENT_URL,
        "sourceName": "Scancondo",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "exact project name, rent listing identifier, and direct Scancondo project/rental detail",
        "availability": "Scancondo page marks this unit as available for rent",
        "listingStatus": "active_as_listed",
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
        "snapshotMethod": "Direct Scancondo rent detail shows the exact project, SK31-0017, vacancy label and unit metrics.",
        "sourceName": "Scancondo 個別租賃掛牌",
        "source": RENT_URL,
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
            "sourceUrl": "https://propertyhub.in.th/en/projects/sena-kith-mrt-bangkae-phase-2",
        },
        "saleMarket": {
            "sourceUrl": "https://propertyhub.in.th/en/condo-for-sale/bangkok",
            "minimumPriceTHB": 1_360_000,
            "minimumAreaSqm": 26.25,
            "listingUrl": "https://propertyhub.in.th/en/listings/condo-for-sale-fully-furnished-fully-furnished-near-mrt-bang-khae-sena-kith-mrt-bangkae-phase-2---6125912",
            "roomType": "1 bedroom",
            "updated": "2026-10-16",
        },
        "rentListing": sample,
        "rentEvidence": {
            "directListingDetails": "Listing SK31-0017, one bedroom, 26.4 sqm, 6th floor, ฿8,500/month (about ฿322/sqm/month). The page displays its vacancy status.",
            "projectMatchingEvidence": "The Scancondo page names Sena Kith MRT Bangkae Phase 2; its project details state 378 units, two buildings and eight floors, matching the Hipflat project.",
            "listingPageUrl": RENT_URL,
        },
        "yieldNote": "The direct sale market sample is also one bedroom, so the same-bedroom lowest sale and rental figures can support a one-bedroom yield estimate. No two-bedroom sale sample is currently verified; the default two-bedroom estimate remains unavailable.",
    }
    (REPORTS / "sena-kith-bangkae-phase-2-rent-enrichment-2026-10-18.json").write_text(
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
                "availability": "marked vacant on direct listing",
                "source": RENT_URL,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
