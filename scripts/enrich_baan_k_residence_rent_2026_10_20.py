"""Add directly linked Baan K Residence rentals verified on Hipflat."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3188
PROJECT = "Baan K Residence"
CHECKED_AT = "2026-10-20"
HIPFLAT = "https://www.hipflat.co.th/projects/baan-k-residence-exzblv"
SIAM108 = "https://www.108siam.com/en/projects/thailand/bangkok/bang-rak/si-lom/baan-k-residence?eq=rent"

samples = [
    {
        "id": "47t40c8n88cec4978ueutchh3u02u982",
        "price": 48000,
        "area": 55,
        "priceSqm": 873,
        "beds": 1,
        "roomType": "1BR",
        "title": "Baan K Residence，1 房，55 ㎡，฿48,000/月",
        "url": "https://www.hipflat.co.th/ads/47t40c8n88cec4978ueutchh3u02u982",
        "sourceName": "Hipflat（刊登者：108Siam）",
        "projectName": PROJECT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_and_direct_listing_link",
        "listingStatus": "availability_unconfirmed_date_unknown",
        "verificationNote": "Hipflat 精確專案頁將此個別物件列為 Baan K Residence，1 房、55㎡、฿48,000/月，並連到此物件頁；108Siam 專案頁目前也列相同面積與租金的 1 房房源。個別物件未提供更新日，是否仍可租請向刊登者確認。",
    },
    {
        "id": "4lunl3478ll3l2a2en72l37l3u0heael",
        "price": 48000,
        "area": 50,
        "priceSqm": 960,
        "beds": 1,
        "roomType": "1BR",
        "title": "Baan K Residence，1 房，50 ㎡，฿48,000/月",
        "url": "https://www.hipflat.co.th/ads/4lunl3478ll3l2a2en72l37l3u0heael",
        "sourceName": "Hipflat（刊登者：FazWaz）",
        "projectName": PROJECT,
        "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_and_direct_listing_link",
        "listingStatus": "availability_unconfirmed_date_unknown",
        "verificationNote": "Hipflat 精確專案頁將此個別物件列為 Baan K Residence，1 房、50㎡、฿48,000/月，並連到此物件頁；專案頁目前列兩筆出租。個別物件未提供更新日，是否仍可租請向刊登者確認。",
    },
]


def load_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_array(filename: str, prefix: str, rows: list[dict], suffix: str, compact: bool = False) -> None:
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, **options) + suffix, encoding="utf-8")


manual_prefix, manual_rows, manual_suffix = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": PROJECT}
    manual_rows.append(manual)
rent = {
    "count": 2,
    "observedCount": 2,
    "countKind": "manual_verified_listing",
    "average": 48000,
    "minimum": 48000,
    "minimumArea": 55,
    "averageSqm": 916,
    "minimumSqm": 873,
    "asOf": CHECKED_AT,
    "sourceName": "Hipflat 個別出租掛牌",
    "source": HIPFLAT,
    "minimumSourceUrl": samples[0]["url"],
    "minimumSqmSourceUrl": samples[0]["url"],
    "samples": samples,
    "byBedroom": {
        "1": {
            "count": 2,
            "minimum": 48000,
            "minimumArea": 55,
            "area": 55,
            "priceSqm": 873,
            "minimumSqm": 873,
            "averageSqm": 916,
            "sourceUrl": samples[0]["url"],
            "minimumSourceUrl": samples[0]["url"],
            "minimumSqmSourceUrl": samples[0]["url"],
        }
    },
}
manual.update({"asOf": CHECKED_AT, "rent": rent})
save_array("bangkok-manual-market-samples.js", manual_prefix, manual_rows, manual_suffix, compact=True)

cross_prefix, cross_rows, cross_suffix = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "asOf": CHECKED_AT,
    "sourceName": "Hipflat / 108Siam",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "observedCount": 0,
        "sourceUrl": HIPFLAT,
        "note": "本次核對的 Hipflat 專案頁列 2 筆出租、未列出售物件；另查 108Siam 專案頁僅列出租單位。尚無可核實出售物件，故不計投報率。",
        "listings": [],
    },
    "rent": {
        "activeListingCount": 2,
        "displayedResultCount": 2,
        "observedCount": 2,
        "sourceUrl": HIPFLAT,
        "note": "Hipflat 精確專案頁列出 2 筆 1 房出租：฿48,000/月、55㎡（฿873/㎡/月）及 ฿48,000/月、50㎡（฿960/㎡/月），並提供各自的個別物件連結。108Siam 專案頁亦顯示目前有 2 筆 1 房出租，價格均為 ฿48,000/月。單筆更新日期未公開，實際空置狀態待刊登者確認。",
        "listings": [
            {
                "listingId": row["id"],
                "price": row["price"],
                "area": row["area"],
                "priceSqm": row["priceSqm"],
                "bedrooms": 1,
                "listedAt": "未提供更新日",
                "url": row["url"],
                "sourceName": row["sourceName"],
                "statusLabel": "專案頁列出租；單筆更新日及現況待確認",
            }
            for row in samples
        ],
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁／個別掛牌", "url": HIPFLAT, "statusLabel": "精確專案頁列兩筆 1 房出租，並可開啟個別房源。"},
        {"sourceName": "108Siam 專案頁", "url": SIAM108, "statusLabel": "專案頁列 2 筆出租：1 房 50㎡及 55㎡，均為 ฿48,000/月；未找到出售單位。"},
        {"sourceName": "Hipflat 1 房出租單筆（55㎡）", "url": samples[0]["url"], "statusLabel": "฿48,000/月、55㎡、1 房（฿873/㎡/月）；刊登更新日未提供，現況待確認。"},
        {"sourceName": "Hipflat 1 房出租單筆（50㎡）", "url": samples[1]["url"], "statusLabel": "฿48,000/月、50㎡、1 房（฿960/㎡/月）；刊登更新日未提供，現況待確認。"},
    ],
    "yieldStatus": "not_calculated_no_verified_sale_listing",
    "yieldNote": "已核實兩筆個別出租物件，但目前沒有可核實的出售掛牌，因此不估算投報率。",
}
existing = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if existing is None:
    cross_rows.append(crosscheck)
else:
    existing.update(crosscheck)
save_array("bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT,
    "checkedAt": CHECKED_AT,
    "coordinates": {"verified": True, "sourceUrl": "https://www.thaigerproperty.com/projects/thailand/bangkok/bang-rak/si-lom/baan-k-residence"},
    "rentSamples": samples,
    "saleStatus": "No sale listings shown on the checked Hipflat project page; no sale sample used.",
    "yieldStatus": "Not calculated: no verified sale listing.",
    "sources": [HIPFLAT, SIAM108],
    "notes": [
        "The two individual rent links are linked directly from Hipflat's exact project page; both bedroom count, area, and monthly rent are shown in its unit rows.",
        "108Siam's project page independently lists two 1-bedroom units at ฿48,000/month and gives the same 50 sqm and 55 sqm areas.",
        "Neither source provides a per-listing update date; current vacancy remains unconfirmed.",
    ],
}
(REPORTS / "baan-k-residence-rent-enrichment-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

html = (DIST / "index.html").read_text(encoding="utf-8")
html = html.replace("bangkok-manual-market-samples.js?v=20261020-duliya-place-market-4517", "bangkok-manual-market-samples.js?v=20261020-baan-k-rent-3188")
html = html.replace("bangkok-market-crosschecks.js?v=20261020-duliya-place-market-4517", "bangkok-market-crosschecks.js?v=20261020-baan-k-rent-3188")
(DIST / "index.html").write_text(html, encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "rentSamples": len(samples), "lowestRentTHB": 48000, "lowestRentAreaSqm": 55, "lowestRentRateTHBPerSqmMonth": round(48000 / 55, 2), "sale": "not found", "yield": "not calculated"}, ensure_ascii=False))
