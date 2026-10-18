import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3007
PROJECT = "Panburi"
AS_OF = "2026-10-18"
PH_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-panburi"
PH_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-panburi"
PH_RENT_SAMPLE_URL = "https://propertyhub.in.th/en/listings/panburi-4-bedrooms-for-rent---3771788"
DD_RENT_URL = "https://www.ddproperty.com/en/property-for-rent/at-panburi-apartments-1311"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/panburi-iwhglk"

DD_LISTINGS = [
    {"listingId": "500429267", "price": 170000, "area": 450, "bedrooms": 4,
     "listedAt": "2026-10-12", "url": "https://www.ddproperty.com/en/property/panburi-apartments-bangkok-for-rent-500429267"},
    {"listingId": "500614034", "price": 155000, "area": 450, "bedrooms": 4,
     "listedAt": "2026-10-02", "url": "https://www.ddproperty.com/en/property/panburi-apartments-bangkok-for-rent-500614034"},
    {"listingId": "500431182", "price": 160000, "area": 450, "bedrooms": 4,
     "listedAt": "2026-09-22", "url": "https://www.ddproperty.com/en/property/panburi-apartments-bangkok-for-rent-500431182"},
]


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


def update_crosschecks():
    path = DIST / "bangkok-market-crosschecks.js"
    rows = read_array(path, "BANGKOK_MARKET_CROSSCHECKS")
    record = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if record is None:
        record = {"hipflatId": PROJECT_ID, "projectName": PROJECT}
        rows.append(record)
    record.update({
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "asOf": AS_OF,
        "sourceName": "DDproperty",
        "projectSourceUrl": DD_RENT_URL,
        "rent": {
            "activeListingCount": len(DD_LISTINGS),
            "sourceUrl": DD_RENT_URL,
            "listings": [{**row, "sourceName": "DDproperty", "priceSqm": round(row["price"] / row["area"], 2)}
                         for row in DD_LISTINGS],
        },
        "availabilitySources": [
            {"sourceName": "PropertyHub 出售", "url": PH_SALE_URL, "statusLabel": "目前 0 筆；未找到可核實出售掛牌"},
            {"sourceName": "PropertyHub 出租", "url": PH_RENT_SAMPLE_URL, "statusLabel": "1 筆連結樣本，฿160,000/月；更新日未提供"},
            {"sourceName": "Hipflat", "url": HIPFLAT_URL, "statusLabel": "專案頁顯示目前租盤，未見出售樣本"},
        ],
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows)


def update_availability_report():
    path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "sale",
         "status": "no_current_matching_listing",
         "verification_note": "PropertyHub 專案出售頁顯示 No matched properties for Sale；Hipflat 專案頁目前列出租盤，未核對到出售物件。沒有用鄰近 Condo 代替。",
         "source_1": PH_SALE_URL, "source_2": HIPFLAT_URL, "source_3": ""},
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "rent",
         "status": "current_project_listings_cross_checked",
         "verification_note": "DDproperty 專案出租頁列出 3 筆；三筆個別頁均為 4 房、450㎡、Panburi/133 Pan Rd，月租 ฿155,000、฿160,000、฿170,000，刊登日期 2026-10-02 至 2026-10-12。PropertyHub 另有 ฿160,000/450㎡ 連結樣本，可能為跨平台重複刊登，故不併入 DDproperty 交叉樣本數。刊登者未確認即時空置。",
         "source_1": DD_RENT_URL, "source_2": DD_LISTINGS[1]["url"], "source_3": PH_RENT_SAMPLE_URL},
    ])
    with path.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (int(row["hipflat_id"]), row["market"])))


def write_report():
    project_rows = read_array(DIST / "bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    project = next(row for row in project_rows if int(row["id"]) == PROJECT_ID)
    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "coordinates": {
            "status": "verified",
            "latitude": project["lat"],
            "longitude": project["lng"],
            "source": project.get("locationSourceUrl"),
            "crossCheck": HIPFLAT_URL,
        },
        "completion": {"year": 2002, "source": HIPFLAT_URL},
        "sale": {"status": "no_current_matching_listing", "sampleCount": 0, "source": PH_SALE_URL},
        "rent": {
            "status": "current_project_listings_cross_checked",
            "propertyHubSample": {"monthlyRentThb": 160000, "areaSqm": 450, "bedrooms": 4, "url": PH_RENT_SAMPLE_URL,
                                  "lastUpdate": "2026-10-17T02:48:52.624Z"},
            "ddpropertyActiveListingCount": len(DD_LISTINGS),
            "ddpropertyListings": [{**row, "rentThbPerSqmMonth": round(row["price"] / row["area"], 2)} for row in DD_LISTINGS],
            "ddpropertyProjectSource": DD_RENT_URL,
            "deduplicationNote": "The ฿160,000/450㎡ PropertyHub ad may cross-post the DDproperty ฿160,000/450㎡ unit; platform feeds are kept separate and are not added together.",
            "availabilityCaveat": "Listings are visible on project feeds; the advertisers have not confirmed current vacancy.",
        },
        "yield": {"status": "not_calculable", "reason": "No verified current sale listing is available for a purchase-price baseline."},
    }
    (REPORTS / "panburi-market-enrichment-2026-10-18.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_asset_version():
    path = DIST / "index.html"
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r"bangkok-market-crosschecks\.js\?v=[^\"']+",
                     "bangkok-market-crosschecks.js?v=20261018c-panburi-dd-rent", text)
    if updated == text and "bangkok-market-crosschecks.js?v=20261018c-panburi-dd-rent" not in text:
        raise ValueError("Could not update cross-check cache key")
    path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    update_crosschecks()
    update_availability_report()
    write_report()
    update_asset_version()
    print(json.dumps({"project": PROJECT, "hipflatId": PROJECT_ID,
                      "ddpropertyRentListings": len(DD_LISTINGS), "saleSamples": 0,
                      "yield": "not calculable without sale listing"}, ensure_ascii=False, indent=2))
