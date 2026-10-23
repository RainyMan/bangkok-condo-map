"""Refresh verified listing availability for 31 Residence."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
CHECKED = "2026-10-23"
PROJECT_ID = 3006
PROJECT = "31 Residence"
SALE_PROJECT_URL = "https://www.ddproperty.com/en/project/6787-31-residence"
RENT_PROJECT_URL = "https://www.ddproperty.com/en/condo-for-rent/at-31-residence-6787"


def read_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript data format in {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def write_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


prefix, rows, suffix = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
project = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if not project or project.get("projectName") != PROJECT:
    raise RuntimeError("31 Residence crosscheck row not found; no data changed")

project["asOf"] = CHECKED
project["sourceName"] = "DDproperty / PropertyHub / Hipflat"
project["sale"] = {
    "activeListingCount": 0,
    "sourceUrl": SALE_PROJECT_URL,
    "note": (
        "DDproperty 專案頁於本次核查仍顯示 For Sale (0)，沒有可核實的現行出售單筆掛牌；"
        "PropertyHub 專案出售頁亦顯示無匹配房源。沒有出售基準，不計投報率。"
    ),
}
project["rent"]["activeListingCount"] = 3
project["rent"]["sourceUrl"] = RENT_PROJECT_URL
project["rent"]["note"] = (
    "DDproperty 專案出租結果頁顯示 3 筆在架掛牌；三筆直接物件頁於本次核查均可開啟，"
    "均標示 31 Residence、3 房，租金 ฿84,000–฿95,000/月、面積 186–270㎡。"
    "租盤資料已核對，但因沒有出售樣本而不計投報率。"
)
for row in project["rent"].get("listings", []):
    if row.get("id") == "11088237":
        row["priceSqm"] = round(row["price"] / row["area"], 2)
    elif row.get("id") == "60002949":
        row["priceSqm"] = round(row["price"] / row["area"], 2)
    elif row.get("id") == "60247061":
        row["priceSqm"] = round(row["price"] / row["area"], 2)

project["availabilitySources"] = [
    {
        "sourceName": "DDproperty 專案出售頁",
        "url": SALE_PROJECT_URL,
        "statusLabel": "本次頁面核查顯示 For Sale (0)；沒有本案直接售盤。",
    },
    {
        "sourceName": "PropertyHub 出售專案頁",
        "url": "https://propertyhub.in.th/en/condo-for-sale/project-31-residence",
        "statusLabel": "專案頁顯示沒有匹配出售掛牌。",
    },
    {
        "sourceName": "DDproperty 專案出租結果頁",
        "url": RENT_PROJECT_URL,
        "statusLabel": "本次頁面核查列 3 筆在架出租掛牌，全部標為 31 Residence。",
    },
    *[
        {
            "sourceName": f"DDproperty 出租單筆 {sample['id']}",
            "url": sample["url"],
            "statusLabel": f"{sample['bedrooms']} 房 · {sample['area']}㎡ · ฿{sample['price']:,}/月 · 刊登日 {sample['listedAt']}；本次頁面核查可開啟。",
        }
        for sample in project["rent"].get("listings", [])
    ],
]
project["yieldStatus"] = "no_current_sale_listing"
project["yieldNote"] = "租盤有 3 筆直接物件頁，但 DDproperty 專案售盤為 0，無購入價依據，不計投報率。"
write_array("bangkok-market-crosschecks.js", prefix, rows, suffix)

REPORTS.mkdir(exist_ok=True)
report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED,
    "sale": {"activeListingCount": 0, "projectPage": SALE_PROJECT_URL},
    "rent": {
        "activeListingCount": 3,
        "projectPage": RENT_PROJECT_URL,
        "listings": project["rent"].get("listings", []),
    },
    "yieldStatus": project["yieldStatus"],
    "yieldNote": project["yieldNote"],
    "sourceObservation": "DDproperty pages returned in the research session were indexed four days before the check; all three direct rental pages remained accessible.",
}
(REPORTS / "31-residence-market-check-2026-10-23.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "checkedAt": CHECKED, "sale": 0, "rent": 3, "yield": project["yieldStatus"]}, ensure_ascii=False))
