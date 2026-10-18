"""Record Family Town's exact Condothai rental listing with its stale status."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3642
NAME = "Family Town"
CHECKED = "2026-10-18"
RENT_URL = (
    "https://www.rightmove.condothai.co.th/room/23048/"
    "%E0%B9%81%E0%B8%9F%E0%B8%A1%E0%B8%A1%E0%B8%B4%E0%B8%A5%E0%B8%B5%E0%B9%88%20"
    "%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C%20%5BFamily%20Town%5D/12/?distance=3"
)


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
    price, area, beds = 8_000, 30, 1
    rate = price / area
    sample = {
        "id": "23048",
        "price": price,
        "area": area,
        "priceSqm": round(rate),
        "beds": beds,
        "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 30 ㎡ · ฿8,000/月",
        "url": RENT_URL,
        "sourceName": "Condothai",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "Exact Family Town project and direct Condothai rental unit 23048",
        "availability": "The direct listing says it was last updated more than 30 days ago; current availability is unconfirmed.",
        "listingStatus": "availability_unconfirmed_update_over_30d",
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "averageSqm": round(rate),
        "minimumSqm": round(rate),
        "asOf": CHECKED,
        "snapshotMethod": "Direct Condothai room 23048 rental detail. The page labels this listing as updated more than 30 days ago.",
        "sourceName": "Condothai 個別租賃掛牌（更新超過 30 日）",
        "source": RENT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": price,
                "area": area,
                "priceSqm": round(rate),
                "minimumSqm": rate,
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
        "averageSqm": round(
            sum(float(row["price"]) / float(row["area"]) for row in samples) / len(samples)
        ),
        "minimumSqm": round(float(lowest_rate["price"]) / float(lowest_rate["area"])),
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "samples": samples,
    }
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    (REPORTS / "family-town-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "projectName": NAME,
                "checkedAt": CHECKED,
                "listing": sample,
                "details": {
                    "bedrooms": 1,
                    "bathrooms": 1,
                    "floor": 5,
                    "areaSqm": area,
                    "monthlyRentTHB": price,
                    "rentTHBPerSqmMonthExact": rate,
                    "availability": "unconfirmed; source says last updated more than 30 days ago",
                    "sourcePage": RENT_URL,
                },
                "yieldNote": "This is a one-bedroom historical rental reference. A current two-bedroom ROI still requires a verified two-bedroom sale and rent sample.",
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
            "rent_sample_updated": "",
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
                "rentTHBPerSqmMonthExact": rate,
                "availability": sample["availability"],
                "source": RENT_URL,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
