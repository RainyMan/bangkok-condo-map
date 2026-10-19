"""Add verified coordinates and source-linked rental listings for The Great Condo Petchkasem 48."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3175
PROJECT_NAME = "The Great Condo Petchkasem 48"
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/the-great-condo-petchkasem-48-jvfwpo"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/the-great-condo"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-the-great-condo"
DDPROPERTY_PROJECT = "https://www.ddproperty.com/en/project/9755-the-great-condo-petchkasem-48"
RENTCONDO_PROJECT = "https://rentcondobkk.com/index.php/เช่าคอนโด/เดอะเกรท-คอนโด-เพชรเกษม-48"
RENTCONDO_BASE = "https://rentcondobkk.com/index.php/ให้เช่า/คอนโด"
COORDINATE_SOURCE = RENTCONDO_PROJECT
COORDINATE_CHECK = "https://www.condonayoo.com/the-great-condo-petchkasem-48/"


def load_js_array(path: Path, variable: str) -> tuple[str, list[dict], str]:
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JS array format: {path}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_js_array(path: Path, prefix: str, rows: list[dict], suffix: str) -> None:
    path.write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix, encoding="utf-8")


def upsert(rows: list[dict], record: dict) -> None:
    index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record


rent_rows = [
    {
        "id": "46736",
        "price": 4000,
        "area": 30,
        "priceSqm": 133.33,
        "beds": 1,
        "roomType": "1BR",
        "title": "The Great Condo Petchkasem 48 · 1 房 · 30 ㎡ · ฿4,000/月",
        "url": f"{RENTCONDO_BASE}/46736/GC31-0001",
        "sourceName": "RentcondoBkk",
        "projectName": PROJECT_NAME,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_date_unknown",
        "verificationNote": "單筆頁列 1 房、30㎡、฿4,000/月，另註明公用費 ฿445/月；專案彙整頁同一代碼列 ฿4,500/月，採直接單筆頁金額並標示待向刊登者確認。",
    },
    {
        "id": "171056",
        "price": 5000,
        "area": 31,
        "priceSqm": 161.29,
        "beds": 1,
        "roomType": "1BR",
        "title": "The Great Condo Petchkasem 48 · 1 房 · 31 ㎡ · ฿5,000/月",
        "url": f"{RENTCONDO_BASE}/171056/GC31-0010",
        "sourceName": "RentcondoBkk",
        "projectName": PROJECT_NAME,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_date_unknown",
        "verificationNote": "專案頁顯示此單筆代碼 1 房、31㎡、฿5,000/月；單筆詳情頁核對樓層與面積，頁面未標刊登更新日。",
    },
    {
        "id": "92914",
        "price": 5500,
        "area": 30,
        "priceSqm": 183.33,
        "beds": 0,
        "roomType": "Studio",
        "title": "The Great Condo Petchkasem 48 · Studio · 30 ㎡ · ฿5,500/月",
        "url": f"{RENTCONDO_BASE}/92914/GC31-0002",
        "sourceName": "RentcondoBkk",
        "projectName": PROJECT_NAME,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_date_unknown",
        "verificationNote": "專案頁顯示此單筆代碼 Studio、30㎡、฿5,500/月；單筆詳情頁核對房型與面積，頁面未標刊登更新日。",
    },
]

rent_rates = [row["price"] / row["area"] for row in rent_rows]
rent_1br = rent_rows[:2]
sale_url = "https://assets.propertyhub.in.th/listings/a033746-the-great-condo-petchkasem-48---6005471"
rent_sample_rows = [
    {
        "id": row["id"],
        "price": row["price"],
        "area": row["area"],
        "priceSqm": row["priceSqm"],
        "beds": row["beds"],
        "roomType": row["roomType"],
        "title": row["title"],
        "url": row["url"],
        "sourceName": row["sourceName"],
        "projectName": row["projectName"],
        "checkedAt": CHECKED_AT,
        "matchedBy": row["matchedBy"],
        "listingStatus": row["listingStatus"],
        "verificationNote": row["verificationNote"],
    }
    for row in rent_rows
]

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
prefix, rows, suffix = load_js_array(manual_path, "window.BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if record is None:
    raise RuntimeError("Expected existing verified two-bedroom sale record was not found")
record["asOf"] = CHECKED_AT
record["rent"] = {
    "count": 3,
    "observedCount": 3,
    "countKind": "manual_verified_listing",
    "average": round(sum(row["price"] for row in rent_rows) / len(rent_rows)),
    "minimum": 4000,
    "minimumArea": 30,
    "averageSqm": round(sum(rent_rates) / len(rent_rates)),
    "minimumSqm": round(min(rent_rates), 2),
    "minimumSourceUrl": rent_rows[0]["url"],
    "minimumSqmSourceUrl": rent_rows[0]["url"],
    "asOf": CHECKED_AT,
    "sourceName": "RentcondoBkk 單筆租盤",
    "source": RENTCONDO_PROJECT,
    "samples": rent_sample_rows,
    "byBedroom": {
        "1": {
            "beds": 1,
            "minimum": 4000,
            "area": 30,
            "minimumSqm": round(4000 / 30, 2),
            "minimumSourceUrl": rent_rows[0]["url"],
            "minimumSqmSourceUrl": rent_rows[0]["url"],
            "average": 4500,
            "averageSqm": round(sum(row["price"] / row["area"] for row in rent_1br) / len(rent_1br), 2),
            "sampleCount": 2,
        }
    },
    "note": "RentcondoBkk 專案頁列出 3 筆租盤，已逐筆開啟對應房源頁。最低一房單筆詳情列 ฿4,000/月、30㎡，彙整頁同代碼列 ฿4,500/月，採較低的直接單筆詳情值並標示現況待向刊登者確認。Studio 不納入房型投報。",
}
record["availabilitySources"] = [
    row for row in record.get("availabilitySources", [])
    if row.get("sourceName") not in {"RentcondoBkk 租盤專案頁", "RentcondoBkk 直租樣本", "PropertyHub 出租專案頁"}
] + [
    {"sourceName": "RentcondoBkk 租盤專案頁", "url": RENTCONDO_PROJECT, "statusLabel": "頁面列出 3 筆本案租盤；單筆更新日未提供，房源現況待確認。"},
    {"sourceName": "RentcondoBkk 最低租金單筆", "url": rent_rows[0]["url"], "statusLabel": "單筆頁列 ฿4,000/月、30㎡、1 房；同代碼彙整價為 ฿4,500/月，採單筆詳情並註明價差。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "目前顯示 0 筆；與 RentcondoBkk 專案頁列出的 3 筆不同，租盤可用性尚待刊登方確認。"},
]
record["yieldStatus"] = "unavailable_same_bedroom_rent_missing"
record["yieldNote"] = "兩房最低出售樣本為 ฿1,899,000／57㎡；目前核對到的一房與 Studio 租盤不能配對兩房試算，因此兩房投報率保持待補。"
save_js_array(manual_path, prefix, rows, suffix)

coord_path = ROOT / "dist/bangkok-verified-coordinates.js"
prefix, coord_rows, suffix = load_js_array(coord_path, "window.BANGKOK_VERIFIED_COORDINATES")
upsert(coord_rows, {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.7214584,
    "lng": 100.4406967,
    "locationVerified": True,
    "sourceName": "RentcondoBkk 專案頁 GeoCoordinates",
    "sourceUrl": COORDINATE_SOURCE,
    "verificationSourceUrl": COORDINATE_CHECK,
    "verificationMethod": "RentcondoBkk ApartmentComplex GeoCoordinates cross-checked against Condonayoo Google Maps coordinates and the exact Thai project name and address; pins differ by about 32 m.",
})
save_js_array(coord_path, prefix, coord_rows, suffix)

cross_path = ROOT / "dist/bangkok-market-crosschecks.js"
prefix, cross_rows, suffix = load_js_array(cross_path, "window.BANGKOK_MARKET_CROSSCHECKS")
cross = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if cross is None:
    raise RuntimeError("Expected existing cross-check record was not found")
cross["asOf"] = CHECKED_AT
cross["sourceName"] = "PropertyHub / RentcondoBkk"
cross["rent"] = {
    "activeListingCount": 3,
    "sourceUrl": RENTCONDO_PROJECT,
    "listings": [
        {
            "id": row["id"],
            "price": row["price"],
            "area": row["area"],
            "priceSqm": row["priceSqm"],
            "bedrooms": row["beds"],
            "url": row["url"],
            "sourceName": "RentcondoBkk",
            "statusLabel": row["verificationNote"],
        }
        for row in rent_rows
    ],
}
cross["availabilitySources"] = [
    row for row in cross.get("availabilitySources", [])
    if row.get("sourceName") not in {"RentcondoBkk 租盤專案頁", "RentcondoBkk 座標頁", "CondoNayoo 座標交叉核對"}
] + [
    {"sourceName": "RentcondoBkk 租盤專案頁", "url": RENTCONDO_PROJECT, "statusLabel": "列出 3 筆出租掛牌；本次已打開三筆單筆頁，更新日未列，現況待確認。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "頁面目前顯示 0 筆出租，與 RentcondoBkk 的 3 筆不同。"},
    {"sourceName": "DDproperty 專案頁", "url": DDPROPERTY_PROJECT, "statusLabel": "目前顯示 0 筆出租，無法獨立確認 RentcondoBkk 掛牌仍可租。"},
    {"sourceName": "RentcondoBkk 座標頁", "url": COORDINATE_SOURCE, "statusLabel": "ApartmentComplex GeoCoordinates 13.7214584, 100.4406967；地址為 58 Soi Petchkasem 48。"},
    {"sourceName": "CondoNayoo 座標交叉核對", "url": COORDINATE_CHECK, "statusLabel": "專案頁列 Google Maps 座標 13.721198, 100.440833，與 RentcondoBkk 點位相距約 32 公尺。"},
]
cross["roi"] = {
    "status": "not_calculable",
    "reason": "兩房最低出售樣本為 ฿1,899,000／57㎡，但目前核對到的一房與 Studio 租盤沒有兩房租金可配對；不跨房型估算兩房投報。",
}
save_js_array(cross_path, prefix, cross_rows, suffix)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "selected": {"lat": 13.7214584, "lng": 100.4406967, "source": COORDINATE_SOURCE},
        "crossCheck": {"lat": 13.721198, "lng": 100.440833, "source": COORDINATE_CHECK},
        "distanceBetweenPinsM": 32,
        "decision": "Use the property page GeoCoordinates and retain the independent project Google Maps point as corroboration.",
    },
    "sale": {
        "bedrooms": 2,
        "priceTHB": 1_899_000,
        "areaSqm": 57,
        "source": sale_url,
        "updated": "2026-10-17",
    },
    "rent": {
        "verifiedDirectListings": rent_rows,
        "lowestOneBedroomTHBPerMonth": 4000,
        "lowestOneBedroomAreaSqm": 30,
        "lowestOneBedroomRateTHBPerSqmMonth": round(4000 / 30, 2),
        "availability": "unconfirmed_date_unknown",
        "crossSourceConflict": "PropertyHub and DDproperty show zero rent listings, while RentcondoBkk lists three. The GC31-0001 summary shows ฿4,500/month but its individual page says ฿4,000/month plus ฿445 common fee; use the direct page price with the conflict disclosed.",
    },
    "yield": {
        "calculated": False,
        "reason": "The lowest verified sale is two-bedroom; the checked rents are one-bedroom and studio only.",
    },
    "sources": [HIPFLAT, PROPERTYHUB_PROJECT, PROPERTYHUB_RENT, DDPROPERTY_PROJECT, RENTCONDO_PROJECT, COORDINATE_CHECK, sale_url],
}
(ROOT / "reports/the-great-condo-petchkasem-48-enrichment-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "coordinatesVerified": True, "rentalSamples": len(rent_rows), "lowestRentTHB": 4000, "lowestRentSqm": 30, "twoBedroomYield": "not calculated: no matched two-bedroom rent"}, ensure_ascii=False))
