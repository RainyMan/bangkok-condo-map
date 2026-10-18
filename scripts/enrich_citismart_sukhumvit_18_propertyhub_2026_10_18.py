"""Attach directly verifiable PropertyHub sale/rent listings for CitiSmart Sukhumvit 18."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED = "2026-10-18"
PROJECT_ID = 4158
PROJECT = "CitiSmart Sukhumvit 18"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-citi-smart-sukhumvit-18"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-citi-smart-sukhumvit-18"
SALE_URL = "https://propertyhub.in.th/en/listings/a036282-citismart-sukhumvit-18---6065846"
RENT_URL = (
    "https://propertyhub.in.th/en/listings/for-rent-condo-citi-smart-sukhumvit-18-"
    "bts-asok-khlong-toei-khlong-toei-bangkok-cx-83519-live-chat-with-us-add-line-"
    "connexproperty--aa270910---3932325"
)


def load_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = ROOT / "dist" / filename
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{symbol} = "
    if not text.startswith(prefix) or not text.rstrip().endswith(";"):
        raise ValueError(f"Unexpected data file format: {filename}")
    return path, json.loads(text[len(prefix) : text.rfind(";")])


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    sale = {
        "id": "6065846",
        "price": 10_000_000,
        "area": 75,
        "priceSqm": 133_333,
        "beds": 2,
        "roomType": "2BR",
        "title": "A036282 CitiSmart Sukhumvit 18，2 房，75 ㎡，฿10,000,000",
        "url": SALE_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "checkedAt": CHECKED,
        "updated": "2026-10-17",
        "matchedBy": "exact_project_name_listing_id_bedrooms_area_and_current_project_inventory",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }
    rent = {
        "id": "3932325",
        "price": 35_000,
        "area": 75,
        "priceSqm": 467,
        "beds": 2,
        "roomType": "2BR",
        "title": "Citi Smart Sukhumvit 18 CX-83519，2 房，75 ㎡，฿35,000/月",
        "url": RENT_URL,
        "sourceName": "PropertyHub",
        "projectName": PROJECT,
        "checkedAt": CHECKED,
        "updated": "2026-10-18",
        "matchedBy": "exact_project_name_listing_id_bedrooms_area_and_same_day_listing_update",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }

    market_path, market_rows = load_array(
        "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
    )
    record = next((row for row in market_rows if int(row["hipflatId"]) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "name": PROJECT}
        market_rows.append(record)
    if record.get("name") != PROJECT:
        raise ValueError(f"Hipflat ID {PROJECT_ID} has unexpected project name: {record.get('name')}")

    def preserve_samples(existing: dict | None, sample: dict, url: str) -> dict:
        market = dict(existing or {})
        samples = [row for row in market.get("samples", []) if row.get("url") != url]
        samples.append(sample)
        market["samples"] = samples
        return market

    # Keep PropertyScout's separate market summary and averages. These exact
    # PropertyHub samples are merged into the same displayed source object;
    # ROI selects the verified 2BR sale and keeps its area paired to its link.
    record["sale"] = preserve_samples(record.get("sale"), sale, SALE_URL)
    record["rent"] = preserve_samples(record.get("rent"), rent, RENT_URL)
    record["completedYear"] = 2005
    record["completedYearSourceUrl"] = RENT_PROJECT_URL
    save_array(
        market_path,
        "BANGKOK_MANUAL_MARKET_SAMPLES",
        sorted(market_rows, key=lambda row: int(row["hipflatId"])),
    )

    cross_path, cross_rows = load_array(
        "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
    )
    cross = next((row for row in cross_rows if int(row["hipflatId"]) == PROJECT_ID), None)
    if cross is None:
        cross = {"hipflatId": PROJECT_ID, "projectName": PROJECT}
        cross_rows.append(cross)
    cross.update(
        {
            "asOf": CHECKED,
            "sourceName": "PropertyHub",
            "projectSourceUrl": SALE_PROJECT_URL,
            "sale": {
                "activeListingCount": 12,
                "sourceUrl": SALE_PROJECT_URL,
                "listings": [
                    {
                        "id": sale["id"],
                        "price": sale["price"],
                        "area": sale["area"],
                        "priceSqm": sale["priceSqm"],
                        "bedrooms": sale["beds"],
                        "listedAt": "2026-10-17",
                        "url": SALE_URL,
                    }
                ],
            },
            "rent": {
                "activeListingCount": 259,
                "sourceUrl": RENT_PROJECT_URL,
                "listings": [
                    {
                        "id": rent["id"],
                        "price": rent["price"],
                        "area": rent["area"],
                        "priceSqm": rent["priceSqm"],
                        "bedrooms": rent["beds"],
                        "listedAt": "2026-10-18",
                        "url": RENT_URL,
                    }
                ],
            },
        }
    )
    save_array(
        cross_path,
        "BANGKOK_MARKET_CROSSCHECKS",
        sorted(cross_rows, key=lambda row: int(row["hipflatId"])),
    )

    report = {
        "checkedAt": CHECKED,
        "project": {
            "hipflatId": PROJECT_ID,
            "name": PROJECT,
            "coordinate": [13.735018, 100.562226],
            "coordinateSource": "https://propertyscout.co.th/en/bangkok/condo/citi-smart-sukhumvit-18/",
            "completedYear": 2005,
            "completedYearSource": RENT_PROJECT_URL,
        },
        "saleListing": sale,
        "rentalListing": rent,
        "twoBedroomYieldEstimate": {
            "purchasePrice": sale["price"],
            "purchaseAreaSqm": sale["area"],
            "saleSource": SALE_URL,
            "monthlyRentPerSqm": rent["price"] / rent["area"],
            "estimatedMonthlyRentAtSaleArea": round(rent["price"] / rent["area"] * sale["area"]),
            "rentSource": RENT_URL,
            "agentMonthsDeducted": 1,
            "commonFeeDeducted": False,
            "netYieldPercent": round(rent["price"] * 11 / sale["price"] * 100, 2),
            "formula": "(2BR rent per sqm × lowest linked 2BR sale area × 11) ÷ lowest linked 2BR sale total × 100",
            "note": "The observed sale price/area are one linked two-bedroom unit; rent is also a same-bedroom direct listing. No verified common fee is available, so it is not deducted.",
        },
        "limitations": [
            "The 10M sale listing was refreshed in the PropertyHub project inventory on 2026-10-17; its unit detail page does not expose a separate last-update date, so current availability still needs confirmation.",
            "The 35,000/month rent listing page reports an update on 2026-10-18.",
            "PropertyHub listing availability does not independently confirm the unit remains available for sale or rent.",
        ],
    }
    report_path = ROOT / "reports" / "citismart-sukhumvit-18-market-enrichment-2026-10-18.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "hipflatId": PROJECT_ID,
                "salePriceTwoBedroom": sale["price"],
                "saleAreaSqm": sale["area"],
                "monthlyRentTwoBedroom": rent["price"],
                "netYieldPercentBeforeCommonFee": report["twoBedroomYieldEstimate"]["netYieldPercent"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
