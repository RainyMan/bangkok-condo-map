"""Record a direct Pinklao Pavilion rental listing as a historical sample."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3794
NAME = "Pinklao Pavilion"
CHECKED = "2026-10-18"
RENT_URL = (
    "https://connex.in.th/detail/"
    "%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-"
    "%E0%B8%9B%E0%B8%B4%E0%B9%88%E0%B8%99%E0%B9%80%E0%B8%81%E0%B8%A5%E0%B9%89%E0%B8%B2-"
    "%E0%B8%9E%E0%B8%B2%E0%B8%A7%E0%B8%B4%E0%B8%A5%E0%B9%80%E0%B8%A5%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%99-"
    "mrt-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%A2%E0%B8%B5%E0%B9%88%E0%B8%82%E0%B8%B1%E0%B8%99-"
    "%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%9A%E0%B8%B3%E0%B8%AB%E0%B8%A3%E0%B8%B8-"
    "%E0%B9%80%E0%B8%82%E0%B8%95-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%9E%E0%B8%A5%E0%B8%B1%E0%B8%94-"
    "%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-cx-138669"
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
    price, area, beds = 7_500, 54, 2
    exact_rate = price / area
    sample = {
        "id": "CX-138669",
        "price": price,
        "area": area,
        "priceSqm": round(exact_rate),
        "beds": beds,
        "roomType": "2BR",
        "title": f"{NAME} · 2 房 · 54 ㎡ · ฿7,500/月 · 目前不可租",
        "url": RENT_URL,
        "sourceName": "Connex",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "Exact Pinklao Pavilion project name, address, and unit ID CX-138669",
        "availability": "The individual listing says status ไม่ว่าง (unavailable); preserve as a historical sample, not a currently rentable unit.",
        "listingStatus": "confirmed_unavailable",
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
    old_samples = project.get("rent", {}).get("samples", [])
    unique = {row.get("url"): row for row in old_samples if row.get("url")}
    unique[RENT_URL] = sample
    samples = list(unique.values())
    lowest_total = min(samples, key=lambda row: float(row["price"]))
    lowest_rate = min(samples, key=lambda row: float(row["price"]) / float(row["area"]))
    rates = [float(row["price"]) / float(row["area"]) for row in samples]
    beds_samples = [row for row in samples if int(row.get("beds") or 0) == beds]
    lowest_bed_total = min(beds_samples, key=lambda row: float(row["price"]))
    lowest_bed_rate = min(beds_samples, key=lambda row: float(row["price"]) / float(row["area"]))
    project["rent"] = {
        "count": len(samples),
        "observedCount": len(samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(float(row["price"]) for row in samples) / len(samples)),
        "minimum": float(lowest_total["price"]),
        "minimumArea": float(lowest_total["area"]),
        "averageSqm": round(sum(rates) / len(rates)),
        "minimumSqm": round(float(lowest_rate["price"]) / float(lowest_rate["area"])),
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "asOf": CHECKED,
        "sourceName": "Connex 個別租賃掛牌（目前不可租，歷史樣本）",
        "source": RENT_URL,
        "snapshotMethod": "Direct Connex unit page CX-138669. The indexed detail reports 2 bedrooms, 54 sqm, ฿7,500/month and status unavailable.",
        "byBedroom": {
            str(beds): {
                "count": len(beds_samples),
                "minimum": float(lowest_bed_total["price"]),
                "area": float(lowest_bed_total["area"]),
                "minimumSqm": float(lowest_bed_rate["price"]) / float(lowest_bed_rate["area"]),
                "minimumSqmSourceUrl": lowest_bed_rate["url"],
                "sourceUrl": lowest_bed_total["url"],
            }
        },
        "samples": samples,
    }
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    (REPORTS / "pinklao-pavilion-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "projectName": NAME,
                "checkedAt": CHECKED,
                "listing": sample,
                "details": {
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "floor": 2,
                    "areaSqm": area,
                    "monthlyRentTHB": price,
                    "rentTHBPerSqmMonthExact": exact_rate,
                    "availability": "unavailable per direct listing status",
                    "sourcePage": RENT_URL,
                },
                "crossCheck": {
                    "source": "https://zmyhome.com/rent/condo/project-list/13599/owner",
                    "finding": "The project-specific rent page also lists Pinklao Pavilion's 2-bedroom, 54 sqm unit at ฿7,000/month; this corroborates project and room type but is not used as the sample because it does not expose an individual unit URL.",
                },
                "yieldNote": "This is a historical two-bedroom asking-rent sample marked unavailable. It is included as market evidence and should not be interpreted as current availability.",
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
    target = next(item for item in coverage if item["hipflat_id"] == str(PROJECT_ID))
    target.update(
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

    print(json.dumps({"hipflatId": PROJECT_ID, "price": price, "area": area, "THBperSqmMonth": exact_rate, "beds": beds, "listingStatus": sample["listingStatus"], "source": RENT_URL}, ensure_ascii=False))


if __name__ == "__main__":
    main()
