"""Add verified Building H location, direct two-bedroom samples, and yield."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3662
NAME = "Happy Condo Ladprao 101 Building H"
AS_OF = "2026-10-20"
HIPFLAT = "https://www.hipflat.co.th/en/projects/happy-condo-ladprao-101-building-h-rbmbrd"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-happy-condo-ladprao-101"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-happy-condo-ladprao-101"
SALE_URL = "https://propertyhub.in.th/en/listings/for-sell-condo-happy-condo-ladprao-101-building-h-floor-4-2-bed-room-room-size-62-sqm--bc9009e7---6366489"
RENT_URL = "https://propertyhub.in.th/en/listings/for-rent-happy-condo-ladprao-101-2-bedrooms-2-bathrooms-62-3-sq-m-4th-floor-building-h-22-000-thb---6170152"
BAM_URL = "https://www.bam.co.th/en/npa/property/62596"
MAP_URL = "https://maps.google.com/?q=13.788325%2C100.629008"
LAT, LNG = 13.788325, 100.629008
SALE_PRICE, SALE_AREA = 3_100_000, 62.0
RENT_PRICE, RENT_AREA = 22_000, 62.3
FEE_RATE = 35.0
rent_rate = RENT_PRICE / RENT_AREA
estimated_monthly_rent = rent_rate * SALE_AREA
annual_fee = FEE_RATE * SALE_AREA * 12
yield_after_agent = (estimated_monthly_rent * 11 - annual_fee) / SALE_PRICE * 100
yield_without_agent = (estimated_monthly_rent * 12 - annual_fee) / SALE_PRICE * 100


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise ValueError(f"Unexpected {symbol} format")
    return filename, json.loads(match.group(2)), match.group(3)


def save_array(filename: str, symbol: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


coordinate = {
    "hipflatId": PROJECT_ID,
    "name": NAME,
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "BAM 資產管理公司／Google Maps 專案點位",
    "sourceUrl": BAM_URL,
    "verificationSourceUrl": HIPFLAT,
    "mapUrl": MAP_URL,
    "verificationMethod": "exact_parent_condo_google_maps_pin; parent_complex_pin_not_building_h_entrance",
    "note": "Google Maps pin is the Happy Condo Ladprao 101 complex location from BAM's exact-project asset page; it is a campus-level point, not a surveyed Building H entrance.",
}
filename, coordinates, suffix = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
coordinates.append(coordinate)
coordinates.sort(key=lambda row: int(row["hipflatId"]))
save_array(filename, "BANGKOK_VERIFIED_COORDINATES", coordinates, suffix)

sale_sample = {
    "id": "6366489", "price": SALE_PRICE, "area": SALE_AREA, "priceSqm": round(SALE_PRICE / SALE_AREA),
    "beds": 2, "roomType": "2BR", "title": f"{NAME}，2 房，62 ㎡，฿3,100,000",
    "url": SALE_URL, "sourceName": "PropertyHub", "updated": "2026-10-19T17:30:00+07:00",
    "checkedAt": AS_OF, "matchedBy": "exact_building_h_project_card_and_direct_listing",
    "listingStatus": "active_as_listed",
}
rent_sample = {
    "id": "6170152", "price": RENT_PRICE, "area": RENT_AREA, "priceSqm": round(RENT_PRICE / RENT_AREA),
    "beds": 2, "roomType": "2BR", "title": f"{NAME}，2 房，62.3 ㎡，฿22,000/月",
    "url": RENT_URL, "sourceName": "PropertyHub", "updated": "2026-10-19T10:25:00+07:00",
    "checkedAt": AS_OF, "matchedBy": "exact_building_h_project_card_and_direct_listing",
    "listingStatus": "active_as_listed",
}
markets = {
    "hipflatId": PROJECT_ID,
    "name": NAME,
    "sale": {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": SALE_PRICE, "minimum": SALE_PRICE, "minimumArea": SALE_AREA,
        "minimumSampleUpdated": "2026-10-19", "averageSqm": round(SALE_PRICE / SALE_AREA),
        "minimumSqm": round(SALE_PRICE / SALE_AREA), "minimumSqmSampleUpdated": "2026-10-19",
        "asOf": AS_OF, "sourceName": "PropertyHub 直接掛牌",
        "source": PROPERTYHUB_SALE, "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL, "samples": [sale_sample],
        "byBedroom": {"2": {"count": 1, "minimum": SALE_PRICE, "area": SALE_AREA,
                              "minimumArea": SALE_AREA, "minimumSqm": SALE_PRICE / SALE_AREA,
                              "priceSqm": SALE_PRICE / SALE_AREA, "sourceUrl": SALE_URL,
                              "minimumSourceUrl": SALE_URL, "minimumSqmSourceUrl": SALE_URL}},
    },
    "rent": {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": RENT_PRICE, "minimum": RENT_PRICE, "minimumArea": RENT_AREA,
        "minimumSampleUpdated": "2026-10-19", "averageSqm": round(RENT_PRICE / RENT_AREA),
        "minimumSqm": round(RENT_PRICE / RENT_AREA, 2), "minimumSqmSampleUpdated": "2026-10-19",
        "asOf": AS_OF, "sourceName": "PropertyHub 直接掛牌",
        "source": PROPERTYHUB_RENT, "minimumSourceUrl": RENT_URL,
        "minimumSqmSourceUrl": RENT_URL, "samples": [rent_sample],
        "byBedroom": {"2": {"count": 1, "minimum": RENT_PRICE, "area": RENT_AREA,
                              "minimumArea": RENT_AREA, "minimumSqm": RENT_PRICE / RENT_AREA,
                              "priceSqm": RENT_PRICE / RENT_AREA, "sourceUrl": RENT_URL,
                              "minimumSourceUrl": RENT_URL, "minimumSqmSourceUrl": RENT_URL}},
    },
    "fee": {"rate": FEE_RATE, "status": "public", "source": BAM_URL,
            "note": "BAM exact-project asset page states common fee ฿35/㎡/month; verify current juristic-person billing."},
}
filename, rows, suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
rows = [row for row in rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
rows.append(markets)
rows.sort(key=lambda row: int(row["hipflatId"]))
save_array(filename, "BANGKOK_MANUAL_MARKET_SAMPLES", rows, suffix)

crosscheck = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "PropertyHub／BAM",
    "projectSourceUrl": HIPFLAT,
    "location": {"lat": LAT, "lng": LNG, "sourceUrl": MAP_URL,
                 "verificationSourceUrl": BAM_URL,
                 "note": "Google Maps project-campus pin; not a Building H entrance survey."},
    "sale": {"verifiedIndividualSamples": 1, "listings": [sale_sample], "sourceUrl": PROPERTYHUB_SALE,
             "note": "PropertyHub project page refreshed the Building H two-bedroom ฿3,100,000 / 62㎡ listing on 2026-10-19."},
    "rent": {"verifiedIndividualSamples": 1, "listings": [rent_sample], "sourceUrl": PROPERTYHUB_RENT,
             "note": "PropertyHub project page refreshed the Building H two-bedroom ฿22,000 / month / 62.3㎡ listing on 2026-10-19."},
    "availabilitySources": [
        {"sourceName": "Hipflat Building H project", "url": HIPFLAT, "statusLabel": "Confirms the Building H subproject identity."},
        {"sourceName": "BAM exact-project asset page", "url": BAM_URL, "statusLabel": "Confirms Happy Condo Ladprao 101 campus, 8-building/7-floor development and common fee ฿35/㎡/month; Google Maps button supplies the campus pin."},
        {"sourceName": "PropertyHub direct two-bedroom sale", "url": SALE_URL, "statusLabel": "Building H, 2 bedrooms, 62㎡, ฿3,100,000; project index last refreshed 2026-10-19."},
        {"sourceName": "PropertyHub direct two-bedroom rent", "url": RENT_URL, "statusLabel": "Building H, 2 bedrooms, 62.3㎡, ฿22,000/month; project index last refreshed 2026-10-19."},
    ],
    "yieldStatus": "calculated_current_same_bedroom_lowest_total_sale_and_rent_rate",
    "yieldEstimate": {
        "bedrooms": 2, "salePrice": SALE_PRICE, "saleAreaSqm": SALE_AREA,
        "saleSampleUrl": SALE_URL, "rentPrice": RENT_PRICE, "rentAreaSqm": RENT_AREA,
        "rentRatePerSqmPerMonth": round(rent_rate, 4),
        "estimatedMonthlyRentAtSaleArea": round(estimated_monthly_rent),
        "commonFeeBahtPerSqmPerMonth": FEE_RATE, "annualCommonFee": round(annual_fee),
        "netAnnualYieldWithOneAgentMonthPercent": round(yield_after_agent, 2),
        "netAnnualYieldWithoutAgentMonthPercent": round(yield_without_agent, 2),
        "formula": "((lowest 2BR rent / its area) × lowest 2BR sale area × (12 − 1 agent month) − fee per sqm × sale area × 12) / lowest 2BR sale total × 100",
        "rentSampleUrl": RENT_URL,
    },
    "yieldNote": "兩房最低出售掛牌為 ฿3,100,000／62㎡；同房型最低直接租盤為 ฿22,000／月／62.3㎡。按租金單價估算此出售面積月租 ฿21,894，採公開管理費 ฿35／㎡／月後，扣一個月仲介費淨年投報 6.93%，不扣仲介費 7.64%。未含稅、維修與交易成本；實際出租和管理費需向刊登者及管理處確認。",
}
filename, rows, suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
rows = [row for row in rows if int(row.get("hipflatId", -1)) != PROJECT_ID]
rows.append(crosscheck)
rows.sort(key=lambda row: int(row["hipflatId"]))
save_array(filename, "BANGKOK_MARKET_CROSSCHECKS", rows, suffix)

index_path = DIST / "index.html"
index_text = index_path.read_text(encoding="utf-8")
index_text = index_text.replace(
    'bangkok-verified-coordinates.js?v=20261020-q31-poly-chalee-coordinate-batch',
    'bangkok-verified-coordinates.js?v=20261020-happy-condo-building-h',
).replace(
    'bangkok-manual-market-samples.js?v=20261020-belgravia-3134',
    'bangkok-manual-market-samples.js?v=20261020-happy-condo-building-h',
).replace(
    'bangkok-market-crosschecks.js?v=20261020-belgravia-3134',
    'bangkok-market-crosschecks.js?v=20261020-happy-condo-building-h',
)
index_path.write_text(index_text, encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID, "project": NAME, "checkedAt": AS_OF,
    "coordinate": {"lat": LAT, "lng": LNG, "source": MAP_URL, "sourcePage": BAM_URL,
                   "verification": "Exact parent condo complex; map point is campus-level, not Building H entrance."},
    "sale": sale_sample, "rent": rent_sample,
    "commonFee": {"bahtPerSqmPerMonth": FEE_RATE, "source": BAM_URL,
                  "status": "Public project figure; verify current juristic-person billing."},
    "yield": crosscheck["yieldEstimate"], "sources": [HIPFLAT, BAM_URL, MAP_URL, PROPERTYHUB_SALE, PROPERTYHUB_RENT, SALE_URL, RENT_URL],
}
(ROOT / "reports/happy-condo-ladprao-101-building-h-market-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": [LAT, LNG], "sale": SALE_PRICE,
                  "saleArea": SALE_AREA, "rent": RENT_PRICE, "rentArea": RENT_AREA,
                  "yieldAfterAgentPercent": round(yield_after_agent, 2),
                  "yieldWithoutAgentPercent": round(yield_without_agent, 2)}, ensure_ascii=False))
