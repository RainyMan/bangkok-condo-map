"""Add directly checkable sale/rent evidence for Muang Thai - Phatra Complex."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3479
NAME = "Muang Thai - Phatra Complex"
CHECKED = "2026-10-18"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/muang-thai-phatra-complex-hhgufs"
SALE_URL = "https://www.livinginsider.com/detail/condo-for-sale-muang-thai-phatra-complex-1bedroom-3129186"
RENT_URL = "https://zmyhome.com/property/V98839"


def load_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
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
    sale_price, sale_area, sale_beds = 5_000_000, 87.28, 1
    sale_rate = sale_price / sale_area
    sale_sample = {
        "id": "LI-3129186",
        "price": sale_price,
        "area": sale_area,
        "priceSqm": round(sale_rate),
        "beds": sale_beds,
        "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 87.28 ㎡ · ฿5,000,000",
        "url": SALE_URL,
        "sourceName": "LivingInsider",
        "projectName": NAME,
        "updated": "2026-09-25",
        "created": "2026-06-29",
        "checkedAt": CHECKED,
        "matchedBy": "exact project-name label and direct condo listing detail",
        "listingStatus": "listed_recently_bumped_under_30d",
    }
    sale = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": sale_price,
        "minimum": sale_price,
        "minimumArea": sale_area,
        "minimumSampleUpdated": "2026-09-25",
        "averageSqm": round(sale_rate),
        "minimumSqm": round(sale_rate),
        "minimumSqmSampleUpdated": "2026-09-25",
        "asOf": CHECKED,
        "snapshotMethod": "Exact LivingInsider project page and direct individual listing detail; listing was bumped 2026-09-25.",
        "sourceName": "LivingInsider 個別出售掛牌",
        "source": "https://www.livinginsider.com/project/muang-thai-phatra-complex-condo-buysell",
        "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL,
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": sale_price,
                "area": sale_area,
                "minimumArea": sale_area,
                "priceSqm": round(sale_rate),
                "minimumSqm": sale_rate,
                "sourceUrl": SALE_URL,
                "minimumSourceUrl": SALE_URL,
                "minimumSqmSourceUrl": SALE_URL,
            }
        },
        "samples": [sale_sample],
    }

    rent_price, rent_area, rent_beds = 29_000, 78, 1
    rent_rate = rent_price / rent_area
    rent_sample = {
        "id": "ZMY-V98839",
        "price": rent_price,
        "area": rent_area,
        "priceSqm": round(rent_rate),
        "beds": rent_beds,
        "roomType": "1BR",
        "title": f"{NAME} · 1 房 · 78 ㎡ · ฿29,000/月",
        "url": RENT_URL,
        "sourceName": "ZmyHome",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "direct owner listing names the exact Muangthai-Phatra Complex Condominium project",
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    manual_path, rows = load_array(
        "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
    )
    record = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": NAME}
        rows.append(record)
    record.update({"name": NAME, "asOf": CHECKED, "sale": sale})
    existing_rent = record.setdefault("rent", {})
    samples = {sample.get("url"): sample for sample in existing_rent.get("samples", [])}
    samples[RENT_URL] = rent_sample
    existing_rent["samples"] = list(samples.values())
    rows.sort(key=lambda row: int(row["hipflatId"]))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    # Preserve the existing PropertyHub MRT-side point. The direct sale and rent
    # pages identify the same project but do not provide a better project pin.
    purchase_price, purchase_area = sale_price, sale_area
    estimated_monthly_rent = rent_rate * purchase_area
    after_agent = estimated_monthly_rent * 11
    net_yield_no_fee = after_agent / purchase_price * 100
    report = {
        "hipflatId": PROJECT_ID,
        "projectName": NAME,
        "checkedAt": CHECKED,
        "projectSourceUrl": HIPFLAT_URL,
        "coordinate": {
            "lat": 13.78686855345889,
            "lng": 100.57416101765932,
            "sourceUrl": "https://propertyhub.in.th/en/projects/mueng-thai-patara-complex",
            "status": "existing exact-project PropertyHub point retained; this batch adds no coordinate override",
        },
        "saleListing": sale_sample,
        "saleListingEvidence": {
            "projectPageUrl": sale["source"],
            "projectPageCount": 1,
            "directDetailStates": "1 bedroom, 87.28 sqm, floor range 11-20, price ฿5,000,000 (฿57,287/sqm)",
            "lastBumped": "2026-09-25",
            "note": "The direct listing does not explicitly show an in-stock badge. Its project page and detail were accessible at the 2026-10-18 check; no 2-bedroom residential sale listing with a recent availability confirmation was found in this batch.",
        },
        "rentListing": rent_sample,
        "rentListingEvidence": {
            "directPageUrl": RENT_URL,
            "directPageDetails": "1 bedroom, 78 sqm, floor 17, ฿29,000/month (฿371.79/sqm/month)",
            "availability": "The listing source showed InStock in its structured page data when directly checked; the search index last crawled it about two weeks before this audit, so availability is conservatively flagged unconfirmed in the app.",
        },
        "existingTwoBedroomRentBaseline": {
            "sourceUrl": "https://propertyhub.in.th/en/listings/t1429-condo-for-rent-muang-thai-phatra-complex-beautiful-room-fully-furnished-special-price---3812341",
            "monthlyRentTHB": 25000,
            "areaSqm": 90,
            "bedrooms": 2,
            "pricePerSqmMonthTHB": 278,
            "note": "Retained from the existing PropertyHub data; two listings on the project page have identical unit price, area, bedroom count and floor and may be syndicated duplicates.",
        },
        "yieldEstimate": {
            "bedrooms": 1,
            "purchasePriceTHB": purchase_price,
            "purchaseAreaSqm": purchase_area,
            "rentRateTHBPerSqmMonth": round(rent_rate, 2),
            "estimatedMonthlyRentTHB": round(estimated_monthly_rent),
            "annualRentAfterOneAgentMonthTHB": round(after_agent),
            "commonFeeDeducted": False,
            "netAnnualYieldPercentBeforeCommonFee": round(net_yield_no_fee, 2),
            "formula": "((29000 / 78) * 87.28 * 11) / 5000000 * 100",
            "note": "Indicative 1-bedroom cross-listing estimate; management fee is not verified. The default 2-bedroom yield remains unavailable because this batch found no recent, checkable 2-bedroom sale listing.",
        },
    }
    report_path = REPORTS / "muang-thai-phatra-market-enrichment-2026-10-18.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "sale": f"{sale_price:,} THB / {sale_area} sqm / {round(sale_rate):,} THB/sqm",
                "rent": f"{rent_price:,} THB/mo / {rent_area} sqm / {round(rent_rate)} THB/sqm/mo",
                "oneBedroomYieldAfterOneAgentMonthBeforeFee": round(net_yield_no_fee, 2),
                "twoBedroomSale": "no recent direct listing verified",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
