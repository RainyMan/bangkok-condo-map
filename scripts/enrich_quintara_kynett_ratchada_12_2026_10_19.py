"""Record a verified map point and resolve misattributed market leads for Quintara Kynett Ratchada 12."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3382
NAME = "Quintara Kynett Ratchada 12"
CHECKED = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/projects/quintara-kynett-ratchada-12-xlrzjc"
MAP_SOURCE = "https://thinkofliving.com/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/project/quintara-kynett-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2-12-599491/"
MAP_CORROBORATION = "https://www.homenayoo.com/quintara-kynett-ratchada-12/"
DD_PROJECT = "https://www.ddproperty.com/en/project/7445-quintara-kynett-ratchada-12"
DD_MISLINKED_SALE = "https://www.ddproperty.com/en/property/quintara-kynett-ratchada-12-bangkok-for-sale-500523860"
PROPERTYSCOUT_RENT = "https://propertyscout.co.th/en/1-br-condo-quintara-kynett-ratchada-12-near-mrt-huai-khwang-2236641/"
LIVINGINSIDER_RENT = "https://www.livinginsider.com/en/detail/condo-for-rent-condo-quintara-kynett-ratchada-12-studio-3207926"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-quintara-kynett-ratchada-12"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-quintara-kynett-ratchada-12"
FEE_SOURCE = "https://www.idealproperty.com.sg/quintara-kynett-ratchada-12/"


def load(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected data format: {filename} / {symbol}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save(filename: str, symbol: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix, encoding="utf-8")


coordinates = [
    {
        "hipflatId": PROJECT_ID,
        "name": NAME,
        "lat": 13.774717,
        "lng": 100.574669,
        "locationVerified": True,
        "sourceName": "ThinkOfLiving 專案 Google Maps 點位",
        "sourceUrl": MAP_SOURCE,
        "verificationSourceUrl": HIPFLAT,
        "verificationMethod": "exact_project_name_and_ratchadaphisek_12_address_cross_checked",
    }
]
prefix, rows, suffix = load("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if index is None:
    rows.append(coordinates[0])
else:
    rows[index] = coordinates[0]
save("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", prefix, rows, suffix)

# Keep the direct rent lead visible and source-linked, but do not promote it to
# current rental market data: its unit type conflicts across portals and its
# availability/update date is not confirmed.
rent_sample = {
    "id": "3207926",
    "price": 14_000,
    "area": 22,
    "priceSqm": 636,
    "roomType": "STUDIO_OR_ONE_BEDROOM_UNCONFIRMED",
    "title": "Quintara Kynett Ratchada 12，22㎡，3 樓，฿14,000/月",
    "url": LIVINGINSIDER_RENT,
    "sourceName": "LivingInsider",
    "projectName": NAME,
    "updated": "2026-08-30",
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_name_and_direct_listing_page",
    "listingStatus": "availability_unconfirmed_update_over_30d",
}
prefix, rows, suffix = load("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
entry = next((row for row in rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if entry is None:
    entry = {"hipflatId": PROJECT_ID, "name": NAME}
    rows.append(entry)
entry["completedYear"] = 2021
entry["completedYearSourceUrl"] = DD_PROJECT
entry["fee"] = {
    "rate": 55,
    "status": "historical_indicative",
    "note": "銷售資料所列管理費 ฿55/㎡/月，屬歷史專案資料；現行收費需向管委會確認。",
    "source": FEE_SOURCE,
}
rent = entry.setdefault("rent", {})
samples = rent.setdefault("samples", [])
samples[:] = [sample for sample in samples if sample.get("url") != LIVINGINSIDER_RENT]
samples.append(rent_sample)
save("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", prefix, rows, suffix)

prefix, rows, suffix = load("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
record = {
    "hipflatId": PROJECT_ID,
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "DDproperty / PropertyHub / LivingInsider",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 0,
        "sourceUrl": DD_PROJECT,
        "note": "DDproperty 專案頁的一張 ฿4,100,000 卡片雖掛在本案頁面，單筆內文與標題指向 Cool House Ratchada 12，排除為錯誤關聯。PropertyHub 專案頁目前無已核實的售盤。",
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 1,
        "sourceUrl": PROPERTYHUB_RENT,
        "listings": [
            {
                "id": "3207926",
                "price": 14_000,
                "area": 22,
                "priceSqm": 636,
                "bedrooms": None,
                "listedAt": "2026-08-30",
                "url": LIVINGINSIDER_RENT,
                "statusLabel": "直接頁列 22㎡／3 樓／฿14,000；超過 30 日未更新，房型另有 studio／1 房兩種描述，現況與房型待確認，不納入投報。",
            }
        ],
        "note": "保留可直達的出租物件頁，但不作為現行租金基準；PropertyScout 的同案 22㎡房源顯示租約至 2026-08，當前可租狀態未確認。",
    },
    "availabilitySources": [
        {"sourceName": "ThinkOfLiving 專案點位", "url": MAP_SOURCE, "statusLabel": "專案頁列 Google Maps 點位 13.774717, 100.574669；地址及 Hipflat 專案名稱一致。"},
        {"sourceName": "Homenayoo 地圖交叉核對", "url": MAP_CORROBORATION, "statusLabel": "另列 Google Maps 點位 13.774730, 100.574668；與主要點位約差 2 公尺。"},
        {"sourceName": "DDproperty 專案出售頁", "url": DD_PROJECT, "statusLabel": "專案頁顯示一筆掛牌；其連結單筆頁內容實際是 Cool House Ratchada 12，排除。"},
        {"sourceName": "DDproperty 錯誤關聯出售物件", "url": DD_MISLINKED_SALE, "statusLabel": "標題列 Quintara、฿4,100,000／50㎡，但物件內文標明 Cool House Ratchada 12，不當成本案售盤。"},
        {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE, "statusLabel": "核對時未找到本案可核實出售單筆掛牌。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "核對時未找到本案出租掛牌。"},
        {"sourceName": "LivingInsider 出租單筆頁", "url": LIVINGINSIDER_RENT, "statusLabel": "฿14,000/月、22㎡、3 樓；更新日 2026-08-30，超過 30 日。房型 studio 與 1 房來源描述不一，僅保留未確認樣本。"},
        {"sourceName": "PropertyScout 出租單筆頁", "url": PROPERTYSCOUT_RENT, "statusLabel": "同為 22㎡／฿14,500/月的 1 房頁面註明租約至 2026-08；與 LivingInsider 面積樓層吻合但租金、房型不同，可能為同一單位，未合併或視為現行租盤。"},
        {"sourceName": "完工年交叉來源", "url": DD_PROJECT, "statusLabel": "DDproperty 專案頁列 2021；PropertyScout 單筆租屋頁列 2024，採 2021 並保留此差異待進一步核實。"},
    ],
    "yieldStatus": "not_calculated",
    "yieldNote": "本案目前沒有可核實的出售單筆掛牌；出租線索過期且房型資料矛盾，因此不計算投報率。",
}
index = next((i for i, row in enumerate(rows) if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if index is None:
    rows.append(record)
else:
    rows[index] = record
rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
save("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", prefix, rows, suffix)

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": CHECKED,
    "coordinate": {"lat": 13.774717, "lng": 100.574669, "source": MAP_SOURCE, "corroboration": MAP_CORROBORATION, "status": "verified"},
    "completionYear": {"selected": 2021, "source": DD_PROJECT, "conflict": {"year": 2024, "source": PROPERTYSCOUT_RENT}},
    "managementFee": {"bahtPerSqmPerMonth": 55, "source": FEE_SOURCE, "status": "historical_indicative"},
    "sale": {"status": "no_verified_individual_listing", "excluded": {"price": 4_100_000, "areaSqm": 50, "source": DD_MISLINKED_SALE, "reason": "The individual listing description identifies Cool House Ratchada 12, not Quintara Kynett."}},
    "rent": {"unconfirmedListing": {"price": 14_000, "areaSqm": 22, "listedAt": "2026-08-30", "source": LIVINGINSIDER_RENT, "roomTypeConflict": "LivingInsider calls it studio; PropertyScout describes a 1-bedroom unit with the same area and floor.", "status": "availability_unconfirmed_update_over_30d"}, "corroboratingPage": PROPERTYSCOUT_RENT},
    "roi": {"calculated": False, "reason": "No verified sale baseline; rent availability and room type are unconfirmed."},
    "sources": [HIPFLAT, MAP_SOURCE, MAP_CORROBORATION, DD_PROJECT, DD_MISLINKED_SALE, PROPERTYHUB_SALE, PROPERTYHUB_RENT, LIVINGINSIDER_RENT, PROPERTYSCOUT_RENT, FEE_SOURCE],
}
(ROOT / "reports/quintara-kynett-ratchada-12-market-check-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "coordinateVerified": True, "unconfirmedRent": rent_sample["id"], "saleListingExcluded": True, "roi": "not calculated"}, ensure_ascii=False))
