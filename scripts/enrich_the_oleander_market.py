"""Add exact PropertyHub listing samples for The Oleander."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_PATH = ROOT / "dist" / "bangkok-manual-market-samples.js"
INDEX_PATH = ROOT / "dist" / "index.html"
REPORT_PATH = ROOT / "reports" / "the-oleander-market-enrichment-2026-10-18.json"
PROJECT_ID = 3750
CHECKED_AT = "2026-10-18"
SALE_PAGE = "https://propertyhub.in.th/en/condo-for-sale/project-the-oleander"
RENT_PAGE = "https://propertyhub.in.th/en/condo-for-rent/project-the-oleander"

SALE_SAMPLES = [
    {"id": "4706033", "price": 8_500_000, "area": 61, "beds": 1, "title": "Pet-Friendly 1-BR 61 Sqm, The Oleander Near BTS Nana", "url": "https://propertyhub.in.th/en/listings/1-br-condo-at-the-oleander-near-bts-nana-id-1818346--b1140929---4706033", "updated": CHECKED_AT},
    {"id": "4860202", "price": 19_500_000, "area": 165, "beds": 3, "title": "3-BR Condo For Sale At The Oleander, 18th-Floor Near BTS Nana", "url": "https://propertyhub.in.th/en/listings/3-br-condo-at-the-oleander-near-bts-nana-id-1695916--aa9e09e4---4860202", "updated": CHECKED_AT},
    {"id": "5096899", "price": 15_200_000, "area": 124.8, "beds": 2, "title": "2 Bed 2 Bath 124 SQ.M at The Oleander", "url": "https://propertyhub.in.th/en/listings/2-bed-2-bath-124-sq-m-at-the-oleander--94650892---5096899", "updated": CHECKED_AT},
    {"id": "6414516", "price": 13_000_000, "area": 90, "beds": 2, "title": "The Oleander 90 sqm Corner Condo with City View in Bangkok", "url": "https://propertyhub.in.th/en/listings/the-oleander-90-sqm-corner-condo-with-city-view-in-bangkok---6414516", "updated": CHECKED_AT},
    {"id": "5094689", "price": 19_800_000, "area": 165, "beds": 3, "title": "3 Bedroom 2 Bathroom 165 SQ.M The Oleander", "url": "https://propertyhub.in.th/en/listings/3-bedroom-2-bathroom-165-sq-m-the-oleander---5094689", "updated": CHECKED_AT},
    {"id": "5538343", "price": 15_990_000, "area": 125, "beds": 2, "title": "The Oleander Sukhumvit 11 for Sale, 2 bedrooms", "url": "https://propertyhub.in.th/en/listings/%EF%B8%8Fthe-oleander-sukhumvit-11-for-sale-bts-ploenchit-mrt-petchaburi-2b-2b---5538343", "updated": CHECKED_AT},
    {"id": "4788176", "price": 12_990_000, "area": 125, "beds": 2, "title": "The Oleander 2 bedrooms, for sale", "url": "https://propertyhub.in.th/en/listings/the-oleander-2-bedrooms-for-sale---4788176", "updated": CHECKED_AT},
    {"id": "3769628", "price": 10_000_000, "area": 89, "beds": 1, "title": "The Oleander 1 bedroom, for sale", "url": "https://propertyhub.in.th/en/listings/the-oleander-1-bedroom-for-sale---3769628", "updated": CHECKED_AT},
]

RENT_SAMPLES = [
    {"id": "6185964", "price": 55_000, "area": 122, "beds": 2, "title": "2-BR Condo at The Oleander near BTS Nana", "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-the-oleander-122-sqm-near-bts-nana-id-3045865---6185964", "updated": "2026-10-08"},
    {"id": "4119581", "price": 57_000, "area": 120, "beds": 2, "title": "2-BR Condo at The Oleander near BTS Nana", "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-the-oleander-near-bts-nana-id-303773--be230a03---4119581", "updated": "2026-10-08"},
    {"id": "4630680", "price": 57_000, "area": 120, "beds": 2, "title": "2-BR Condo At The Oleander, 9th Floor, 120 Sqm Near BTS Nana", "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-the-oleander-near-bts-nana-id-1754425--92140837---4630680", "updated": "2026-10-08"},
    {"id": "6076764", "price": 65_000, "area": 122.4, "beds": 2, "title": "2-BR Condo at The Oleander near BTS Nana", "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-the-oleander-near-bts-nana-id-2828451---6076764", "updated": "2026-10-08"},
    {"id": "5571300", "price": 120_000, "area": 285, "beds": 4, "title": "4-BR Condo At The Oleander, Near BTS Nana", "url": "https://propertyhub.in.th/en/listings/4-br-condo-at-the-oleander-near-bts-nana-id-2284609--ac730923---5571300", "updated": "2026-10-08"},
    {"id": "6401429", "price": 51_000, "area": 125, "beds": 2, "title": "2-BR Condo at The Oleander near BTS Nana", "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-the-oleander-near-bts-nana-id-2834778---6401429", "updated": "2026-10-08"},
    {"id": "5621436", "price": 110_000, "area": 285, "beds": 4, "title": "For Rent Condo, The Oleander Sukhumvit 11, CX-138798", "url": "https://propertyhub.in.th/en/listings/for-rent-condo-the-oleander-sukhumvit-11-bts-nana-khlong-tan-nuea-watthana-bangkok-cx-138798-live-chat-with-us-add-line-connexproperty--ba7b0a68---5621436", "updated": "2026-10-08"},
    {"id": "5609455", "price": 57_000, "area": 120, "beds": 2, "title": "The Oleander | Charming 2 Bed Condo in Nana For Rent - BR11364CD", "url": "https://propertyhub.in.th/en/listings/the-oleander-charming-2-bed-condo-in-nana-for-rent-br11364cd---5609455", "updated": "2026-10-08"},
    {"id": "4611914", "price": 57_000, "area": 120, "beds": 2, "title": "#P262 The Oleander Fully furnished", "url": "https://propertyhub.in.th/en/listings/p262-the-oleander-fully-furnished---4611914", "updated": "2026-10-07"},
    {"id": "5618342", "price": 67_000, "area": 122.4, "beds": 2, "title": "LTH13668 – Condo for Rent | The Oleander | 122.40 sqm", "url": "https://propertyhub.in.th/en/listings/lth13668-condo-for-rent-the-oleander-122-40-sqm-2-beds-2-baths-near-bts-nana-67k-month---5618342", "updated": "2026-10-07"},
    {"id": "4431090", "price": 55_000, "area": 125, "beds": 2, "title": "for rent The Oleander. 2bed 125sqm. Line id: @pfagent", "url": "https://propertyhub.in.th/en/listings/for-rent-the-oleander-2bed-125sqm-line-id-pfagent---4431090", "updated": "2026-10-06"},
    {"id": "5848047", "price": 67_000, "area": 122, "beds": 2, "title": "The Oleander. 2bed 122sqm. Line id: @pfagent", "url": "https://propertyhub.in.th/en/listings/the-oleander-2bed-122sqm-line-id-pfagent---5848047", "updated": "2026-10-05"},
]


def market(samples: list[dict], source_url: str, is_rent: bool) -> dict:
    for sample in samples:
        sample.update({
            "priceSqm": round(sample["price"] / sample["area"]),
            "roomType": f"{sample['beds']}BR",
            "sourceName": "PropertyHub",
            "projectName": "The Oleander",
            "checkedAt": CHECKED_AT,
            "matchedBy": "exact_propertyhub_project_page_and_direct_listing_project_name",
            "listingStatus": "active_as_listed",
        })
    lowest_total = min(samples, key=lambda row: row["price"])
    lowest_rate = min(samples, key=lambda row: row["price"] / row["area"])
    by_bedroom = {}
    for beds in sorted({row["beds"] for row in samples}):
        room_samples = [row for row in samples if row["beds"] == beds]
        room_low_total = min(room_samples, key=lambda row: row["price"])
        room_low_rate = min(room_samples, key=lambda row: row["price"] / row["area"])
        by_bedroom[str(beds)] = {
            "count": len(room_samples),
            "minimum": room_low_total["price"],
            "area": room_low_total["area"],
            "minimumArea": room_low_total["area"],
            "priceSqm": round(room_low_total["price"] / room_low_total["area"]),
            "minimumSqm": round(room_low_rate["price"] / room_low_rate["area"]),
            "averageSqm": round(sum(row["price"] / row["area"] for row in room_samples) / len(room_samples)),
            "sourceUrl": room_low_total["url"],
            "minimumSourceUrl": room_low_total["url"],
            "minimumSqmSourceUrl": room_low_rate["url"],
        }
    return {
        "count": len(samples),
        "platformCount": len(samples),
        "observedCount": len(samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(row["price"] for row in samples) / len(samples)),
        "minimum": lowest_total["price"],
        "minimumArea": lowest_total["area"],
        "averageSqm": round(sum(row["price"] / row["area"] for row in samples) / len(samples)),
        "minimumSqm": round(lowest_rate["price"] / lowest_rate["area"]),
        "minimumSampleUpdated": lowest_total.get("updated"),
        "minimumSqmSampleUpdated": lowest_rate.get("updated"),
        "asOf": CHECKED_AT,
        "snapshotMethod": "PropertyHub exact project page: every listed card opened and matched to The Oleander direct listing",
        "sourceName": "PropertyHub 專案單筆掛牌",
        "source": source_url,
        "minimumSourceUrl": lowest_total["url"],
        "minimumSqmSourceUrl": lowest_rate["url"],
        "byBedroom": by_bedroom,
        "samples": samples,
    }


text = MANUAL_PATH.read_text(encoding="utf-8")
match = re.fullmatch(r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*", text, re.S)
if not match:
    raise ValueError("Unexpected manual market sample data format")
rows = json.loads(match.group(1))
project = next((row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": "The Oleander"}
    rows.append(project)
project["sale"] = market(SALE_SAMPLES, SALE_PAGE, False)
project["rent"] = market(RENT_SAMPLES, RENT_PAGE, True)
project["replaceSale"] = True
project["replaceRent"] = True
rows.sort(key=lambda row: int(row["hipflatId"]))
MANUAL_PATH.write_text("window.BANGKOK_MANUAL_MARKET_SAMPLES = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

index_text = INDEX_PATH.read_text(encoding="utf-8")
index_text, replacements = re.subn(
    r"bangkok-manual-market-samples\.js\?v=[^\"']+",
    "bangkok-manual-market-samples.js?v=20261018b-oleander-propertyhub-listings",
    index_text,
    count=1,
)
if replacements != 1:
    raise ValueError("Could not find the manual market asset cache key")
INDEX_PATH.write_text(index_text, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": "The Oleander",
    "checkedAt": CHECKED_AT,
    "projectPages": {"sale": SALE_PAGE, "rent": RENT_PAGE},
    "projectPageFacts": {
        "saleListingCount": len(SALE_SAMPLES),
        "rentListingCount": 12,
        "completionYear": 2007,
        "floors": 27,
        "units": 78,
        "utilityFeeThbPerSqm": 35,
        "utilityFeeNote": "PropertyHub labels this Utility Fee; it is not treated as a confirmed common-area management fee and is not deducted from yield.",
    },
    "saleSamples": SALE_SAMPLES,
    "rentSamples": RENT_SAMPLES,
    "yieldBaseline": {
        "bedrooms": 2,
        "purchase": {"priceThb": 12_990_000, "areaSqm": 125, "sourceUrl": SALE_SAMPLES[6]["url"]},
        "rent": {"monthlyRentThb": 51_000, "sampleAreaSqm": 125, "rentThbPerSqmMonth": 408, "sourceUrl": RENT_SAMPLES[5]["url"]},
        "annualYieldAfterOneMonthAgentFeePercent": round(51_000 * 11 / 12_990_000 * 100, 2),
        "commonFeeDeducted": False,
        "reason": "Published fee is labeled Utility Fee and requires confirmation before treating it as a management fee.",
    },
    "roi": "Calculated from the lowest linked two-bedroom sale and lowest two-bedroom rent rate applied to the same sale sample's area.",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "hipflatId": PROJECT_ID,
    "verifiedSaleListings": len(SALE_SAMPLES),
    "verifiedRentListings": len(RENT_SAMPLES),
    "twoBedroomSaleMinimum": {"price": 12_990_000, "area": 125, "sourceUrl": SALE_SAMPLES[6]["url"]},
    "twoBedroomRentMinimum": {"price": 51_000, "area": 125, "sourceUrl": RENT_SAMPLES[5]["url"]},
    "annualYieldAfterOneMonthAgentFeePercent": report["yieldBaseline"]["annualYieldAfterOneMonthAgentFeePercent"],
    "report": str(REPORT_PATH),
}, ensure_ascii=False, indent=2))
