"""Record a PropertyHub project/listing mismatch for UTD Aries."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3047
PROJECT_NAME = "UTD Aries Hotel & residence"
AS_OF = "2026-10-19"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/utd-aries-hotel-residence-yfpfkb"
PH_PROJECT_URL = "https://propertyhub.in.th/projects/utd-aries-hotel-residence"
PH_LISTING_URL = "https://propertyhub.in.th/en/listings/for-sale-condo-1-bedroom-at-la-green-hotel-residence---5893289"
RENT_URL = "https://www.hipflat.co.th/ads/874a40428anc71194c73nua13u0h14a2"


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
    "sourceName": "Hipflat / PropertyHub 交叉核對",
    "projectSourceUrl": HIPFLAT_URL,
    "sale": {
        "activeListingCount": 0,
        "sourceUrl": PH_PROJECT_URL,
        "note": "PropertyHub 專案頁雖列 1 筆出售，但其連結物件頁標題為 La Green Hotel & Residence，且內文地點寫 Bang Tao, Phuket，與 UTD Aries 的曼谷專案不符；排除該售盤。Hipflat 專案頁目前沒有出售單位。",
    },
    "rent": {
        "activeListingCount": 7,
        "sourceUrl": HIPFLAT_URL,
        "listings": [
            {
                "listingId": "U1366316",
                "price": 6_500,
                "area": 20,
                "bedrooms": 0,
                "listedAt": "2026-10-17",
                "url": RENT_URL,
                "sourceName": "Hipflat",
                "priceSqm": 325,
            }
        ],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT_URL, "statusLabel": "顯示 7 筆出租，未列出售單位。"},
        {"sourceName": "PropertyHub 專案頁", "url": PH_PROJECT_URL, "statusLabel": "顯示 1 筆出售，但所連物件頁與專案地點不符。"},
        {"sourceName": "PropertyHub 錯配物件頁", "url": PH_LISTING_URL, "statusLabel": "雖列 UTD Aries 關聯，但房源敘述地點為 Bang Tao, Phuket；排除為曼谷售盤。"},
        {"sourceName": "Hipflat 出租物件頁", "url": RENT_URL, "statusLabel": "Studio 20㎡、฿6,500/月；頁面更新日 2026-10-17。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "未找到可核實的現行出售物件；PropertyHub 唯一出售結果與專案地點不符，因此不建立購入價或投報率。",
}
update_array(ROOT / "dist/bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS", record)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": AS_OF,
    "projectLocation": {"hipflatUrl": HIPFLAT_URL, "location": "UTD Aries Soi On Nut 17 Yaek 16, Suan Luang, Bangkok 10250"},
    "saleAvailability": {
        "hipflat": {"url": HIPFLAT_URL, "displayedRentUnits": 7, "displayedSaleUnits": 0},
        "propertyHubProject": {"url": PH_PROJECT_URL, "displayedSaleUnits": 1},
        "propertyHubLinkedListing": {
            "url": PH_LISTING_URL,
            "listingId": "5893289",
            "shownPriceTHB": 5_500_000,
            "shownAreaSqm": 30,
            "mismatch": "The direct listing body says the property location is Bang Tao, Phuket, despite its project association showing UTD Aries Hotel & residence, Suan Luang, Bangkok.",
            "decision": "Exclude from Bangkok project sale samples and ROI.",
        },
        "decision": "No current sale sample verified for this Bangkok project.",
    },
    "rent": {
        "url": RENT_URL,
        "priceTHBPerMonth": 6_500,
        "areaSqm": 20,
        "roomType": "Studio",
        "priceTHBPerSqmPerMonth": 325,
        "updatedAt": "2026-10-17",
        "status": "Retain the existing direct Hipflat sample; it matches the exact project page.",
    },
    "yield": {"calculated": False, "reason": "No project-matched current sale listing is available for the purchase-price baseline."},
    "sources": [HIPFLAT_URL, PH_PROJECT_URL, PH_LISTING_URL, RENT_URL],
}
(ROOT / "reports/utd-aries-sale-listing-mismatch-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Recorded UTD Aries listing mismatch; preserved the verified Hipflat rent and withheld the mismatched sale from ROI.")
