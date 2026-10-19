"""Add directly linked current sale and rent samples for Hipflat project 4599."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 4599
AS_OF = "2026-10-19"
PROJECT_NAME = "Sapphire Luxurious Condominium Rama 3"
PROJECT_URL = "https://propertyhub.in.th/en/projects/sapphire-rama-iii"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-sapphire-rama-iii"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-sapphire-rama-iii"

sale_samples = [
    {
        "id": "500547336",
        "price": 4_605_000,
        "area": 43.42,
        "priceSqm": 106_057,
        "beds": 2,
        "roomType": "2BR",
        "title": "2 房，43.42 ㎡，8 樓，฿4,605,000",
        "url": "https://www.ddproperty.com/en/property/sapphire-luxurious-condominium-rama-iii-bangkok-for-sale-500547336",
        "sourceName": "DDproperty",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-18",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "5359153",
        "price": 2_700_000,
        "area": 34.73,
        "priceSqm": 77_743,
        "beds": 1,
        "roomType": "1BR",
        "title": "1 房，34.73 ㎡，5–10 樓，฿2,700,000",
        "url": "https://asset-direct-v2.propertyhub.in.th/en/listings/s4372for-sale-new-condo-sapphire-condominium---5359153",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-17",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6434375",
        "price": 5_820_000,
        "area": 43.42,
        "priceSqm": 134_040,
        "beds": 2,
        "roomType": "2BR",
        "title": "2 房，43.42 ㎡，7 樓，฿5,820,000",
        "url": "https://propertyhub.in.th/en/listings/2-bedroom-condo-for-sale-at-sapphire-luxurious-condominium-rama-3-5692418---6434375",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-18",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id",
        "listingStatus": "active_as_listed",
    },
]

rent_samples = [
    {
        "id": "6349927",
        "price": 30_000,
        "area": 55,
        "priceSqm": 545,
        "beds": 2,
        "roomType": "2BR",
        "title": "2 房，55 ㎡，25 樓，฿30,000/月",
        "url": "https://propertyhub.in.th/en/listings/for-rent-sapphire-rama-iii-2-bedrooms-2-bathrooms-fully-furnished-and-equipped-with-appliances-near-bts-chong-nonsi---6349927",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-18",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "6347501",
        "price": 30_000,
        "area": 54,
        "priceSqm": 556,
        "beds": 2,
        "roomType": "2BR",
        "title": "2 房，54 ㎡，24 樓，฿30,000/月",
        "url": "https://propertyhub.in.th/en/listings/for-rent-sapphire-rama-iii-2-bedrooms-2-bathrooms-fully-furnished-and-equipped-with-all-appliances---6347501",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-18",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "5732408",
        "price": 17_000,
        "area": 34,
        "priceSqm": 500,
        "beds": 1,
        "roomType": "1BR",
        "title": "1 房，34 ㎡，2 樓，฿17,000/月",
        "url": "https://propertyhub.in.th/en/listings/z4242-200169-condo-for-rent-sapphire-condominium-rama-3",
        "sourceName": "PropertyHub",
        "projectName": PROJECT_NAME,
        "updated": "2026-10-17",
        "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_and_listing_id",
        "listingStatus": "active_as_listed",
    },
]

manual_record = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "sale": {
        "asOf": AS_OF,
        "sourceName": "PropertyHub／DDproperty 單筆掛牌",
        "source": SALE_PROJECT_URL,
        "samples": sale_samples,
    },
    "rent": {
        "asOf": AS_OF,
        "sourceName": "PropertyHub 單筆掛牌",
        "source": RENT_PROJECT_URL,
        "samples": rent_samples,
    },
    "fee": {
        "rate": 60,
        "status": "public",
        "note": "PropertyHub 專案頁公布 60 THB/㎡/月；實際費用向管委會確認。",
        "source": PROJECT_URL,
    },
    "completedYearSourceUrl": PROJECT_URL,
}

def update_array_assignment(path: Path, variable: str, record: dict) -> None:
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JS array format: {path}")
    rows = json.loads(match.group(2))
    index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record
    path.write_text(match.group(1) + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + match.group(3), encoding="utf-8")


update_array_assignment(ROOT / "dist/bangkok-manual-market-samples.js", "window.BANGKOK_MANUAL_MARKET_SAMPLES", manual_record)

coordinate_path = ROOT / "dist/bangkok-propertyscout-details.js"
coordinate_text = coordinate_path.read_text(encoding="utf-8")
coordinate_match = re.fullmatch(r"(window\.BANGKOK_PROPERTYSCOUT_DETAILS\s*=\s*)(\[.*\])(\s*;?\s*)", coordinate_text, re.S)
if not coordinate_match:
    raise RuntimeError(f"Unexpected JS array format: {coordinate_path}")
coordinate_rows = json.loads(coordinate_match.group(2))
coordinate_record = next((row for row in coordinate_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if coordinate_record is None:
    raise RuntimeError("Verified PropertyScout coordinates for project 4599 not found")
coordinate_record["locationVerificationSourceUrl"] = "https://www.checkraka.com/condo/article/121925/"
coordinate_record["verificationMethod"] = "propertyscout_project_pin_crosschecked_with_checkraka_project_location"
coordinate_path.write_text(
    coordinate_match.group(1) + json.dumps(coordinate_rows, ensure_ascii=False, separators=(",", ":")) + coordinate_match.group(3),
    encoding="utf-8",
)

crosscheck_path = ROOT / "dist/bangkok-market-crosschecks.js"
crosscheck_record = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": AS_OF,
    "sourceName": "PropertyHub／DDproperty",
    "projectSourceUrl": PROJECT_URL,
    "sale": {
        "activeListingCount": 17,
        "sourceUrl": SALE_PROJECT_URL,
        "listings": [{key: sample[key] for key in ("id", "price", "area", "beds", "url", "updated")} for sample in sale_samples],
    },
    "rent": {
        "activeListingCount": 28,
        "sourceUrl": RENT_PROJECT_URL,
        "listings": [{key: sample[key] for key in ("id", "price", "area", "beds", "url", "updated")} for sample in rent_samples],
    },
    "commonFeeTHBPerSqmMonthly": 60,
    "commonFeeSourceUrl": PROJECT_URL,
    "availabilitySources": [
        {"sourceName": "PropertyHub 專案資訊與掛牌", "url": PROJECT_URL, "statusLabel": "核對日顯示 17 筆出售、28 筆出租；最低兩房出售 ฿4,605,000/43.42㎡；兩房出租最低觀察租金 ฿30,000/月。"},
        {"sourceName": "DDproperty 兩房最低總價掛牌", "url": sale_samples[0]["url"], "statusLabel": "兩房、43.42㎡、฿4,605,000；列示中。"},
        {"sourceName": "PropertyScout 座標與行情摘要", "url": "https://propertyscout.co.th/en/bangkok/condo/sapphire-luxurious-condominium-rama-iii/", "statusLabel": "專案座標已核實；專案摘要最低價不代替單筆掛牌。"},
    ],
}
update_array_assignment(ROOT / "dist/bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS", crosscheck_record)

coverage_path = ROOT / "reports/bangkok-coverage-2026-10-19.csv"
with coverage_path.open(encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)
    rows = list(reader)
    fieldnames = reader.fieldnames
for row in rows:
    if row.get("hipflat_id") == str(PROJECT_ID):
        row["sale_individual_listing_link"] = "yes"
        row["sale_source"] = sale_samples[0]["url"]
        row["sale_sample_updated"] = "2026-10-18"
        row["rent_individual_listing_link"] = "yes"
        row["rent_source"] = rent_samples[0]["url"]
        row["rent_sample_updated"] = "2026-10-18"
        row["missing"] = ""
        break
else:
    raise RuntimeError("Project 4599 not found in coverage report")
with coverage_path.open("w", encoding="utf-8-sig", newline="") as destination:
    writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

sale_price, sale_area = 4_605_000, 43.42
rent_rate = 30_000 / 55
estimated_monthly_rent = round(rent_rate * sale_area)
annual_common_fee = 60 * sale_area * 12
net_yield = (estimated_monthly_rent * 11 - annual_common_fee) / sale_price * 100
report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": AS_OF,
    "coordinates": {
        "lat": 13.673492948902071,
        "lng": 100.53845846493441,
        "source": "https://propertyscout.co.th/en/bangkok/condo/sapphire-luxurious-condominium-rama-iii/",
        "independentCrosscheck": {
            "lat": 13.673449,
            "lng": 100.538252,
            "source": "https://www.checkraka.com/condo/article/121925/",
        },
    },
    "sale": {
        "lowestTwoBedroomTotalTHB": sale_price,
        "areaSqm": sale_area,
        "priceTHBPerSqm": round(sale_price / sale_area),
        "listingSource": sale_samples[0]["url"],
        "projectListingSource": SALE_PROJECT_URL,
        "listingRefreshDate": "2026-10-18",
        "additionalSamples": [sample for sample in sale_samples[1:]],
    },
    "rent": {
        "twoBedroomSampleMonthlyTHB": 30_000,
        "twoBedroomSampleAreaSqm": 55,
        "lowestObservedTwoBedroomRentTHBPerSqmMonthly": round(rent_rate, 2),
        "listingSource": rent_samples[0]["url"],
        "projectListingSource": RENT_PROJECT_URL,
        "listingRefreshDate": "2026-10-18",
        "additionalSamples": [sample for sample in rent_samples[1:]],
    },
    "commonFee": {"THBPerSqmMonthly": 60, "source": PROJECT_URL},
    "yield": {
        "formula": "(estimated monthly rent × 11 − annual common fee) ÷ lowest two-bedroom sale total × 100",
        "monthlyRentEstimateTHB": estimated_monthly_rent,
        "annualCommonFeeTHB": round(annual_common_fee),
        "netYieldPercent": round(net_yield, 2),
        "grossYieldBeforeCostsPercent": round(estimated_monthly_rent * 12 / sale_price * 100, 2),
        "agentMonthOnlyYieldPercent": round(estimated_monthly_rent * 11 / sale_price * 100, 2),
        "note": "兩房售價採最低總價掛牌，面積取同一物件；月租依 30,000/55㎡ 的兩房租金單價乘 43.42㎡，並扣 1 個月仲介與已公布管理費。",
    },
    "projectFactsConflict": {
        "propertyHubProjectYearBuilt": 2023,
        "propertyScoutMarketYear": 2024,
        "decision": "保留現有畫面完工年份資料，待取得開發商或政府來源釐清，不用衝突資訊覆蓋。",
    },
    "sourcePages": [PROJECT_URL, SALE_PROJECT_URL, RENT_PROJECT_URL],
}
(ROOT / "reports/sapphire-luxurious-condominium-rama-3-market-enrichment-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Updated project {PROJECT_ID}: {len(sale_samples)} sale samples, {len(rent_samples)} rent samples, net yield {net_yield:.2f}%")
