"""Attach linked two-bedroom sale/rent samples and recalculate the ROI baseline."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKED = "2026-10-19"
PROJECT_ID = 4403
NAME = "Lumpini Place Narathiwat 24"
SALE_URL = "https://www.ddproperty.com/en/property/lumpini-place-narathiwas-24-bangkok-for-sale-11085613"
RENT_URL = "https://propertyhub.in.th/listings/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-lumpini-place-narathiwas-24-%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%99%E0%B8%8A%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%B5-id-2279348---5369115"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/lumpini-place-narathiwat-24-u80uthee12e9tl4h7atl3714713eecu2"
DD_PROJECT_URL = "https://www.ddproperty.com/en/condo-for-sale/at-lumpini-place-narathiwas-24-492"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/lumpini-place-narathiwas-24"
PROPERTYHUB_RENT_FEED = "https://propertyhub.in.th/en/condo-for-rent/%E0%B8%A3%E0%B8%9E-%E0%B9%80%E0%B8%8B%E0%B8%99%E0%B8%95%E0%B9%8C%E0%B8%AB%E0%B8%A5%E0%B8%B8%E0%B8%A2%E0%B8%AA%E0%B9%8C/142"


def load_array(filename: str, symbol: str) -> tuple[Path, str, list[dict]]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    marker = f"window.{symbol} = "
    start = text.index(marker) + len(marker)
    rows, _ = json.JSONDecoder().raw_decode(text[start:])
    return path, text, rows


def write_array(path: Path, text: str, symbol: str, rows: list[dict]) -> None:
    marker = f"window.{symbol} = "
    start = text.index(marker)
    data_start = start + len(marker)
    _, end = json.JSONDecoder().raw_decode(text[data_start:])
    updated = text[:data_start] + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + text[data_start + end:]
    path.write_text(updated, encoding="utf-8", newline="")


def sample(listing_id: str, kind: str, price: int, area: float, url: str, source: str, updated: str, title: str) -> dict:
    return {
        "id": listing_id,
        "kind": kind,
        "price": price,
        "area": area,
        "priceSqm": round(price / area),
        "beds": 2,
        "roomType": "2BR",
        "title": title,
        "url": url,
        "sourceName": source,
        "projectName": NAME,
        "updated": updated,
        "checkedAt": CHECKED,
        "matchedBy": "exact_project_feed_and_direct_listing_id",
        "listingStatus": "active_as_listed",
    }


sale = sample("11085613", "sale", 4_800_000, 70, SALE_URL, "DDproperty", "2026-09-30",
              "2 bedrooms, 70 sqm, ฿4,800,000; shown on project feed refreshed Sep 30, 2026")
rent = sample("5369115", "rent", 20_000, 73, RENT_URL, "PropertyHub", "2026-10-15",
              "2 bedrooms, 73 sqm, ฿20,000/month; refreshed Oct 15, 2026")

manual_path, manual_text, manual_rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": NAME, "asOf": CHECKED}
    manual_rows.append(manual)
manual["name"] = NAME
manual["asOf"] = CHECKED
manual["fee"] = {
    "rate": 35,
    "status": "public",
    "note": "Hipflat 專案頁公開管理費 ฿35/㎡/月；請向管委會確認最新費率。",
    "source": "https://www.hipflat.co.th/en/projects/lumpini-place-narathiwas-24-ensvqa",
}
for kind, listing in (("sale", sale), ("rent", rent)):
    market = manual.setdefault(kind, {})
    samples = market.setdefault("samples", [])
    samples[:] = [row for row in samples if str(row.get("id")) != listing["id"] and row.get("url") != listing["url"]]
    samples.append(listing)
    market.update({
        "count": max(int(market.get("count", 0)), 1),
        "observedCount": max(int(market.get("observedCount", 0)), 1),
        "countKind": "manual_verified_listing",
        "asOf": CHECKED,
        "sourceName": listing["sourceName"],
    })

cross_path, cross_text, cross_rows = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next((row for row in cross_rows if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID}
    cross_rows.append(cross)
cross.update({
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "DDproperty / PropertyHub",
    "projectSourceUrl": DD_PROJECT_URL,
    "availabilitySources": [
        {"sourceName": "Hipflat", "url": HIPFLAT_URL, "statusLabel": "專案頁刊載售租房源與 ฿35/㎡管理費"},
        {"sourceName": "PropertyHub", "url": PROPERTYHUB_PROJECT_URL, "statusLabel": "專案掛牌交叉核對"},
        {"sourceName": "PropertyHub 租盤更新頁", "url": PROPERTYHUB_RENT_FEED, "statusLabel": "2 房租盤 ฿20,000/月、73㎡，更新 2026-10-15"},
    ],
    "sale": {"activeListingCount": 14, "sourceUrl": DD_PROJECT_URL, "samples": [{"url": SALE_URL, "price": 4_800_000, "area": 70, "bedrooms": 2, "priceSqm": 68_571, "listedAt": "2026-09-30"}]},
    "rent": {"sourceUrl": PROPERTYHUB_PROJECT_URL, "samples": [{"url": RENT_URL, "price": 20_000, "area": 73, "bedrooms": 2, "priceSqm": 274, "listedAt": "2026-10-15"}]},
})

write_array(manual_path, manual_text, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)
write_array(cross_path, cross_text, "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html, count_manual = re.subn(r"bangkok-manual-market-samples\.js\?v=[^\"']+", "bangkok-manual-market-samples.js?v=20261019-lumpini-2br-lowest-listings", html, count=1)
html, count_cross = re.subn(r"bangkok-market-crosschecks\.js\?v=[^\"']+", "bangkok-market-crosschecks.js?v=20261019-lumpini-2br-crosscheck", html, count=1)
html, count_app = re.subn(r"app\.js\?v=[^\"']+", "app.js?v=20261019-merge-bedroom-summaries-with-direct-lows-v144", html, count=1)
if (count_manual, count_cross, count_app) != (1, 1, 1):
    raise RuntimeError("Could not update all cache-busters")
index_path.write_text(html, encoding="utf-8", newline="")

print("Updated project 4403 with direct 2BR listing evidence.")
print("Selected sale: THB 4,800,000 / 70 sqm = THB 68,571/sqm.")
print("Rent rate: THB 20,000 / 73 sqm = THB 274/sqm/month; modeled at 70 sqm = THB 19,178/month.")
print("Gross annual yield: 4.79%; net after one broker month and THB 35/sqm/month fee: 3.78%.")
