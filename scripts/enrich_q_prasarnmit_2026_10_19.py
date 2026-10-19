"""Add source-linked Q Prasarnmit coordinates and bedroom-specific live samples."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
PROJECT_ID = 6370
NAME = "Q Prasarnmit"
HIPFLAT = "https://www.hipflat.co.th/projects/q-prasarnmit-gewivt"
CONDONAYOO = "https://www.condonayoo.com/q-prasarnmit/"
THINK_OF_LIVING = "https://thinkofliving.com/project/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/7198/"
PROPERTYHUB_PROJECT = "https://propertyhub.in.th/en/projects/q-prasarnmit"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/listings/lth11276-q-prasarnmit-for-sale-size-60-sqm-2-bed-2-bath-bts-phrom-phong-station-only-8-652-mb---4833341"
PROPERTYHUB_RENT_MIN_TOTAL = "https://propertyhub.in.th/en/listings/q-prasarnmit-full-featured-common-area--af0f0990---5518547"
PROPERTYHUB_RENT_MIN_RATE = "https://propertyhub.in.th/en/listings/2-br-condo-at-q-prasarnmit-near-mrt-phetchaburi-id-1807754--aefe094f---4680107"
HIPFLAT_SALE_2BR = "https://www.hipflat.co.th/ads/19344n4l8ue28nc983h41cn03u08l2eu"
GOOGLE_MAPS = "https://www.google.com/maps?q=13.743605,100.567028"


def load_array(filename: str, symbol: str):
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format in {filename}")
    return path, text[: match.start(1)], json.loads(match.group(1))


def save_array(path: Path, prefix: str, rows: list[dict], *, pretty: bool = False):
    body = json.dumps(rows, ensure_ascii=False, indent=2 if pretty else None,
                      separators=None if pretty else (",", ":"))
    path.write_text(prefix + body + ";\n", encoding="utf-8", newline="\n")


def sample(*, sample_id: str, kind: str, price: int, area: int, beds: int,
           url: str, title: str, source_name: str, updated: str | None,
           status: str, matched_by: str) -> dict:
    row = {
        "id": sample_id, "kind": kind, "price": price, "area": area,
        "priceSqm": round(price / area, 2), "beds": beds, "roomType": "2BR",
        "title": title, "url": url, "sourceName": source_name,
        "projectName": NAME, "checkedAt": AS_OF, "matchedBy": matched_by,
        "listingStatus": status,
    }
    if updated:
        row["updated"] = updated
    return row


sale_sample = sample(
    sample_id="19344n4l8ue28nc983h41cn03u08l2eu", kind="sale",
    price=8_200_000, area=60, beds=2, url=HIPFLAT_SALE_2BR,
    title="Q Prasarnmit，2 房，60㎡，฿8,200,000",
    source_name="Hipflat", updated=None,
    status="availability_unconfirmed_date_unknown",
    matched_by="exact_project_page_current_listing_card_and_direct_listing_link",
)
rent_min_total = sample(
    sample_id="5518547", kind="rent", price=45_000, area=60, beds=2,
    url=PROPERTYHUB_RENT_MIN_TOTAL,
    title="Q Prasarnmit，2 房，60㎡，฿45,000/月",
    source_name="PropertyHub", updated="2026-09-22",
    status="active_as_listed",
    matched_by="exact_project_page_listing_card_latest_refreshed_2026_09_22",
)
rent_min_rate = sample(
    sample_id="1807754", kind="rent", price=52_000, area=70, beds=2,
    url=PROPERTYHUB_RENT_MIN_RATE,
    title="Q Prasarnmit，2 房，70㎡，฿52,000/月",
    source_name="PropertyHub", updated="2026-09-22",
    status="active_as_listed",
    matched_by="exact_project_page_listing_card_latest_refreshed_2026_09_22",
)
sale_samples = [sale_sample]
rent_samples = [rent_min_total, rent_min_rate]

coordinates_path, coordinate_prefix, coordinates = load_array(
    "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = {int(row["hipflatId"]): row for row in coordinates}
coordinate_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": NAME,
    "lat": 13.743605, "lng": 100.567028, "locationVerified": True,
    "sourceName": "Google Maps 專案點位",
    "sourceUrl": GOOGLE_MAPS,
    "verificationSourceUrl": CONDONAYOO,
    "corroborationSourceUrl": THINK_OF_LIVING,
    "hipflatAddressSourceUrl": HIPFLAT,
    "verificationMethod": "Condonayoo 專案頁標示 Google Maps 座標 13.743605,100.567028；ThinkOfLiving 同案座標 13.743654,100.566932 互相印證。兩頁均指向 Sukhumvit 31 的 Q Prasarnmit，Hipflat 專案頁地址亦為 Q 31, Sukhumvit 31。",
    "checkedAt": AS_OF,
}
save_array(coordinates_path, coordinate_prefix,
           [coordinate_rows[key] for key in sorted(coordinate_rows)])

manual_path, manual_prefix, manual = load_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = {int(row["hipflatId"]): row for row in manual}
manual_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": NAME,
    "sale": {"samples": sale_samples},
    "rent": {"samples": rent_samples},
    "fee": {
        "rate": 100, "note": "PropertyHub 專案頁刊載管理費 ฿100/㎡/月",
        "source": PROPERTYHUB_PROJECT, "status": "published",
    },
    "completedYear": 2019,
    "completedYearSourceUrl": PROPERTYHUB_PROJECT,
}
save_array(manual_path, manual_prefix, [manual_rows[key] for key in sorted(manual_rows)])

# The current PropertyHub project page and Condonayoo agree on 2019; Hipflat
# still says Oct 2020. Record the two-source year in the compiled project row,
# preserving the disagreement in the cross-check record below.
ph_map = DIST / "bangkok-propertyhub-map.js"
ph_text = ph_map.read_text(encoding="utf-8")
old = '"id":6370,"lat":null,"lng":null,"completedYear":2020,"station":null'
new = ('"id":6370,"lat":null,"lng":null,"completedYear":2019,'
       f'"completedYearSourceUrl":"{PROPERTYHUB_PROJECT}","station":null')
if old not in ph_text:
    if new not in ph_text:
        raise RuntimeError("Expected Q Prasarnmit PropertyHub row was not found")
else:
    ph_map.write_text(ph_text.replace(old, new, 1), encoding="utf-8", newline="\n")

cross_path, cross_prefix, crosschecks = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = {int(row["hipflatId"]): row for row in crosschecks}
cross_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "Hipflat / PropertyHub / Google Maps / Condonayoo / ThinkOfLiving",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 8, "sourceUrl": HIPFLAT,
        "bedroomMinimums": {"2": {"price": 8_200_000, "area": 60,
                                      "sourceUrl": HIPFLAT_SALE_2BR}},
        "note": "Hipflat 專案頁列出 8 筆出售，兩房最低掛牌為 ฿8,200,000／60㎡；直接房源連結附於樣本。掛牌頁未提供更新時間，仍應向刊登者確認可售狀態。PropertyHub 的兩房最低掛牌為 ฿8,652,000／60㎡，高於 Hipflat 樣本。",
    },
    "rent": {
        "activeListingCount": 46, "sourceUrl": HIPFLAT,
        "listings": rent_samples,
        "note": "Hipflat 專案頁顯示 ฿45,000／60㎡（฿750／㎡）與 ฿34,000／72㎡（฿472／㎡）等兩房掛牌；低單價一筆的出租來源另標示 2026-11-15 起可入住，故投報採用 PropertyHub 於 2026-09-22 更新的兩房 ฿52,000／70㎡（฿742.86／㎡）作為目前可租低單價樣本。PropertyHub 同日更新兩房 ฿45,000／60㎡掛牌，供最低總租金參考。",
        "lowestRoomRateUsedForYield": 742.86,
        "lowestRoomRateSourceUrl": PROPERTYHUB_RENT_MIN_RATE,
    },
    "fee": {"rate": 100, "unit": "THB/sqm/month", "sourceUrl": PROPERTYHUB_PROJECT},
    "completionYear": {
        "selected": 2019, "sourceUrl": PROPERTYHUB_PROJECT,
        "corroboratingSourceUrl": CONDONAYOO,
        "conflictingSourceUrl": HIPFLAT,
        "note": "PropertyHub 專案頁與 Condonayoo 標示 2019；Hipflat 標示 2020，保留此來源差異。",
    },
    "coordinates": {
        "lat": 13.743605, "lng": 100.567028,
        "sourceUrl": GOOGLE_MAPS,
        "verificationSourceUrl": CONDONAYOO,
        "corroborationSourceUrl": THINK_OF_LIVING,
    },
    "yieldStatus": "calculated_from_lowest_two_bedroom_sale_and_current_two_bedroom_rent_rate",
    "yieldInputs": {
        "purchasePrice": 8_200_000, "purchaseArea": 60,
        "rentPerSqmPerMonth": 742.86, "monthlyRentEstimate": 44_571.43,
        "managementFeePerSqmPerMonth": 100,
        "deductOneAgentMonth": True, "deductManagementFee": True,
        "netAnnualYieldPercent": round(((742.86 * 60 * 11 - 100 * 60 * 12) / 8_200_000) * 100, 2),
    },
}
save_array(cross_path, cross_prefix,
           [cross_rows[key] for key in sorted(cross_rows)], pretty=True)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html = html.replace(
    "bangkok-verified-coordinates.js?v=20261019-sathit-google-place",
    "bangkok-verified-coordinates.js?v=20261019-q-prasarnmit-map-pin",
).replace(
    "bangkok-manual-market-samples.js?v=20261019-sathit-hipflat-rent-samples",
    "bangkok-manual-market-samples.js?v=20261019-q-prasarnmit-two-bedroom-listings",
).replace(
    "bangkok-market-crosschecks.js?v=20261019-sathit-rent-no-sale-check",
    "bangkok-market-crosschecks.js?v=20261019-q-prasarnmit-yield-sources",
).replace(
    "app.js?v=20261019-lowest-two-bedroom-roi-v190",
    "app.js?v=20261019-q-prasarnmit-listings-v191",
)
index_path.write_text(html, encoding="utf-8", newline="\n")

report = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": AS_OF,
    "coordinates": {"lat": 13.743605, "lng": 100.567028,
                    "googleMaps": GOOGLE_MAPS,
                    "condonayoo": CONDONAYOO,
                    "thinkOfLiving": THINK_OF_LIVING},
    "sale": {"lowestTwoBedroom": sale_sample,
             "propertyHubComparison": {"price": 8_652_000, "area": 60,
                                       "url": PROPERTYHUB_SALE}},
    "rent": {"lowestCurrentRateTwoBedroom": rent_min_rate,
             "lowestTotalTwoBedroom": rent_min_total,
             "futureAvailableLowerRate": {"price": 34_000, "area": 72,
                                           "rate": 472,
                                           "availableFrom": "2026-11-15",
                                           "url": "https://www.hipflat.co.th/ads/8at04ca08cllh11332l4n8tu3u0hea32"}},
    "fee": {"rate": 100, "source": PROPERTYHUB_PROJECT},
    "yield": cross_rows[PROJECT_ID]["yieldInputs"],
    "completionYear": cross_rows[PROJECT_ID]["completionYear"],
}
(ROOT / "reports" / "q-prasarnmit-market-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"project": NAME, "coordinate": [13.743605, 100.567028],
                  "saleSample": sale_sample, "rentSamples": rent_samples,
                  "yield": cross_rows[PROJECT_ID]["yieldInputs"]}, ensure_ascii=True))
