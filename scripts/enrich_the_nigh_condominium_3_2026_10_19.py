"""Verify The Nigh Condominium 3's exact location and linked market samples."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3386
PROJECT = "The Nigh Condominium 3"
AS_OF = "2026-10-19"

HIPFLAT = "https://www.hipflat.co.th/en/projects/the-nigh-condominium-3-zyrcjp"
HOME = "https://www.home.co.th/condo/the-nigh-condominium-3-4776"
PROPERTYHUB = "https://propertyhub.in.th/projects/the-nigh-condo-3-ngamwongwan---13152"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-the-nigh-condo-3-ngamwongwan---13152"
RENTCONDO_PROJECT = "https://rentcondobkk.com/index.php/%E0%B8%8B%E0%B8%B7%E0%B9%89%E0%B8%AD-%E0%B8%82%E0%B8%B2%E0%B8%A2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B9%80%E0%B8%94%E0%B8%AD%E0%B8%B0-%E0%B9%84%E0%B8%99%E0%B8%99%E0%B9%8C-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1-3"
SALE_1 = "https://rentcondobkk.com/index.php/%E0%B8%82%E0%B8%B2%E0%B8%A2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/115078/TNC08-0002"
SALE_2 = "https://rentcondobkk.com/index.php/%E0%B8%82%E0%B8%B2%E0%B8%A2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/95300/TNC08-0001"
RENT_SOLD = "https://www.rentcondobkk.com/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/95300/TNC08-0001"
ZMYHOME_SOLD = "https://zmyhome.com/property/V154571"
ZMYHOME_PROJECT = "https://zmyhome.com/project/V13155"
SCANCONDO = "https://www.scancondo.com/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B9%80%E0%B8%94%E0%B8%AD%E0%B8%B0-%E0%B9%84%E0%B8%99%E0%B8%99%E0%B9%8C-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1-3"
LAT, LNG = 13.8494207, 100.5590098
GOOGLE_MAPS = "https://goo.gl/maps/1webFX2ZxH6pZsTe6"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError(f"Unexpected array format in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict], *, pretty: bool = False) -> None:
    if pretty:
        payload = json.dumps(rows, ensure_ascii=False, indent=2)
    else:
        payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    (DIST / filename).write_text(
        f"window.{symbol} = {payload};\n",
        encoding="utf-8",
    )


def main() -> None:
    catalogue = read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    project = next(row for row in catalogue if int(row["id"]) == PROJECT_ID)
    project.update({
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "locationSourceUrl": GOOGLE_MAPS,
        "locationSourceName": "Google Maps 專案地點",
        "addressSourceUrl": HOME,
        "completedYear": 2014,
        "units": 70,
        "floors": 8,
        "area": {"min": 28.22, "max": 35.05},
        "address": "Ngamwongwan Road, Lat Yao, Chatuchak, Bangkok 10900, Thailand",
        "marketDataStatus": "two_sale_listings_observed_rent_unavailable",
        "sourceDescription": (
            "Google Maps exact place pin identifies The Nigh Condo 3 at the project address; "
            "Home.co.th independently confirms the project name and Ngamwongwan Road, Lat Yao, "
            "Chatuchak address. Home.co.th lists 70 units, 28.22–35.05 sqm; RentcondoBKK and "
            "Scancondo list 2014 completion and 8 floors. PropertyHub instead lists 2012 and 77 units, "
            "so completion year is retained as the majority-source value with the discrepancy recorded. "
            "Two individual 1-bedroom sale ads are observed on RentcondoBKK; update dates are absent. "
            "Its only exact-project rental ad says rented already, and PropertyHub shows zero current ads; "
            "no current rent or ROI is inferred."
        ),
    })
    completeness = dict(project.get("dataCompleteness") or {})
    completeness.update({"coordinates": True, "saleSample": True, "rentSample": False, "yield": False})
    project["dataCompleteness"] = completeness
    write_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", catalogue)

    coordinates = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
    coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
    coordinates.append({
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "sourceName": "Google Maps exact project place pin",
        "sourceUrl": GOOGLE_MAPS,
        "verificationSourceUrl": HOME,
        "corroborationSourceUrl": HIPFLAT,
        "verificationMethod": (
            "RentcondoBKK's project map link resolves to the Google Maps place named The Nigh Condo 3 "
            "at 13.8494207,100.5590098. Home.co.th independently identifies the exact Ngamwongwan Road, "
            "Lat Yao, Chatuchak project and Hipflat supplies the catalogue identity."
        ),
        "asOf": AS_OF,
    })
    coordinates.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinates)

    sale_samples = [
        {
            "url": SALE_1,
            "price": 1_650_000,
            "area": 29,
            "bedrooms": 1,
            "priceSqm": 56_896.55,
            "sourceName": "RentcondoBKK",
            "listingStatus": "availability_unconfirmed_date_unknown",
        },
        {
            "url": SALE_2,
            "price": 1_950_000,
            "area": 31,
            "bedrooms": 1,
            "priceSqm": 62_903.23,
            "sourceName": "RentcondoBKK",
            "listingStatus": "availability_unconfirmed_date_unknown",
        },
    ]
    manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    manual = [row for row in manual if int(row.get("hipflatId", -1)) != PROJECT_ID]
    manual.append({
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "replaceSale": True,
        "sale": {
            "count": 2,
            "observedCount": 2,
            "countKind": "manual_verified_listing",
            "average": 1_800_000,
            "minimum": 1_650_000,
            "minimumArea": 29,
            "minimumSourceUrl": SALE_1,
            "averageSqm": 59_899.89,
            "minimumSqm": 56_896.55,
            "minimumSqmSourceUrl": SALE_1,
            "asOf": AS_OF,
            "sourceName": "RentcondoBKK 單筆出售掛牌",
            "source": RENTCONDO_PROJECT,
            "byBedroom": {
                "1": {
                    "beds": 1,
                    "count": 2,
                    "minimum": 1_650_000,
                    "minimumArea": 29,
                    "area": 29,
                    "minimumSqm": 56_896.55,
                    "average": 1_800_000,
                    "averageSqm": 59_899.89,
                    "minimumSourceUrl": SALE_1,
                    "minimumSqmSourceUrl": SALE_1,
                    "sourceUrl": SALE_1,
                },
            },
            "samples": sale_samples,
        },
    })
    manual.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

    crosschecks = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
    crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != PROJECT_ID]
    crosschecks.append({
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "asOf": AS_OF,
        "sourceName": "RentcondoBKK / PropertyHub",
        "projectSourceUrl": RENTCONDO_PROJECT,
        "availabilitySources": [
            {"sourceName": "Google Maps 專案地點", "url": GOOGLE_MAPS, "statusLabel": "The Nigh Condo 3 地圖點位與名稱相符"},
            {"sourceName": "Home.co.th 專案頁", "url": HOME, "statusLabel": "確認 Ngamwongwan Road 地址、70 戶及 28.22–35.05 ㎡；未列完工年"},
            {"sourceName": "PropertyHub 專案頁", "url": PROPERTYHUB, "statusLabel": "目前顯示 0 售、0 租；資料列 2012 年、77 戶"},
            {"sourceName": "RentcondoBKK 專案頁", "url": RENTCONDO_PROJECT, "statusLabel": "目前列 2 筆出售、1 筆出租；出售掛牌未提供更新日"},
            {"sourceName": "RentcondoBKK 出租物件（已租出）", "url": RENT_SOLD, "statusLabel": "฿6,000／月、31 ㎡；頁面明示已租出，不作現行租金或投報樣本"},
            {"sourceName": "Zmyhome 已售物件", "url": ZMYHOME_SOLD, "statusLabel": "฿2.25M／28 ㎡，2023-11 已售；只作歷史參考"},
            {"sourceName": "Zmyhome 專案資料", "url": ZMYHOME_PROJECT, "statusLabel": "列 2014 年、70 戶、8 層及歷史管理費 ฿35／㎡／月；費用未核實，不納入試算"},
            {"sourceName": "Scancondo 專案資料", "url": SCANCONDO, "statusLabel": "列 2014 年、70 戶、8 層"},
        ],
        "sale": {"activeListingCount": 2, "sourceUrl": RENTCONDO_PROJECT, "listings": sale_samples},
        "rent": {"activeListingCount": 0, "sourceUrl": PROPERTYHUB, "listings": []},
        "yieldStatus": "not_calculated_no_current_exact_project_rent",
        "yieldNote": "目前有兩筆單房出售掛牌，但出租頁唯一的直接樣本已標示租出，PropertyHub 專案頁為 0 租盤；不以已租出或不同專案的租金計算投報。",
    })
    crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks, pretty=True)

    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "coordinates": {"status": "verified", "lat": LAT, "lng": LNG, "source": GOOGLE_MAPS, "corroboratingAddressSource": HOME},
        "projectDetails": {
            "address": "Ngamwongwan Road, Lat Yao, Chatuchak, Bangkok 10900",
            "units": 70,
            "floors": 8,
            "floorAreaSqm": [28.22, 35.05],
            "completionYear": 2014,
            "completionYearConflict": "PropertyHub lists 2012 and 77 units; Home.co.th, RentcondoBKK, Scancondo, and Zmyhome support 70 units/8 floors, with RentcondoBKK, Scancondo, and Zmyhome listing 2014.",
            "historicalCommonFee": {"rate": 35, "unit": "THB/sqm/month", "source": ZMYHOME_PROJECT, "status": "historical_unverified_not_applied"},
        },
        "sale": {"status": "two_direct_listings_observed_availability_unconfirmed", "samples": sale_samples},
        "rent": {
            "status": "no_verified_current_exact_project_rent",
            "currentSampleCount": 0,
            "source": PROPERTYHUB,
            "excludedListing": {"url": RENT_SOLD, "price": 6000, "area": 31, "bedrooms": 1, "status": "confirmed_unavailable_rented"},
        },
        "yield": {"status": "not_calculated", "reason": "No verified current exact-project rent sample; the only direct rental listing is marked rented."},
    }
    (REPORTS / "the-nigh-condominium-3-verification-2026-10-19.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    availability_path = REPORTS / "listing-availability-checks-2026-10-19.csv"
    with availability_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    sale_note = "RentcondoBKK exact-project page lists two sale ads. Direct pages show 1-bedroom units at ฿1,650,000/29 sqm and ฿1,950,000/31 sqm. Listing update dates and seller availability are not stated; use only as observed asking-price samples, not confirmed available inventory."
    rent_note = "PropertyHub exact-project page currently shows zero rentals. RentcondoBKK's only exact-project direct rental page lists ฿6,000/31 sqm but explicitly says the unit is rented; exclude it from current rent and ROI."
    rows.extend([
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "sale", "status": "listing_observed_availability_unconfirmed_date_unknown", "verification_note": sale_note, "source_1": SALE_1, "source_2": SALE_2, "source_3": RENTCONDO_PROJECT},
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "rent", "status": "no_current_matching_listing", "verification_note": rent_note, "source_1": PROPERTYHUB, "source_2": RENT_SOLD, "source_3": RENTCONDO_PROJECT},
    ])
    with availability_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (int(row["hipflat_id"]), row["market"])))

    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    versions = {
        "bangkok-catalogue.js": "20261019-thenigh-coordinates-sales",
        "bangkok-verified-coordinates.js": "20261019-thenigh-coordinates-sales",
        "bangkok-manual-market-samples.js": "20261019-thenigh-coordinates-sales",
        "bangkok-market-crosschecks.js": "20261019-thenigh-coordinates-sales",
        "app.js": "20261019-roi-recalc-v184",
    }
    for asset, version in versions.items():
        html, replacements = re.subn(
            rf"({re.escape(asset)}\?v=)[^\"']+",
            rf"\g<1>{version}",
            html,
            count=1,
        )
        if replacements != 1:
            raise ValueError(f"Could not update exactly one cache key for {asset}")
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": "verified", "saleSamples": 2, "currentRentSamples": 0, "yield": "not_calculated"}, ensure_ascii=True))


if __name__ == "__main__":
    main()
