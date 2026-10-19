"""Record address- and listing-verified data for Hipflat project 3294."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3294
PROJECT = "SP Mansion, Thonglor 8"
HIPFLAT = "https://www.hipflat.co.th/en/projects/sp-mansion-thonglor-8-tollji"
SALE_URL = "https://www.hipflat.co.th/ads/h93l07928082u0477u9ht9n93ul3a04t"
RENT_URL = "https://www.hipflat.co.th/ads/t79903048l34t82nn4e7117e3u02u912"


def read_array(filename: str, variable: str) -> tuple[str, list[dict]]:
    path = ROOT / "dist" / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{variable}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError(f"Unexpected format in {path}")
    return variable, json.loads(match.group(1))


def write_array(filename: str, variable: str, rows: list[dict]) -> None:
    (ROOT / "dist" / filename).write_text(
        f"window.{variable} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


sale = {
    "id": "h93l07928082u0477u9ht9n93ul3a04t",
    "price": 6_900_000,
    "area": 66,
    "priceSqm": round(6_900_000 / 66),
    "beds": 1,
    "roomType": "1BR",
    "title": "SP Mansion Rama 9 · 1 房 · 66 ㎡ · ฿6,900,000",
    "url": SALE_URL,
    "sourceName": "Hipflat",
    "projectName": PROJECT,
    "checkedAt": "2026-10-19",
    "matchedBy": "Hipflat exact project page lists this linked unit at ฿6,900,000, 1 bedroom and 66 sqm; page address is Soi Rama 9 Soi 17, Bang Kapi, Huai Khwang.",
    "listingStatus": "active_as_listed",
}
rent_one_bed = {
    "id": "t79903048l34t82nn4e7117e3u02u912",
    "price": 26_300,
    "area": 80,
    "priceSqm": round(26_300 / 80),
    "beds": 1,
    "roomType": "1BR",
    "title": "SP Mansion Rama 9 · 1 房 · 80 ㎡ · ฿26,300/月",
    "url": RENT_URL,
    "sourceName": "Hipflat",
    "projectName": PROJECT,
    "checkedAt": "2026-10-19",
    "matchedBy": "Hipflat exact project page lists this linked unit at ฿26,300/month, 1 bedroom and 80 sqm; page address is Soi Rama 9 Soi 17, Bang Kapi, Huai Khwang.",
    "listingStatus": "active_as_listed",
}
rent_two_bed = {
    "id": "u1ca002t8t1u7tluutca9a023u02u9nt",
    "price": 36_000,
    "area": 160,
    "priceSqm": round(36_000 / 160),
    "beds": 2,
    "roomType": "2BR",
    "title": "SP Mansion Rama 9 · 2 房 · 160 ㎡ · ฿36,000/月",
    "url": "https://www.hipflat.co.th/ads/u1ca002t8t1u7tluutca9a023u02u9nt",
    "sourceName": "Hipflat",
    "projectName": PROJECT,
    "checkedAt": "2026-10-19",
    "matchedBy": "Hipflat exact project page lists this linked unit at ฿36,000/month, 2 bedrooms and 160 sqm, floor 12; page address is Soi Rama 9 Soi 17, Bang Kapi, Huai Khwang.",
    "listingStatus": "active_as_listed",
}

sale_market = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 6_900_000,
    "minimum": 6_900_000,
    "minimumArea": 66,
    "averageSqm": 104_545,
    "minimumSqm": 104_545,
    "minimumSampleUpdated": "2026-10-19",
    "minimumSqmSampleUpdated": "2026-10-19",
    "asOf": "2026-10-19",
    "sourceName": "Hipflat 專案個別掛牌",
    "source": HIPFLAT,
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "byBedroom": {"1": {"count": 1, "minimum": 6_900_000, "area": 66, "minimumArea": 66, "minimumSqm": 104_545, "sourceUrl": SALE_URL, "minimumSourceUrl": SALE_URL}},
    "samples": [sale],
}
rent_market = {
    "count": 5,
    "observedCount": 2,
    "countKind": "manual_verified_listing",
    "average": 31_150,
    "minimum": 26_300,
    "minimumArea": 80,
    "averageSqm": 277,
    "minimumSqm": 225,
    "minimumSampleUpdated": "2026-10-19",
    "minimumSqmSampleUpdated": "2026-10-19",
    "asOf": "2026-10-19",
    "sourceName": "Hipflat 專案個別掛牌",
    "source": HIPFLAT,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": rent_two_bed["url"],
    "byBedroom": {
        "1": {"count": 1, "minimum": 26_300, "area": 80, "minimumArea": 80, "minimumSqm": 328.75, "sourceUrl": RENT_URL, "minimumSourceUrl": RENT_URL, "minimumSqmSourceUrl": RENT_URL},
        "2": {"count": 1, "minimum": 36_000, "area": 160, "minimumArea": 160, "minimumSqm": 225, "sourceUrl": rent_two_bed["url"], "minimumSourceUrl": rent_two_bed["url"], "minimumSqmSourceUrl": rent_two_bed["url"]},
    },
    "samples": [rent_one_bed, rent_two_bed],
}

coordinate = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT,
    "lat": 13.75818478,
    "lng": 100.5915596,
    "locationVerified": True,
    "sourceName": "Ishikawa Shoji 精確地址地圖座標",
    "sourceUrl": "https://ishikawashoji.com/property/sp-mansion/",
    "verificationSourceUrl": HIPFLAT,
    "corroborationSourceUrl": "https://www.thailand-property.com/condo/12688/sp-mansion-thonglor-8",
    "verificationMethod": "Ishikawa Shoji identifies SP Mansion at 362/2 Soi Rama IX 17; Hipflat confirms the same Rama 9 Soi 17, Bang Kapi, Huai Khwang project; Thailand-Property structured map coordinate is within approximately 30 m.",
}
market = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT,
    "completedYear": 1995,
    "completedYearSourceUrl": HIPFLAT,
    "replaceSale": True,
    "replaceRent": True,
    "sale": sale_market,
    "rent": rent_market,
}

for filename, variable, row in [
    ("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinate),
    ("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", market),
]:
    _, rows = read_array(filename, variable)
    matches = [index for index, item in enumerate(rows) if int(item.get("hipflatId", -1)) == PROJECT_ID]
    if matches:
        rows[matches[0]] = row
        for index in reversed(matches[1:]):
            rows.pop(index)
    else:
        rows.append(row)
    write_array(filename, variable, rows)

gross_yield = ((26_300 / 80 * 66) * 12) / 6_900_000 * 100
after_one_agent_month = ((26_300 / 80 * 66) * 11) / 6_900_000 * 100
report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT,
    "checkedAt": "2026-10-19",
    "coordinate": {"lat": coordinate["lat"], "lng": coordinate["lng"], "sourceUrl": coordinate["sourceUrl"], "corroborationSourceUrl": coordinate["corroborationSourceUrl"]},
    "sale": {"price": 6_900_000, "areaSqm": 66, "bedrooms": 1, "url": SALE_URL},
    "rent": {"pricePerMonth": 26_300, "areaSqm": 80, "bedrooms": 1, "url": RENT_URL},
    "yieldBaseline": {
        "bedrooms": 1,
        "purchasePrice": 6_900_000,
        "purchaseAreaSqm": 66,
        "rentPerSqmMonth": round(26_300 / 80, 2),
        "estimatedRentOnSaleArea": round(26_300 / 80 * 66),
        "grossAnnualYieldPercent": round(gross_yield, 2),
        "annualYieldAfterOneAgentMonthPercent": round(after_one_agent_month, 2),
        "commonFeeDeducted": False,
        "commonFeeNote": "No project-specific common fee was verified.",
    },
    "scopeNote": "Hipflat project page shows 1 sale and 5 rental listings and links the lowest 1-bedroom sale/rent details. The saved individual rent comparison includes one 1-bedroom and one 2-bedroom. Same-name Thonglor listings in Watthana were excluded.",
}
(ROOT / "reports" / "sp-mansion-rama9-market-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": PROJECT, "grossYieldPercent": round(gross_yield, 2), "afterOneAgentMonthPercent": round(after_one_agent_month, 2), "report": "reports/sp-mansion-rama9-market-2026-10-19.json"}, ensure_ascii=False))
