"""Record current sale availability evidence for Raintree Village Apartment."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3028
PROJECT_NAME = "Raintree Village Apartment"
AS_OF = "2026-10-19"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/raintree-village-apartment-uiptlk"
DD_PROJECT_URL = "https://www.ddproperty.com/en/project/6616-raintree-village-apartment"
DD_RENT_URL = "https://www.ddproperty.com/en/property-for-rent/at-raintree-village-apartment-6616"
RENT_LISTING_URL = "https://www.ddproperty.com/en/property/raintree-village-apartment-bangkok-for-rent-11599801"


def update_array(path: Path, variable: str, record: dict) -> None:
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


record = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": AS_OF,
    "sourceName": "DDproperty / Hipflat",
    "projectSourceUrl": DD_PROJECT_URL,
    "sale": {
        "activeListingCount": 0,
        "sourceUrl": DD_PROJECT_URL,
        "note": "DDproperty 專案頁核對為 0 間出售。Hipflat 最新英文專案頁亦未列出售單位。舊搜尋快取曾摘要 ฿13,500,000 / 100㎡，但沒有個別售屋連結且目前無法驗證在架，不列作現行樣本。",
    },
    "rent": {
        "activeListingCount": 13,
        "sourceUrl": DD_RENT_URL,
        "listings": [
            {
                "listingId": "11599801",
                "price": 95_000,
                "area": 268,
                "bedrooms": 3,
                "listedAt": "2026-10-12",
                "url": RENT_LISTING_URL,
                "sourceName": "DDproperty",
                "priceSqm": 354.48,
            }
        ],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 英文專案頁", "url": HIPFLAT_URL, "statusLabel": "最新頁面列出租屋，未列現行出售單位。"},
        {"sourceName": "DDproperty 專案頁", "url": DD_PROJECT_URL, "statusLabel": "顯示 0 間出售；出租頁另有掛牌。"},
        {"sourceName": "DDproperty 出租清單", "url": DD_RENT_URL, "statusLabel": "專案出租頁顯示 13 筆；個別房源頁於 2026-10-12 更新。"},
        {"sourceName": "舊 Hipflat 搜尋快取", "url": HIPFLAT_URL, "statusLabel": "曾摘要 ฿13,500,000 / 100㎡，但未提供可核實的個別出售頁；不作現行售價。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "尚未核實現行出售掛牌，沒有購入價格基準；保留已核對租盤，不估算投報率。",
}
update_array(ROOT / "dist/bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS", record)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": AS_OF,
    "saleAvailability": {
        "ddproperty": {"url": DD_PROJECT_URL, "displayedActiveListings": 0, "checkedFromCurrentProjectPage": True},
        "hipflat": {"url": HIPFLAT_URL, "currentEnglishProjectPageShowsSaleListing": False},
        "oldHipflatSearchSnapshot": {
            "priceTHB": 13_500_000,
            "areaSqm": 100,
            "bedrooms": 2,
            "sourceUrl": HIPFLAT_URL,
            "limitation": "Search cache approximately three months old and no direct unit listing URL was discoverable; excluded as current sample.",
        },
        "decision": "No current sale sample added; do not calculate ROI until a direct, verifiable sale listing appears.",
    },
    "rent": {
        "source": RENT_LISTING_URL,
        "projectListingPage": DD_RENT_URL,
        "priceTHBPerMonth": 95_000,
        "areaSqm": 268,
        "bedrooms": 3,
        "priceTHBPerSqmPerMonth": 354.48,
        "updatedAt": "2026-10-12",
        "status": "Direct DDproperty listing; exact project name and address match.",
    },
    "yield": {"calculated": False, "reason": "No current, source-linked sale unit is available for the purchase-price baseline."},
    "sources": [HIPFLAT_URL, DD_PROJECT_URL, DD_RENT_URL, RENT_LISTING_URL],
}
(ROOT / "reports/raintree-village-apartment-sale-availability-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Recorded Raintree Village Apartment sale availability; retained the direct rent listing and withheld unsupported ROI.")
