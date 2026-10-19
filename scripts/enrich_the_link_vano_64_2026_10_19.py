from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"


def read_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    path = DIST / filename
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


project_id = 4271
name = "The Link Vano 64"
hipflat_url = "https://www.hipflat.co.th/en/projects/the-link-vano-64-yobsua"
propertyhub_project_url = "https://propertyhub.in.th/en/projects/the-link-vano-sukhumvit-64"
coordinate = {
    "hipflatId": project_id,
    "name": name,
    "lat": 13.68695128906525,
    "lng": 100.6063688211051,
    "locationVerified": True,
    "sourceName": "PropertyHub 專案頁（專案名稱與地址核對）",
    "sourceUrl": propertyhub_project_url,
    "verificationSourceUrl": hipflat_url,
    "verificationMethod": "exact_project_name_and_district_project_page_coordinates",
    "asOf": AS_OF,
}

sale_samples = [
    {
        "id": "60169385", "price": 2290000, "area": 36, "priceSqm": 63611,
        "beds": 1, "roomType": "1BR", "url": "https://www.ddproperty.com/en/property/the-link-vano-64-bangkok-for-sale-60169385",
        "title": "The Link Vano 64，1 房，36 ㎡，฿2,290,000",
        "sourceName": "DDproperty", "projectName": name, "checkedAt": AS_OF,
        "updated": "2026-09-23", "matchedBy": "exact_project_name_and_listing_address",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "500547096", "price": 4500000, "area": 60, "priceSqm": 75000,
        "beds": 2, "roomType": "2BR", "url": "https://www.ddproperty.com/en/property/the-link-vano-64-bangkok-for-sale-500547096",
        "title": "The Link Vano 64，2 房，60 ㎡，฿4,500,000",
        "sourceName": "DDproperty", "projectName": name, "checkedAt": AS_OF,
        "updated": "2026-10-05", "listedAt": "2026-09-11",
        "matchedBy": "exact_project_name_and_listing_address_reposted_on_project_results",
        "listingStatus": "active_as_listed",
    },
]
rent_samples = [
    {
        "id": "500590032", "price": 12000, "area": 36, "priceSqm": 333,
        "beds": 1, "roomType": "1BR", "url": "https://www.ddproperty.com/en/property/the-link-vano-64-bangkok-for-rent-500590032",
        "title": "The Link Vano 64，1 房，36 ㎡，฿12,000／月",
        "sourceName": "DDproperty", "projectName": name, "checkedAt": AS_OF,
        "updated": "2026-09-25", "matchedBy": "exact_project_name_and_listing_address",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "FX-001957", "price": 25000, "area": 61, "priceSqm": 410,
        "beds": 2, "roomType": "2BR", "url": "https://www.livinginsider.com/en/detail/condo-for-rent-condo-the-link-vano-sukhumvit-64-2bedroom-3236554",
        "title": "The Link Vano Sukhumvit 64，2 房，61 ㎡，฿25,000／月",
        "sourceName": "Livinginsider", "projectName": name, "checkedAt": AS_OF,
        "updated": "2026-09-25", "listedAt": "2026-09-19", "availableFrom": "2026-09-29",
        "matchedBy": "exact_project_name_and_listing_detail",
        "listingStatus": "active_as_listed",
    },
]

coordinate_rows = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = [row for row in coordinate_rows if int(row.get("hipflatId", 0)) != project_id]
coordinate_rows.append(coordinate)
coordinate_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinate_rows)

market_rows = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
existing = next((row for row in market_rows if int(row.get("hipflatId", 0)) == project_id), None)
if existing is None:
    existing = {"hipflatId": project_id, "name": name}
    market_rows.append(existing)
for kind, samples in (("sale", sale_samples), ("rent", rent_samples)):
    old_market = existing.get(kind) or {}
    by_url = {sample.get("url"): sample for sample in old_market.get("samples", []) if sample.get("url")}
    for sample in samples:
        by_url[sample["url"]] = sample
    combined = sorted(by_url.values(), key=lambda sample: (float(sample["price"]), sample["url"]))
    total = len(combined)
    low_total = min(combined, key=lambda sample: float(sample["price"]))
    low_sqm = min(combined, key=lambda sample: float(sample["price"]) / float(sample["area"]))
    by_bedroom = {}
    for beds in sorted({int(sample["beds"]) for sample in combined}):
        room_rows = [sample for sample in combined if int(sample["beds"]) == beds]
        room_total = min(room_rows, key=lambda sample: float(sample["price"]))
        room_sqm = min(room_rows, key=lambda sample: float(sample["price"]) / float(sample["area"]))
        by_bedroom[str(beds)] = {
            "count": len(room_rows),
            "minimum": room_total["price"],
            "area": room_total["area"],
            "minimumArea": room_total["area"],
            "priceSqm": round(float(room_total["price"]) / float(room_total["area"])),
            "minimumSqm": round(float(room_sqm["price"]) / float(room_sqm["area"])),
            "sourceUrl": room_total["url"],
            "minimumSourceUrl": room_total["url"],
            "minimumSqmSourceUrl": room_sqm["url"],
        }
    old_market.update({
        "count": total,
        "observedCount": total,
        "countKind": "manual_verified_listing",
        "average": round(sum(float(sample["price"]) for sample in combined) / total),
        "minimum": low_total["price"],
        "minimumArea": low_total["area"],
        "minimumSampleUpdated": low_total.get("updated"),
        "averageSqm": round(sum(float(sample["price"]) / float(sample["area"]) for sample in combined) / total),
        "minimumSqm": round(float(low_sqm["price"]) / float(low_sqm["area"])),
        "minimumSqmSampleUpdated": low_sqm.get("updated"),
        "asOf": AS_OF,
        "sourceName": "DDproperty、Livinginsider 個別掛牌",
        "source": propertyhub_project_url,
        "minimumSourceUrl": low_total["url"],
        "minimumSqmSourceUrl": low_sqm["url"],
        "samples": combined,
        "byBedroom": by_bedroom,
    })
    existing[kind] = old_market
existing["fee"] = {
    "rate": 40,
    "note": "DDproperty 專案資料公布的公共管理費；實際現行費率請向管委會確認。",
    "source": "https://www.ddproperty.com/en/property/the-link-vano-64-bangkok-for-sale-500547096",
    "status": "published_indicative",
}
market_rows.sort(key=lambda row: int(row["hipflatId"]))
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", market_rows)

purchase_price = 4500000
purchase_area = 60
rent_rate = 25000 / 61
monthly_rent = round(rent_rate * purchase_area)
annual_fee = 40 * purchase_area * 12
net_yield_with_agent_and_fee = ((monthly_rent * 11 - annual_fee) / purchase_price) * 100
report = {
    "hipflatId": project_id,
    "name": name,
    "asOf": AS_OF,
    "identityAndLocation": {
        "hipflatProjectUrl": hipflat_url,
        "propertyHubProjectUrl": propertyhub_project_url,
        "propertyHubProjectId": "1743",
        "coordinates": {"lat": coordinate["lat"], "lng": coordinate["lng"]},
        "coordinateMatch": "PropertyHub project page name, district and project address match the Hipflat project; embedded project coordinates",
    },
    "saleSamples": sale_samples,
    "rentSamples": rent_samples,
    "fee": existing["fee"],
    "yieldScenario": {
        "beds": 2,
        "purchasePriceTHB": purchase_price,
        "purchaseAreaSqm": purchase_area,
        "saleSourceUrl": sale_samples[1]["url"],
        "rentRateTHBPerSqmPerMonth": round(rent_rate, 2),
        "estimatedMonthlyRentTHB": monthly_rent,
        "rentSourceUrl": rent_samples[1]["url"],
        "deductOneAgentMonth": True,
        "annualCommonFeeTHB": annual_fee,
        "deductCommonFee": True,
        "netAnnualYieldPercent": round(net_yield_with_agent_and_fee, 2),
        "formula": "((round(25000 / 61 * 60) * 11 - 40 * 60 * 12) / 4500000) * 100",
    },
    "completionYearConflict": {
        "propertyHubProjectPage": 2014,
        "ddPropertyProjectSummaryAndListingMetadata": 2016,
        "status": "unresolved; completion year not changed automatically",
    },
}
report_path = ROOT / "reports" / "the-link-vano-64-enrichment-2026-10-19.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": project_id, "coordinateRows": len(coordinate_rows), "manualMarketProjects": len(market_rows), "saleSamples": len(sale_samples), "rentSamples": len(rent_samples), "yieldPercent": round(net_yield_with_agent_and_fee, 2), "report": str(report_path)}, ensure_ascii=False))