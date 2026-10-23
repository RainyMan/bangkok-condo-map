"""Verify Haa Dao Condominium's map point and record current listing checks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3669
PROJECT = "Haa Dao Condominium"
CHECKED_AT = "2026-10-23"
HIPFLAT = "https://www.hipflat.co.th/en/projects/haa-dao-condominium-2144ll0n11e724ht77eec19cnu4a11h7"
FAZWAZ = "https://www.fazwaz.com/projects/thailand/bangkok/phaya-thai/sam-sen-nai/haa-dao-condominium"
TRIPADVISOR = "https://www.tripadvisor.com.sg/Restaurant_Review-g293916-d8734036-Reviews-Medium_Rare_Steak_Wine-Bangkok.html"
GOOGLE_MAPS = "https://maps.google.com/maps?daddr=12%2F1+Soi+Pradiphat+10%2C+Bangkok+10400+Thailand%4013.78959%2C100.54188&saddr="
LAT = 13.78959
LNG = 100.54188


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


coord_prefix, coord_rows, coord_suffix = load_array(
    "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"
)
coordinate = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT,
    "lat": LAT,
    "lng": LNG,
    "locationVerified": True,
    "sourceName": "Google Maps 地址釘點",
    "sourceUrl": GOOGLE_MAPS,
    "verificationSourceUrl": HIPFLAT,
    "corroborationSourceUrl": FAZWAZ,
    "verificationMethod": "Hipflat address identifies Above Medium Rare Residence, Pradiphat 10; FazWaz independently places Haa Dao 10m from Medium Rare Steak & Wine; TripAdvisor's Google Maps route for the venue at 12/1 Soi Pradiphat 10 resolves to 13.78959, 100.54188, within the stated 10m.",
        "asOf": CHECKED_AT,
}
existing_coordinate = next((row for row in coord_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing_coordinate is None:
    coord_rows.append(coordinate)
else:
    existing_coordinate.update(coordinate)
save_array("bangkok-verified-coordinates.js", coord_prefix, coord_rows, coord_suffix)

cross_prefix, cross_rows, cross_suffix = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "Hipflat / FazWaz",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": FAZWAZ,
        "note": "FazWaz 專案頁目前顯示 No Units Available、View All (0)；Hipflat 專案頁也顯示目前沒有可用房源。沒有找到可核實的現行出售單筆掛牌。",
        "listings": [],
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": FAZWAZ,
        "note": "FazWaz 專案頁目前顯示 No Units Available、View All (0)；Hipflat 專案頁也顯示目前沒有可用房源。沒有找到可核實的現行出租單筆掛牌。",
        "listings": [],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat Bangkok 專案頁", "url": HIPFLAT, "statusLabel": "目前沒有可用房源。"},
        {"sourceName": "FazWaz 專案頁", "url": FAZWAZ, "statusLabel": "No Units Available；View All (0)。專案資料標示 1992 年完工、2 層。"},
        {"sourceName": "Tripadvisor / Google Maps 地點", "url": TRIPADVISOR, "statusLabel": "Medium Rare Steak & Wine 地址為 12/1 Soi Pradiphat 10；Google Maps 路線座標 13.78959, 100.54188。FazWaz 指出其距 Haa Dao 約 10m。"},
    ],
    "yieldStatus": "not_calculated_no_current_direct_sale_or_rent",
    "yieldNote": "Hipflat 與 FazWaz 專案頁均沒有現行房源；沒有可比的出售與出租單筆樣本，不計投報率。",
}
existing_cross = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing_cross is None:
    cross_rows.append(crosscheck)
else:
    existing_cross.update(crosscheck)
save_array("bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "verified": True,
        "lat": LAT,
        "lng": LNG,
        "sourceUrl": GOOGLE_MAPS,
        "verificationSourceUrl": HIPFLAT,
        "corroborationSourceUrl": FAZWAZ,
        "method": coordinate["verificationMethod"],
    },
    "saleAndRent": {
        "verifiedSaleListings": 0,
        "verifiedRentListings": 0,
        "yield": "not calculated",
        "sources": [HIPFLAT, FAZWAZ],
    },
    "sourceNotes": [
        "Hipflat names the address as Above Medium Rare Residence, Pradiphat 10.",
        "FazWaz identifies Haa Dao Condominium in Sam Sen Nai, Bangkok and places Medium Rare Steak & Wine 10m from the project.",
        "Tripadvisor lists Medium Rare Steak & Wine at 12/1 Soi Pradiphat 10; its linked Google Maps route resolves to 13.78959, 100.54188.",
        "FazWaz currently says No Units Available and View All (0); no direct sale or rent listings were added.",
    ],
}
(REPORTS / "haa-dao-condominium-2026-10-23.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "lat": LAT, "lng": LNG, "coordinateStatus": "verified by address and nearby map pin", "saleListings": 0, "rentListings": 0, "yield": "not calculated"}, ensure_ascii=False))
