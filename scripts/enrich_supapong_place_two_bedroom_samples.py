"""Add exact Supapong Place two-bedroom sale and rental samples."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT_ID = 3765
NAME = "Supapong Place"
CHECKED = "2026-10-18"
HIPFLAT = "https://www.hipflat.co.th/en/projects/supapong-place-fyvkhz"
SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-supapong-place"
RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-supapong-place"
SALE_URL = "https://propertyhub.in.th/en/listings/a033874-supapong-place---6005652"
RENT_URL = "https://propertyscout.co.th/en/2-br-condo-supapong-place-near-mrt-ratchadaphisek-3316018/"

SALE_PRICE, SALE_AREA, SALE_DATE = 2_400_000, 60.0, "2026-08-17"
RENT_PRICE, RENT_AREA, RENT_DATE = 14_000, 68.0, "2026-09-14"
RENT_RATE = RENT_PRICE / RENT_AREA
MONTHLY_RENT_AT_SALE_AREA = round(RENT_RATE * SALE_AREA)
GROSS_YIELD = MONTHLY_RENT_AT_SALE_AREA * 12 / SALE_PRICE * 100
AFTER_AGENT_YIELD = MONTHLY_RENT_AT_SALE_AREA * 11 / SALE_PRICE * 100


def read_array(path: pathlib.Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{symbol} = "
    if not text.startswith(prefix):
        raise RuntimeError(f"Unexpected JavaScript array format: {path}")
    return json.loads(text[len(prefix):].strip().rstrip(";"))


def write_array(path: pathlib.Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_sample = {
    "id": "6005652", "price": SALE_PRICE, "area": SALE_AREA,
    "priceSqm": round(SALE_PRICE / SALE_AREA), "beds": 2,
    "roomType": "TWO_BED_ROOM", "title": "A033874 Supapong Place · 2BR · 60 sqm · ฿2,400,000",
    "url": SALE_URL, "sourceName": "PropertyHub", "projectName": NAME,
    "updated": SALE_DATE, "checkedAt": CHECKED,
    "matchedBy": "Exact Supapong Place sale project page showed 8 listings and one 2-bedroom property at ฿2,400,000 / 60 sqm; direct page confirms project, 2 bedrooms and floor 23.",
    "listingStatus": "availability_unconfirmed_update_over_30d",
}
rent_sample = {
    "id": "3316018", "price": RENT_PRICE, "area": RENT_AREA,
    "priceSqm": round(RENT_RATE), "beds": 2,
    "roomType": "TWO_BED_ROOM", "title": "Supapong Place · 2BR · 68 sqm · ฿14,000/month",
    "url": RENT_URL, "sourceName": "PropertyScout", "projectName": NAME,
    "updated": RENT_DATE, "checkedAt": CHECKED,
    "matchedBy": "Exact PropertyScout Supapong Place listing; 2 bedrooms, 68 sqm, ฿14,000/month; source status said confirmed available about one month before check. PropertyHub exact-project rent page showed no matched properties.",
    "listingStatus": "availability_unconfirmed_update_over_30d",
}

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual = read_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
existing = next((row for row in manual if int(row.get("hipflatId", -1)) == PROJECT_ID), {})
sale_samples = [sample for sample in (existing.get("sale") or {}).get("samples", []) if sample.get("url") != SALE_URL]
rent_samples = [sample for sample in (existing.get("rent") or {}).get("samples", []) if sample.get("url") != RENT_URL]
sale_samples.append(sale_sample)
rent_samples.append(rent_sample)
manual = [row for row in manual if int(row.get("hipflatId", -1)) != PROJECT_ID]
manual.append({"hipflatId": PROJECT_ID, "name": NAME, "asOf": CHECKED,
               "sale": {"samples": sale_samples}, "rent": {"samples": rent_samples}})
write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

report = {
    "project": NAME, "hipflatId": PROJECT_ID, "checkedAt": CHECKED,
    "sources": {"hipflatProject": HIPFLAT, "saleProject": SALE_PROJECT,
                "rentProject": RENT_PROJECT, "saleListing": SALE_URL, "rentListing": RENT_URL},
    "sale": {"twoBedroomListingsOnExactProjectPage": 1,
             "twoBedroomMinimum": {"priceThb": SALE_PRICE, "areaSqm": SALE_AREA,
                                   "pricePerSqmThb": round(SALE_PRICE / SALE_AREA),
                                   "listingId": "6005652", "updated": SALE_DATE,
                                   "availability": "Unconfirmed; project-page card was last updated 2026-08-17."}},
    "rent": {"propertyHubExactProjectPage": "No matched properties for rent at check time.",
             "twoBedroomSample": {"priceThbPerMonth": RENT_PRICE, "areaSqm": RENT_AREA,
                                  "pricePerSqmMonthThb": round(RENT_RATE, 2),
                                  "listingId": "3316018", "listed": RENT_DATE,
                                  "availability": "PropertyScout marked confirmed available about one month before 2026-10-18; current availability is unconfirmed."}},
    "yieldEstimate": {"bedrooms": 2, "purchasePriceThb": SALE_PRICE,
                      "purchaseAreaSqm": SALE_AREA,
                      "rentRateThbPerSqmMonth": round(RENT_RATE, 4),
                      "estimatedMonthlyRentAtPurchaseAreaThb": MONTHLY_RENT_AT_SALE_AREA,
                      "grossAnnualYieldPercent": round(GROSS_YIELD, 2),
                      "afterOneAgentMonthBeforeCommonFeePercent": round(AFTER_AGENT_YIELD, 2),
                      "commonFee": "Unverified; excluded.",
                      "formula": "((14,000 / 68) * 60 * 11) / 2,400,000 * 100",
                      "purchaseSource": SALE_URL, "rentSource": RENT_URL},
    "notes": [
        "The lowest total two-bedroom sale sample in the exact PropertyHub project results is ฿2,400,000 for 60 sqm; the other displayed sale listings are one-bedroom.",
        "The only current two-bedroom rent sample found in the checked PropertyScout project results is ฿14,000/month for 68 sqm; it is not a confirmed current vacancy.",
        "The lowest total listed rent on PropertyScout includes one-bedroom units, so the yield uses a same-bedroom two-bedroom rate.",
        "The rent rate is used to scale rent to the 60 sqm purchase unit; one month of rent is deducted for agent management. Common fee is not published as an amount and is not deducted.",
    ],
}
(ROOT / "reports/supapong-place-two-bedroom-samples-2026-10-18.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "twoBedroomSale": [SALE_PRICE, SALE_AREA],
                  "twoBedroomRent": [RENT_PRICE, RENT_AREA],
                  "rentPerSqm": round(RENT_RATE, 2),
                  "monthlyRentAtSaleArea": MONTHLY_RENT_AT_SALE_AREA,
                  "grossYield": round(GROSS_YIELD, 2),
                  "afterOneAgentMonthBeforeFee": round(AFTER_AGENT_YIELD, 2)}, ensure_ascii=False))
