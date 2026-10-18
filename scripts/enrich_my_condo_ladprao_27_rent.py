"""Add individually verified FazWaz rentals for My Condo Ladprao 27."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3925
NAME = "My Condo Ladprao 27"
CHECKED = "2026-10-18"
PROJECT_URL = "https://www.fazwaz.co.th/en/property-for-rent/thailand/bangkok/chatuchak/chantharakasem/at-my-condo-ladprao-27"

LISTINGS = [
    {
        "id": "U1725214", "price": 13000, "area": 51, "beds": 2,
        "url": "https://www.fazwaz.co.th/en/property-rent/2-bedroom-condo-for-rent-at-my-condo-ladprao-27-in-chantharakasem-bangkok-u1725214",
        "title": f"{NAME} · 2 房 · 51 ㎡ · ฿13,000/月",
        "listed": "2024-01-30", "updated": "2 months ago", "available": "2027-03-01",
        "status": "active_future_availability",
    },
    {
        "id": "U5548750", "price": 9500, "area": 25.34, "beds": 1,
        "url": "https://www.fazwaz.co.th/en/property-rent/1-bedroom-condo-for-rent-at-my-condo-ladprao-27-in-chantharakasem-bangkok-u5548750",
        "title": f"{NAME} · 1 房 · 25.34 ㎡ · ฿9,500/月",
        "listed": "2025-05-29", "updated": "1 month ago", "available": "2027-06-01",
        "status": "active_future_availability",
    },
    {
        "id": "U1659004", "price": 9000, "area": 26, "beds": 0,
        "url": "https://www.fazwaz.co.th/en/property-rent/studio-condo-for-rent-at-my-condo-ladprao-27-in-chantharakasem-bangkok-u1659004",
        "title": f"{NAME} · 套房 · 26 ㎡ · ฿9,000/月",
        "listed": "2023-08-31", "updated": "1 month ago", "available": "2027-10-01",
        "status": "active_future_availability",
    },
    {
        "id": "U1851828", "price": 12000, "area": 35, "beds": 1,
        "url": "https://www.fazwaz.co.th/en/property-rent/1-bedroom-condo-for-rent-at-my-condo-ladprao-27-in-chantharakasem-bangkok-u1851828",
        "title": f"{NAME} · 1 房 · 35 ㎡ · ฿12,000/月",
        "listed": "2024-05-28", "updated": "7 months ago", "available": "2027-03-01",
        "status": "active_future_availability_update_7mo",
    },
]


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
    samples = []
    for item in LISTINGS:
        rate = item["price"] / item["area"]
        room = "2 房" if item["beds"] == 2 else "1 房" if item["beds"] == 1 else "套房"
        samples.append({
            "id": item["id"], "price": item["price"], "area": item["area"],
            "priceSqm": round(rate), "beds": item["beds"],
            "roomType": "2BR" if item["beds"] == 2 else "1BR" if item["beds"] == 1 else "STUDIO",
            "title": item["title"], "url": item["url"], "sourceName": "FazWaz",
            "projectName": NAME, "listed": item["listed"], "updated": item["updated"],
            "checkedAt": CHECKED,
            "matchedBy": f"Exact project name, project unit count and FazWaz unit ID {item['id']}",
            "availability": f"Source lists this unit for rent at ฿{item['price']:,}/month and {item['area']} sqm; stated availability is {item['available']}.",
            "availableFrom": item["available"], "listingStatus": item["status"],
        })

    lowest_total = min(samples, key=lambda row: float(row["price"]))
    lowest_rate = min(samples, key=lambda row: float(row["price"]) / float(row["area"]))
    room_summaries = {}
    for beds in sorted({int(row["beds"]) for row in samples if int(row["beds"]) > 0}):
        subset = [row for row in samples if int(row["beds"]) == beds]
        low_total = min(subset, key=lambda row: float(row["price"]))
        low_rate = min(subset, key=lambda row: float(row["price"]) / float(row["area"]))
        room_summaries[str(beds)] = {
            "count": len(subset), "minimum": low_total["price"], "area": low_total["area"],
            "minimumSqm": low_rate["price"] / low_rate["area"],
            "minimumSqmSourceUrl": low_rate["url"], "sourceUrl": low_total["url"],
        }

    rent = {
        "count": len(samples), "observedCount": len(samples),
        "countKind": "manual_verified_listing", "average": round(sum(row["price"] for row in samples) / len(samples)),
        "minimum": lowest_total["price"], "minimumArea": lowest_total["area"],
        "averageSqm": round(sum(row["price"] / row["area"] for row in samples) / len(samples)),
        "minimumSqm": round(lowest_rate["price"] / lowest_rate["area"]),
        "minimumSourceUrl": lowest_total["url"], "minimumSqmSourceUrl": lowest_rate["url"],
        "asOf": CHECKED, "sourceName": "FazWaz 個別租賃掛牌（頁面列明未來可入住日）",
        "source": PROJECT_URL,
        "snapshotMethod": "Checked four direct FazWaz unit pages against the exact My Condo Ladprao 27 project; each page states the project, rent, area, bedroom type, unit ID, and availability date.",
        "byBedroom": room_summaries, "samples": samples,
    }

    manual_path, rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(project)
    project["name"] = NAME
    project["rent"] = rent
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    report = {
        "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": CHECKED,
        "projectPage": PROJECT_URL, "sampleCount": len(samples), "rent": rent,
        "matchingTwoBedroomSale": {
            "minimumTHB": 2790000, "areaSqm": 51.05,
            "source": "https://propertyhub.in.th/en/listings/for-sale-condo-my-condo-ladprao-27-mrt-lat-phrao-chankasem-chatuchak-bangkok-cx-120431-live-chat-with-us-add-line-connexproperty--a8990927---5680475",
        },
        "twoBedroomYieldInput": {
            "monthlyRentTHBPerSqm": room_summaries["2"]["minimumSqm"],
            "purchasePriceTHB": 2790000, "purchaseAreaSqm": 51.05,
            "estimatedMonthlyRentTHB": room_summaries["2"]["minimumSqm"] * 51.05,
            "grossAnnualYieldPercent": (room_summaries["2"]["minimumSqm"] * 51.05 * 12 / 2790000) * 100,
            "note": "Rental unit is listed for availability on 2027-03-01; this is a forward asking-rent estimate, not confirmed immediate occupancy.",
        },
    }
    (REPORTS / "my-condo-ladprao-27-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    coverage_path = REPORTS / "bangkok-coverage-2026-10-18.csv"
    with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
        headers = list(coverage[0])
    target = next(row for row in coverage if row["hipflat_id"] == str(PROJECT_ID))
    target.update({
        "rent_sample": "yes", "rent_individual_listing_link": "yes",
        "rent_source": room_summaries["2"]["sourceUrl"],
        "rent_sample_updated": "active listing; available 2027-03-01",
        "missing": "",
    })
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(coverage)

    print(json.dumps({
        "hipflatId": PROJECT_ID, "name": NAME, "count": len(samples),
        "minimumRent": lowest_total["price"], "minimumRentUrl": lowest_total["url"],
        "lowestRentRate": rent["minimumSqm"], "lowestRentRateUrl": lowest_rate["url"],
        "twoBedroomRent": room_summaries["2"], "grossYieldPercent": report["twoBedroomYieldInput"]["grossAnnualYieldPercent"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
