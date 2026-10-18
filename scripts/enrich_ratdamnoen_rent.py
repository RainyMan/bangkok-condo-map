"""Record the direct Ratdamnoen rental listing with a stale-availability flag."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3224
NAME = "Ratdamnoen Condominium"
CHECKED = "2026-10-18"
RENT_URL = "https://www.fazwaz.com/property-rent/2-bedroom-condo-for-rent-at-ratdamnoen-condominium-in-wat-sommanat-bangkok-u1670124"


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
    price, area, beds = 15_000, 92, 2
    exact_rate = price / area
    rounded_rate = round(exact_rate)
    sample = {
        "id": "U1670124",
        "price": price,
        "area": area,
        "priceSqm": rounded_rate,
        "beds": beds,
        "roomType": "2BR",
        "title": f"{NAME} · 2 房 · 92 ㎡ · ฿15,000/月 · 超過一年未更新",
        "url": RENT_URL,
        "sourceName": "FazWaz",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "Exact project name, address district, and unit ID U1670124",
        "availability": "The direct unit page lists this as rent ฿15,000/month, but says updated over one year ago; current availability is unconfirmed.",
        "listingStatus": "availability_unconfirmed_stale_over_year",
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
    room_samples = [row for row in samples if int(row.get("beds") or 0) == beds]
    lowest_room_total = min(room_samples, key=lambda row: float(row["price"]))
    lowest_room_rate = min(room_samples, key=lambda row: float(row["price"]) / float(row["area"]))
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
        "sourceName": "FazWaz 個別租賃掛牌（超過一年未更新）",
        "source": RENT_URL,
        "snapshotMethod": "Direct FazWaz unit page U1670124. It lists rent, exact area and bedroom count and states the listing was updated over one year ago.",
        "byBedroom": {
            str(beds): {
                "count": len(room_samples),
                "minimum": float(lowest_room_total["price"]),
                "area": float(lowest_room_total["area"]),
                "minimumSqm": float(lowest_room_rate["price"]) / float(lowest_room_rate["area"]),
                "minimumSqmSourceUrl": lowest_room_rate["url"],
                "sourceUrl": lowest_room_total["url"],
            }
        },
        "samples": samples,
    }
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    (REPORTS / "ratdamnoen-condominium-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "projectName": NAME,
                "checkedAt": CHECKED,
                "listing": sample,
                "details": {
                    "bedrooms": beds,
                    "bathrooms": 2,
                    "floor": 7,
                    "areaSqm": area,
                    "monthlyRentTHB": price,
                    "rentTHBPerSqmMonthExact": exact_rate,
                    "listedOn": "2023-09-20",
                    "updated": "over one year ago, exact date not given",
                    "availability": "unconfirmed due to stale listing",
                    "sourcePage": RENT_URL,
                },
                "crossCheck": {
                    "source": "https://www.thailand-property.com/condo/3696/ratdamnoen-condominium",
                    "finding": "The project page reports three current rental units from ฿15,000 to ฿25,000 and completion in 1984; the direct unit detail is used for exact unit attributes.",
                },
                "yieldNote": "This is a two-bedroom rental sample. The rate is useful for a same-bedroom estimate, but availability is unconfirmed because the unit page has not been updated in over a year.",
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
            "rent_sample_updated": "over 1 year ago; current availability unconfirmed",
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
