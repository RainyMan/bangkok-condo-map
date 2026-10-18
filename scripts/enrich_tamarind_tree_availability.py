"""Record an exact-project current-listing check for Tamarind Tree Residence."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3171
PROJECT = "Tamarind Tree Residence"
AS_OF = "2026-10-18"
HIPFLAT = "https://www.hipflat.co.th/en/projects/tamarind-tree-residence-jprzey"
HISTORICAL = "https://8.condoable.com/ad_24827_%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%94%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1tamarindtreeresidence.htm"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Unexpected asset format: {path.name}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, indent=2)};\n", encoding="utf-8")


def main() -> None:
    crosscheck_path = DIST / "bangkok-market-crosschecks.js"
    crosschecks = [row for row in read_array(crosscheck_path, "BANGKOK_MARKET_CROSSCHECKS") if int(row.get("hipflatId", -1)) != PROJECT_ID]
    crosschecks.append({
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "asOf": AS_OF,
        "sourceName": "Hipflat",
        "projectSourceUrl": HIPFLAT,
        "sale": {"activeListingCount": 0, "sourceUrl": HIPFLAT},
        "rent": {"activeListingCount": 0, "sourceUrl": HIPFLAT},
        "availabilitySources": [
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "目前無出售或出租房源"},
            {"sourceName": "Condoable 歷史出售訂金廣告", "url": HISTORICAL, "statusLabel": "約 13 年前刊登；日期及現況過舊，不作現行價格或投報依據"},
        ],
    })
    crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(crosscheck_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

    csv_path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    note = "Hipflat exact-project page, checked 2026-10-18, states that no properties are currently available. A Condoable down-payment ad for this exact condo is approximately 13 years old and does not establish current availability or price; it is excluded from market values and ROI. No nearby project listings were substituted."
    for market in ("sale", "rent"):
        rows.append({
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF,
            "market": market, "status": "no_current_matching_listing",
            "verification_note": note, "source_1": HIPFLAT, "source_2": HISTORICAL, "source_3": "",
        })
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (int(row["hipflat_id"]), row["market"])))

    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "projectSource": HIPFLAT,
        "projectPageEvidence": "The exact Hipflat project page states: currently no properties available in Tamarind Tree Residence.",
        "marketAvailability": {
            "sale": {"status": "no_current_matching_listing", "currentSampleCount": 0, "source": HIPFLAT},
            "rent": {"status": "no_current_matching_listing", "currentSampleCount": 0, "source": HIPFLAT},
        },
        "excludedHistoricalSource": {
            "url": HISTORICAL,
            "description": "Exact-project down-payment advertisement, about 13.4 years old; no current availability confirmed.",
            "usedForCurrentMarketOrROI": False,
        },
        "roi": {"status": "not_calculable", "reason": "No current, exact-project sale or rental listings were available on the source check date."},
        "coordinates": {"status": "unverified", "reason": "The available project page provides a soi-level address and does not expose an exact project pin; no coordinate added."},
    }
    (REPORTS / "tamarind-tree-residence-availability-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(r"bangkok-market-crosschecks\.js\?v=[^\"']+", "bangkok-market-crosschecks.js?v=20261018t-tamarind-no-current-listings", html, count=1)
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "sale": "no_current_matching_listing", "rent": "no_current_matching_listing", "roi": "not_calculable", "coordinates": "unverified"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
