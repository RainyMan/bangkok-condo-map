from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3433
NAME = "V One Tower"
AS_OF = "2026-10-19"
PROPERTYSCOUT = "https://propertyscout.co.th/en/bangkok/commercial/v-one-tower/"
OFFICIAL = "https://www.v-onetower.com/en/"
HIPFLAT = "https://www.hipflat.co.th/en/projects/v-one-tower-1a8clc4a119unlle431tlcnta3l4e41u"


def load_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot read {symbol} in {filename}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


coordinates = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinates = [row for row in coordinates if int(row.get("hipflatId", -1)) != PROJECT_ID]
coordinates.append({
    "hipflatId": PROJECT_ID,
    "name": NAME,
    "lat": 13.755878696690804,
    "lng": 100.57222081960728,
    "locationVerified": True,
    "sourceName": "PropertyScout 專案頁地圖座標",
    "sourceUrl": PROPERTYSCOUT,
    "verificationSourceUrl": OFFICIAL,
    "verificationMethod": "PropertyScout exact project coordinates; V.ONE Tower official page confirms the same project and 123 Rama 9 Road address",
})
coordinates.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinates)

catalogue = load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
project = next(row for row in catalogue if int(row["id"]) == PROJECT_ID)
project.update({
    "locationVerified": True,
    "locationSourceUrl": PROPERTYSCOUT,
    "locationSourceName": "PropertyScout 專案頁",
    "locationVerificationSourceUrl": OFFICIAL,
    "locationVerificationMethod": "PropertyScout 座標與 V.ONE Tower 官方 123 Rama 9 Road 地址核對",
    "dataCompleteness": {"coordinates": True, "saleSample": False, "rentSample": False, "yield": False},
    "marketDataStatus": "commercial_project_no_verified_residential_sale_or_rent_samples",
})
save_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", catalogue)

crosschecks = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != PROJECT_ID]
crosschecks.append({
    "hipflatId": PROJECT_ID,
    "projectName": NAME,
    "asOf": AS_OF,
    "sourceName": "PropertyScout / V.ONE Tower 官方資料",
    "projectSourceUrl": HIPFLAT,
    "sale": {"activeListingCount": 0, "sourceUrl": PROPERTYSCOUT, "note": "尚未找到可核對為住宅 Condo 的出售單筆掛牌。"},
    "rent": {"activeListingCount": 0, "sourceUrl": PROPERTYSCOUT, "note": "PropertyScout 頁面目前有一筆 72 ㎡、฿86,400/月的商辦出租單位；因該頁將 V. One Tower 分類為 commercial，未當作住宅 Condo 租金樣本。"},
    "availabilitySources": [
        {"sourceName": "PropertyScout 專案頁", "url": PROPERTYSCOUT, "statusLabel": "專案地圖提供座標；頁面分類為商業辦公大樓，列有一筆商辦出租，不納入住宅 Condo 售租樣本。"},
        {"sourceName": "V.ONE Tower 官方網站", "url": OFFICIAL, "statusLabel": "官方地址為 123 Rama 9 Road, Huai Khwang, Bangkok 10310，與 PropertyScout 專案名稱及地區相符。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "未找到可核實的住宅 Condo 出售與出租單筆樣本；商辦出租資料不套用至住宅投報率。",
})
crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": AS_OF,
    "coordinate": {
        "status": "verified",
        "lat": 13.755878696690804,
        "lng": 100.57222081960728,
        "primarySource": PROPERTYSCOUT,
        "crossCheck": OFFICIAL,
        "method": "PropertyScout project point matched the official V.ONE Tower project and its 123 Rama 9 Road address.",
    },
    "residentialMarket": {
        "sale": "No direct residential listing verified.",
        "rent": "One PropertyScout office listing (72 sqm, THB 86,400/month) is excluded because the source classifies this as a commercial building.",
        "yield": "not calculated; no verified residential sale and rental listing pair.",
    },
}
(REPORTS / "v-one-tower-coordinate-and-market-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
for filename, version in (
    ("bangkok-verified-coordinates.js", "20261019-v-one-tower-3433"),
    ("bangkok-market-crosschecks.js", "20261019-v-one-tower-3433"),
):
    html, changed = re.subn(rf"{re.escape(filename)}\?v=[^\"']+", f"{filename}?v={version}", html, count=1)
    if changed != 1:
        raise RuntimeError(f"Could not update cache version for {filename}")
index_path.write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": report["coordinate"], "residentialYield": report["residentialMarket"]["yield"]}, ensure_ascii=False))
