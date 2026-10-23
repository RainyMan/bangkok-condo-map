"""Record a checked no-listing state for The Sis Condominium without inventing samples."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dist" / "bangkok-market-crosschecks.js"
REPORT = ROOT / "reports" / "the-sis-condominium-market-availability-2026-10-23.json"
HIPFLAT_ID = 3820
HIPFLAT = "https://www.hipflat.co.th/en/projects/the-sis-condominium-yqeweo"
FAZWAZ = "https://www.fazwaz.co.th/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3/%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%99%E0%B8%84%E0%B8%A3/%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B9%81%E0%B8%84/%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B9%81%E0%B8%84%E0%B9%80%E0%B8%AB%E0%B8%99%E0%B8%B7%E0%B8%AD/%E0%B9%80%E0%B8%94%E0%B8%AD%E0%B8%B0-%E0%B8%8B%E0%B8%B4%E0%B8%AA-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B9%81%E0%B8%84"
THAILAND_PROPERTY = "https://www.thailand-property.com/condo/3968/the-sis-condominium"

text = PATH.read_text(encoding="utf-8")
match = re.search(r"window\.BANGKOK_MARKET_CROSSCHECKS\s*=\s*(\[.*\]);", text, re.S)
if not match:
    raise ValueError(f"Cannot parse {PATH}")
rows = json.loads(match.group(1))
sources = [
    {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "2026-10-23 核對頁面未列可用的出售或出租物件。"},
    {"sourceName": "FazWaz 專案頁", "url": FAZWAZ, "statusLabel": "2026-10-23 核對專案頁未列出售或出租掛牌。"},
    {"sourceName": "Thailand-Property 專案頁", "url": THAILAND_PROPERTY, "statusLabel": "專案頁顯示 0 間出售、0 間出租。"},
]
record = {
    "hipflatId": HIPFLAT_ID,
    "projectName": "The Sis Condominium",
    "asOf": "2026-10-23",
    "sourceName": "Hipflat / FazWaz / Thailand-Property availability check",
    "projectSourceUrl": HIPFLAT,
    "sale": {"activeListingCount": 0, "sourceUrl": HIPFLAT, "note": "本次核對 Hipflat、FazWaz 與 Thailand-Property，未找到可核實的本案現行出售單筆掛牌；不填售價樣本。"},
    "rent": {"activeListingCount": 0, "sourceUrl": HIPFLAT, "note": "本次核對 Hipflat、FazWaz 與 Thailand-Property，未找到可核實的本案現行出租單筆掛牌；不填租金樣本。"},
    "availabilitySources": sources,
    "yieldStatus": "not_calculated_no_current_sale_or_rent_listing",
    "yieldNote": "本次核對未找到可核實的現行出售與出租單筆掛牌，沒有同房型售租配對可依最低售價及最低租金估算投報率。",
}
existing_index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == HIPFLAT_ID), None)
if existing_index is None:
    rows.append(record)
else:
    rows[existing_index] = record
rows.sort(key=lambda row: int(row["hipflatId"]))
PATH.write_text("window.BANGKOK_MARKET_CROSSCHECKS=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
REPORT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": HIPFLAT_ID, "status": record["yieldStatus"], "sources": len(sources)}, ensure_ascii=False))
