"""Record independently checked current availability for LK Tower."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = 3004
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/lk-tower-yvbgnf"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-lk-tower---20199"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-lk-tower---20199"
SCANCONDO_SALE = "https://eng.scancondo.com/buy-sell/condo/Condo-LK-Tower"
SCANCONDO_RENT = "https://eng.scancondo.com/rent-condo/Condo-LK-Tower"
FAZWAZ = "https://www.fazwaz.co.th/โครงการ/กรุงเทพมหานคร/บึงกุ่ม/นวลจันทร์/แอล-เค-ทาวเวอร์"
SOURCES = [
    {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "頁面顯示目前無可用房源；專案資訊列 2021 年完工、8 層、340 戶。"},
    {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE, "statusLabel": "目前沒有匹配出售掛牌。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "目前沒有匹配出租掛牌。"},
    {"sourceName": "Scancondo 出售頁", "url": SCANCONDO_SALE, "statusLabel": "專案頁標示本案目前沒有空置出售物件；附近樓盤不納入本案。"},
    {"sourceName": "Scancondo 出租頁", "url": SCANCONDO_RENT, "statusLabel": "專案頁標示本案目前沒有空置出租物件；附近樓盤不納入本案。"},
    {"sourceName": "FazWaz 專案頁", "url": FAZWAZ, "statusLabel": "目前未列出售或出租掛牌。"},
]

path = ROOT / "dist/bangkok-market-crosschecks.js"
text = path.read_text(encoding="utf-8")
match = re.fullmatch(r"(window\.BANGKOK_MARKET_CROSSCHECKS\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
if not match:
    raise RuntimeError("Unexpected cross-check data format")
rows = json.loads(match.group(2))
record = {
    "hipflatId": PROJECT_ID,
    "projectName": "LK Tower",
    "asOf": CHECKED_AT,
    "sourceName": "Hipflat / PropertyHub 多平台核對",
    "projectSourceUrl": HIPFLAT,
    "sale": {"activeListingCount": 0, "sourceUrl": PROPERTYHUB_SALE, "note": "核對 Hipflat、PropertyHub、Scancondo 與 FazWaz 後，未找到可核實的本案現行出售單筆掛牌；附近專案掛牌排除。"},
    "rent": {"activeListingCount": 0, "sourceUrl": PROPERTYHUB_RENT, "note": "核對 Hipflat、PropertyHub、Scancondo 與 FazWaz 後，未找到可核實的本案現行出租單筆掛牌；附近專案掛牌排除。"},
    "availabilitySources": SOURCES,
    "yieldStatus": "not_calculated",
    "yieldNote": "沒有本案現行出售與出租單筆樣本，不能建立可靠的購入價或租金基準，因此不計投報率。",
}
index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if index is None:
    rows.append(record)
else:
    rows[index] = record
path.write_text(match.group(1) + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + match.group(3), encoding="utf-8")

report = {
    "hipflatId": PROJECT_ID,
    "project": "LK Tower",
    "checkedAt": CHECKED_AT,
    "identity": {
        "hipflatProjectUrl": HIPFLAT,
        "address": "Nuan Chan Road, Nuan Chan, Bueng Kum, Bangkok 10230",
        "coordinates": {"lat": 13.82200134, "lng": 100.6426991, "source": "https://www.home.co.th/condo/lk-tower-10919", "verification": HIPFLAT},
        "completedYear": 2021,
        "floors": 8,
        "units": 340,
    },
    "availability": {
        "sale": {"activeListingCount": 0, "checkedSources": [HIPFLAT, PROPERTYHUB_SALE, SCANCONDO_SALE, FAZWAZ]},
        "rent": {"activeListingCount": 0, "checkedSources": [HIPFLAT, PROPERTYHUB_RENT, SCANCONDO_RENT, FAZWAZ]},
        "excluded": "Nearby project listings displayed on Scancondo are not LK Tower units and are excluded.",
    },
    "yield": {"calculated": False, "reason": "No verified current sale or rent unit exists to establish matched price and rent inputs."},
    "sources": SOURCES,
}
(ROOT / "reports/lk-tower-market-availability-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Recorded six source-linked availability checks; kept sale, rent and ROI unavailable without matched units.")
