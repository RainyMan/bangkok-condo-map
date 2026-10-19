"""Verify and enrich Hipflat project 3436 using its current Vittorio name."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3436
NAME = "GALERIE rue de 39"
CURRENT_NAME = "Vittorio Sukhumvit 39"
CHECKED_AT = "2026-10-20"
LAT, LNG = 13.730786, 100.570792
COORD_REVIEW = "https://www.condonayoo.com/vittorio-sukhumvit-39/"
COORD_MAP = "https://www.google.com/maps/search/?api=1&query=13.730786%2C100.570792"
HIPFLAT = "https://www.hipflat.co.th/en/projects/galerie-rue-de-39-xjxfpx"
PH_SALE_PAGE = "https://propertyhub.in.th/en/condo-for-sale/project-vittorio-sukhumvit-39"
PH_RENT_PAGE = "https://propertyhub.in.th/en/condo-for-rent/project-vittorio-sukhumvit-39"

sale_samples = [
    {"id": "5890552", "price": 32350000, "area": 100.0, "priceSqm": 323500, "beds": 2, "roomType": "2BR", "title": "2 Bedrooms 2 Bathrooms 101 SQ.M Vittorio", "url": "https://propertyhub.in.th/en/listings/2-bedrooms-2-bathrooms-101-sq-m-vittorio--9c4808d7---5890552", "sourceName": "PropertyHub", "projectName": CURRENT_NAME, "updated": "2026-10-18", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_project_listing_page", "listingStatus": "active_as_listed", "verificationNote": "PropertyHub 個別頁列 2 房、100㎡、฿32,350,000；Vittorio Sukhumvit 39 專案頁的 2 房掛牌排序中，總價低於其餘可核對 2 房樣本。"},
    {"id": "4718794", "price": 32500000, "area": 102.0, "priceSqm": 318627.45, "beds": 2, "roomType": "2BR", "title": "2 Beds with Bathtub 102 sq.m. Ultra Luxury Condo at Vittorio", "url": "https://propertyhub.in.th/en/listings/2-beds-with-bathtub-102-sq-m-ultra-luxury-condo-good-location-bts-phrom-phong-150-m-at-vittorio-condo-for-sale---4718794", "sourceName": "PropertyHub", "projectName": CURRENT_NAME, "updated": "2026-09-30", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_project_listing_page", "listingStatus": "active_as_listed", "verificationNote": "PropertyHub 專案出售頁所列 2 房掛牌：102㎡、฿32,500,000。"},
    {"id": "6394475", "price": 33000000, "area": 102.0, "priceSqm": 323529.41, "beds": 2, "roomType": "2BR", "title": "Vittorio Sukhumvit 39 Contemporary 2 Bed Luxury Condo", "url": "https://propertyhub.in.th/en/listings/vittorio-sukhumvit-39-contemporary-2-bed-luxury-condo-br16517cd---6394475", "sourceName": "PropertyHub", "projectName": CURRENT_NAME, "updated": "2026-10-17", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_project_listing_page", "listingStatus": "active_as_listed", "verificationNote": "PropertyHub 專案出售頁所列 2 房掛牌：102㎡、฿33,000,000。"},
]
rent_samples = [
    {"id": "6422794", "price": 120000, "area": 141.67, "priceSqm": 847.04, "beds": 2, "roomType": "2BR", "title": "2-BR Condo at Vittorio Sukhumvit 39 near BTS Phrom Phong", "url": "https://propertyhub.in.th/en/listings/2-br-condo-at-vittorio-sukhumvit-39-near-bts-phrom-phong-id-3311436---6422794", "sourceName": "PropertyHub", "projectName": CURRENT_NAME, "updated": "2026-10-19", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_project_listing_page", "listingStatus": "active_as_listed", "verificationNote": "PropertyHub 個別頁列 2 房、141.67㎡、฿120,000/月；同房型近期可核對樣本中最低租金單價。"},
    {"id": "6419027", "price": 120000, "area": 137.0, "priceSqm": 875.91, "beds": 2, "roomType": "2BR", "title": "100m To BTS Phrom Phong | 2-BR Vittorio Sukhumvit 39", "url": "https://propertyhub.in.th/en/listings/100m-to-bts-phrom-phong-2-br-vittorio-sukhumvit-39-id-3311263---6419027", "sourceName": "PropertyHub", "projectName": CURRENT_NAME, "updated": "2026-10-19", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_project_listing_page", "listingStatus": "active_as_listed", "verificationNote": "PropertyHub 專案出租頁所列 2 房掛牌：137㎡、฿120,000/月。"},
    {"id": "3931663", "price": 100000, "area": 110.0, "priceSqm": 909.09, "beds": 2, "roomType": "2BR", "title": "For Rent Condo Vittorio Sukhumvit 39 BTS Phrom Phong CX-77902", "url": "https://propertyhub.in.th/en/listings/for-rent-condo-vittorio-sukhumvit-39-bts-phrom-phong-watthana-watthana-bangkok-cx-77902-live-chat-with-us-add-line-connexproperty--a31c0913---3931663", "sourceName": "PropertyHub", "projectName": CURRENT_NAME, "updated": "2026-10-16", "checkedAt": CHECKED_AT, "matchedBy": "exact_project_name_and_project_listing_page", "listingStatus": "active_as_listed", "verificationNote": "PropertyHub 專案出租頁所列 2 房掛牌：110㎡、฿100,000/月。"},
]


def load_array(filename: str, symbol: str):
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format: {filename}")
    return path, match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(path: Path, prefix: str, rows: list[dict], suffix: str, compact: bool = True):
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    path.write_text(prefix + json.dumps(rows, ensure_ascii=False, **options) + suffix, encoding="utf-8")


def upsert(rows: list[dict], key: str, value: dict):
    row = next((item for item in rows if int(item.get(key, -1)) == PROJECT_ID), None)
    if row is None:
        rows.append(value)
    else:
        row.update(value)
    return row or value


sale_min = min(sale_samples, key=lambda sample: sample["price"])
sale_rate_min = min(sale_samples, key=lambda sample: sample["price"] / sample["area"])
rent_min = min(rent_samples, key=lambda sample: sample["price"])
rent_rate_min = min(rent_samples, key=lambda sample: sample["price"] / sample["area"])
sale_average = round(sum(s["price"] for s in sale_samples) / len(sale_samples))
sale_average_sqm = round(sum(s["price"] / s["area"] for s in sale_samples) / len(sale_samples))
rent_average = round(sum(s["price"] for s in rent_samples) / len(rent_samples))
rent_average_sqm = round(sum(s["price"] / s["area"] for s in rent_samples) / len(rent_samples))
fee_rate = 120
projected_rent = round(rent_rate_min["price"] / rent_rate_min["area"] * sale_min["area"])
net_yield = round(((projected_rent * 11) - fee_rate * sale_min["area"] * 12) / sale_min["price"] * 100, 2)

# Preserve Hipflat's original project name, while cross-linking the current
# project identity and independently confirmed coordinates/details.
for filename, symbol, key in [
    ("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", "id"),
    ("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", "id"),
]:
    path, prefix, rows, suffix = load_array(filename, symbol)
    project = next((row for row in rows if int(row.get(key, -1)) == PROJECT_ID), None)
    if not project:
        raise RuntimeError(f"Project {PROJECT_ID} missing from {filename}")
    project.update({
        "address": "Soi Sukhumvit 39, Khlong Tan Nuea, Watthana, Bangkok 10110, THA",
        "completedYear": 2017, "completedYearSourceUrl": COORD_REVIEW,
        "floors": 28, "units": 88,
        "area": {"min": 100, "max": 306},
        "currentProjectName": CURRENT_NAME,
        "nameAliases": [CURRENT_NAME, "VITTORIO Sukhumvit 39"],
        "propertyHubProjectUrl": "https://propertyhub.in.th/en/projects/vittorio-sukhumvit-39",
    })
    if filename == "bangkok-catalogue.js":
        project.update({
            "locationVerified": True, "locationSourceUrl": COORD_MAP,
            "locationVerificationSourceUrl": COORD_REVIEW,
            "marketDataStatus": "verified_coordinates_current_two_bedroom_sale_rent_samples_roi",
            "dataCompleteness": {**project.get("dataCompleteness", {}), "coordinates": True, "saleSample": True, "rentSample": True, "yield": True},
            "sourceDescription": "GALERIE rue de 39 現名 Vittorio Sukhumvit 39；同址、開發商及 88 戶規模已交叉核對。",
        })
    else:
        project.update({"propertyHubSaleUrl": PH_SALE_PAGE, "propertyHubRentUrl": PH_RENT_PAGE})
    save_array(path, prefix, rows, suffix)

path, prefix, rows, suffix = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
upsert(rows, "hipflatId", {
    "hipflatId": PROJECT_ID, "name": NAME, "lat": LAT, "lng": LNG,
    "locationVerified": True, "sourceName": "CondoNayoo 專案頁公布的 Google Maps 座標",
    "sourceUrl": COORD_MAP, "verificationSourceUrl": COORD_REVIEW,
    "corroborationSourceUrl": "https://www.ddproperty.com/en/project/2084-galerie-rue-de-39",
    "verificationMethod": "CondoNayoo confirms the former name GALERIE rue de 39, current name VITTORIO Sukhumvit 39, Sukhumvit 39 address, and Google Maps coordinates; DDproperty and PropertyHub project pages corroborate the former/current project identity.",
})
save_array(path, prefix, rows, suffix)

path, prefix, rows, suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": NAME}
    rows.append(manual)
sale_by_bed = {"2": {"count": len(sale_samples), "minimum": sale_min["price"], "area": sale_min["area"], "minimumArea": sale_min["area"], "priceSqm": sale_min["price"] / sale_min["area"], "minimumSqm": sale_min["price"] / sale_min["area"], "minimumSourceUrl": sale_min["url"], "sourceUrl": sale_min["url"], "minimumSqmSourceUrl": sale_rate_min["url"]}}
rent_by_bed = {"2": {"count": len(rent_samples), "minimum": rent_min["price"], "area": rent_min["area"], "minimumArea": rent_min["area"], "minimumSqm": rent_rate_min["price"] / rent_rate_min["area"], "averageSqm": rent_average_sqm, "minimumSourceUrl": rent_min["url"], "sourceUrl": rent_min["url"], "minimumSqmSourceUrl": rent_rate_min["url"]}}
manual.update({
    "asOf": CHECKED_AT, "replaceSale": True, "replaceRent": True,
    "fee": {"rate": fee_rate, "status": "public", "note": "CondoNayoo 專案頁列管理費 ฿120/㎡/月；年度管理費以室內面積 × ฿120 × 12 估算。", "source": COORD_REVIEW},
    "sale": {
        "count": 71, "observedCount": len(sale_samples), "countKind": "manual_verified_listing",
        "average": sale_average, "minimum": sale_min["price"], "minimumArea": sale_min["area"],
        "minimumSampleUpdated": sale_min["updated"], "averageSqm": sale_average_sqm,
        "minimumSqm": round(sale_rate_min["price"] / sale_rate_min["area"]),
        "minimumSqmSampleUpdated": sale_rate_min["updated"], "asOf": CHECKED_AT,
        "sourceName": "PropertyHub 個別出售掛牌", "source": PH_SALE_PAGE,
        "minimumSourceUrl": sale_min["url"], "minimumSqmSourceUrl": sale_rate_min["url"],
        "samples": sale_samples, "byBedroom": sale_by_bed,
    },
    "rent": {
        "count": 145, "observedCount": len(rent_samples), "countKind": "manual_verified_listing",
        "average": rent_average, "minimum": rent_min["price"], "minimumArea": rent_min["area"],
        "minimumSampleUpdated": rent_min["updated"], "averageSqm": rent_average_sqm,
        "minimumSqm": round(rent_rate_min["price"] / rent_rate_min["area"], 2),
        "minimumSqmSampleUpdated": rent_rate_min["updated"], "asOf": CHECKED_AT,
        "sourceName": "PropertyHub 個別出租掛牌", "source": PH_RENT_PAGE,
        "minimumSourceUrl": rent_min["url"], "minimumSqmSourceUrl": rent_rate_min["url"],
        "samples": rent_samples, "byBedroom": rent_by_bed,
    },
})
save_array(path, prefix, rows, suffix)

path, prefix, rows, suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
upsert(rows, "hipflatId", {
    "hipflatId": PROJECT_ID, "projectName": NAME, "currentProjectName": CURRENT_NAME,
    "asOf": CHECKED_AT, "sourceName": "Hipflat + PropertyHub + CondoNayoo + DDproperty",
    "projectSourceUrl": HIPFLAT,
    "sale": {"activeListingCount": 71, "displayedResultCount": 71, "observedCount": len(sale_samples), "sourceUrl": PH_SALE_PAGE,
             "note": "PropertyHub 專案出售頁列出 71 筆；本批核對 3 筆 2 房個別物件，最低總價฿32,350,000（100㎡）。", "listings": [{"listingId": s["id"], "price": s["price"], "area": s["area"], "priceSqm": s["price"] / s["area"], "bedrooms": 2, "lastRefreshed": s["updated"], "url": s["url"], "sourceName": "PropertyHub", "statusLabel": "PropertyHub 個別 2 房掛牌；狀態按頁面刷新日標示"} for s in sale_samples]},
    "rent": {"activeListingCount": 145, "displayedResultCount": 145, "observedCount": len(rent_samples), "sourceUrl": PH_RENT_PAGE,
             "note": "PropertyHub 專案出租頁列出 145 筆；本批核對 3 筆 2 房個別物件，最低單價฿846.86/㎡/月（฿120,000、141.67㎡）。", "listings": [{"listingId": s["id"], "price": s["price"], "area": s["area"], "priceSqm": s["price"] / s["area"], "bedrooms": 2, "lastRefreshed": s["updated"], "url": s["url"], "sourceName": "PropertyHub", "statusLabel": "PropertyHub 個別 2 房掛牌；狀態按頁面刷新日標示"} for s in rent_samples]},
    "availabilitySources": [
        {"sourceName": "CondoNayoo 專案身分、規模與座標", "url": COORD_REVIEW, "statusLabel": "確認 GALERIE rue de 39 為 Vittorio Sukhumvit 39 舊名；28 層、88 戶、2017 完工，Google Maps 座標 13.730786, 100.570792；管理費฿120/㎡/月。"},
        {"sourceName": "Google Maps 點位", "url": COORD_MAP, "statusLabel": f"{LAT}, {LNG}"},
        {"sourceName": "DDproperty 舊名專案頁", "url": "https://www.ddproperty.com/en/project/2084-galerie-rue-de-39", "statusLabel": "GALERIE rue de 39 專案、Sukhumvit 39 地址交叉核對。"},
        {"sourceName": "PropertyHub 售租專案頁", "url": PH_SALE_PAGE, "statusLabel": "現行品牌名 Vittorio Sukhumvit 39；專案頁列售租掛牌。"},
    ],
    "yieldStatus": "estimated_from_current_two_bedroom_listing_samples_and_published_common_fee",
    "yieldNote": f"以兩房最低售價฿{sale_min['price']:,}、同一物件面積{sale_min['area']:g}㎡，乘兩房最低租金單價฿{rent_rate_min['price'] / rent_rate_min['area']:.2f}/㎡/月估租฿{projected_rent:,}/月；扣一個月仲介費及已查證管理費฿{fee_rate}/㎡/月後，估算淨年投報率{net_yield:.2f}%。",
})
save_array(path, prefix, rows, suffix, compact=False)

html_path = DIST / "index.html"
html = html_path.read_text(encoding="utf-8")
for name in ["bangkok-catalogue.js", "bangkok-propertyhub-map.js", "bangkok-verified-coordinates.js", "bangkok-manual-market-samples.js", "bangkok-market-crosschecks.js", "app.js"]:
    html = re.sub(rf"({re.escape(name)}\?v=)[^\"']+", rf"\g<1>20261020-vittorio-3436", html)
html_path.write_text(html, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID, "hipflatName": NAME, "currentName": CURRENT_NAME, "checkedAt": CHECKED_AT,
    "coordinates": {"lat": LAT, "lng": LNG, "coordinateSource": COORD_MAP, "verificationSource": COORD_REVIEW},
    "projectDetails": {"floors": 28, "units": 88, "completedYear": 2017, "areaRangeSqm": [100, 306], "commonFeeBahtPerSqmPerMonth": fee_rate},
    "saleSamples": sale_samples, "rentSamples": rent_samples,
    "yieldInputs": {"salePrice": sale_min["price"], "areaSqm": sale_min["area"], "rentRatePerSqm": rent_rate_min["price"] / rent_rate_min["area"], "estimatedMonthlyRent": projected_rent, "managementFeePerMonth": fee_rate * sale_min["area"], "agentDeductionMonths": 1, "netAnnualYieldPercent": net_yield},
    "sources": [HIPFLAT, PH_SALE_PAGE, PH_RENT_PAGE, COORD_REVIEW, COORD_MAP, "https://www.ddproperty.com/en/project/2084-galerie-rue-de-39"],
    "note": "PropertyHub listings use the current project name Vittorio Sukhumvit 39; CondoNayoo explicitly documents GALERIE rue de 39 as its former name.",
}
(REPORTS / "galerie-rue-de-39-vittorio-market-coordinate-yield-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "coords": [LAT, LNG], "saleMinimum2BR": sale_min["price"], "rentMinimumSqm2BR": round(rent_rate_min["price"] / rent_rate_min["area"], 2), "rentAreaForYield": sale_min["area"], "monthlyRentEstimate": projected_rent, "commonFee": fee_rate, "netYield": net_yield}, ensure_ascii=False))
