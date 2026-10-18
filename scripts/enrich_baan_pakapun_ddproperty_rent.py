"""Add current, directly linked DDproperty rental samples for Baan Pakapun."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3223
PROJECT_NAME = "Baan Pakapun"
CHECKED_AT = "2026-10-18"
RENT_PROJECT_URL = "https://www.ddproperty.com/en/condo-for-rent/at-baan-pakapun-6801"
RENT_FILTERED_URL = "https://www.ddproperty.com/en/condo-for-rent/at-baan-pakapun-6801/priced-over-40k-thb"
SALE_PROJECT_URL = "https://www.ddproperty.com/en/condo-for-sale/at-baan-pakapun-6801"

LISTINGS = [
    {
        "id": "11097960", "price": 70_000, "area": 140, "beds": 2,
        "roomType": "2BR", "updated": "2026-10-09",
        "title": "Baan Pakapun，2 房，140 ㎡，฿70,000/月",
        "url": "https://www.ddproperty.com/en/property/baan-pakapun-bangkok-for-rent-11097960",
    },
    {
        "id": "11097944", "price": 95_000, "area": 250, "beds": 3,
        "roomType": "3BR", "updated": "2026-10-07",
        "title": "Baan Pakapun，3 房，250 ㎡，฿95,000/月",
        "url": "https://www.ddproperty.com/en/property/baan-pakapun-bangkok-for-rent-11097944",
    },
    {
        "id": "60192183", "price": 140_000, "area": 385, "beds": 4,
        "roomType": "4BR Duplex/Penthouse", "updated": "2026-10-03",
        "title": "Baan Pakapun，4+1 房 Duplex，385 ㎡，฿140,000/月",
        "url": "https://www.ddproperty.com/en/property/baan-pakapun-bangkok-for-rent-60192183",
    },
]


def load_array(path: Path, symbol: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not read {symbol} from {path}")
    return json.loads(match.group(1))


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


manual_path = DIST / "bangkok-manual-market-samples.js"
projects = load_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
project = next((row for row in projects if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
if project is None:
    project = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
    projects.append(project)
project["asOf"] = CHECKED_AT

samples = [
    {
        **listing,
        "priceSqm": round(listing["price"] / listing["area"]),
        "sourceName": "DDproperty",
        "projectName": PROJECT_NAME,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_DDproperty_project_id_6801_and_project_address",
        "listingStatus": "active_as_listed",
    }
    for listing in LISTINGS
]
rent_rates = [listing["price"] / listing["area"] for listing in LISTINGS]
minimum_total = min(LISTINGS, key=lambda row: row["price"])
minimum_rate = min(LISTINGS, key=lambda row: row["price"] / row["area"])
by_bedroom: dict[str, dict] = {}
for listing in LISTINGS:
    key = str(listing["beds"])
    rate = listing["price"] / listing["area"]
    by_bedroom[key] = {
        "count": 1,
        "minimum": listing["price"],
        "area": listing["area"],
        "minimumSqm": rate,
        "averageSqm": rate,
        "sourceUrl": listing["url"],
        "minimumSqmSourceUrl": listing["url"],
    }
project["rent"] = {
    "count": len(LISTINGS),
    "observedCount": len(LISTINGS),
    "countKind": "manual_verified_listing",
    "average": round(sum(row["price"] for row in LISTINGS) / len(LISTINGS)),
    "minimum": minimum_total["price"],
    "minimumArea": minimum_total["area"],
    "minimumSampleUpdated": minimum_total["updated"],
    "averageSqm": round(sum(rent_rates) / len(rent_rates)),
    "minimumSqm": min(rent_rates),
    "minimumSqmSampleUpdated": minimum_rate["updated"],
    "asOf": CHECKED_AT,
    "sourceName": "DDproperty 個別出租掛牌",
    "source": RENT_PROJECT_URL,
    "minimumSourceUrl": minimum_total["url"],
    "minimumSqmSourceUrl": minimum_rate["url"],
    "samples": samples,
    "byBedroom": by_bedroom,
}
save_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", projects)

availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
with availability_path.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
    columns = list(rows[0]) if rows else [
        "hipflat_id", "condo", "checked_at", "market", "status",
        "verification_note", "source_1", "source_2", "source_3",
    ]
rows = [row for row in rows if row.get("hipflat_id") != str(PROJECT_ID)]
rows.extend([
    {
        "hipflat_id": str(PROJECT_ID),
        "condo": PROJECT_NAME,
        "checked_at": CHECKED_AT,
        "market": "rent",
        "status": "direct_listing_cross_checked_active_as_listed",
        "verification_note": (
            "DDproperty 精確專案頁的三張可見卡片均列出地址 26 Soi Methi Niwet、專案 Baan Pakapun，"
            "房型／面積／月租分別為 2房 140㎡ ฿70,000、3房 250㎡ ฿95,000、4+1房 duplex 385㎡ ฿140,000；"
            "單筆頁面可開啟，發布日期為 2026-10-03 至 2026-10-09。未聯絡刊登者確認空置。"
        ),
        "source_1": RENT_PROJECT_URL,
        "source_2": LISTINGS[0]["url"],
        "source_3": LISTINGS[2]["url"],
    },
    {
        "hipflat_id": str(PROJECT_ID),
        "condo": PROJECT_NAME,
        "checked_at": CHECKED_AT,
        "market": "sale",
        "status": "no_active_listing_found",
        "verification_note": (
            "DDproperty 精確專案出售頁於 2026-10-18 顯示未找到掛牌，專案頁亦標示 For Sale (0)；"
            "Hipflat 專案摘要沒有出售起價，因此不補造售價或投報率。"
        ),
        "source_1": SALE_PROJECT_URL,
        "source_2": "https://www.ddproperty.com/en/project/6801-baan-pakapun",
        "source_3": "https://www.hipflat.co.th/en/projects/baan-pakapan-hcpziy",
    },
])
with availability_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "status": "verified",
        "source": "https://www.thaigerproperty.com/projects/thailand/bangkok/khlong-toei/khlong-tan/baan-pakapun",
        "corroboratedBy": "https://www.hipflat.co.th/en/projects/baan-pakapan-hcpziy",
    },
    "rentalListings": samples,
    "rentalSummary": {
        "count": len(LISTINGS),
        "averageMonthlyRentThb": project["rent"]["average"],
        "minimumMonthlyRentThb": minimum_total["price"],
        "minimumRentPsmThb": round(min(rent_rates), 2),
        "averageRentPsmThb": round(sum(rent_rates) / len(rent_rates), 2),
    },
    "saleAvailability": {
        "status": "no_active_listing_found",
        "source": SALE_PROJECT_URL,
        "projectSource": "https://www.ddproperty.com/en/project/6801-baan-pakapun",
    },
    "roi": {
        "status": "not_calculated",
        "reason": "DDproperty 精確出售專案頁沒有現行掛牌，Hipflat 也沒有出售起價；缺少購入價格基準。",
    },
}
report_path = ROOT / "reports" / "baan-pakapun-ddproperty-rent-2026-10-18.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "rentSamples": len(samples), "saleListings": 0, "report": str(report_path)}, ensure_ascii=False))
