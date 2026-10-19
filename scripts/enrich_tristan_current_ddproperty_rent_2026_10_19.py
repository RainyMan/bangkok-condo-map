"""Add a current, direct DDproperty rental sample to Tristan."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3299
PROJECT_NAME = "Tristan"
CHECKED_AT = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/tristan-qgokep"
DD_RENT_LISTING = "https://www.ddproperty.com/en/property/tristan-sukhumvit-39-bangkok-for-rent-10784405"
PROPERTYHUB_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-tristan-condominium--baf90a18"


def load_js_array(filename: str, variable: str) -> tuple[str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript array format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_js_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix, encoding="utf-8")


def upsert(rows: list[dict], record: dict) -> None:
    index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record


rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 55_000,
    "minimum": 55_000,
    "minimumArea": 153,
    "minimumSampleUpdated": "2026-10-05",
    "averageSqm": round(55_000 / 153),
    "minimumSqm": round(55_000 / 153, 2),
    "minimumSqmSampleUpdated": "2026-10-05",
    "asOf": CHECKED_AT,
    "sourceName": "DDproperty 單筆出租掛牌",
    "source": DD_RENT_LISTING,
    "minimumSourceUrl": DD_RENT_LISTING,
    "minimumSqmSourceUrl": DD_RENT_LISTING,
    "byBedroom": {
        "3": {
            "count": 1,
            "minimum": 55_000,
            "area": 153,
            "minimumSqm": round(55_000 / 153, 2),
            "minimumSourceUrl": DD_RENT_LISTING,
            "minimumSqmSourceUrl": DD_RENT_LISTING,
        }
    },
    "samples": [{
        "id": "10784405",
        "price": 55_000,
        "area": 153,
        "priceSqm": round(55_000 / 153, 2),
        "beds": 3,
        "roomType": "3BR",
        "title": "Tristan · 3 房 · 153 ㎡ · ฿55,000/月",
        "url": DD_RENT_LISTING,
        "sourceName": "DDproperty",
        "projectName": "Tristan Condominium Sukhumvit 39",
        "updated": "2026-10-05",
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_project_name_address_room_count_area_and_direct_ddproperty_listing",
        "listingStatus": "availability_unconfirmed_update_under_30d",
        "verificationNote": "DDproperty 單筆頁列出 Tristan Condominium、3 房、153㎡、฿55,000/月，地址 23/1 Sukhumvit 39；頁面標示 2026-10-05 刊登。PropertyHub 專案出租頁目前顯示無匹配房源；此筆由 DDproperty 直接頁核實，仍需向刊登者確認現況。",
    }],
}
prefix, rows, suffix = load_js_array("bangkok-manual-market-samples.js", "window.BANGKOK_MANUAL_MARKET_SAMPLES")
upsert(rows, {"hipflatId": PROJECT_ID, "name": PROJECT_NAME, "rent": rent})
save_js_array("bangkok-manual-market-samples.js", prefix, rows, suffix)

prefix, rows, suffix = load_js_array("bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS")
previous = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), {})
crosscheck = {
    **previous,
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": CHECKED_AT,
    "sourceName": "DDproperty 單筆出租與 PropertyHub 專案頁核對",
    "projectSourceUrl": HIPFLAT,
    "rent": {
        "activeListingCount": 1,
        "sourceUrl": DD_RENT_LISTING,
        "propertyHubProjectUrl": PROPERTYHUB_RENT_PROJECT,
        "listings": [{
            "id": "10784405",
            "price": 55_000,
            "area": 153,
            "priceSqm": round(55_000 / 153, 2),
            "bedrooms": 3,
            "listedAt": "2026-10-05",
            "url": DD_RENT_LISTING,
            "listingStatus": "availability_unconfirmed_update_under_30d",
        }],
        "note": "DDproperty 目前有一筆 3 房租盤，直接頁刊登日為 2026-10-05；PropertyHub 專案出租頁目前顯示無匹配房源。僅將 DDproperty 直接頁這筆列為租樣本。",
    },
    "availabilitySources": [
        {"sourceName": "DDproperty 租屋單筆頁", "url": DD_RENT_LISTING, "statusLabel": "3 房、153㎡、฿55,000/月，刊登日 2026-10-05；尚未向刊登者確認在架狀態。"},
        {"sourceName": "PropertyHub 專案出租頁", "url": PROPERTYHUB_RENT_PROJECT, "statusLabel": "目前顯示無匹配出租物件。"},
    ],
    "yieldStatus": "not_calculated_same_bedroom_rent_missing",
    "yieldNote": "目前核對到的租盤為三房，現有最低出售基準為兩房；不混用房型計算預設兩房投報。",
}
upsert(rows, crosscheck)
save_js_array("bangkok-market-crosschecks.js", prefix, rows, suffix)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
replacements = {
    "bangkok-manual-market-samples.js?v=20261019b-thippharoek-dated-rent-sample": "bangkok-manual-market-samples.js?v=20261019c-tristan-ddproperty-rent",
    "bangkok-market-crosschecks.js?v=20261019b-thippharoek-stale-rent-crosscheck": "bangkok-market-crosschecks.js?v=20261019c-tristan-ddproperty-rent-check",
}
for old, new in replacements.items():
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
    "rentSample": {"rentThbPerMonth": 55_000, "areaSqm": 153, "rentThbPerSqmMonth": round(55_000 / 153, 2), "bedrooms": 3, "listedAt": "2026-10-05", "sourceUrl": DD_RENT_LISTING},
    "yield": {"calculated": False, "reason": "The verified rental is 3-bedroom; this project’s lowest purchase baseline is 2-bedroom, so no same-bedroom default yield is available."},
    "limitation": "DDproperty provides the direct current listing; PropertyHub’s project rent page currently shows no matched rental units. Availability remains unconfirmed with the advertiser.",
}
(REPORTS / "tristan-current-ddproperty-rent-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "rentThbPerMonth": 55_000, "areaSqm": 153, "bedrooms": 3, "sameBedroomYield": "not calculated; current sale baseline is two-bedroom"}))
