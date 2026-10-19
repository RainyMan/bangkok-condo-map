import copy
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-10-19"
HIPFLAT_ID = 3438
ALIAS_ID = 5491
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/bridge-narathiwat-zhocxc"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/bridge-sathorn-narathiwas"
PROPERTYHUB_SALE_FEED = "https://propertyhub.in.th/en/condo-for-sale/project-bridge-sathorn-narathiwas"
PROPERTYHUB_RENT_FEED = "https://propertyhub.in.th/en/condo-for-rent/project-bridge-sathorn-narathiwas"
COORDINATE_SOURCE = "https://thinkofliving.com/คอนโด/bridge-สาทร-นราธิวาส-คอนโด-low-rise-สไตล์-modern-loft-luxury-จากปริญสิริ-รีวิวฉบับที่-528-127058-รีวิวโครงการ/"
ADDRESS_SOURCE = "https://www.ddproperty.com/en/property/bridge-sathorn-narathiwas-bangkok-for-sale-500296082"


def read_js_array(path: Path, variable: str):
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{variable} ="
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript data header in {path}")
    return json.loads(text[len(prefix):].strip().rstrip(";"))


def write_js_array(path: Path, variable: str, rows):
    path.write_text(
        f"window.{variable} =" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def upsert(rows, key, value):
    for index, row in enumerate(rows):
        if str(row.get(key)) == str(value[key]):
            rows[index] = value
            return
    rows.append(value)


def update_project_map():
    path = ROOT / "dist/bangkok-propertyhub-map.js"
    rows = read_js_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    source = next(row for row in rows if int(row["id"]) == ALIAS_ID)
    target = next(row for row in rows if int(row["id"]) == HIPFLAT_ID)
    for market in ("sale", "rent"):
        target[market] = copy.deepcopy(source[market])
    target.update({
        "lat": 13.703568,
        "lng": 100.539973,
        "completedYear": 2015,
        "completedYearSourceUrl": HIPFLAT_URL,
        "floors": 8,
        "units": 91,
        "fee": {
            "rate": 55,
            "note": "Hipflat 專案頁標示管理費 ฿55/㎡；現行費率請向管委會確認。",
            "source": HIPFLAT_URL,
            "status": "published_indicative",
        },
        "address": "7 Naradhiwas Rajanagarindra Rd, Chong Nonsi, Yan Nawa, Bangkok 10120",
        "locationVerified": True,
        "locationSourceUrl": COORDINATE_SOURCE,
        "locationSourceName": "ThinkOfLiving 專案評測明列座標",
        "propertyHubProjectUrl": PROPERTYHUB_PROJECT_URL,
        "propertyHubSaleUrl": PROPERTYHUB_SALE_FEED,
        "propertyHubRentUrl": PROPERTYHUB_RENT_FEED,
        "marketDataStatus": "propertyhub_exact_project_id_alias_match",
    })
    target.pop("propertyHubProjectId", None)
    write_js_array(path, "BANGKOK_PROPERTYHUB_PROJECTS", rows)


def update_city_summary():
    path = ROOT / "dist/bangkok-propertyhub-city-summaries.js"
    rows = read_js_array(path, "BANGKOK_PROPERTYHUB_CITY_SUMMARIES")
    source = next(row for row in rows if int(row["id"]) == ALIAS_ID)
    record = copy.deepcopy(source)
    record["id"] = HIPFLAT_ID
    record["sale"]["source"] = PROPERTYHUB_SALE_FEED
    record["rent"]["source"] = PROPERTYHUB_RENT_FEED
    upsert(rows, "id", record)
    write_js_array(path, "BANGKOK_PROPERTYHUB_CITY_SUMMARIES", rows)


def add_direct_samples():
    project_map = read_js_array(ROOT / "dist/bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    alias = next(row for row in project_map if int(row["id"]) == ALIAS_ID)
    source = read_js_array(ROOT / "dist/bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    alias_detail = next(row for row in source if int(row["id"]) == ALIAS_ID)
    samples = []
    for kind in ("sale", "rent"):
        for item in alias_detail[kind].get("samples", []):
            sample = copy.deepcopy(item)
            sample["sourceName"] = "PropertyHub"
            sample["checkedAt"] = AS_OF
            sample["matchedBy"] = "same_propertyhub_project_id_1247_and_hipflat_project_alias_description"
            sample["listingStatus"] = "availability_unconfirmed_update_under_30d"
            samples.append(sample)

    path = ROOT / "dist/bangkok-manual-market-samples.js"
    rows = read_js_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    record = {
        "hipflatId": HIPFLAT_ID,
        "name": "Bridge Narathiwat",
        "completedYear": 2015,
        "completedYearSourceUrl": HIPFLAT_URL,
        "fee": copy.deepcopy(alias["fee"]),
        "sale": {"samples": [sample for sample in samples if sample["kind"] == "sale"]},
        "rent": {"samples": [sample for sample in samples if sample["kind"] == "rent"]},
        "marketIdentityNote": "Hipflat Bridge Narathiwat page's project description explicitly names Bridge Sathorn-Narathiwas and states the same Prinsiri 8-floor, 91-unit project. PropertyHub project ID 1247 and direct listings were matched to that alias.",
    }
    upsert(rows, "hipflatId", record)
    write_js_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)


def update_coverage():
    path = ROOT / "reports/bangkok-coverage-2026-10-19.csv"
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        fields = reader.fieldnames
    row = next(item for item in rows if item["hipflat_id"] == str(HIPFLAT_ID))
    sale = read_js_array(ROOT / "dist/bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    sale = next(item for item in sale if int(item["id"]) == ALIAS_ID)["sale"]
    rent = read_js_array(ROOT / "dist/bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    rent = next(item for item in rent if int(item["id"]) == ALIAS_ID)["rent"]
    sale_update = next(sample["updated"] for sample in sale["samples"] if sample["url"] == sale["minimumSourceUrl"])
    rent_update = next(sample["updated"] for sample in rent["samples"] if sample["url"] == rent["minimumSqmSourceUrl"])
    row.update({
        "coordinates": "yes",
        "coordinate_source": COORDINATE_SOURCE,
        "sale_sample": "yes",
        "sale_market_value": "yes",
        "sale_individual_listing_link": "yes",
        "sale_source": sale["minimumSourceUrl"],
        "sale_sample_updated": sale_update,
        "sale_availability_checked": "yes",
        "sale_availability_note": "Hipflat lists active sale units; PropertyHub direct project feed and linked individual listing verified by exact project ID/name alias on 2026-10-19.",
        "rent_sample": "yes",
        "rent_individual_listing_link": "yes",
        "rent_source": rent["minimumSqmSourceUrl"],
        "rent_sample_updated": rent_update,
        "rent_availability_checked": "yes",
        "rent_availability_note": "Hipflat lists active rental units; PropertyHub direct project feed and linked individual listing verified by exact project ID/name alias on 2026-10-19.",
        "yield_status": "calculated_estimate",
        "yield_note": "1BR fallback: ฿3,290,000 lowest linked 1BR sale / 33 sqm from the same listing; lowest linked 1BR rent rate ฿22,000/45 sqm = ฿489/sqm/month; common fee ฿55/sqm/month. With 11 rental months and 12 months common fee, net estimate is 4.73%/year. No two-bedroom sale/rent pair was listed in the checked feed.",
        "missing": "",
    })
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def update_availability_report():
    path = ROOT / "reports/listing-availability-checks-2026-10-19.csv"
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        fields = reader.fieldnames
    rows = [row for row in rows if not (row["hipflat_id"] == str(HIPFLAT_ID) and row["market"] in {"sale", "rent"})]
    note = "Hipflat page identifies Bridge Narathiwat as Bridge Sathorn-Narathiwas and matches Prinsiri, 8 floors, 91 units. PropertyHub project ID 1247 exposes direct listing pages; the individual sample links were updated within 30 days of the check."
    rows.extend([
        {"hipflat_id": str(HIPFLAT_ID), "condo": "Bridge Narathiwat", "checked_at": AS_OF, "market": "sale", "status": "exact_project_current_listings_found", "verification_note": note, "source_1": HIPFLAT_URL, "source_2": PROPERTYHUB_SALE_FEED, "source_3": "https://propertyhub.in.th/en/listings/cs543-for-sale-bridge-sathorn-narathiwast-brt-chan-road-064-665-4666---6043171"},
        {"hipflat_id": str(HIPFLAT_ID), "condo": "Bridge Narathiwat", "checked_at": AS_OF, "market": "rent", "status": "exact_project_current_listings_found", "verification_note": note, "source_1": HIPFLAT_URL, "source_2": PROPERTYHUB_RENT_FEED, "source_3": "https://propertyhub.in.th/en/listings/condo-1-bedroom-for-rent-at-bridge-sathorn-narathiwas-near-central-rama-3-ref-a17230142---4834461"},
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def update_cache_tags():
    path = ROOT / "dist/index.html"
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"bangkok-propertyhub-map\.js\?v=[^\"]+", "bangkok-propertyhub-map.js?v=20261019-bridge-narathiwat-alias-3438", html)
    html = re.sub(r"bangkok-propertyhub-city-summaries\.js\?v=[^\"]+", "bangkok-propertyhub-city-summaries.js?v=20261019-bridge-narathiwat-alias-3438", html)
    html = re.sub(r"bangkok-manual-market-samples\.js\?v=[^\"]+", "bangkok-manual-market-samples.js?v=20261019-bridge-narathiwat-verified-samples-3438", html)
    path.write_text(html, encoding="utf-8")


def write_audit_report():
    report = {
        "hipflatId": HIPFLAT_ID,
        "project": "Bridge Narathiwat",
        "checkedAt": AS_OF,
        "identityMatch": {
            "hipflatProjectUrl": HIPFLAT_URL,
            "matchedProjectName": "Bridge Sathorn-Narathiwas",
            "matchedPropertyHubProjectId": "1247",
            "evidence": "Hipflat's own project description names Bridge Sathorn-Narathiwas, developer Prinsiri, 8 floors, 91 units, unit sizes and the Narathiwat Rajanagarindra Road location; the PropertyHub direct project and listing pages name the same project.",
            "duplicateHipflatId": ALIAS_ID,
        },
        "coordinate": {
            "lat": 13.703568,
            "lng": 100.539973,
            "sourceUrl": COORDINATE_SOURCE,
            "verificationUrl": HIPFLAT_URL,
            "verification": "ThinkOfLiving publishes this exact project pin; Hipflat and DDproperty independently identify the matching Bridge project and Naradhiwas Rajanagarindra Road address.",
        },
        "projectFacts": {
            "completedYear": 2015,
            "floors": 8,
            "units": 91,
            "feeThbPerSqmMonth": 55,
            "sourceUrl": HIPFLAT_URL,
            "completionYearNote": "PropertyHub project details show 2014, while Hipflat and Thailand-Property show 2015. The map follows the Hipflat-listed Hipflat ID's 2015 completion year; the conflict is retained for follow-up.",
        },
        "sale": {
            "saleFeedUrl": PROPERTYHUB_SALE_FEED,
            "lowestTotalSample": {
                "priceThb": 3290000,
                "areaSqm": 33,
                "bedrooms": 1,
                "url": "https://propertyhub.in.th/en/listings/cs543-for-sale-bridge-sathorn-narathiwast-brt-chan-road-064-665-4666---6043171",
                "updatedAt": "2026-10-16T14:50:30.511Z",
            },
            "sourceNote": "PropertyHub project listing results show the matching 1-bedroom project sample. Hipflat lists active sale units for the project.",
        },
        "rent": {
            "rentFeedUrl": PROPERTYHUB_RENT_FEED,
            "lowestPsmSample": {
                "monthlyRentThb": 22000,
                "areaSqm": 45,
                "bedrooms": 1,
                "rentThbPerSqmMonth": 489,
                "url": "https://propertyhub.in.th/en/listings/condo-1-bedroom-for-rent-at-bridge-sathorn-narathiwas-near-central-rama-3-ref-a17230142---4834461",
                "updatedAt": "2026-10-16T02:14:54.991Z",
            },
            "sourceNote": "PropertyHub project listing results and Hipflat's available-unit page report rental listings for the same project.",
        },
        "yield": {
            "status": "estimated_from_1br_because_no_2br_pair_was_found",
            "formula": "(((22,000 THB/month ÷ 45 sqm) × 33 sqm × 11 months) − (55 THB/sqm/month × 33 sqm × 12 months)) ÷ 3,290,000 THB × 100",
            "netAnnualYieldPercent": 4.73,
            "assumptions": ["One-month agent management fee deducted", "Common fee deducted", "No sale/rent pair for a two-bedroom unit was found in the checked project feed"],
        },
        "sources": {
            "hipflatProject": HIPFLAT_URL,
            "propertyHubProject": PROPERTYHUB_PROJECT_URL,
            "thinkOfLivingCoordinate": COORDINATE_SOURCE,
            "ddpropertyAddressCheck": ADDRESS_SOURCE,
        },
    }
    (ROOT / "reports/bridge-narathiwat-verified-alias-samples-2026-10-19.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    update_project_map()
    update_city_summary()
    add_direct_samples()
    update_coverage()
    update_availability_report()
    update_cache_tags()
    write_audit_report()


if __name__ == "__main__":
    main()
