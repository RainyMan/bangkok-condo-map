import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3007
PROJECT = "Panburi"
AS_OF = "2026-10-19"
PH_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-panburi"
PH_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-panburi"
PH_RENT_SAMPLE_URL = "https://propertyhub.in.th/en/listings/panburi-4-bedrooms-for-rent---3771788"
DD_RENT_URL = "https://www.ddproperty.com/en/property-for-rent/at-panburi-apartments-1311"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/panburi-iwhglk"
REALTORS_URL = "https://therealtors.net/project/Panburi-Apartments"
DOTPROPERTY_SALE_URL = "https://www.dotproperty.co.th/en/ads/4-bedroom-condo-for-sale-in-panburi-si-lom-bangkok_e1eeb47f63c7-6ed1-8da6-c64b-b9c108e4"
DD_PROJECT_URL = "https://www.ddproperty.com/en/project/1311-panburi-apartments"

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
        "sale": {
            "activeListingCount": 0,
            "sourceUrl": PH_SALE_URL,
            "note": "PropertyHub 出售專案頁為 0 筆；The Realtors 專案頁也列 0 間出售。DotProperty 找到一筆超過一年且價格異常的舊頁面，排除於目前出售樣本。",
        },
        "rent": {
            "activeListingCount": len(DD_LISTINGS),
            "sourceUrl": DD_RENT_URL,
            "listings": [{**row, "sourceName": "DDproperty", "priceSqm": round(row["price"] / row["area"], 2)}
                         for row in DD_LISTINGS],
        },
        "availabilitySources": [
            {"sourceName": "PropertyHub 出售專案頁", "url": PH_SALE_URL, "statusLabel": "目前 0 筆；未找到可核實出售掛牌。"},
            {"sourceName": "The Realtors 專案頁", "url": REALTORS_URL, "statusLabel": "專案頁目前列 0 間出售、1 間出租。"},
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT_URL, "statusLabel": "專案頁列出租庫存，未列現行出售房源。"},
            {"sourceName": "DotProperty 舊出售頁", "url": DOTPROPERTY_SALE_URL, "statusLabel": "頁面標示 4 房、450㎡，售價僅 ฿150,000（฿333/㎡），且來源已超過一年；與同物件฿165,000/月以上租金量級明顯衝突，不納入目前出售行情。"},
            {"sourceName": "PropertyHub 出租", "url": PH_RENT_SAMPLE_URL, "statusLabel": "1 筆連結樣本，฿160,000/月；更新日未提供"},
        ],
        "yieldStatus": "no_current_sale_listing",
        "yieldNote": "目前沒有可信且在架的本案出售樣本；陳舊異常售價已排除，沒有購入價基準可計算投報。",
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows)


def update_availability_report():
    output_path = REPORTS / "listing-availability-checks-2026-10-19.csv"
    source_path = output_path if output_path.exists() else REPORTS / "listing-availability-checks-2026-10-18.csv"
    with source_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        rows = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    rows.extend([
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "sale",
         "status": "no_current_matching_listing",
         "verification_note": "PropertyHub 專案出售頁為 0 筆、The Realtors 為 0 間出售，Hipflat 目前僅顯示租盤。DotProperty 一筆標價฿150,000/450㎡的頁面已超過一年，售價低於月租且異常，排除於現行售盤。沒有用鄰近 Condo 代替。",
         "source_1": PH_SALE_URL, "source_2": REALTORS_URL, "source_3": DOTPROPERTY_SALE_URL},
        {"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": "rent",
         "status": "current_project_listings_cross_checked",
         "verification_note": "DDproperty 專案出租頁列出 3 筆；三筆個別頁均為 4 房、450㎡、Panburi/133 Pan Rd，月租 ฿155,000、฿160,000、฿170,000，刊登日期 2026-10-02 至 2026-10-12。PropertyHub 另有 ฿160,000/450㎡ 連結樣本，可能為跨平台重複刊登，故不併入 DDproperty 交叉樣本數。刊登者未確認即時空置。",
         "source_1": DD_RENT_URL, "source_2": DD_LISTINGS[1]["url"], "source_3": PH_RENT_SAMPLE_URL},
    ])
    with output_path.open("w", encoding="utf-8-sig", newline="") as destination:
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
        "sale": {"status": "no_current_matching_listing", "sampleCount": 0, "source": PH_SALE_URL,
                 "crossChecks": [PH_SALE_URL, REALTORS_URL, HIPFLAT_URL],
                 "excludedHistoricalOutlier": {"url": DOTPROPERTY_SALE_URL, "askingPriceThb": 150000, "areaSqm": 450,
                                               "reason": "The page is over one year old and lists a sale price below the unit's monthly rent; excluded from current sale and yield baselines."}},
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
    (REPORTS / "panburi-market-enrichment-2026-10-19.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_asset_version():
    path = DIST / "index.html"
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r"bangkok-market-crosschecks\.js\?v=[^\"']+",
                     "bangkok-market-crosschecks.js?v=20261019-panburi-sale-audit", text)
    if updated == text and "bangkok-market-crosschecks.js?v=20261019-panburi-sale-audit" not in text:
        raise ValueError("Could not update cross-check cache key")
    path.write_text(updated, encoding="utf-8")

    coverage_path = REPORTS / "bangkok-coverage-2026-10-19.csv"
    with coverage_path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    fields = list(rows[0])
    for row in rows:
        if row["hipflat_id"] == str(PROJECT_ID):
            row["sale_source"] = PH_SALE_URL
            row["sale_availability_checked"] = "4"
            row["sale_availability_note"] = "PropertyHub 0; The Realtors 0; Hipflat no current sale; DotProperty >1y ฿150,000/450㎡ anomalous listing excluded."
            row["yield_status"] = "no_current_sale_listing"
            row["yield_note"] = "No reliable current sale listing; anomalous stale DotProperty asking price excluded."
            row["missing"] = "出售（已查核：無可信現行掛牌）；投報待售價"
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    update_crosschecks()
    update_availability_report()
    write_report()
    update_asset_version()
    print(json.dumps({"project": PROJECT, "hipflatId": PROJECT_ID,
                      "ddpropertyRentListings": len(DD_LISTINGS), "saleSamples": 0,
                      "saleAvailabilitySources": 4,
                      "yield": "not calculable without sale listing"}, ensure_ascii=False, indent=2))
