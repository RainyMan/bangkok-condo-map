"""Add the current direct Hipflat rental listing for Lucky Star Condo."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3679
NAME = "Lucky Star Condo"
CHECKED = "2026-10-18"
PROJECT_URL = "https://www.hipflat.co.th/projects/lucky-star-condo-cixvtd"
LISTING_URL = "https://www.hipflat.co.th/ads/9en8tua18t00la4u2aa7n9h03u0h14a3"


def read_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = DIST / filename
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"), re.S,
    )
    if not match:
        raise ValueError(f"Cannot parse {symbol} from {path}")
    return path, json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n", encoding="utf-8",
    )


def main() -> None:
    price, area, beds = 4363, 30, 1
    rate = price / area
    sample = {
        "id": "U1970420", "price": price, "area": area,
        "priceSqm": round(rate), "beds": beds, "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 30 ㎡ · ฿4,363/月",
        "url": LISTING_URL, "sourceName": "Hipflat", "projectName": NAME,
        "updated": "2026-10-18 (頁面顯示 16 小時前更新)", "checkedAt": CHECKED,
        "matchedBy": "Exact Hipflat project name, unit address and unit ID U1970420",
        "availability": "Direct listing shows ฿4,363/month, 1 bedroom, 30 sqm, and unit ID U1970420; page was refreshed 16 hours before the check.",
        "listingStatus": "active_as_listed",
    }
    manual_path, rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(project)
    project["name"] = NAME
    samples = {row.get("url"): row for row in project.get("rent", {}).get("samples", []) if row.get("url")}
    samples[LISTING_URL] = sample
    sample_rows = list(samples.values())
    rates = [float(row["price"]) / float(row["area"]) for row in sample_rows]
    project["rent"] = {
        "count": len(sample_rows), "observedCount": len(sample_rows),
        "countKind": "manual_verified_listing", "average": round(sum(float(row["price"]) for row in sample_rows) / len(sample_rows)),
        "minimum": min(float(row["price"]) for row in sample_rows),
        "minimumArea": min(sample_rows, key=lambda row: float(row["price"]))["area"],
        "averageSqm": round(sum(rates) / len(rates)), "minimumSqm": round(min(rates)),
        "minimumSourceUrl": min(sample_rows, key=lambda row: float(row["price"]))["url"],
        "minimumSqmSourceUrl": min(sample_rows, key=lambda row: float(row["price"]) / float(row["area"]))["url"],
        "asOf": CHECKED, "sourceName": "Hipflat 個別出租掛牌",
        "source": PROJECT_URL,
        "snapshotMethod": "Direct Hipflat unit page U1970420 matches the Lucky Star Condo project and address; current 1-bedroom rent and area are displayed and the listing was refreshed 16 hours before the check.",
        "byBedroom": {"1": {
            "count": len(sample_rows), "minimum": price, "area": area,
            "minimumSqm": rate, "minimumSqmSourceUrl": LISTING_URL, "sourceUrl": LISTING_URL,
        }},
        "samples": sample_rows,
    }
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    sale_price, sale_area = 920000, 28
    rent_for_sale_area = rate * sale_area
    report = {
        "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": CHECKED,
        "projectPage": PROJECT_URL, "listing": sample,
        "details": {"bedrooms": beds, "areaSqm": area, "monthlyRentTHB": price,
                    "rentTHBPerSqmMonthExact": rate, "pageUpdated": "16 hours before check"},
        "crossCheck": {"coordinateProjectPage": "https://propertyhub.in.th/en/projects/lucky-star-condo",
                       "coordinateFinding": "PropertyHub project detail matches the exact Lucky Star Condo at 240/85 Soi Ratchadaphisek 36, Yaek 19-8."},
        "oneBedroomYieldInput": {
            "monthlyRentTHBPerSqm": rate, "purchasePriceTHB": sale_price,
            "purchaseAreaSqm": sale_area, "estimatedMonthlyRentTHB": rent_for_sale_area,
            "grossAnnualYieldPercent": rent_for_sale_area * 12 / sale_price * 100,
        },
        "yieldNote": "The rent sample is 1 bedroom and is paired only with the lowest 1-bedroom sale estimate; no 2-bedroom rent sample was found for this project.",
    }
    (REPORTS / "lucky-star-condo-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    coverage_path = REPORTS / "bangkok-coverage-2026-10-18.csv"
    with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
        headers = list(coverage[0])
    target = next(row for row in coverage if row["hipflat_id"] == str(PROJECT_ID))
    target.update({"rent_sample": "yes", "rent_individual_listing_link": "yes",
                   "rent_source": LISTING_URL, "rent_sample_updated": "2026-10-18; source refreshed 16 hours before check",
                   "missing": ""})
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(coverage)

    print(json.dumps({"hipflatId": PROJECT_ID, "name": NAME, "price": price,
                      "area": area, "THBperSqmMonth": rate,
                      "grossOneBedroomYieldPercent": report["oneBedroomYieldInput"]["grossAnnualYieldPercent"],
                      "source": LISTING_URL}, ensure_ascii=False))


if __name__ == "__main__":
    main()
