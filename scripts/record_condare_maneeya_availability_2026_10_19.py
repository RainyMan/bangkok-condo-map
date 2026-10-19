"""Record the current no-rent availability check for Condare Maneeya."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3022
PROJECT_NAME = "Condare Maneeya"
AS_OF = "2026-10-19"
HIPFLAT_URL = "https://www.hipflat.co.th/projects/condare-maneeya-vmdoxl"
PROPERTYHUB_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-condare-maneeya"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/en/projects/condare-maneeya"
OLD_SALE_URL = "https://www.rightmove.condothai.co.th/room/60158/Condare%20Maneeya/0/?distance=3"


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
    "sourceName": "PropertyHub",
    "projectSourceUrl": PROPERTYHUB_PROJECT_URL,
    "sale": {
        "activeListingCount": 1,
        "sourceUrl": PROPERTYHUB_PROJECT_URL,
        "note": "PropertyHub 專案資訊較舊，列出 1 筆出售；沒有取得近期更新的直接掛牌，不能判為現行可售。Hipflat 專案頁目前顯示無可用物件。",
        "historicalSamples": [
            {
                "price": 3_811_000,
                "area": 88.05,
                "beds": 2,
                "url": OLD_SALE_URL,
                "statusLabel": "2026-10-18 核對時來源未提供 30 日內更新日期；保留為未確認參考，不作為現行最低價或投報基準。",
            }
        ],
    },
    "rent": {
        "activeListingCount": 0,
        "sourceUrl": PROPERTYHUB_RENT_URL,
        "note": "PropertyHub 專案出租頁顯示 No matched properties for Rent；Hipflat 專案頁亦顯示目前沒有可用物件。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT_URL, "statusLabel": "目前沒有可用物件。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT_URL, "statusLabel": "未配對到出租房源；頁面快取較舊，需等下次更新再核對。"},
        {"sourceName": "PropertyHub 專案資訊", "url": PROPERTYHUB_PROJECT_URL, "statusLabel": "頁面資料列出 1 筆出售、0 筆出租；與 Hipflat 的現況文字不同，現行售租供給仍待新掛牌確認。"},
        {"sourceName": "Condothai 舊出售樣本", "url": OLD_SALE_URL, "statusLabel": "兩房 88.05㎡、฿3,811,000；無近期更新證據，僅保留歷史參考。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "目前沒有可核實的現行租金樣本；舊售屋樣本亦超過 30 日未更新，因此不計算或顯示投報率。",
}
update_array(ROOT / "dist/bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS", record)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": AS_OF,
    "availability": {
        "hipflatProjectPage": {"url": HIPFLAT_URL, "result": "The project page says no properties are currently available.", "sourceIndexAge": "about 3 weeks before 2026-10-19"},
        "propertyHubRentProjectPage": {"url": PROPERTYHUB_RENT_URL, "result": "No matched properties for Rent.", "sourceIndexAge": "about 3 months before 2026-10-19", "limitation": "Search index is older; treat as supporting absence evidence, not proof of live availability."},
        "propertyHubProjectOverview": {"url": PROPERTYHUB_PROJECT_URL, "displayedForSale": 1, "displayedForRent": 0, "sourceIndexAge": "about 3 months before 2026-10-19"},
    },
    "saleHistoricalSample": {
        "priceTHB": 3_811_000,
        "areaSqm": 88.05,
        "bedrooms": 2,
        "source": OLD_SALE_URL,
        "checkedAt": "2026-10-18",
        "status": "availability_unconfirmed_update_over_30d",
        "decision": "Keep only as unconfirmed historical context; do not use as current market price or ROI purchase baseline.",
    },
    "rent": {"currentSampleVerified": False, "decision": "Do not impute rent from nearby projects or a different property type."},
    "yield": {"calculated": False, "reason": "No current, source-linked rental unit was verified."},
    "sources": [HIPFLAT_URL, PROPERTYHUB_RENT_URL, PROPERTYHUB_PROJECT_URL, OLD_SALE_URL],
}
(ROOT / "reports/condare-maneeya-availability-check-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Recorded Condare Maneeya availability evidence; no current rent or ROI was added.")
