import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3009
PROJECT = "Ruam Rudee Penthouse"
AS_OF = "2026-10-18"
HIPFLAT_PROJECT = "https://www.hipflat.co.th/en/projects/ruam-rudee-penthouse-lvukdc"
HIPFLAT_RENT = "https://www.hipflat.co.th/en/ads/4lh747ac878a4c1318hh3hc83u0heue7"
BKK_FINDER = "https://www.bkkfinder.com/en/project/60l8p8x/ruam-rudee-penthouse"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=13.73742%2C100.54896"
DD_PROJECT = "https://www.ddproperty.com/en/project/8486-ruamrudee-penthouse"
DD_SALE = "https://www.ddproperty.com/en/condo-for-sale/at-ruamrudee-penthouse-8486"
DD_RENT = "https://www.ddproperty.com/en/condo-for-rent/at-ruamrudee-penthouse-8486"
DD_RENT_295 = "https://www.ddproperty.com/en/property/ruamrudee-penthouse-bangkok-for-rent-500560313"
DD_RENT_300 = "https://www.ddproperty.com/en/property/ruamrudee-penthouse-bangkok-for-rent-500174798"


def read_array(path, symbol):
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError(f"Unexpected asset format: {path.name}")
    return json.loads(match.group(1))


def write_array(path, symbol, rows, compact=False):
    body = json.dumps(rows, ensure_ascii=False, separators=(",", ":") if compact else None,
                      indent=None if compact else 2)
    path.write_text(f"window.{symbol} = {body};\n", encoding="utf-8")


def update_manual_market():
    path = DIST / "bangkok-manual-market-samples.js"
    rows = read_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    row = next((item for item in rows if int(item.get("hipflatId", -1)) == PROJECT_ID), None)
    if row is None:
        row = {"hipflatId": PROJECT_ID, "name": PROJECT}
        rows.append(row)
    hipflat_sample = {
        "id": "U1124970", "price": 120000, "area": 300, "priceSqm": 400,
        "beds": 3, "roomType": "3BR", "title": "Ruam Rudee Penthouse · 3 房 · 300 ㎡ · ฿120,000/月",
        "url": HIPFLAT_RENT, "sourceName": "Hipflat", "projectName": PROJECT,
        "updated": AS_OF, "checkedAt": AS_OF, "matchedBy": "exact_project_name_listing_and_address",
        "listingStatus": "active_as_listed",
    }
    dd_sample = {
        "id": "500560313", "price": 120000, "area": 295, "priceSqm": 407,
        "beds": 3, "roomType": "3BR", "title": "Ruamrudee Penthouse · 3 房 · 295 ㎡ · ฿120,000/月",
        "url": DD_RENT_295, "sourceName": "DDproperty", "projectName": PROJECT,
        "updated": "2026-10-18", "checkedAt": AS_OF, "matchedBy": "exact_project_name_and_address",
        "listingStatus": "active_as_listed",
    }
    row["rent"] = {
        "count": 2, "observedCount": 2, "countKind": "manual_verified_listing",
        "average": 120000, "minimum": 120000, "minimumArea": 300,
        "minimumSampleUpdated": AS_OF, "averageSqm": 403.39, "minimumSqm": 400,
        "minimumSqmSampleUpdated": AS_OF, "asOf": AS_OF,
        "sourceName": "DDproperty + Hipflat 個別租盤",
        "source": DD_RENT,
        "minimumSourceUrl": HIPFLAT_RENT, "minimumSqmSourceUrl": HIPFLAT_RENT,
        "byBedroom": {"3": {
            "count": 2, "minimum": 120000, "area": 300, "priceSqm": 400, "minimumSqm": 400,
            "sourceUrl": HIPFLAT_RENT, "minimumSqmSourceUrl": HIPFLAT_RENT,
        }},
        "samples": [dd_sample, hipflat_sample],
    }
    rows.sort(key=lambda item: int(item.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows, compact=True)


def update_crosscheck():
    path = DIST / "bangkok-market-crosschecks.js"
    rows = read_array(path, "BANGKOK_MARKET_CROSSCHECKS")
    row = next(item for item in rows if int(item.get("hipflatId", -1)) == PROJECT_ID)
    row.update({
        "asOf": AS_OF,
        "sourceName": "DDproperty",
        "projectSourceUrl": DD_PROJECT,
        "sale": {"activeListingCount": 0, "sourceUrl": DD_SALE},
        "rent": {
            "activeListingCount": 2,
            "sourceUrl": DD_RENT,
            "listings": [
                {"id": "500174798", "price": 120000, "area": 300, "priceSqm": 400, "bedrooms": 3,
                 "listedAt": "2026-09-17", "url": DD_RENT_300, "sourceName": "DDproperty",
                 "potentialCrossPost": True},
                {"id": "500560313", "price": 120000, "area": 295, "priceSqm": 407, "bedrooms": 3,
                 "listedAt": AS_OF, "url": DD_RENT_295, "sourceName": "DDproperty"},
            ],
        },
        "availabilitySources": [
            {"sourceName": "Hipflat 租盤", "url": HIPFLAT_RENT,
             "statusLabel": "1 筆 3 房／300㎡／฿120,000/月，頁面顯示更新於 2026-10-18"},
            {"sourceName": "BKK Finder 座標與專案", "url": BKK_FINDER,
             "statusLabel": "Google Maps 導向座標 13.73742,100.54896；所示 ฿13.5M 為資料頁參考價，不當作售屋掛牌"},
        ],
    })
    rows.sort(key=lambda item: int(item.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows)


def update_availability_csv():
    path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        rows = [item for item in reader if not (item["hipflat_id"] == str(PROJECT_ID) and item["market"] in {"sale", "rent"})]
    rows.extend([
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "sale",
         "status": "no_current_matching_listing",
         "verification_note": "DDproperty 專案頁列出售 0 筆，DDproperty 專案出售頁 FAQ 亦列出售 0 筆。BKK Finder 頁面提供的 ฿13.5M 為參考價，不是可點回的出售掛牌，故不納入樣本或投報。",
         "source_1": DD_PROJECT, "source_2": DD_SALE, "source_3": BKK_FINDER},
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "rent",
         "status": "current_listing_cross_checked",
         "verification_note": "Hipflat 個別掛牌：3 房、300㎡、฿120,000/月，更新於 2026-10-18；DDproperty 專案頁列 2 筆，另有 3 房、295㎡、฿120,000/月掛牌於 2026-10-18。DDproperty 的 300㎡／฿120,000 項目與 Hipflat 房源規格完全相同，視為疑似跨站重複，只將 Hipflat 300㎡與 DDproperty 295㎡兩筆列入每㎡樣本；未向刊登者確認空置。",
         "source_1": HIPFLAT_RENT, "source_2": DD_RENT_295, "source_3": DD_RENT},
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda item: (int(item["hipflat_id"]), item["market"])))


def write_report():
    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "location": {"status": "verified", "latitude": 13.73742, "longitude": 100.54896,
                     "googleMaps": MAP_URL, "projectIdentity": HIPFLAT_PROJECT,
                     "corroboratingSource": BKK_FINDER},
        "completion": {"year": 1983, "source": HIPFLAT_PROJECT},
        "sale": {"status": "no_current_matching_listing", "sampleCount": 0,
                 "ddpropertyProject": DD_PROJECT, "ddpropertySalePage": DD_SALE,
                 "excludedReferencePrice": {"priceThb": 13500000, "source": BKK_FINDER,
                                             "reason": "reference/assessment page, not an individual resale listing"}},
        "rent": {
            "status": "two_cross_checked_samples",
            "uniqueSampleCount": 2,
            "minimumThbPerSqmMonth": 400,
            "samples": [
                {"source": "Hipflat", "monthlyRentThb": 120000, "areaSqm": 300, "bedrooms": 3,
                 "thbPerSqmMonth": 400, "url": HIPFLAT_RENT, "updated": AS_OF},
                {"source": "DDproperty", "monthlyRentThb": 120000, "areaSqm": 295, "bedrooms": 3,
                 "thbPerSqmMonth": 407, "url": DD_RENT_295, "listedAt": AS_OF},
            ],
            "ddpropertyProjectCount": 2,
            "potentialDuplicate": {"url": DD_RENT_300, "reason": "Same 3BR, 300㎡ and ฿120,000 asking rent as the Hipflat listing; omitted from unique-sample metrics."},
            "availabilityCaveat": "Listings are shown as active on source pages; advertiser vacancy has not been confirmed.",
        },
        "yield": {"status": "not_calculable", "reason": "No current individual resale listing is available for a purchase-price baseline."},
    }
    (REPORTS / "ruam-rudee-penthouse-market-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_cache_keys():
    path = DIST / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"bangkok-manual-market-samples\.js\?v=[^\"']+",
                  "bangkok-manual-market-samples.js?v=20261018t-ruam-rudee-rent-samples", text)
    text = re.sub(r"bangkok-market-crosschecks\.js\?v=[^\"']+",
                  "bangkok-market-crosschecks.js?v=20261018d-ruam-rudee-current-listings", text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    update_manual_market()
    update_crosscheck()
    update_availability_csv()
    write_report()
    update_cache_keys()
    print(json.dumps({"project": PROJECT, "hipflatId": PROJECT_ID, "verifiedRentSamples": 2,
                      "minimumRentThbPerSqmMonth": 400, "saleSamples": 0,
                      "yield": "not calculable"}, ensure_ascii=False, indent=2))
