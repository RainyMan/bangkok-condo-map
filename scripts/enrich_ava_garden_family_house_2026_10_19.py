"""Verify Ava Garden Family House's location and project facts; record listing gaps."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3289
PROJECT_NAME = "Ava Garden Family House"
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/ava-garden-family-house-vhniib"
THINK_OF_LIVING = "https://thinkofliving.com/project/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/2432/"
DD_PROJECT = "https://www.ddproperty.com/en/project/2432-ava-garden-family-house"
DD_STATUS = "https://www.ddproperty.com/en/reviews/2432-ava-garden-family-house"
HOME_PROJECT = "https://www.home.co.th/condo/ava-garden-family-house-4837"


def load_js_array(filename: str, variable: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript array format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_js_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


def upsert(rows: list[dict], record: dict) -> None:
    index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record


# ThinkOfLiving publishes longitude, latitude in that order. DDproperty and
# Hipflat independently identify the same Lat Phrao 71 / Soi Nak Niwat 13
# project, developer, completion year, floor count, and unit count.
coordinates = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "lat": 13.80122,
    "lng": 100.604207,
    "locationVerified": True,
    "sourceName": "ThinkOfLiving 專案 Google Maps 座標",
    "sourceUrl": THINK_OF_LIVING,
    "verificationSourceUrl": DD_PROJECT,
    "corroborationSourceUrl": DD_PROJECT,
    "verificationMethod": "ThinkOfLiving 專案頁列 100.604207, 13.80122；DDproperty 專案頁與 Hipflat 文字均核對為 Soi Nak Niwat 13、Lat Phrao 71、Siam Amago、5 層、45 戶。Hipflat 摘要地址的 Huai Khwang 行政區與兩個獨立專案來源不一致，採用相符的 Lat Phrao 點位及地址。",
}
prefix, rows, suffix = load_js_array("bangkok-verified-coordinates.js", "window.BANGKOK_VERIFIED_COORDINATES")
upsert(rows, coordinates)
save_js_array("bangkok-verified-coordinates.js", prefix, rows, suffix)

prefix, projects, suffix = load_js_array("bangkok-catalogue.js", "window.BANGKOK_CONDO_CATALOGUE")
project = next(row for row in projects if int(row["id"]) == PROJECT_ID)
project.update({
    "address": "Soi Nak Niwat 13 (Soi Pengsuk), Lat Phrao 71 Road, Lat Phrao, Bangkok 10230",
    "completedYear": 2013,
    "completedYearSourceUrl": DD_PROJECT,
    "units": 45,
    "floors": 5,
    "marketDataStatus": "no_verified_current_individual_listings",
    "dataCompleteness": {"coordinates": True, "saleSample": False, "rentSample": False, "yield": False},
})
save_js_array("bangkok-catalogue.js", prefix, projects, suffix)

crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": CHECKED_AT,
    "sourceName": "DDproperty / Hipflat / ThinkOfLiving 專案與掛牌核對",
    "projectSourceUrl": DD_STATUS,
    "sale": {
        "activeListingCount": 0,
        "sourceUrl": DD_STATUS,
        "note": "DDproperty 專案狀態頁顯示 0 間出售；未找到可核對本案名稱、地址及單位資訊的現行單筆出售掛牌。Home.co.th 的 ฿1,720,000 是已結案新建案起價，不能當作二手房樣本。",
    },
    "rent": {
        "activeListingCount": 0,
        "sourceUrl": DD_STATUS,
        "note": "DDproperty 專案狀態頁顯示 0 間出租；未找到可核對本案名稱、地址及單位資訊的現行單筆出租掛牌。",
    },
    "availabilitySources": [
        {"sourceName": "DDproperty 專案掛牌狀態", "url": DD_STATUS, "statusLabel": "專案頁列出 0 間出售、0 間出租；未加入其他相似名稱專案的房源。"},
        {"sourceName": "DDproperty 專案資料", "url": DD_PROJECT, "statusLabel": "專案為 Soi Nak Niwat 13，2013 完工、5 層、45 戶；行情資料顯示無交易數據。"},
        {"sourceName": "Hipflat 專案資料", "url": HIPFLAT, "statusLabel": "專案描述為 Soi Nak Niwat 13、Lat Phrao，2 棟、5 層、45 戶、2013 年完工；頁首地理標籤與地址摘要有區域衝突，已以 DDproperty 與 ThinkOfLiving 交叉核對。"},
        {"sourceName": "ThinkOfLiving 座標與專案資料", "url": THINK_OF_LIVING, "statusLabel": "專案頁提供 Google Maps 點位 13.80122, 100.604207，並列 2013 完工、5 層、45 戶。"},
        {"sourceName": "Home.co.th 新案資料", "url": HOME_PROJECT, "statusLabel": "列出專案已結案及 ฿1,720,000 歷史新案起價；未將該起價作為二手售價樣本。"},
        {"sourceName": "PropertyHub 相似名稱排除", "url": "https://propertyhub.in.th/projects/avacas-garden-family-house", "statusLabel": "Avacas Garden Family House 位於 Ram Inthra 123 / Min Buri，與本案 Lat Phrao 地址不同，排除其掛牌。"},
    ],
    "yieldStatus": "not_calculated_no_verified_current_sale_or_rent_samples",
    "yieldNote": "沒有本案可核實的現行單筆出售與出租樣本，不能可靠計算投報率。",
}
prefix, rows, suffix = load_js_array("bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS")
upsert(rows, crosscheck)
save_js_array("bangkok-market-crosschecks.js", prefix, rows, suffix)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
revisions = {
    "bangkok-catalogue.js?v=20261019-esta-bliss-enrichment-3473": "bangkok-catalogue.js?v=20261019-ava-garden-address-completion",
    "bangkok-verified-coordinates.js?v=20261019-v-one-tower-3433": "bangkok-verified-coordinates.js?v=20261019-ava-garden-thinkofliving-point",
    "bangkok-market-crosschecks.js?v=20261019-supalai-park-ekamai-current-2br": "bangkok-market-crosschecks.js?v=20261019-ava-garden-market-audit",
}
for old, new in revisions.items():
    if old in html:
        html = html.replace(old, new, 1)
    elif new not in html:
        raise RuntimeError(f"Expected cache tag not found: {old}")
index_path.write_text(html, encoding="utf-8")

REPORTS.mkdir(exist_ok=True)
report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "coordinates": {"lat": coordinates["lat"], "lng": coordinates["lng"], "sourceUrl": THINK_OF_LIVING, "crosscheckUrl": DD_PROJECT, "hipflatUrl": HIPFLAT},
    "projectFacts": {"address": project["address"], "completedYear": 2013, "floors": 5, "units": 45, "sourceUrl": DD_PROJECT, "corroboratingSourceUrl": HIPFLAT},
    "availability": {"saleVerifiedCurrentListings": 0, "rentVerifiedCurrentListings": 0, "statusSourceUrl": DD_STATUS},
    "yield": {"calculated": False, "reason": crosscheck["yieldNote"]},
    "exclusions": ["Home.co.th historical new-project starting price is not a resale listing.", "PropertyHub Avacas Garden Family House is a different project in Min Buri."],
    "locationConflict": "Hipflat page header/address summary includes Wang Thonglang / Huai Khwang while its project narrative names Soi Nak Niwat 13, Lat Phrao; DDproperty and ThinkOfLiving agree on the Lat Phrao project and location.",
}
(REPORTS / "ava-garden-family-house-enrichment-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [coordinates["lat"], coordinates["lng"]], "completion": 2013, "floors": 5, "units": 45, "currentSamples": {"sale": 0, "rent": 0}, "yield": "not calculated"}, ensure_ascii=True))
