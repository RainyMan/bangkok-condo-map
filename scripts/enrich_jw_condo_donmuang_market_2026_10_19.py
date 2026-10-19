from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ID = 4430
NAME = "JW CONDO @DONMUANG"
CHECKED = "2026-10-19"
SALE_PRICE, SALE_AREA, BEDS = 1_700_000, 26.8, 1
RENT_PRICE, RENT_AREA = 7_000, 27.0
SALE_URL = "https://assets.propertyhub.in.th/listings/a050074-jw-condo---6142682"
SALE_RATE_URL = "https://propertyhub.in.th/en/listings/s020057-jw-condo---6352938"
RENT_URL = "https://asset-direct-v2.propertyhub.in.th/en/listings/for-rent-jw-condo-1-bed-27-sq-m-2nd-floor--ac5f0927---1930800"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-jw-condo"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/projects/jw-condo"
PROPERTYSCOUT_URL = "https://propertyscout.co.th/en/bangkok/condo/jw-condo-donmuang/"


def load_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot parse {symbol}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


sale_rate = round(SALE_PRICE / SALE_AREA)
rent_rate = RENT_PRICE / RENT_AREA
sale = {
    "id": "6142682",
    "price": SALE_PRICE,
    "area": SALE_AREA,
    "priceSqm": sale_rate,
    "beds": BEDS,
    "bedrooms": BEDS,
    "roomType": "1BR",
    "title": "JW Condo，1 房，26.8 ㎡，฿1,700,000",
    "url": SALE_URL,
    "sourceName": "PropertyHub",
    "projectName": NAME,
    "updated": "2026-10-07",
    "checkedAt": CHECKED,
    "matchedBy": "PropertyHub_exact_project_feed_and_direct_listing_A050074_1BR_26.8sqm_1700000",
    "listingStatus": "active_as_listed",
}
sale_rate_sample = {
    "id": "6352938",
    "price": SALE_PRICE,
    "area": 29.0,
    "priceSqm": round(SALE_PRICE / 29.0),
    "beds": BEDS,
    "bedrooms": BEDS,
    "roomType": "1BR",
    "title": "JW Condo，1 房，29 ㎡，฿1,700,000",
    "url": SALE_RATE_URL,
    "sourceName": "PropertyHub",
    "projectName": NAME,
    "updated": "2026-10-07",
    "checkedAt": CHECKED,
    "matchedBy": "PropertyHub_exact_project_feed_and_direct_listing_S020057_1BR_29sqm_1700000",
    "listingStatus": "active_as_listed",
}
rent = {
    "id": "1930800",
    "price": RENT_PRICE,
    "area": RENT_AREA,
    "priceSqm": round(rent_rate),
    "beds": BEDS,
    "bedrooms": BEDS,
    "roomType": "1BR",
    "title": "JW Condo，1 房，27 ㎡，฿7,000/月",
    "url": RENT_URL,
    "sourceName": "PropertyHub",
    "projectName": NAME,
    "updated": "2026-10-16",
    "checkedAt": CHECKED,
    "matchedBy": "PropertyHub_exact_project_feed_and_direct_listing_1930800_1BR_27sqm_7000_month",
    "listingStatus": "active_as_listed",
}

manual = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
row = next((item for item in manual if int(item.get("hipflatId", -1)) == ID), None)
if row is None:
    row = {"hipflatId": ID, "name": NAME}
    manual.append(row)
row.update({
    "name": NAME,
    "asOf": CHECKED,
    "sale": {"samples": [sale, sale_rate_sample]},
    "rent": {"samples": [rent]},
    "feeVerification": {
        "status": "not_found",
        "sourceUrl": SALE_PROJECT_URL,
        "note": "PropertyHub project information page did not publish a common-area fee amount; no fee is deducted from ROI.",
    },
})
manual.sort(key=lambda item: int(item["hipflatId"]))
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

crosschecks = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next((item for item in crosschecks if int(item.get("hipflatId", -1)) == ID), None)
if cross is None:
    cross = {"hipflatId": ID, "projectName": NAME}
    crosschecks.append(cross)
cross.update({
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "PropertyHub",
    "projectSourceUrl": SALE_PROJECT_URL,
    "sale": {
        "activeListingCount": 17,
        "sourceUrl": SALE_PROJECT_URL,
        "listings": [
            {"id": sale["id"], "price": SALE_PRICE, "area": SALE_AREA,
             "priceSqm": sale_rate, "bedrooms": BEDS, "title": sale["title"],
             "url": SALE_URL, "listedAt": sale["updated"]},
            {"id": sale_rate_sample["id"], "price": SALE_PRICE, "area": sale_rate_sample["area"],
             "priceSqm": sale_rate_sample["priceSqm"], "bedrooms": BEDS,
             "title": sale_rate_sample["title"], "url": SALE_RATE_URL,
             "listedAt": sale_rate_sample["updated"]},
        ],
    },
    "rent": {
        "activeListingCount": 20,
        "sourceUrl": RENT_PROJECT_URL,
        "listings": [{"id": rent["id"], "price": RENT_PRICE, "area": RENT_AREA,
                      "priceSqm": round(rent_rate), "bedrooms": BEDS, "title": rent["title"],
                      "url": RENT_URL, "listedAt": rent["updated"]}],
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 出售專案頁", "url": SALE_PROJECT_URL,
         "statusLabel": "專案頁列出 17 筆出售物件；A050074 一房 26.8㎡、฿1,700,000，2026-10-07 更新。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": RENT_PROJECT_URL,
         "statusLabel": "專案頁列出 20 筆出租物件；ID 1930800 一房 27㎡、฿7,000/月，2026-10-16 更新。"},
        {"sourceName": "PropertyScout 專案與座標", "url": PROPERTYSCOUT_URL,
         "statusLabel": "JW Condo @ Donmuang 專案點位；13.924070, 100.598357。"},
    ],
})
crosschecks.sort(key=lambda item: int(item["hipflatId"]))
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

modeled_monthly_rent = RENT_PRICE / RENT_AREA * SALE_AREA
gross_yield = modeled_monthly_rent * 12 / SALE_PRICE * 100
after_agent_yield = modeled_monthly_rent * 11 / SALE_PRICE * 100
report = {
    "hipflatId": ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "coordinates": {"lat": 13.92407, "lng": 100.598357, "verifiedSourceUrl": PROPERTYSCOUT_URL},
    "sale": sale,
    "saleLowestPricePerSqmSample": sale_rate_sample,
    "rent": rent,
    "saleProjectPage": {"url": SALE_PROJECT_URL, "visibleResults": 17},
    "rentProjectPage": {"url": RENT_PROJECT_URL, "visibleResults": 20},
    "projectFacts": {
        "completedYear": 2017,
        "buildings": 6,
        "floors": 8,
        "units": 673,
        "sourceUrl": RENT_PROJECT_URL,
        "commonAreaFee": "not published",
    },
    "yieldRecalculation": {
        "bedrooms": BEDS,
        "purchasePriceThb": SALE_PRICE,
        "purchaseAreaSqmFromSameLowestSaleListing": SALE_AREA,
        "rentListingPriceThbPerMonth": RENT_PRICE,
        "rentListingAreaSqm": RENT_AREA,
        "sameBedroomRentRateThbPerSqmMonth": round(rent_rate, 2),
        "estimatedMonthlyRentAtSaleAreaThb": round(modeled_monthly_rent),
        "grossAnnualYieldPercent": round(gross_yield, 2),
        "annualYieldAfterOneAgentMonthPercent": round(after_agent_yield, 2),
        "commonAreaFeeDeducted": False,
        "commonAreaFeeReason": "No published and verified common-area fee was found.",
        "sourceSaleUrl": SALE_URL,
        "sourceRentUrl": RENT_URL,
        "defaultNetYieldPercent": round(after_agent_yield, 2),
    },
    "limitations": [
        "The sale listing was refreshed 2026-10-07 and the rent listing 2026-10-16; availability has not been reconfirmed directly with advertisers.",
        "The default estimate uses a one-bedroom pair because the checked PropertyHub project information lists studio and one-bedroom unit types, not two bedrooms.",
        "The estimate assumes 11 paid rental months by default and excludes taxes, repairs, transaction costs, and unverified management fees.",
    ],
}
(ROOT / "reports" / "jw-condo-donmuang-direct-samples-yield-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

availability = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
if availability.exists():
    with availability.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        rows = [item for item in reader if not (
            item.get("hipflat_id") == str(ID) and item.get("market") in {"sale", "rent"}
        )]
    rows.extend([
        {"hipflat_id": str(ID), "condo": NAME, "checked_at": CHECKED, "market": "sale",
         "status": "active_as_listed", "verification_note": "PropertyHub project page shows A050074, 1BR/26.8sqm/฿1.7m refreshed 2026-10-07; availability not reconfirmed with advertiser.",
         "source_1": SALE_URL, "source_2": SALE_PROJECT_URL, "source_3": PROPERTYSCOUT_URL},
        {"hipflat_id": str(ID), "condo": NAME, "checked_at": CHECKED, "market": "rent",
         "status": "active_as_listed", "verification_note": "PropertyHub project page shows listing 1930800, 1BR/27sqm/฿7,000, refreshed 2026-10-16; availability not reconfirmed with advertiser.",
         "source_1": RENT_URL, "source_2": RENT_PROJECT_URL, "source_3": PROPERTYSCOUT_URL},
    ])
    with availability.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

coverage = ROOT / "reports" / "bangkok-coverage-2026-10-19.csv"
with coverage.open("r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    fields = reader.fieldnames or []
    rows = list(reader)
for item in rows:
    if item.get("hipflat_id") == str(ID):
        item.update({"sale_sample": "yes", "sale_market_value": "yes",
                     "sale_individual_listing_link": "yes", "sale_source": SALE_URL,
                     "sale_sample_updated": sale["updated"], "rent_sample": "yes",
                     "rent_individual_listing_link": "yes", "rent_source": RENT_URL,
                     "rent_sample_updated": rent["updated"], "missing": ""})
with coverage.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print(json.dumps({"hipflatId": ID, "saleThb": SALE_PRICE, "saleSqm": SALE_AREA,
                  "modeledRentThbPerMonth": round(modeled_monthly_rent),
                  "grossYieldPercent": round(gross_yield, 2),
                  "afterOneAgentMonthPercent": round(after_agent_yield, 2)}, ensure_ascii=False))
