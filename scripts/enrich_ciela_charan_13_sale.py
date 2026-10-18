"""Attach an individually verified current Ciela Charan 13 sale listing."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3905
URL = "https://propertyscout.co.th/en/1-br-condo-ciela-charan-13-station-near-mrt-tha-phra-1441724/"


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
    file = "bangkok-manual-market-samples.js"
    projects = read_array(file, "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in projects if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": "Ciela Charan 13 Station"}
        projects.append(project)
    sale = project.setdefault("sale", {"samples": []})
    samples = sale.setdefault("samples", [])
    sample = {
        "id": "1441724",
        "price": 2_790_000,
        "area": 21.23,
        "priceSqm": 131_418,
        "beds": 1,
        "roomType": "1BR",
        "title": "Ciela Charan 13 Station，1 房，21.23 ㎡，฿2,790,000",
        "url": URL,
        "sourceName": "PropertyScout",
        "projectName": "Ciela Charan 13 Station",
        "updated": "2026-10-18",
        "checkedAt": "2026-10-18",
        "matchedBy": "exact_project_name_and_individual_listing_detail",
        "listingStatus": "active_as_listed",
    }
    samples[:] = [item for item in samples if item.get("url") != URL]
    samples.append(sample)
    write_array(file, "BANGKOK_MANUAL_MARKET_SAMPLES", projects)

    log_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    rows = [row for row in rows if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] == "sale")]
    rows.append({
        "hipflat_id": str(PROJECT_ID),
        "condo": "Ciela Charan 13 Station",
        "checked_at": "2026-10-18",
        "market": "sale",
        "status": "active_recently_confirmed",
        "verification_note": "PropertyScout 個別物件頁核對到 1 房、21.23 ㎡、฿2,790,000；頁面顯示今天確認可售並更新於今天，且列出專案名稱及樓層。",
        "source_1": URL,
        "source_2": "https://propertyhub.in.th/en/projects/ciela-charan-13-station",
        "source_3": "https://propertyhub.in.th/en/condo-for-rent/project-ciela-charan-13-station",
    })
    with log_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    sample_rent_rate = 426
    floor_area = 21.23
    purchase_price = 2_790_000
    monthly_rent = round(sample_rent_rate * floor_area)
    net_after_fee_and_one_month = (monthly_rent * 11 - 55 * floor_area * 12) / purchase_price * 100
    report = {
        "projectId": PROJECT_ID,
        "name": "Ciela Charan 13 Station",
        "checkedAt": "2026-10-18",
        "saleListing": {"price": purchase_price, "bedrooms": 1, "areaSqm": floor_area, "pricePerSqm": 131_418, "url": URL, "availability": "confirmed today; updated today"},
        "rentBaseline": {"rentPerSqmMonth": sample_rent_rate, "source": "https://propertyhub.in.th/en/listings/s2934-for-rent-ciela-charan-13-station---4981463", "note": "Existing PropertyHub one-bedroom low rent per-sqm sample."},
        "fee": {"rateThbPerSqmMonth": 55, "source": "https://propertyhub.in.th/en/projects/ciela-charan-13-station"},
        "yieldEstimate": {"monthlyRent": monthly_rent, "agentMonthsDeducted": 1, "annualFee": round(55 * floor_area * 12, 2), "yieldAfterOneMonthAgentAndFeePct": round(net_after_fee_and_one_month, 2)},
    }
    (ROOT / "reports" / "ciela-charan-13-sale-enrichment-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"projectId": PROJECT_ID, "saleListing": URL, "netYieldAfterAgentAndFee": round(net_after_fee_and_one_month, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
