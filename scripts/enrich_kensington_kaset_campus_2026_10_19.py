from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_IDS = (4527, 5610)
NAME = "Kensington Kaset Campus"
HIPFLAT_URLS = {
    4527: "https://www.hipflat.co.th/en/projects/kensington-kaset-campus-lrpmsz",
    5610: "https://www.hipflat.co.th/en/projects/kensington-kaset-campus-u4t4l0en13ne0l1h2elt1han4lell1ha",
}
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/kensington-kaset-campus"


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_sample = {
    "id": "CX-135284", "price": 3_790_000, "area": 42.02, "priceSqm": 90_195,
    "beds": 2, "roomType": "2BR", "url": "https://propertyhub.in.th/en/listings/for-sale-condo-kensington-kaset-campus-bts-bang-bua-lat-yao-chatuchak-bangkok-cx-135284-live-chat-with-us-add-line-connexproperty--b9b209b6",
    "title": "Kensington Kaset Campus，2 房 2 衛，42.02 ㎡，฿3,790,000",
    "sourceName": "PropertyHub", "projectName": NAME, "checkedAt": AS_OF,
    "updated": "2026-10-17", "matchedBy": "exact_project_listing_name_room_type_and_price_on_project_page",
    "listingStatus": "active_as_listed",
}
rent_sample = {
    "id": "6237061", "price": 18_000, "area": 42, "priceSqm": 429,
    "beds": 2, "roomType": "2BR", "url": "https://propertyhub.in.th/en/listings/2-br-condo-for-rent-kensington-kaset-campus-lat-yao-id-2899532---6237061",
    "title": "Kensington Kaset Campus，2 房 2 衛，42 ㎡，฿18,000／月",
    "sourceName": "PropertyHub", "projectName": NAME, "checkedAt": AS_OF,
    "updated": "2026-10-02", "matchedBy": "exact_project_listing_name_room_type_and_area_on_project_page",
    "listingStatus": "active_as_listed",
}

markets = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
for project_id in PROJECT_IDS:
    project = next((row for row in markets if int(row.get("hipflatId", 0)) == project_id), None)
    if project is None:
        project = {"hipflatId": project_id, "name": NAME}
        markets.append(project)
    for kind, sample in (("sale", sale_sample), ("rent", rent_sample)):
        market = project.setdefault(kind, {})
        by_url = {row.get("url"): row for row in market.get("samples", []) if row.get("url")}
        by_url[sample["url"]] = sample
        combined = list(by_url.values())
        low_total = min(combined, key=lambda row: float(row["price"]))
        low_rate = min(combined, key=lambda row: float(row["price"]) / float(row["area"]))
        bedrooms = {}
        for beds in sorted({int(row["beds"]) for row in combined if row.get("beds")}):
            room_rows = [row for row in combined if int(row["beds"]) == beds]
            room_low = min(room_rows, key=lambda row: float(row["price"]))
            room_rate = min(room_rows, key=lambda row: float(row["price"]) / float(row["area"]))
            bedrooms[str(beds)] = {
                "count": len(room_rows), "minimum": room_low["price"],
                "area": room_low["area"], "minimumArea": room_low["area"],
                "priceSqm": round(float(room_low["price"]) / float(room_low["area"])),
                "minimumSqm": round(float(room_rate["price"]) / float(room_rate["area"])),
                "minimumSourceUrl": room_low["url"], "sourceUrl": room_low["url"],
                "minimumSqmSourceUrl": room_rate["url"],
            }
        market.update({
            "count": len(combined), "observedCount": len(combined),
            "countKind": "manual_verified_listing", "samples": combined,
            "minimum": low_total["price"], "minimumArea": low_total["area"],
            "minimumSourceUrl": low_total["url"],
            "minimumSqm": round(float(low_rate["price"]) / float(low_rate["area"])),
            "minimumSqmSourceUrl": low_rate["url"], "byBedroom": bedrooms,
            "asOf": AS_OF, "sourceName": "PropertyHub 個別掛牌",
            "source": PROPERTYHUB_PROJECT_URL,
        })
    project.update({
        "fee": {
            "rate": 40,
            "note": "PropertyHub 專案頁公布公共管理費 ฿40／㎡／月；請向管委會確認現行實收費率。",
            "source": PROPERTYHUB_PROJECT_URL,
            "status": "published_indicative",
        },
        "completedYear": 2018,
        "completedYearSourceUrl": PROPERTYHUB_PROJECT_URL,
    })
markets.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

coordinates = read_array("bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS")
coord = next((row for row in coordinates if row.get("hipflatId") == PROJECT_IDS[0]), {})
estimated_rent = round(18_000 / 42 * 42.02)
annual_fee = 40 * 42.02 * 12
net_yield = (estimated_rent * 11 - annual_fee) / 3_790_000 * 100
report = {
    "hipflatIds": list(PROJECT_IDS), "name": NAME, "asOf": AS_OF,
    "duplicateProjectRecords": "Both Hipflat IDs resolve to the same named project and PropertyScout coordinate/source; identical direct listing samples are attached to both records.",
    "hipflatProjectUrls": [HIPFLAT_URLS[project_id] for project_id in PROJECT_IDS],
    "propertyhubProjectUrl": PROPERTYHUB_PROJECT_URL,
    "coordinates": {"lat": coord.get("lat"), "lng": coord.get("lng"), "source": coord.get("locationSourceUrl")},
    "completedYear": 2018, "feeTHBPerSqmPerMonth": 40,
    "saleSamples": [sale_sample], "rentSamples": [rent_sample],
    "excludedLowerMislabelledSale": {
        "priceTHB": 2_690_000, "areaSqm": 32,
        "reason": "The project-page record labelled 2 bedrooms has direct-detail text describing one bedroom; excluded from verified two-bedroom minimum.",
        "source": "https://propertyhub.in.th/en/listings/condo-for-sell-kensington-kaset-campus-tel-0999983897---4327105",
    },
    "yieldScenario": {
        "beds": 2, "purchasePriceTHB": 3_790_000, "purchaseAreaSqm": 42.02,
        "saleSourceUrl": sale_sample["url"], "rentRateTHBPerSqmPerMonth": round(18_000 / 42, 2),
        "estimatedMonthlyRentTHB": estimated_rent, "rentSourceUrl": rent_sample["url"],
        "deductOneAgentMonth": True, "deductCommonFee": True,
        "annualCommonFeeTHB": round(annual_fee), "netAnnualYieldPercent": round(net_yield, 2),
        "formula": "((round((18000 / 42) * 42.02) * 11 - 40 * 42.02 * 12) / 3790000) * 100",
    },
}
(ROOT / "reports" / "kensington-kaset-campus-enrichment-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatIds": PROJECT_IDS, "saleTHB": 3_790_000, "saleAreaSqm": 42.02, "rentTHB": 18_000, "rentAreaSqm": 42, "netYieldPercent": round(net_yield, 2)}, ensure_ascii=False))
