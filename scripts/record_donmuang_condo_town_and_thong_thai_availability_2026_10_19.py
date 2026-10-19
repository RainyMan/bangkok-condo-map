import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-10-19"


def read_js_array(path: Path, variable: str):
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{variable} ="
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected JavaScript data header in {path}")
    return json.loads(text[len(prefix):].strip().rstrip(";"))


def write_js_array(path: Path, variable: str, rows, indent=None):
    options = {"ensure_ascii": False}
    if indent is None:
        options["separators"] = (",", ":")
    else:
        options["indent"] = indent
    path.write_text(f"window.{variable} =" + json.dumps(rows, **options) + ";\n", encoding="utf-8")


def upsert_by_id(rows, hipflat_id, value):
    for index, row in enumerate(rows):
        if int(row.get("hipflatId", 0)) == hipflat_id:
            rows[index] = value
            return
    rows.append(value)


special_sale = {
    "id": "SAM-V199382",
    "price": 169000,
    "area": 31.04,
    "priceSqm": 5445,
    "beds": None,
    "roomType": None,
    "title": "SAM 管理資產出售 · Donmuang Condo Town · D 棟 84/391 · 31.04 ㎡",
    "url": "https://zmyhome.com/property/V199382",
    "sourceName": "SAM（泰國資產管理公司管理資產）",
    "projectName": "Donmuang Condo Town",
    "matchedBy": "exact_project_name_condominium_registration_and_unit_84_391",
    "sampleType": "bank_asset_sale",
    "specialAsset": True,
    "checkedAt": AS_OF,
    "listingStatus": "availability_unconfirmed_date_unknown",
    "statusNote": "ZmyHome 房源頁列 SAM 管理資產、D 棟 84/391、31.04 ㎡及 ฿169,000，頁面標示 Updated 但未列明更新日；需向 SAM 確認現況。僅作特殊資產來源線索，不併入一般售價或投報。",
}

manual = read_js_array(ROOT / "dist/bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
upsert_by_id(manual, 3088, {
    "hipflatId": 3088,
    "name": "Donmuang Condo Town",
    "completedYear": 1993,
    "completedYearSourceUrl": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717",
    "sale": {"samples": [special_sale]},
    "asOf": AS_OF,
})
write_js_array(ROOT / "dist/bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

crosschecks = read_js_array(ROOT / "dist/bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosschecks_3063 = next(row for row in crosschecks if int(row.get("hipflatId", 0)) == 3063)
crosschecks_3063["availabilitySources"] = [
    source for source in crosschecks_3063.get("availabilitySources", [])
    if source.get("url") != "https://zmyhome.com/buy/condo/project-list/13261"
]
historical_thong_thai_source = {
    "sourceName": "ZmyHome 個別售盤（歷史／未驗證）",
    "url": "https://zmyhome.com/property/V179791",
    "statusLabel": "個別房源頁列 1 房 30㎡ ฿360,000，但頁面約 5 個月前擷取且明示屋主尚未驗證、資訊可能過時；不列為現行出售樣本或投報基準。",
}
if historical_thong_thai_source["url"] not in {source.get("url") for source in crosschecks_3063.get("availabilitySources", [])}:
    crosschecks_3063.setdefault("availabilitySources", []).append(historical_thong_thai_source)

crosschecks_3088 = {
    "hipflatId": 3088,
    "projectName": "Donmuang Condo Town",
    "asOf": AS_OF,
    "sourceName": "Hipflat / PropertyHub / Dot Property",
    "projectSourceUrl": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks",
    "sale": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "sourceUrl": "https://propertyhub.in.th/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717",
        "checkedAt": AS_OF,
        "note": "一般市場出售頁無可核實掛牌；另有一筆 SAM 管理資產，獨立列為特殊資產。",
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "sourceUrl": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717",
        "checkedAt": AS_OF,
    },
    "availabilitySources": [
        {
            "sourceName": "Hipflat 專案頁",
            "url": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks",
            "statusLabel": "專案頁目前顯示無可用物件。",
        },
        {
            "sourceName": "PropertyHub 出售專案頁",
            "url": "https://propertyhub.in.th/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717",
            "statusLabel": "未列一般市場出售掛牌；SAM 管理資產另列，不混作一般售盤。",
        },
        {
            "sourceName": "PropertyHub 出租專案頁",
            "url": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717",
            "statusLabel": "專案頁及 Don Mueang 租屋索引均標示本案目前沒有出租掛牌。",
        },
        {
            "sourceName": "FazWaz 專案頁",
            "url": "https://www.fazwaz.co.th/en/projects/thailand/bangkok/don-mueang/don-mueang/donmuang-condo-town",
            "statusLabel": "專案頁顯示 No Units Available；周邊區域總數不視為本案售租數量。",
        },
        {
            "sourceName": "Dot Property 專案頁",
            "url": "https://www.dotproperty.co.th/en/condo/1414/donmuang-condo-town",
            "statusLabel": "頁面標題顯示 0 個出售及出租單位，專案敘述為 Soi Ploy Pailin–Sermpridi，5 層 4 棟、244 戶。",
        },
        {
            "sourceName": "SAM 管理資產單筆（ZmyHome）",
            "url": "https://zmyhome.com/property/V199382",
            "statusLabel": "D 棟 84/391、31.04㎡、฿169,000；頁面未列明更新日，現況待 SAM 確認，排除一般行情與投報。",
        },
    ],
    "yieldStatus": "not_calculated_special_asset_only_no_rent",
    "yieldNote": "目前無一般市場的可核實售租配對。SAM 管理資產掛牌未確認現況且無同案租金樣本，故只保留來源連結，不計投報。",
}
upsert_by_id(crosschecks, 3088, crosschecks_3088)
write_js_array(ROOT / "dist/bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks, indent=2)

coverage_path = ROOT / "reports/bangkok-coverage-2026-10-19.csv"
with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
    coverage = list(csv.DictReader(handle))
    coverage_fields = list(coverage[0].keys())
for row in coverage:
    if int(row["hipflat_id"]) == 3088:
        row.update({
            "sale_sample": "yes",
            "sale_market_value": "no",
            "sale_individual_listing_link": special_sale["url"],
            "sale_source": "SAM 管理資產（特殊掛牌）",
            "sale_availability_checked": AS_OF,
            "sale_availability_note": "SAM 管理資產房源 V199382：D 棟 84/391、31.04㎡、฿169,000；頁面未列明更新日，現況待確認。僅保留特殊資產連結，不納入一般市場均價或投報。",
            "rent_sample": "no",
            "rent_source": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717",
            "rent_availability_checked": AS_OF,
            "rent_availability_note": "PropertyHub、Hipflat、FazWaz 專案頁未列本案現行租盤；附近專案排除。",
            "yield_status": "not_calculated",
            "yield_note": "特殊資產售盤尚未確認現況，且無本案租盤，沒有可靠售租配對，不計投報。",
            "missing": "出售行情（僅特殊資產掛牌）, 出租",
        })
    elif int(row["hipflat_id"]) == 3063:
        row["sale_availability_note"] = "PropertyHub 出售頁及 Hipflat 專案頁目前無本案現行單筆售盤。ZmyHome 彙整頁曾顯示 1 房 30㎡ ฿360,000，但資料已爬取約 5 個月且未驗證屋主，排除。"

with coverage_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=coverage_fields)
    writer.writeheader()
    writer.writerows(coverage)

availability_path = ROOT / "reports/listing-availability-checks-2026-10-19.csv"
with availability_path.open(encoding="utf-8-sig", newline="") as handle:
    availability = list(csv.DictReader(handle))
    availability_fields = list(availability[0].keys())
availability = [row for row in availability if not (row["hipflat_id"] in {"3063", "3088"})]
availability.extend([
    {
        "hipflat_id": "3088", "condo": "Donmuang Condo Town", "checked_at": AS_OF,
        "market": "sale", "status": "special_asset_only_availability_unconfirmed",
        "verification_note": "Exact-project SAM-managed asset V199382 lists D building unit 84/391, 31.04 sqm, THB 169,000. Page says Updated but provides no update date; owner-managed asset page labels it SAM. Keep as special asset only; exclude from ordinary resale and yield.",
        "source_1": "https://zmyhome.com/property/V199382", "source_2": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks", "source_3": "https://www.dotproperty.co.th/en/condo/1414/donmuang-condo-town",
    },
    {
        "hipflat_id": "3088", "condo": "Donmuang Condo Town", "checked_at": AS_OF,
        "market": "rent", "status": "no_current_matching_listing",
        "verification_note": "Exact-project PropertyHub rental page, Hipflat project page, and FazWaz project page do not show a current rental unit. Nearby-project results excluded.",
            "source_1": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717", "source_2": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks", "source_3": "https://www.fazwaz.co.th/en/projects/thailand/bangkok/don-mueang/don-mueang/donmuang-condo-town",
    },
    {
        "hipflat_id": "3063", "condo": "Thong Thai Condominium", "checked_at": AS_OF,
        "market": "sale", "status": "no_current_matching_listing_historical_unverified_candidate_excluded",
        "verification_note": "PropertyHub exact-project sale page shows no listings and Hipflat says no available properties. ZmyHome project page retains a 1BR 30 sqm THB 360,000 listing but warns it may be inaccurate or outdated and is not owner-verified; page crawl is about five months old, so excluded from current sample.",
        "source_1": "https://propertyhub.in.th/en/condo-for-sale/project-thong-thai-condominium-3", "source_2": "https://www.hipflat.co.th/en/projects/thong-thai-condominium-zcpcep", "source_3": "https://zmyhome.com/property/V179791",
    },
    {
        "hipflat_id": "3063", "condo": "Thong Thai Condominium", "checked_at": AS_OF,
        "market": "rent", "status": "no_current_matching_listing",
        "verification_note": "PropertyHub exact-project rent page and Hipflat project page show no current matching rental listings. Nearby projects and old neighborhood rentals excluded.",
        "source_1": "https://propertyhub.in.th/en/condo-for-rent/project-thong-thai-condominium-3", "source_2": "https://www.hipflat.co.th/en/projects/thong-thai-condominium-zcpcep", "source_3": "https://zmyhome.com/property/V179791",
    },
])
with availability_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=availability_fields)
    writer.writeheader()
    writer.writerows(availability)

report = {
    "asOf": AS_OF,
    "project": {"hipflatId": 3088, "name": "Donmuang Condo Town", "hipflatProject": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks", "completedYear": 1993, "completedYearSource": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B9%8C---19717"},
    "coordinate": {"status": "already_verified", "source": "https://www.google.com/maps/search/?api=1&query=13.92020951%2C100.59302676", "latitude": 13.92020951, "longitude": 100.59302676},
    "sale": {"kind": "special_bank_asset", "priceTHB": 169000, "areaSqm": 31.04, "pricePerSqmTHB": 5445, "bedrooms": None, "unit": "Building D, unit 84/391", "source": "https://zmyhome.com/property/V199382", "manager": "SAM (Sukhumvit Asset Management)", "checkedAt": AS_OF, "availability": "The asset page says Updated but provides no date; contact SAM to confirm current status.", "decision": "Listed on the condo card under Special listings only, excluded from ordinary sale statistics and ROI."},
    "rent": {"status": "no_current_verified_listing", "checkedAt": AS_OF, "sources": ["https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717", "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks", "https://www.fazwaz.co.th/en/projects/thailand/bangkok/don-mueang/don-mueang/donmuang-condo-town"]},
    "yield": {"status": "not_calculated", "reason": "The only sale lead is a date-unconfirmed special bank asset, and no exact-project rent sample is available."},
    "crosschecks": [
        {"source": "Hipflat", "url": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks", "finding": "Current project page says no available properties."},
        {"source": "PropertyHub", "url": "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717", "finding": "No matched rent listings for the exact project."},
        {"source": "Dot Property", "url": "https://www.dotproperty.co.th/en/condo/1414/donmuang-condo-town", "finding": "Project page shows zero sale and rent listings; project description identifies Soi Ploy Pailin-Sermpridi, five-floor buildings, 244 units."},
    ],
}
(ROOT / "reports/donmuang-condo-town-special-asset-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

thong_thai_report = {
    "asOf": AS_OF,
    "project": {"hipflatId": 3063, "name": "Thong Thai Condominium", "projectNameOnPropertyHub": "Thong Thai Condominium 3", "hipflatProject": "https://www.hipflat.co.th/en/projects/thong-thai-condominium-zcpcep"},
    "sale": {
        "status": "no_current_verified_listing",
        "sources": [
            {"source": "PropertyHub exact-project sale page", "url": "https://propertyhub.in.th/en/condo-for-sale/project-thong-thai-condominium-3", "finding": "No matched properties for sale."},
            {"source": "Hipflat project page", "url": "https://www.hipflat.co.th/en/projects/thong-thai-condominium-zcpcep", "finding": "Currently no properties available."},
            {"source": "ZmyHome individual historical lead", "url": "https://zmyhome.com/property/V179791", "finding": "1BR, 30 sqm, THB 360,000 (THB 12,000/sqm); page crawl about five months old, owner not verified, and page warns details may be outdated. Excluded from current listing, sale floor and yield."},
        ],
    },
    "rent": {
        "status": "no_current_verified_listing",
        "sources": [
            {"source": "PropertyHub exact-project rent page", "url": "https://propertyhub.in.th/en/condo-for-rent/project-thong-thai-condominium-3", "finding": "No matched properties for rent."},
            {"source": "Hipflat project page", "url": "https://www.hipflat.co.th/en/projects/thong-thai-condominium-zcpcep", "finding": "Currently no properties available."},
        ],
    },
    "projectFacts": {"completedYear": 1994, "floors": 4, "buildings": 3, "units": 640, "source": "https://propertyhub.in.th/en/projects/thong-thai-condominium-3"},
    "yield": {"status": "not_calculated", "reason": "No current exact-project sale and rent samples are verified."},
}
(ROOT / "reports/thong-thai-condominium-availability-2026-10-19.json").write_text(json.dumps(thong_thai_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Updated Donmuang Condo Town special-asset evidence and Thong Thai historical-listing exclusion.")
