"""Add The Brill Vibhavadi 60's confirmed-rented listing as a historical sample."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3295
NAME = "The Brill Condominium Vibhavadi 60"
CHECKED = "2026-10-18"
RENT_URL = (
    "https://www.scancondo.com/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/"
    "%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/144599/BCV07-0001/"
    "%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-%E0%B9%80%E0%B8%94%E0%B8%AD%E0%B8%B0%E0%B8%9A%E0%B8%A3%E0%B8%B4%E0%B8%A5%E0%B8%A5%E0%B9%8C-"
    "%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%A7%E0%B8%B4%E0%B8%A0%E0%B8%B2%E0%B8%A7%E0%B8%94%E0%B8%B5-60-%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99-6-"
    "%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%81%E0%B8%A7%E0%B9%89%E0%B8%B2%E0%B8%87-%E0%B8%AD%E0%B8%A2%E0%B8%B9%E0%B9%88%E0%B8%AA%E0%B8%9A%E0%B8%B2%E0%B8%A2-"
    "%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B9%80%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%AD%E0%B8%A2%E0%B8%B9%E0%B9%88-%E0%B8%88%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%A5%E0%B8%A2-"
    "%E0%B8%AB%E0%B9%89%E0%B8%B2%E0%B8%A1%E0%B8%9E%E0%B8%A5%E0%B8%B2%E0%B8%94"
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
    price, area, beds = 15_000, 83, 1
    exact_rate = price / area
    rounded_rate = round(exact_rate)
    sample = {
        "id": "BCV07-0001",
        "price": price,
        "area": area,
        "priceSqm": rounded_rate,
        "beds": beds,
        "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 83 ㎡ · ฿15,000/月 · 已出租",
        "url": RENT_URL,
        "sourceName": "Scancondo",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "Exact project name and listing code BCV07-0001",
        "availability": "The direct unit page explicitly says this unit is already rented; keep only as a historical rental sample.",
        "listingStatus": "confirmed_unavailable",
    }
    rent = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "averageSqm": rounded_rate,
        "minimumSqm": rounded_rate,
        "asOf": CHECKED,
        "snapshotMethod": "Direct Scancondo listing BCV07-0001. Listing price, area and room count are stated on the page; the page explicitly says rented.",
        "sourceName": "Scancondo 個別租賃掛牌（已出租，歷史樣本）",
        "source": RENT_URL,
        "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": price,
                "area": area,
                "priceSqm": rounded_rate,
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
    rates = [float(row["price"]) / float(row["area"]) for row in samples]
    rows_for_1br = [row for row in samples if int(row.get("beds") or 0) == 1]
    project["rent"] = {
        **rent,
        "count": len(samples),
        "observedCount": len(samples),
        "average": round(sum(float(row["price"]) for row in samples) / len(samples)),
        "minimum": float(lowest_total["price"]),
        "minimumArea": float(lowest_total["area"]),
        "averageSqm": round(sum(rates) / len(rates)),
        "minimumSqm": round(float(lowest_rate["price"]) / float(lowest_rate["area"])),
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "samples": samples,
        "byBedroom": {
            "1": {
                "count": len(rows_for_1br),
                "minimum": min(float(row["price"]) for row in rows_for_1br),
                "area": float(min(rows_for_1br, key=lambda row: float(row["price"]))["area"]),
                "minimumSqm": min(float(row["price"]) / float(row["area"]) for row in rows_for_1br),
                "minimumSqmSourceUrl": min(rows_for_1br, key=lambda row: float(row["price"]) / float(row["area"]))["url"],
                "sourceUrl": min(rows_for_1br, key=lambda row: float(row["price"]))["url"],
            }
        },
    }
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    (REPORTS / "the-brill-vibhavadi-60-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "projectName": NAME,
                "checkedAt": CHECKED,
                "listing": sample,
                "details": {
                    "bedrooms": "1 bedroom in structured unit facts; descriptive copy says 'combined room', so no bathroom count is recorded",
                    "floor": 6,
                    "areaSqm": area,
                    "monthlyRentTHB": price,
                    "rentTHBPerSqmMonthExact": exact_rate,
                    "availability": "confirmed unavailable: direct page says already rented",
                    "sourcePage": RENT_URL,
                },
                "yieldNote": "This is a historical one-bedroom asking-rent sample; current availability is false. It must not be presented as a live rental listing. It does not qualify a two-bedroom ROI by itself.",
                "evidence": {
                    "direct_listing": RENT_URL,
                    "direct_listing_evidence": "Page BCV07-0001 identifies the project, rent ฿15,000/month, structured 1 bedroom, floor 6, 83 sqm, and explicitly says already rented.",
                    "project_match": "Exact English and Thai project name plus listing code BCV07-0001.",
                    "conflict": "The descriptive paragraph says 'combined room' and 2 bathrooms, while the structured listing facts show 1 bedroom and 1 bathroom. Only bedroom count is retained; bathroom details are excluded.",
                },
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

    print(json.dumps({"hipflatId": PROJECT_ID, "price": price, "area": area, "THBperSqmMonth": exact_rate, "listingStatus": sample["listingStatus"], "source": RENT_URL}, ensure_ascii=False))


if __name__ == "__main__":
    main()
