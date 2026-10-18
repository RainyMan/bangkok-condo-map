"""Add verified market samples and project data for Hipflat's Thanapat Vipha."""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3150
NAME = "Thanapat Vipha"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/thanapat-vipha-sfaaic"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/sym-vibha-ladprao"
PROPERTYHUB_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-sym-vibha-ladprao"
PROPERTYHUB_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-sym-vibha-ladprao"
BK_CITYSMART_URL = "https://www.bkkcitismart.com/en/buy/project/P24121101"
BKKFINDER_URL = "https://www.bkkfinder.com/en/project/j9zyfax/sym-vibha-ladprao"

SALE_SAMPLES = [
    {"id": "6145197", "price": 2_300_000, "area": 27.71, "beds": 0, "roomType": "Studio", "updated": "2026-09-12T05:19:00+07:00", "title": "SYM Vipah Ladphrao Studio，27.71㎡", "url": "https://propertyhub.in.th/en/listings/condo-for-sale-sym-vipah-ladphrao---6145197"},
    {"id": "6192178", "price": 2_700_000, "area": 37.0, "beds": 1, "roomType": "1 Bedroom", "updated": "2026-09-12T12:00:00+07:00", "title": "SYM Vibha-Ladprao 1 房，37㎡", "url": "https://propertyhub.in.th/en/listings/for-sell-condo-sym-vibha-ladprao-building-1-floor-17-1-bed-room-room-size-37-sqm--aa2008e6---6192178"},
    {"id": "6325521", "price": 4_990_000, "area": 53.75, "beds": 2, "roomType": "2 Bedroom", "updated": "2026-09-12T05:13:00+07:00", "title": "SYM Vibha-Ladprao 2 房，53.75㎡", "url": "https://propertyhub.in.th/en/listings/a050264-sym-vibha-ladprao---6325521"},
    {"id": "6324630", "price": 5_170_000, "area": 53.75, "beds": 2, "roomType": "2 Bedroom", "updated": "2026-09-11T13:09:00+07:00", "title": "SYM Vibha-Ladprao 2 房，53.75㎡", "url": "https://propertyhub.in.th/en/listings/23rd-floor-2-br-sym-vibha-ladprao-near-bts-mo-chit-id-3224959---6324630"},
    {"id": "6082248", "price": 5_200_000, "area": 53.7, "beds": 2, "roomType": "2 Bedroom", "updated": "2026-09-11T01:29:00+07:00", "title": "SYM Vipha-Ladprao 2 房，53.7㎡", "url": "https://propertyhub.in.th/en/listings/sym-vipha-ladprao-condo-for-sale---6082248"},
]

RENT_SAMPLES = [
    {"id": "6145234", "price": 12_000, "area": 27.71, "beds": 0, "roomType": "Studio", "updated": "2026-10-08T17:05:00+07:00", "title": "SYM Vipah Ladphrao Studio，27.71㎡", "url": "https://propertyhub.in.th/en/listings/condo-for-rent-sym-vipah-ladphrao---6145234"},
    {"id": "6404908", "price": 13_000, "area": 34.0, "beds": 1, "roomType": "1 Bedroom", "updated": "2026-10-11T16:00:00+07:00", "title": "SYM Vibha-Ladprao 1 房，34㎡", "url": "https://propertyhub.in.th/en/listings/condo-for-rent-at-sym-vibha-ladprao-p6909023---6404908"},
    {"id": "5493259", "price": 22_500, "area": 53.0, "beds": 2, "roomType": "2 Bedroom", "updated": "2026-10-11T14:45:00+07:00", "title": "SYM Vibha-Ladprao 2 房，53㎡", "url": "https://propertyhub.in.th/en/listings/z2740141068-condo-for-rent-sym-vipha-ladphrao-condominium---5493259"},
    {"id": "5744615", "price": 25_000, "area": 53.0, "beds": 2, "roomType": "2 Bedroom", "updated": "2026-10-10T10:00:00+07:00", "title": "SYM Vibha-Ladprao 2 房，53㎡", "url": "https://propertyhub.in.th/en/listings/for-rent-sym-vibhaladprao-condominium-fully-furnished-close-to-bts-mo-chit-chomphon-area-chatuchak-district-bangkok-rw007482---5744615"},
]


def read_array(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"window\.BANGKOK_PROPERTYHUB_PROJECTS\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not read project array from {path.name}")
    return json.loads(match.group(1))


def write_array(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "window.BANGKOK_PROPERTYHUB_PROJECTS = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def update_catalogue_address() -> None:
    path = DIST / "bangkok-catalogue.js"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"window\.BANGKOK_CONDO_CATALOGUE\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError("Could not read Bangkok Condo catalogue")
    rows = json.loads(match.group(1))
    item = next(row for row in rows if int(row.get("id", 0)) == PROJECT_ID)
    item["address"] = "Vibhavadi Rangsit Road, Soi 9 (Soi Choei Phuang), Chom Phon, Chatuchak, Bangkok 10900"
    path.write_text("window.BANGKOK_CONDO_CATALOGUE = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def market(samples: list[dict], project_count: int, kind: str) -> dict:
    records = [{**row, "priceSqm": row["price"] / row["area"], "sourceName": "PropertyHub", "projectName": "SYM Vibha - Ladprao", "checkedAt": date.today().isoformat(), "matchedBy": "exact_propertyhub_project_listing_and_detail", **({"listingStatus": "availability_unconfirmed_update_over_30d"} if kind == "sale" and row["updated"] < "2026-09-18" else {})} for row in samples]
    by_total = min(records, key=lambda row: row["price"])
    by_sqm = min(records, key=lambda row: row["priceSqm"])
    grouped: dict[str, list[dict]] = {}
    for row in records:
        beds = int(row["beds"] or 0)
        if beds > 0:
            grouped.setdefault(str(beds), []).append(row)
    by_bedroom = {}
    for beds, group in grouped.items():
        low = min(group, key=lambda row: row["price"])
        low_sqm = min(group, key=lambda row: row["priceSqm"])
        by_bedroom[beds] = {
            "count": len(group), "minimum": low["price"], "area": low["area"],
            "priceSqm": round(low["priceSqm"]), "minimumSqm": round(low_sqm["priceSqm"]),
            "minimumSqmSourceUrl": low_sqm["url"], "sourceUrl": low["url"],
        }
    return {
        "count": project_count, "observedCount": len(records), "countKind": "propertyhub_project_page_sample",
        "average": round(sum(row["price"] for row in records) / len(records)),
        "minimum": by_total["price"], "minimumArea": by_total["area"],
        "minimumSampleUpdated": by_total["updated"], "averageSqm": round(sum(row["priceSqm"] for row in records) / len(records)),
        "minimumSqm": round(by_sqm["priceSqm"]), "minimumSqmSampleUpdated": by_sqm["updated"],
        "asOf": date.today().isoformat(), "sourceName": "PropertyHub 專案頁可見掛牌樣本",
        "source": PROPERTYHUB_SALE_URL if kind == "sale" else PROPERTYHUB_RENT_URL,
        "minimumSourceUrl": by_total["url"], "minimumSqmSourceUrl": by_sqm["url"],
        "samples": sorted(records, key=lambda row: row["price"]), "byBedroom": by_bedroom,
    }


def main() -> None:
    update_catalogue_address()
    project = None
    for filename in ("bangkok-propertyhub-map.js", "bangkok-propertyhub.js"):
        path = DIST / filename
        rows = read_array(path)
        project = next(row for row in rows if int(row.get("id", 0)) == PROJECT_ID)
        project.update({
            "lat": 13.80661558110686, "lng": 100.5597865287567, "locationVerified": True,
            "locationSourceName": "PropertyHub 專案頁原生專案座標",
            "locationSourceUrl": PROPERTYHUB_PROJECT_URL,
            "locationVerificationSourceUrl": BK_CITYSMART_URL,
            "completedYear": 2010, "completedYearSourceUrl": PROPERTYHUB_PROJECT_URL,
            "completedYearConflictNote": "PropertyHub、BKK Finder、Lazudi 均記載 2010；BKK CitySmart 記載 2013，故保留 2010 並在研究紀錄註明來源差異。",
            "units": 728, "floors": 29, "area": {"min": 27, "max": 78}, "beds": None,
            "address": "Vibhavadi Rangsit Road, Soi 9 (Soi Choei Phuang), Chom Phon, Chatuchak, Bangkok 10900",
            "fee": {"rate": 30, "status": "public", "note": "PropertyHub 專案頁及 BKK CitySmart 均刊載 ฿30/㎡/月；實際應向管委會確認。", "source": PROPERTYHUB_PROJECT_URL},
            "propertyHubProjectId": "1191", "propertyHubProjectUrl": PROPERTYHUB_PROJECT_URL,
            "propertyHubSaleUrl": PROPERTYHUB_SALE_URL, "propertyHubRentUrl": PROPERTYHUB_RENT_URL,
            "sale": market(SALE_SAMPLES, 20, "sale"), "rent": market(RENT_SAMPLES, 54, "rent"),
        })
        write_array(path, rows)

    html_path = DIST / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html = re.sub(r'bangkok-catalogue\.js\?v=[^" ]+', "bangkok-catalogue.js?v=20261018d-thanapat-vipha-verified-address", html)
    html = re.sub(r'bangkok-propertyhub-map\.js\?v=[^" ]+', "bangkok-propertyhub-map.js?v=20261018k-thanapat-vipha-market-coordinates", html)
    html = re.sub(r'bangkok-walk-routes\.js\?v=[^" ]+', "bangkok-walk-routes.js?v=20261018j-thanapat-vipha-walk-route", html)
    html_path.write_text(html, encoding="utf-8")

    two_bed_sale = min((row for row in SALE_SAMPLES if row["beds"] == 2), key=lambda row: row["price"])
    two_bed_rent = min((row for row in RENT_SAMPLES if row["beds"] == 2), key=lambda row: row["price"] / row["area"])
    calc_monthly_rent = round(two_bed_rent["price"] / two_bed_rent["area"] * two_bed_sale["area"])
    annual_rent_after_agent = calc_monthly_rent * 11
    annual_fee = 30 * two_bed_sale["area"] * 12
    net_yield = (annual_rent_after_agent - annual_fee) / two_bed_sale["price"] * 100
    report = {
        "hipflatId": PROJECT_ID, "name": NAME, "checkedAt": date.today().isoformat(),
        "projectIdentity": {
            "hipflatProjectUrl": HIPFLAT_URL, "propertyHubProjectUrl": PROPERTYHUB_PROJECT_URL,
            "identitySourceUrl": BK_CITYSMART_URL,
            "match": "BKK CitySmart names SYM Vibha-Ladprao's previous project name as Thanapat Vipha and gives the same Vibhavadi Rangsit Soi 9 / Soi Choei Phuang address, 29 floors and 728 units as the Hipflat record.",
        },
        "location": {"status": "verified_exact_project_map_point", "lat": project["lat"], "lng": project["lng"], "sourceUrl": PROPERTYHUB_PROJECT_URL, "corroboratingSourceUrl": BKKFINDER_URL, "method": "coordinates read from exact PropertyHub project page's embedded project.location object; BKK Finder project pin is within about 15 metres."},
        "projectDetails": {"completedYear": 2010, "units": 728, "floors": 29, "areaSqm": "27-78", "commonFeeThbPerSqmMonth": 30, "sourceUrl": PROPERTYHUB_PROJECT_URL, "corroboratingSourceUrl": "https://www.lazudi.com/th-en/bangkok/project/sym-vibha-ladprao-2813", "yearConflict": "BKK CitySmart shows 2013; PropertyHub, BKK Finder and Lazudi show 2010. The direct PropertyHub listing's generic overview says around 2010-2011 and one old ad snippet says 2014. UI uses 2010; keep discrepancy visible for future manual verification."},
        "marketSamples": {
            "sale": {"sourceUrl": PROPERTYHUB_SALE_URL, "platformListings": 20, "verifiedIndividualSamples": len(SALE_SAMPLES), "samples": SALE_SAMPLES, "lowestTwoBedroom": {"priceThb": two_bed_sale["price"], "areaSqm": two_bed_sale["area"], "priceThbPerSqm": round(two_bed_sale["price"] / two_bed_sale["area"]), "url": two_bed_sale["url"]}},
            "rent": {"sourceUrl": PROPERTYHUB_RENT_URL, "platformListings": 54, "verifiedIndividualSamples": len(RENT_SAMPLES), "samples": RENT_SAMPLES, "lowestTwoBedroomBySqm": {"monthlyRentThb": two_bed_rent["price"], "areaSqm": two_bed_rent["area"], "rentThbPerSqmMonth": round(two_bed_rent["price"] / two_bed_rent["area"], 2), "url": two_bed_rent["url"]}},
        },
        "yieldEstimate": {"bedrooms": 2, "purchasePriceThb": two_bed_sale["price"], "saleAreaSqm": two_bed_sale["area"], "rentSourceRateThbPerSqmMonth": round(two_bed_rent["price"] / two_bed_rent["area"], 2), "estimatedMonthlyRentAtSaleAreaThb": calc_monthly_rent, "deductAgentMonths": 1, "annualCommonFeeThb": annual_fee, "netAnnualYieldPercent": round(net_yield, 2), "formula": "(estimated monthly rent × 11 − common fee × sale area × 12) / lowest two-bedroom sale total × 100", "caveat": "Rent is estimated from the lowest-rent-per-sqm current two-bedroom listing. Both individual listing pages omit a last-update timestamp, but their project index cards show recent refresh dates. Availability must still be confirmed with the poster."},
        "walkingRoute": None,
    }
    routes_path = DIST / "bangkok-walk-routes.js"
    route_match = re.search(r"window\.BANGKOK_WALK_ROUTES\s*=\s*(\[.*\]);", routes_path.read_text(encoding="utf-8"), re.S)
    if route_match:
        report["walkingRoute"] = next((row for row in json.loads(route_match.group(1)) if int(row.get("id", 0)) == PROJECT_ID), None)
    report_path = ROOT / "reports" / "thanapat-vipha-sym-vibha-ladprao-2026-10-18.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
    with availability_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
    rows = [row for row in rows if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    note = f"PropertyHub exact project page lists {len(SALE_SAMPLES)} directly opened sale samples (20 project listings) and {len(RENT_SAMPLES)} rent samples (54 project listings). Two-bedroom lowest sale is THB {two_bed_sale['price']:,} / {two_bed_sale['area']} sqm; lowest two-bedroom rent rate is THB {two_bed_rent['price'] / two_bed_rent['area']:.2f}/sqm/month. Project list refresh dates are within 45 days; individual availability is unconfirmed."
    for kind, source, samples in (("sale", PROPERTYHUB_SALE_URL, SALE_SAMPLES), ("rent", PROPERTYHUB_RENT_URL, RENT_SAMPLES)):
        rows.append({"hipflat_id": str(PROJECT_ID), "condo": NAME, "checked_at": date.today().isoformat(), "market": kind, "status": "project_index_recent_direct_samples_availability_unconfirmed", "verification_note": note, "source_1": source, "source_2": samples[0]["url"], "source_3": samples[-1]["url"]})
    with availability_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": [project["lat"], project["lng"]], "saleSamples": len(SALE_SAMPLES), "rentSamples": len(RENT_SAMPLES), "twoBedroomSale": two_bed_sale["price"], "twoBedroomSaleArea": two_bed_sale["area"], "twoBedroomRentRate": round(two_bed_rent["price"] / two_bed_rent["area"], 2), "netAnnualYieldPercent": round(net_yield, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
