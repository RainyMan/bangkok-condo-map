"""Attach the current directly verified Thana Tower rental listing."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3423
URL = "https://propertyscout.co.th/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-%E0%B8%97%E0%B8%B5%E0%B9%88-%E0%B8%98%E0%B8%99%E0%B8%B2-%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B9%80%E0%B8%A7%E0%B8%AD%E0%B8%A3%E0%B9%8C-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-mrt-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%A2%E0%B8%B5%E0%B9%88%E0%B8%82%E0%B8%B1%E0%B8%99-3363457/"


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
    path = "bangkok-manual-market-samples.js"
    rows = read_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": "Thana Tower"}
        rows.append(project)
    rent = project.setdefault("rent", {"samples": []})
    samples = rent.setdefault("samples", [])
    sample = {
        "id": "3363457",
        "price": 18_000,
        "area": 100,
        "priceSqm": 180,
        "beds": 2,
        "roomType": "2BR",
        "title": "Thana Tower，2 房，100 ㎡，฿18,000/月",
        "url": URL,
        "sourceName": "PropertyScout",
        "projectName": "Thana Tower",
        "updated": "2026-10-04",
        "checkedAt": "2026-10-18",
        "matchedBy": "exact_project_name_and_listing_detail",
        "listingStatus": "active_as_listed",
    }
    samples[:] = [item for item in samples if item.get("url") != URL]
    samples.append(sample)
    write_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    log_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        existing = list(csv.DictReader(stream))
        fields = list(existing[0]) if existing else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    existing = [row for row in existing if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] == "rent")]
    existing.append({
        "hipflat_id": str(PROJECT_ID),
        "condo": "Thana Tower",
        "checked_at": "2026-10-18",
        "market": "rent",
        "status": "active_recently_confirmed",
        "verification_note": "PropertyScout 個別物件頁核對到 Thana Tower 2 房、100 ㎡、฿18,000/月；刊登日 2026-10-04，頁面顯示上週確認空置並經核實。PropertyHub 專案頁目前未匹配到出租物件，故以此直接物件頁補充。",
        "source_1": URL,
        "source_2": "https://propertyhub.in.th/en/condo-for-rent/project-thana-tower",
        "source_3": "https://propertyscout.co.th/en/bangkok/condo/thana-tower/",
    })
    with log_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(existing)

    report = {
        "projectId": PROJECT_ID,
        "name": "Thana Tower",
        "checkedAt": "2026-10-18",
        "rentListing": {"rentPerMonth": 18_000, "bedrooms": 2, "areaSqm": 100, "rentPerSqm": 180, "url": URL, "listed": "2026-10-04", "availability": "confirmed last week; listing marked verified"},
        "projectContext": {"completedYear": 1993, "floors": 22, "units": 170, "source": "https://propertyhub.in.th/en/condo-for-rent/project-thana-tower"},
        "yieldNote": "Rental sample added to the source list. No two-bedroom sale sample is available in the project dataset yet; do not use this rent alone to label a two-bedroom ROI as fully matched.",
    }
    (ROOT / "reports" / "thana-tower-rental-enrichment-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"projectId": PROJECT_ID, "rentListing": URL}, ensure_ascii=False))


if __name__ == "__main__":
    main()
