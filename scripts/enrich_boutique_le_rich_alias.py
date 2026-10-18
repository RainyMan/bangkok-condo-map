"""Attach verified coordinates and current listings for the Boutique Le Rich alias."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3654
PROJECT = "Boutique Le Rich Ratchada-Sutthisan"
ALIAS_PROJECT = "Le Rich Ratchada - Sutthisarn"
AS_OF = "2026-10-18"
LAT, LNG = 13.78982059309066, 100.57195598141152
PH_PROJECT = "https://propertyhub.in.th/en/projects/le-rich-ratchada-sutthisarn"
PH_MAP = "https://propertyhub.in.th/en/condo-for-sale/project-le-rich-ratchada-sutthisarn"
PH_SALE = "https://propertyhub.in.th/en/listings/for-sale-condo-le-rich-ratchada-sutthisarn-corner-unit-ratchadaphisek-din-daeng-bangkok-cx-143314-live-chat-with-us-add-line-connexproperty---6400243"
PH_RENT = "https://propertyhub.in.th/en/listings/condo-for-rent-at-le-rich-ratchada-sutthisarn-b6907045---6246903"
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/boutique-le-rich-ratchadasutthisan-wvfzho"
HIPFLAT_SALE = "https://www.hipflat.co.th/en/ads/7lnal2798lhlaeh40h043h3e3u0cea89"
HIPFLAT_RENT = "https://www.hipflat.co.th/en/ads/714tt8n087h2u9011310thcn3ulu1ea9"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Unexpected asset format: {path.name}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(f"window.{symbol} = {payload};\n", encoding="utf-8")


def sale_market() -> dict:
    sale_url = PH_SALE
    hipflat_url = HIPFLAT_SALE
    return {
        "count": 2,
        "observedCount": 2,
        "countKind": "manual_verified_listing",
        "average": 2875000,
        "minimum": 2800000,
        "minimumArea": 46.7,
        "averageSqm": 62044,
        "minimumSqm": 59957,
        "minimumSampleUpdated": AS_OF,
        "minimumSqmSampleUpdated": AS_OF,
        "asOf": AS_OF,
        "snapshotMethod": "PropertyHub project listing and direct unit page, cross-checked with the current Hipflat unit page",
        "sourceName": "PropertyHub + Hipflat 個別出售掛牌",
        "source": PH_PROJECT,
        "minimumSourceUrl": sale_url,
        "minimumSqmSourceUrl": sale_url,
        "byBedroom": {
            "2": {
                "count": 2,
                "minimum": 2800000,
                "area": 46.7,
                "priceSqm": 59957,
                "minimumSqm": 59957,
                "sourceUrl": sale_url,
                "minimumSqmSourceUrl": sale_url,
            }
        },
        "samples": [
            {
                "id": "6400243", "price": 2800000, "area": 46.7, "beds": 2,
                "roomType": "TWO_BED_ROOM", "updated": AS_OF,
                "title": "Le Rich Ratchada - Sutthisarn · 2 房 · 46.7 ㎡ · ฿2,800,000",
                "url": sale_url, "priceSqm": 59957, "sourceName": "PropertyHub",
                "projectName": ALIAS_PROJECT, "checkedAt": AS_OF,
                "matchedBy": "exact_shared_address_1224_Sutthisan_Winitchai_Rd_alias_project",
                "listingStatus": "active_as_listed",
            },
            {
                "id": "U6381636", "price": 2950000, "area": 46, "beds": 2,
                "roomType": "TWO_BED_ROOM", "updated": AS_OF,
                "title": "Boutique Le Rich Ratchada-Sutthisan · 2 房 · 46 ㎡ · ฿2,950,000",
                "url": hipflat_url, "priceSqm": 64130, "sourceName": "Hipflat",
                "projectName": PROJECT, "checkedAt": AS_OF,
                "matchedBy": "Hipflat_individual_listing_and_project_id_3654",
                "listingStatus": "active_as_listed",
            },
        ],
    }


def rent_market() -> dict:
    return {
        "count": 2,
        "observedCount": 2,
        "countKind": "manual_verified_listing",
        "average": 13500,
        "minimum": 13000,
        "minimumArea": 38,
        "averageSqm": 321,
        "minimumSqm": 300,
        "minimumSampleUpdated": "2026-10-11",
        "minimumSqmSampleUpdated": AS_OF,
        "asOf": AS_OF,
        "snapshotMethod": "PropertyHub exact-project rental listing and current Hipflat two-bedroom rental page",
        "sourceName": "PropertyHub + Hipflat 個別出租掛牌",
        "source": PH_PROJECT,
        "minimumSourceUrl": PH_RENT,
        "minimumSqmSourceUrl": HIPFLAT_RENT,
        "byBedroom": {
            "1": {
                "count": 1, "minimum": 13000, "area": 38,
                "minimumSqm": 13000 / 38, "averageSqm": 13000 / 38,
                "sourceUrl": PH_RENT, "minimumSqmSourceUrl": PH_RENT,
            },
            "2": {
                "count": 1, "minimum": 14000, "area": 46.7,
                "minimumSqm": 14000 / 46.7, "averageSqm": 14000 / 46.7,
                "sourceUrl": HIPFLAT_RENT, "minimumSqmSourceUrl": HIPFLAT_RENT,
            },
        },
        "samples": [
            {
                "id": "6246903", "price": 13000, "area": 38, "beds": 1,
                "roomType": "ONE_BED_ROOM", "updated": "2026-10-11",
                "title": "Le Rich Ratchada - Sutthisarn · 1 房 · 38 ㎡ · ฿13,000/月",
                "url": PH_RENT, "priceSqm": 342, "sourceName": "PropertyHub",
                "projectName": ALIAS_PROJECT, "checkedAt": AS_OF,
                "matchedBy": "exact_shared_address_1224_Sutthisan_Winitchai_Rd_alias_project",
                "listingStatus": "active_as_listed",
            },
            {
                "id": "U6867659", "price": 14000, "area": 46.7, "beds": 2,
                "roomType": "TWO_BED_ROOM", "updated": AS_OF,
                "title": "Boutique Le Rich Ratchada-Sutthisan · 2 房 · 46.7 ㎡ · ฿14,000/月",
                "url": HIPFLAT_RENT, "priceSqm": 14000 / 46.7, "sourceName": "Hipflat",
                "projectName": PROJECT, "checkedAt": AS_OF,
                "matchedBy": "Hipflat_individual_listing_and_project_id_3654",
                "listingStatus": "active_as_listed",
            },
        ],
    }


def update_project_map() -> None:
    common = {
        "lat": LAT,
        "lng": LNG,
        "completedYear": 2011,
        "units": 75,
        "floors": 9,
        "propertyHubProjectId": "1327",
        "propertyHubProjectUrl": PH_PROJECT,
        "locationVerified": True,
        "locationSourceUrl": PH_MAP,
        "locationSourceName": "PropertyHub Le Rich 專案地圖（同址別名）",
        "locationVerificationSourceUrl": HIPFLAT_PROJECT,
        "locationVerificationMethod": "Hipflat Boutique Le Rich page and PropertyHub Le Rich Ratchada-Sutthisarn page identify the same building address: 1224 Sutthisan Winitchai Rd., Ratchadaphisek, Din Daeng. The PropertyHub project map pin is used for coordinates; the address and project alias are cross-checked against Hipflat.",
    }
    path = DIST / "bangkok-propertyhub-map.js"
    rows = read_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    next(row for row in rows if int(row["id"]) == PROJECT_ID).update(common)
    write_array(path, "BANGKOK_PROPERTYHUB_PROJECTS", rows)

    # The walking-route builder reads the research projection while the app
    # reads the map projection. Keep both exact alias joins in sync.
    path = DIST / "bangkok-propertyhub.js"
    rows = read_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    row = next(row for row in rows if int(row["id"]) == PROJECT_ID)
    row.update(common)
    row["marketDataStatus"] = "manual_verified_sale_and_rent_alias_samples"
    write_array(path, "BANGKOK_PROPERTYHUB_PROJECTS", rows)


def update_manual_markets() -> None:
    path = DIST / "bangkok-manual-market-samples.js"
    rows = [row for row in read_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES") if int(row.get("hipflatId", -1)) != PROJECT_ID]
    rows.append({
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "sale": sale_market(),
        "rent": rent_market(),
        "replaceSale": True,
        "replaceRent": True,
        "marketMatchNote": "Hipflat ID 3654 and PropertyHub project ID 1327 are treated as same-building aliases only after matching the full 1224 Sutthisan Winitchai Rd address. Each sample remains linked to its individual listing page.",
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)


def update_cache_keys() -> None:
    path = DIST / "index.html"
    html = path.read_text(encoding="utf-8")
    for filename in ("bangkok-propertyhub-map", "bangkok-manual-market-samples", "bangkok-walk-routes"):
        html = re.sub(rf"{filename}\.js\?v=[^\"']+", f"{filename}.js?v=20261018w-boutique-le-rich-alias", html, count=1)
    path.write_text(html, encoding="utf-8")


def update_availability_report() -> None:
    path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF,
            "market": "sale", "status": "active_as_listed",
            "verification_note": "PropertyHub listing 6400243 shows 2 bedrooms, 46.7 sqm, ฿2,800,000; Hipflat listing U6381636 independently shows the same 2-bedroom project unit type. PropertyHub direct listing timestamp is 2026-10-18.",
            "source_1": PH_SALE, "source_2": HIPFLAT_SALE, "source_3": HIPFLAT_PROJECT,
        },
        {
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF,
            "market": "rent", "status": "active_as_listed",
            "verification_note": "Hipflat listing U6867659 shows 2 bedrooms, 46.7 sqm, ฿14,000/month and was updated today; PropertyHub listing 6246903 independently shows a 1-bedroom unit at ฿13,000/month, 38 sqm.",
            "source_1": HIPFLAT_RENT, "source_2": PH_RENT, "source_3": HIPFLAT_PROJECT,
        },
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (int(row["hipflat_id"]), row["market"])))


def write_report() -> None:
    monthly_rent = 14000
    area = 46.7
    price = 2800000
    annual_agent_adjusted_rent = monthly_rent * 11
    annual_fee = 35 * area * 12
    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "aliasMapping": {
            "propertyHubProjectId": "1327",
            "propertyHubName": ALIAS_PROJECT,
            "matchingAddress": "Le Rich Condominium Office, Le Rich Condominium, 1224 Sutthisan Winitchai Rd., Ratchadaphisek, Din Daeng, Bangkok 10400",
            "hipflatProjectUrl": HIPFLAT_PROJECT,
            "propertyHubProjectUrl": PH_PROJECT,
        },
        "location": {
            "latitude": LAT,
            "longitude": LNG,
            "verified": True,
            "coordinateSource": PH_MAP,
            "identityCrosscheck": HIPFLAT_PROJECT,
            "method": "PropertyHub project map for project ID 1327 provides the point; both Hipflat ID 3654 and PropertyHub ID 1327 show the exact same full 1224 Sutthisan Winitchai Rd address.",
        },
        "saleSamples": [
            {"price": 2800000, "areaSqm": 46.7, "bedrooms": 2, "url": PH_SALE},
            {"price": 2950000, "areaSqm": 46, "bedrooms": 2, "url": HIPFLAT_SALE},
        ],
        "rentSamples": [
            {"monthlyRent": 14000, "areaSqm": 46.7, "bedrooms": 2, "url": HIPFLAT_RENT},
            {"monthlyRent": 13000, "areaSqm": 38, "bedrooms": 1, "url": PH_RENT},
        ],
        "managementFee": {"rateBahtPerSqmPerMonth": 35, "source": PH_PROJECT, "status": "published_indicative"},
        "roi": {
            "status": "estimated_from_verified_two_bedroom_sale_and_rent_listings",
            "purchasePriceBaht": price,
            "areaSqm": area,
            "monthlyRentBaht": monthly_rent,
            "deductAgentOneMonth": True,
            "deductAnnualManagementFee": annual_fee,
            "netAnnualRoiPercent": round((annual_agent_adjusted_rent - annual_fee) / price * 100, 4),
            "formula": "(฿14,000 × 11 − ฿35 × 46.7 × 12) ÷ ฿2,800,000 × 100",
            "note": "One current two-bedroom rental sample was found; it is the room-type low point. Estimate excludes tax, repairs, vacancy and transaction costs.",
        },
        "walkingRoute": {"distanceKm": 0.254, "minutes": 3, "stationId": "BL17", "source": "Valhalla pedestrian routing"},
    }
    (REPORTS / "boutique-le-rich-alias-enrichment-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    update_project_map()
    update_manual_markets()
    update_cache_keys()
    update_availability_report()
    write_report()
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinatesVerified": True, "saleListings": 2, "rentListings": 2, "twoBedroomRoi": 4.7995}, ensure_ascii=False))


if __name__ == "__main__":
    main()
