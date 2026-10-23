"""Document project-name and address collisions for Hipflat project 3315."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3315
PROJECT = "Tropical Garden"
CHECKED_AT = "2026-10-23"
HIPFLAT = "https://www.hipflat.co.th/en/projects/tropical-garden-gaozvo"
DD_PROJECT = "https://www.ddproperty.com/en/project/9401-tropical-garden"
DD_COLLISION = "https://www.ddproperty.com/en/property/tropical-garden-bangkok-for-sale-500532493"
PH_COLLISION = "https://propertyhub.in.th/en/listings/1bed-1bath-mrt-bang-o-54sqm-thb-30-000-mo-fl-6-siam-oriental-tropical-garden-bangkok---6369063"
SODA_DIRECTORY = "https://soda.red/projects/thailand/bangkok-province?page=26"


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


cross_prefix, cross_rows, cross_suffix = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "Hipflat",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": HIPFLAT,
        "note": "Hipflat Bangkok 專案頁目前沒有可用房源。DDproperty 的 Bangkok 專案摘要雖列出 85㎡、฿4.6m 與 ฿5.3m 的舊參考單位，但沒有可直達的個別掛牌，不能當成現行出售樣本。",
        "listings": [],
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": HIPFLAT,
        "note": "Hipflat Bangkok 專案頁目前沒有可用房源，未找到可確認為該 Bangkok 專案的現行租盤。",
        "listings": [],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat Bangkok 專案頁", "url": HIPFLAT, "statusLabel": "目前顯示沒有可用房源；專案地址標為 Soi Phrom Chit。"},
        {"sourceName": "DDproperty Bangkok 專案頁", "url": DD_PROJECT, "statusLabel": "地址標為 4 Soi Sukhumvit 33；頁面列 85㎡、฿4.6m／฿5.3m 參考單位，無個別掛牌連結，舊資料不納入樣本。"},
        {"sourceName": "DDproperty 同名單筆掛牌", "url": DD_COLLISION, "statusLabel": "雖有 Bangkok 地址字樣，內文寫 Pratumnak、Pattaya，屬異地同名案，排除。"},
        {"sourceName": "PropertyHub 同名單筆掛牌", "url": PH_COLLISION, "statusLabel": "專案名為 Siam Oriental Tropical Garden，位置 Bang Lamung、Chonburi，屬芭達雅案，排除。"},
        {"sourceName": "SODA.RED 專案目錄", "url": SODA_DIRECTORY, "statusLabel": "列 Tropical Garden Condominium 地址為 31 Soi Phrom Chit，與 DDproperty Bangkok 專案頁的 Sukhumvit 33 門牌不同。"},
    ],
    "yieldStatus": "not_calculated_no_verified_direct_sale_or_rent",
    "yieldNote": "未找到可確認屬於此 Bangkok 專案的現行出售及出租單筆掛牌；已識別的同名 DDproperty 與 PropertyHub 房源實為芭達雅專案，故不計投報率。",
}
existing = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing is None:
    cross_rows.append(crosscheck)
else:
    existing.update(crosscheck)
save_array("bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "verified": False,
        "reason": "The sources identify different streets and public geocoding resolves only to road geometry, not a building entrance or parcel.",
        "hipflatAddress": "Soi Phrom Chit, Khlong Tan Nuea, Vadhana, Bangkok 10110",
        "ddPropertyAddress": "4 Soi Sukhumvit 33, Bangkok 10110",
        "thirdPartyDirectoryAddress": "31 Soi Phrom Chit, Khlong Tan Nuea, Watthana, Bangkok 10110",
        "osmStreetResults": [
            {"query": "31 Soi Phrom Chit, Khlong Tan Nuea, Watthana, Bangkok 10110", "lat": 13.7372291, "lng": 100.5699003, "featureType": "road geometry; not a building point", "url": "https://nominatim.openstreetmap.org/search?q=31%20Soi%20Phrom%20Chit%2C%20Khlong%20Tan%20Nuea%2C%20Watthana%2C%20Bangkok%2010110&format=html"},
            {"query": "4 Soi Sukhumvit 33, Bangkok 10110", "lat": 13.7349554, "lng": 100.5676396, "featureType": "road geometry; not a building point", "url": "https://nominatim.openstreetmap.org/search?q=4%20Soi%20Sukhumvit%2033%2C%20Bangkok%2010110&format=html"},
        ],
        "sources": [HIPFLAT, DD_PROJECT, SODA_DIRECTORY],
    },
    "saleAndRent": {"verifiedSaleListings": 0, "verifiedRentListings": 0, "yield": "not calculated"},
    "excludedNameCollisions": [
        {"url": DD_COLLISION, "reason": "The direct listing's body identifies Pratumnak, Pattaya despite Bangkok text in its heading/address."},
        {"url": PH_COLLISION, "reason": "The listing belongs to Siam Oriental Tropical Garden in Bang Lamung, Chonburi."},
    ],
    "sources": [HIPFLAT, DD_PROJECT, DD_COLLISION, PH_COLLISION, SODA_DIRECTORY],
}
(REPORTS / "tropical-garden-project-resolution-2026-10-23.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": "unverified; conflicting source addresses", "validSale": 0, "validRent": 0, "yield": "not calculated", "excludedCollisions": 2}, ensure_ascii=False))
