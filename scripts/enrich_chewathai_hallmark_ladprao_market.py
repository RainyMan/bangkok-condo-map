"""Add directly linked sale/rent samples and the published fee for project 3322."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3322
NAME = "Chewathai Hallmark Ladprao - Chokchai 4"
SALE_URL = "https://propertyhub.in.th/en/listings/a050287-chewathai-hallmark-ladprao-chokchai-4---6346585"
RENT_URL = "https://propertyhub.in.th/en/listings/condo-for-rent-at-chewathai-hallmark-ladprao-chokchai-4-c6910019-id-line-condo44---6476456"
PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-chewathai-hallmark-ladprao-chokchai-4"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-chewathai-hallmark-ladprao-chokchai-4"


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
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        projects.append(project)
    project["name"] = NAME
    project["asOf"] = "2026-10-18"
    project["fee"] = {
        "rate": 45,
        "source": PROJECT_URL,
        "status": "publicly_listed",
        "note": "PropertyHub 專案資料列管理費 ฿45/㎡/月；實際應向管委會確認。",
    }

    sale_samples = project.setdefault("sale", {"samples": []}).setdefault("samples", [])
    sale_sample = {
        "id": "6346585",
        "price": 3_950_000,
        "area": 45,
        "priceSqm": 87_778,
        "beds": 2,
        "roomType": "2BR",
        "title": f"{NAME}，2 房，45 ㎡，฿3,950,000",
        "url": SALE_URL,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "updated": "2026-10-17",
        "checkedAt": "2026-10-18",
        "matchedBy": "exact_project_name_and_individual_listing_detail",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    sale_samples[:] = [sample for sample in sale_samples if sample.get("url") != SALE_URL]
    sale_samples.append(sale_sample)

    rent_samples = project.setdefault("rent", {"samples": []}).setdefault("samples", [])
    rent_sample = {
        "id": "6476456",
        "price": 21_000,
        "area": 46,
        "priceSqm": 457,
        "beds": 2,
        "roomType": "2BR",
        "title": f"{NAME}，2 房，46 ㎡，฿21,000/月",
        "url": RENT_URL,
        "sourceName": "PropertyHub",
        "projectName": NAME,
        "updated": "2026-10-18",
        "checkedAt": "2026-10-18",
        "matchedBy": "exact_project_name_and_individual_listing_detail",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    rent_samples[:] = [sample for sample in rent_samples if sample.get("url") != RENT_URL]
    rent_samples.append(rent_sample)
    write_array(filename, "BANGKOK_MANUAL_MARKET_SAMPLES", projects)

    log_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    rows = [row for row in rows if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {
            "hipflat_id": str(PROJECT_ID),
            "condo": NAME,
            "checked_at": "2026-10-18",
            "market": "sale",
            "status": "direct_listing_recently_refreshed_availability_unconfirmed",
            "verification_note": "PropertyHub 個別頁 A050287 識別為本案兩房、45 ㎡、฿3,950,000；專案出售清單於 2026-10-17 10:21 更新。個別頁沒有更新日欄位，實際可售狀況仍待刊登方確認。",
            "source_1": SALE_URL,
            "source_2": SALE_PROJECT_URL,
            "source_3": PROJECT_URL,
        },
        {
            "hipflat_id": str(PROJECT_ID),
            "condo": NAME,
            "checked_at": "2026-10-18",
            "market": "rent",
            "status": "direct_listing_recently_refreshed_availability_unconfirmed",
            "verification_note": "PropertyHub 個別頁 C6910019 識別為本案兩房、46 ㎡、฿21,000/月；專案出租清單於 2026-10-18 09:00 更新。個別頁沒有更新日欄位，實際空置狀況仍待刊登方確認。",
            "source_1": RENT_URL,
            "source_2": PROJECT_URL,
            "source_3": SALE_PROJECT_URL,
        },
    ])
    with log_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    sale_price, sale_area = 3_950_000, 45
    rent_per_sqm = 21_000 / 46
    estimated_monthly_rent = round(rent_per_sqm * sale_area)
    annual_rent_after_agent = estimated_monthly_rent * 11
    annual_fee = 45 * sale_area * 12
    net_yield = round((annual_rent_after_agent - annual_fee) / sale_price * 100, 2)
    report = {
        "projectId": PROJECT_ID,
        "name": NAME,
        "checkedAt": "2026-10-18",
        "saleListing": {"priceThb": sale_price, "bedrooms": 2, "areaSqm": sale_area, "priceThbPerSqm": round(sale_price / sale_area), "url": SALE_URL, "projectPageUpdatedAt": "2026-10-17T10:21", "availability": "unconfirmed with advertiser"},
        "rentListing": {"monthlyRentThb": 21_000, "bedrooms": 2, "areaSqm": 46, "rentThbPerSqmMonth": round(rent_per_sqm, 2), "url": RENT_URL, "projectPageUpdatedAt": "2026-10-18T09:00", "availability": "unconfirmed with advertiser"},
        "managementFee": {"rateThbPerSqmMonth": 45, "source": PROJECT_URL, "note": "Published PropertyHub project information; confirm with juristic office."},
        "yieldEstimate": {
            "purchasePriceThb": sale_price,
            "purchaseAreaSqm": sale_area,
            "monthlyRentAtPurchaseAreaThb": estimated_monthly_rent,
            "agentMonthsDeducted": 1,
            "annualRentAfterAgentThb": annual_rent_after_agent,
            "annualCommonFeeThb": annual_fee,
            "netYieldPercent": net_yield,
            "formula": "(estimated monthly rent × 11 − management fee × purchase area × 12) ÷ purchase price",
        },
    }
    (ROOT / "reports" / "chewathai-hallmark-ladprao-market-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"projectId": PROJECT_ID, "sale": SALE_URL, "rent": RENT_URL, "yieldNetPercent": net_yield}, ensure_ascii=False))


if __name__ == "__main__":
    main()
