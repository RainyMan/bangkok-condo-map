"""Attach a directly linked two-bedroom rental sample to Siamese Exclusive 42."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3538
PROJECT_NAME = "Siamese Exclusive 42"
URL = "https://propertyhub.in.th/en/listings/well-located-2-br-condo-at-siamese-exclusive-42-300m-to-bts-ekkamai-id-2989853---6276823"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-siamese-exclusive-sukhumvit-42"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not find {symbol} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


def main() -> None:
    filename = "bangkok-manual-market-samples.js"
    projects = read_array(filename, "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in projects if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
        projects.append(project)
    project["asOf"] = "2026-10-18"
    rent = project.setdefault("rent", {"samples": []})
    samples = rent.setdefault("samples", [])
    sample = {
        "id": "2989853",
        "price": 42_000,
        "area": 64,
        "priceSqm": 656,
        "beds": 2,
        "roomType": "2BR",
        "title": f"{PROJECT_NAME}，2 房，64 ㎡，฿42,000/月",
        "url": URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": None,
        "checkedAt": "2026-10-18",
        "matchedBy": "exact_project_name_and_individual_listing_detail",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    samples[:] = [item for item in samples if item.get("url") != URL]
    samples.append(sample)
    write_array(filename, "BANGKOK_MANUAL_MARKET_SAMPLES", projects)

    log_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    rows = [row for row in rows if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] == "rent")]
    rows.append({
        "hipflat_id": str(PROJECT_ID),
        "condo": PROJECT_NAME,
        "checked_at": "2026-10-18",
        "market": "rent",
        "status": "direct_listing_availability_unconfirmed",
        "verification_note": "PropertyHub 個別頁列出 Siamese Exclusive 42 兩房、64 ㎡、฿42,000/月，並標示專案完工於 2020 年。個別頁未提供更新日期；雖可打開，空置與目前租金仍待向刊登方確認。專案出租頁目前亦列有該案出租物件。",
        "source_1": URL,
        "source_2": PROJECT_URL,
        "source_3": "https://propertyscout.co.th/en/bangkok/condo/siamese-exclusive-42/",
    })
    with log_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    sale_price, sale_area = 12_300_000, 53.63
    monthly_rent = round((42_000 / 64) * sale_area)
    yield_pct = round(monthly_rent * 11 / sale_price * 100, 2)
    report = {
        "projectId": PROJECT_ID,
        "name": PROJECT_NAME,
        "checkedAt": "2026-10-18",
        "rentListing": {
            "monthlyRentThb": 42_000,
            "bedrooms": 2,
            "areaSqm": 64,
            "rentThbPerSqmMonth": 656.25,
            "url": URL,
            "availability": "unconfirmed; listing has no update date",
        },
        "yieldEstimate": {
            "saleListing": {
                "priceThb": sale_price,
                "areaSqm": sale_area,
                "url": "https://propertyhub.in.th/en/listings/siamese-exclusive-sukhumvit-42-pn-00003960---4974130",
            },
            "rentPerSqmMonth": 656.25,
            "monthlyRentAtSaleUnitAreaThb": monthly_rent,
            "deductedAgentMonths": 1,
            "commonFeeDeducted": False,
            "netYieldBeforeCommonFeePercent": yield_pct,
            "note": "Uses two-bedroom rent per sqm from a direct listing and the area of the project's lowest linked two-bedroom sale listing. Management fee is unavailable; rental listing availability and current terms are unconfirmed.",
        },
        "sources": {"rentProjectPage": PROJECT_URL, "propertyScoutMarketSummary": "https://propertyscout.co.th/en/bangkok/condo/siamese-exclusive-42/"},
    }
    (ROOT / "reports" / "siamese-exclusive-42-rent-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"projectId": PROJECT_ID, "rentListing": URL, "monthlyRentAtLowestTwoBedroomSaleArea": monthly_rent, "netYieldBeforeFeePercent": yield_pct}, ensure_ascii=False))


if __name__ == "__main__":
    main()
