"""Add a recently updated, individually linked Ari Samphan Place rental."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3432
NAME = "Ari Samphan Place"
CHECKED = "2026-10-18"
RENT_URL = "https://propertyscout.co.th/en/2-br-condo-ari-samphan-place-near-bts-sanam-pao-1286667/"


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
    price, area, beds = 14_500, 65, 2
    exact_rate = price / area
    sample = {
        "id": "1286667",
        "price": price,
        "area": area,
        "priceSqm": round(exact_rate),
        "beds": beds,
        "roomType": "2BR",
        "title": f"{NAME} · 2 房 · 65 ㎡ · ฿14,500/月",
        "url": RENT_URL,
        "sourceName": "PropertyScout",
        "projectName": NAME,
        "updated": "2026-10-16",
        "checkedAt": CHECKED,
        "matchedBy": "Exact PropertyScout listing and project name; unit details match two bedrooms and 65 sqm",
        "availability": "Updated two days before the check, but the page says availability upon request.",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "minimumSampleUpdated": "2026-10-16",
        "averageSqm": round(exact_rate),
        "minimumSqm": round(exact_rate),
        "minimumSqmSampleUpdated": "2026-10-16",
        "asOf": CHECKED,
        "snapshotMethod": "Direct PropertyScout rental detail updated 2026-10-16; exact project, bedroom count and unit area verified. Current availability is unconfirmed.",
        "sourceName": "PropertyScout 個別出租掛牌",
        "source": RENT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "2": {
                "count": 1,
                "minimum": price,
                "area": area,
                "priceSqm": round(exact_rate),
                "minimumSqm": exact_rate,
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
        "minimumSampleUpdated": lowest_total.get("updated"),
        "averageSqm": round(
            sum(float(row["price"]) / float(row["area"]) for row in samples) / len(samples)
        ),
        "minimumSqm": round(float(lowest_rate["price"]) / float(lowest_rate["area"])),
        "minimumSqmSampleUpdated": lowest_rate.get("updated"),
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "samples": samples,
    }
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    (REPORTS / "ari-samphan-place-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "projectName": NAME,
                "checkedAt": CHECKED,
                "listing": sample,
                "details": {
                    "bedrooms": beds,
                    "bathrooms": 1,
                    "areaSqm": area,
                    "monthlyRentTHB": price,
                    "rentTHBPerSqmMonthExact": exact_rate,
                    "availability": "unconfirmed; source page says availability upon request",
                    "listedOn": "2023-09-08",
                    "updatedOn": "2026-10-16",
                    "sourcePage": RENT_URL,
                },
                "projectMatchEvidence": "The direct page names Ari Samphan Place and lists 50 units, 8 floors and 1997 completion, matching the Hipflat project.",
                "yieldNote": "This exact two-bedroom rent is eligible as the two-bedroom rent basis. Use the lowest linked two-bedroom sale and its paired area for a same-room yield estimate; confirm vacancy with the source.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
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
            "rent_sample_updated": "2026-10-16",
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
                "rentTHBMonth": price,
                "areaSqm": area,
                "rentTHBPerSqmMonthExact": exact_rate,
                "updated": sample["updated"],
                "availability": sample["availability"],
                "source": RENT_URL,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
