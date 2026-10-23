"""Refresh direct rental evidence for four Bangkok condo projects."""

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKED = "2026-10-23"
COMMUNE_LISTING = "https://zmyhome.com/property/V75006"
COMMUNE_PH_RENT = "https://propertyhub.in.th/en/projects/commune-80-lat-phrao"
LIFE_RENT = "https://assets3.propertyhub.in.th/EN/projects/life-udomsuk-station/for-rent"
LIFE_OVERVIEW = "https://asset-direct-next.propertyhub.in.th/en/projects/life-udomsuk-station"
LIFE_DD = "https://www.ddproperty.com/en/project/14519-life-udomsuk-station"
NIGH_PH = "https://propertyhub.in.th/projects/the-nigh-condo-3-ngamwongwan---13152"
NIGH_RENT = "https://www.rentcondobkk.com/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/95300/TNC08-0001"
DONMUANG_PH = "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%94%E0%B8%AD%E0%B8%99%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C---19717"


def read_array(filename: str, variable: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Missing {variable} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{variable}=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def by_id(rows: list[dict], project_id: int) -> dict:
    return next(row for row in rows if int(row.get("hipflatId", -1)) == project_id)


def add_source(row: dict, source_name: str, url: str, status: str) -> None:
    sources = row.setdefault("availabilitySources", [])
    existing = next((source for source in sources if source.get("url") == url), None)
    value = {"sourceName": source_name, "url": url, "statusLabel": status}
    if existing:
        existing.update(value)
    else:
        sources.append(value)


manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
commune = by_id(manual, 3412)
if commune.get("name") != "Commune 80":
    raise ValueError("Hipflat project 3412 no longer maps to Commune 80")

rent_sample = {
    "id": "ZMY-V75006",
    "price": 15000,
    "area": 70,
    "priceSqm": 214.29,
    "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Commune 80 · 2 房 · 70 ㎡ · ฿15,000/月",
    "url": COMMUNE_LISTING,
    "sourceName": "ZmyHome",
    "projectName": "Commune 80",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_and_ladprao_80_yaek_22_address",
    "listingStatus": "availability_unconfirmed_date_unknown",
    "statusNote": "單筆頁列 Commune 80、2 房、70㎡、฿15,000/月，頁面顯示 Updated 但未提供更新日期。PropertyHub 專案出租頁仍顯示 0 筆；保留直連樣本並標示現況待確認，投報只作未確認掛牌估算。",
}
rent_market = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_direct_listing_date_unknown",
    "average": 15000,
    "minimum": 15000,
    "minimumArea": 70,
    "minimumSampleUpdated": None,
    "averageSqm": 214.29,
    "minimumSqm": 214.29,
    "asOf": CHECKED,
    "sourceName": "ZmyHome 單筆出租掛牌（更新日不明）",
    "source": COMMUNE_LISTING,
    "minimumSourceUrl": COMMUNE_LISTING,
    "minimumSqmSourceUrl": COMMUNE_LISTING,
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": 15000,
            "area": 70,
            "minimumArea": 70,
            "minimumSqm": 214.29,
            "averageSqm": 214.29,
            "sourceUrl": COMMUNE_LISTING,
            "minimumSourceUrl": COMMUNE_LISTING,
            "minimumSqmSourceUrl": COMMUNE_LISTING,
        }
    },
    "samples": [rent_sample],
}
commune["rent"] = rent_market
commune["replaceRent"] = True
commune["asOf"] = CHECKED

crosschecks = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")

commune_crosscheck = by_id(crosschecks, 3412)
commune_crosscheck["asOf"] = CHECKED
commune_crosscheck.setdefault("rent", {}).update({
    "activeListingCount": 0,
    "sourceUrl": COMMUNE_PH_RENT,
    "checkedAt": CHECKED,
    "note": "PropertyHub 本案出租頁為 0 筆。另找到 ZmyHome 一筆精確 2 房、70㎡、฿15,000/月直連掛牌；頁面標示 Updated 但沒有日期，暫列現況待確認樣本，只供條件式投報估算。",
})
add_source(
    commune_crosscheck,
    "ZmyHome 2 房出租單筆",
    COMMUNE_LISTING,
    "精確地址及專案名稱相符；列 2 房、70㎡、฿15,000/月。頁面標示 Updated，未提供更新日期；PropertyHub 專案出租頁同時顯示 0 筆。現況待確認。",
)
commune_crosscheck["roi"] = {
    "status": "estimated_from_date_unconfirmed_2br_rental",
    "reason": "2 房最低售價樣本與最低月租樣本皆為 70㎡；售盤最低總價 ฿2,989,000、租金 ฿15,000/月。租盤日期不明且 PropertyHub 無租盤，投報僅作條件式估算。",
}
commune_crosscheck["yieldStatus"] = "calculated_estimate"
commune_crosscheck["yieldNote"] = "以 2 房最低出售掛牌 ฿2,989,000／70㎡ 和最低月租 ฿15,000／70㎡估算，因兩者面積相同而直接使用月租；租盤更新日期不明、現況未確認，投報率僅供條件式比較。"

life = by_id(crosschecks, 3468)
life["asOf"] = CHECKED
life.setdefault("rent", {}).update({
    "activeListingCount": 0,
    "sourceUrl": LIFE_RENT,
    "checkedAt": CHECKED,
    "note": "PropertyHub 專案出租結果頁目前顯示 No matched properties for Rent；DDproperty 顯示 0 間出租。新版 PropertyHub 專案摘要雖顯示 1 筆，但其租賃結果頁沒有單筆房源連結，因此不作租金樣本或投報基準。",
})
add_source(life, "PropertyHub 專案出租結果（2026-10-23 核對）", LIFE_RENT,
           "直接租賃結果頁顯示 No matched properties for Rent；沒有個別租盤可點。")
add_source(life, "PropertyHub 新版專案摘要", LIFE_OVERVIEW,
           "摘要列 1 筆出租，但連結到出租結果頁後為 0 筆，沒有個別房源頁；不計入租金樣本。")
add_source(life, "DDproperty 專案頁", LIFE_DD,
           "專案頁顯示 0 間出租；未找到可核實的本案出租單筆。")
life["roi"] = {
    "status": "not_calculable_no_direct_rental_listing",
    "reason": "PropertyHub 租賃結果頁與 DDproperty 專案頁均未提供可核實的本案出租單筆；新版摘要的 1 筆數量沒有對應物件頁。",
}
life["yieldStatus"] = "not_calculable_no_current_exact_project_rent"
life["yieldNote"] = "沒有可點開的本案現行出租單筆；PropertyHub 租賃結果頁及 DDproperty 顯示 0 筆，摘要數量不明不作投報基準。"

nigh = by_id(crosschecks, 3386)
nigh["asOf"] = CHECKED
nigh.setdefault("rent", {}).update({
    "activeListingCount": 0,
    "sourceUrl": NIGH_PH,
    "checkedAt": CHECKED,
    "note": "PropertyHub exact-project page currently shows 0 rent listings. RentcondoBKK has a matching 1 房、31㎡ unit page, but it explicitly says rented; excluded from current rent and ROI.",
})
add_source(nigh, "PropertyHub exact-project rent result", NIGH_PH,
           "專案頁顯示 0 筆出租（2026-10-23 核對）。")
add_source(nigh, "RentcondoBKK 直接租盤（已租）", NIGH_RENT,
           "精確專案單筆頁列 1 房、31㎡、฿6,000/月，頁面明示已租出；排除現行租金與投報。")
nigh["roi"] = {
    "status": "not_calculable_no_current_rental_listing",
    "reason": "已找到的精確單筆出租頁明示已租，PropertyHub 專案頁顯示 0 筆出租；沒有現行租盤基準。",
}
nigh["yieldStatus"] = "not_calculated_no_current_rent_listing"
nigh["yieldNote"] = "PropertyHub 專案頁顯示 0 筆出租；唯一核對到的精確出租單筆明示已租，不納入投報。"

donmuang = by_id(crosschecks, 3088)
donmuang.setdefault("rent", {}).update({
    "activeListingCount": 0,
    "sourceUrl": DONMUANG_PH,
    "checkedAt": CHECKED,
    "note": "PropertyHub 精確專案出租頁於 2026-10-23 直接核對，顯示沒有出租掛牌；Hipflat 專案頁近期亦顯示無可用物件。附近樓盤不移作本案租盤。",
})
donmuang["asOf"] = CHECKED
add_source(donmuang, "PropertyHub 出租專案頁（2026-10-23 核對）", DONMUANG_PH,
           "精確專案頁目前顯示沒有出租掛牌；Don Mueang 區域結果未當作本案租盤。")

write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)
write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

availability_checks = [
    {
        "hipflat_id": "3412", "condo": "Commune 80", "checked_at": CHECKED, "market": "rent",
        "status": "direct_listing_date_unknown_unconfirmed",
        "verification_note": "ZmyHome exact-project owner listing states 2BR, 70 sqm, THB 15,000/month; the page shows an Updated badge but no date. PropertyHub exact-project rental result page shows 0. Kept as a date-unconfirmed direct sample; yield is conditional, not confirmed availability.",
        "source_1": COMMUNE_LISTING, "source_2": COMMUNE_PH_RENT,
        "source_3": "https://www.hipflat.co.th/en/projects/commune-80-ohmrsq",
    },
    {
        "hipflat_id": "3468", "condo": "LIFE Udomsuk Station", "checked_at": CHECKED, "market": "rent",
        "status": "no_current_individual_rental_listing",
        "verification_note": "PropertyHub exact-project rent page says no matched properties and DDproperty shows 0 units to rent. New PropertyHub overview count of 1 has no corresponding unit on its direct rent-results page; no rent sample or yield added.",
        "source_1": LIFE_RENT, "source_2": LIFE_DD, "source_3": LIFE_OVERVIEW,
    },
    {
        "hipflat_id": "3386", "condo": "The Nigh Condominium 3", "checked_at": CHECKED, "market": "rent",
        "status": "no_current_rental_listing_matching_direct_unit_marked_rented",
        "verification_note": "PropertyHub exact-project page shows 0 rent listings. Exact project RentcondoBKK unit page lists 1BR, 31 sqm, THB 6,000/month but explicitly labels the unit rented; excluded from rent baseline and yield.",
        "source_1": NIGH_PH, "source_2": NIGH_RENT,
        "source_3": "https://www.hipflat.co.th/en/projects/the-nigh-condominium-3-zyrcjp",
    },
    {
        "hipflat_id": "3088", "condo": "Donmuang Condo Town", "checked_at": CHECKED, "market": "rent",
        "status": "no_current_matching_listing",
        "verification_note": "Live PropertyHub exact-project rent page currently says no rental listings. Hipflat project page also reports no available property; nearby projects excluded.",
        "source_1": DONMUANG_PH,
        "source_2": "https://www.hipflat.co.th/projects/donmuang-condo-town-lgkhks",
        "source_3": "https://www.fazwaz.co.th/en/projects/thailand/bangkok/don-mueang/don-mueang/donmuang-condo-town",
    },
]
report = {
    "checkedAt": CHECKED,
    "scope": "Direct rental sample and availability refresh; no frontend changes.",
    "projects": availability_checks,
    "commune80RentSample": {
        "hipflatId": 3412, "name": "Commune 80", "bedrooms": 2, "monthlyRentTHB": 15000,
        "areaSqm": 70, "rentPerSqmTHB": 214.29, "source": COMMUNE_LISTING,
        "availability": "Listing remains visible and displays Updated; the update date is not provided; current availability is unconfirmed.",
        "calculation": "The mapped lowest 2BR resale unit is 70 sqm; the rent unit is also 70 sqm, so the ROI calculation uses the full THB 15,000 monthly rent without area scaling.",
        "projectSaleBaseline": {"priceTHB": 2989000, "areaSqm": 70,
                                "source": "https://propertyhub.in.th/listings/pet-friendly-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-commune-80-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-80-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88%E0%B8%AA%E0%B8%B8%E0%B8%94-%E0%B8%97%E0%B8%B1%E0%B9%89%E0%B8%87%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%A1%E0%B8%B5%E0%B9%81%E0%B8%84%E0%B9%88-20-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87-%E0%B9%80%E0%B8%A5%E0%B8%B5%E0%B9%89%E0%B8%A2%E0%B8%87%E0%B8%AA%E0%B8%B1%E0%B8%95%E0%B8%A7%E0%B9%8C%E0%B9%84%E0%B8%94%E0%B9%89-%E0%B9%80%E0%B8%9B%E0%B8%B4%E0%B8%94%E0%B9%80%E0%B8%9C%E0%B8%A2---6087703"},
    },
}
(ROOT / "reports/condo-rental-checks-2026-10-23.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

csv_path = ROOT / "reports/listing-availability-checks-2026-10-23.csv"
fields = ["hipflat_id", "condo", "checked_at", "market", "status", "verification_note", "source_1", "source_2", "source_3"]
with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(availability_checks)

print(json.dumps({"updatedProjects": [3412, 3468, 3386, 3088], "rentSample": rent_sample,
                  "report": str(csv_path.relative_to(ROOT))}, ensure_ascii=True))
