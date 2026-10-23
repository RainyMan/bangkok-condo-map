"""Refresh Belgravia Ratchada 17 with a direct PropertyHub rental sample and sale-source checks."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3122
CHECKED = "2026-10-23"
PROPERTYHUB_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-the-belgravia-ratchada-17"
PROPERTYHUB_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-the-belgravia-ratchada-17"
PROPERTYHUB_RENT_ITEM = "https://propertyhub.in.th/en/listings/condo-for-rent-at-the-belgravia-ratchada-17-p6909004---6379931"
DDPROPERTY_PROJECT = "https://www.ddproperty.com/en/project/14821-the-belgravia-ratchada-17"
LIVINGINSIDER_SALE = "https://www.livinginsider.com/en/project/the-belgravia-ratchada-17-condo-buysell"
DEVELOPER_PROJECT = "https://www.thegolden-development.com/en/properties/belgravia-ratchada-17"


def load_array(filename, symbol):
    path = DIST / filename
    content = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", content, re.S)
    if not match:
        raise ValueError(f"Could not parse {filename} / {symbol}")
    return path, content, json.loads(match.group(1))


def save_array(path, content, symbol, rows):
    encoded = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*\[.*\];", content, re.S)
    if not match:
        raise ValueError(f"Could not replace {path.name} / {symbol}")
    array_start = match.group(0).index("[") + match.start()
    array_end = match.end() - 1
    content = content[:array_start] + encoded + content[array_end:]
    path.write_text(content, encoding="utf-8")


sample = {
    "id": "6379931",
    "price": 16500,
    "area": 28.5,
    "priceSqm": 579,
    "beds": 1,
    "roomType": "1BR",
    "title": "The Belgravia @ Ratchada 17 · 1 房 · 28.5 ㎡ · ฿16,500/月",
    "url": PROPERTYHUB_RENT_ITEM,
    "sourceName": "PropertyHub",
    "projectName": "The Belgravia @ Ratchada 17",
    "updated": None,
    "checkedAt": CHECKED,
    "matchedBy": "exact_project_route_listing_and_direct_listing_detail",
    "listingStatus": "availability_unconfirmed_direct_page_update_date_missing",
    "verificationNote": "PropertyHub 專案出租頁顯示此 1 房租盤為 ฿16,500/月、28.5㎡，並標示 UPDATE；個別物件頁 Last Update 欄為空，尚未向刊登者確認仍可出租。",
}

sample_path, sample_text, sample_rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next(row for row in sample_rows if int(row.get("hipflatId", -1)) == PROJECT_ID)
rent_samples = manual.setdefault("rent", {}).setdefault("samples", [])
rent_samples[:] = [row for row in rent_samples if str(row.get("id")) != sample["id"]]
rent_samples.append(sample)
save_array(sample_path, sample_text, "BANGKOK_MANUAL_MARKET_SAMPLES", sample_rows)

cross_path, cross_text, cross_rows = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next(row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID)
cross["asOf"] = CHECKED
cross["sourceName"] = "PropertyHub / DDproperty / Livinginsider"
cross["projectSourceUrl"] = PROPERTYHUB_SALE
cross["sale"] = {
    "activeListingCount": 0,
    "sourceUrl": PROPERTYHUB_SALE,
    "sources": [
        {"sourceName": "PropertyHub 出售專案頁", "activeListingCount": 0, "url": PROPERTYHUB_SALE},
        {"sourceName": "DDproperty 專案頁", "activeListingCount": 0, "url": DDPROPERTY_PROJECT},
    ],
    "excludedCandidates": [
        {
            "sourceName": "Livinginsider 同名搜尋結果（排除）",
            "price": 3450000,
            "area": 829.44,
            "url": LIVINGINSIDER_SALE,
            "reason": "摘要顯示 11 樓、829.44㎡，但專案資料為 8 層，開發商公布住宅戶型約 26.95–39㎡；Livinginsider 專案頁亦顯示該條件下未找到掛牌，未取得可核實的單筆售盤連結，排除。",
        }
    ],
}
cross["rent"] = {
    "activeListingCount": 67,
    "sourceUrl": PROPERTYHUB_RENT,
    "listings": [
        {
            "listingId": sample["id"],
            "bedrooms": 1,
            "price": sample["price"],
            "area": sample["area"],
            "priceSqm": sample["priceSqm"],
            "url": sample["url"],
            "listedAt": "",
            "availability": "unconfirmed_last_update_missing",
        },
        {
            "listingId": "6170172",
            "bedrooms": 2,
            "price": 18000,
            "area": 34,
            "priceSqm": 529,
            "url": "https://propertyhub.in.th/en/listings/for-rent-belgavia-ratchada-17---6170172",
            "listedAt": "",
            "availability": "unconfirmed_last_update_missing",
        },
    ],
}
cross["yieldStatus"] = "not_calculated_no_verified_sale_listing"
cross["yieldNote"] = "PropertyHub 與 DDproperty 專案出售頁均顯示零筆出售；Livinginsider 搜尋到的疑似售盤樓層及面積與本案明顯不符，排除。雖找到 PropertyHub 一房直接租盤，但缺可核實的同房型售盤，故不計投報。"
cross["availabilitySources"] = [
    {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE, "statusLabel": "專案頁顯示 0 筆出售掛牌。"},
    {"sourceName": "DDproperty 專案頁", "url": DDPROPERTY_PROJECT, "statusLabel": "專案頁顯示 For Sale (0)。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT, "statusLabel": "核對時專案頁顯示 67 筆出租；頁面中的 1 房最低租盤標示 UPDATE。"},
    {"sourceName": "PropertyHub 一房直接租盤", "url": PROPERTYHUB_RENT_ITEM, "statusLabel": "฿16,500/月、28.5㎡、1 房；個別頁未提供 Last Update 日期，出租狀態待刊登者確認。"},
    {"sourceName": "Livinginsider 出售頁（錯誤摘要排除）", "url": LIVINGINSIDER_SALE, "statusLabel": "搜尋摘要顯示 11 樓及 829.44㎡，不符合本案 8 層／約 27–39㎡戶型；專案頁顯示沒有符合條件的單筆售盤。"},
    {"sourceName": "開發商專案資料", "url": DEVELOPER_PROJECT, "statusLabel": "提供地址、Google Maps 專案定位、戶型 26.95–39㎡及 8 層；起始售價屬新案／開發商資訊，不作二手售盤樣本。"},
]
save_array(cross_path, cross_text, "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": "Belgravia Ratchada 17",
    "checkedAt": CHECKED,
    "coordinates": {
        "verified": True,
        "source": "https://propertyhub.in.th/en/projects/the-belgravia-ratchada-17",
        "projectPage": "https://www.thegolden-development.com/en/properties/belgravia-ratchada-17",
    },
    "sale": {
        "verifiedSecondhandListings": 0,
        "sources": [PROPERTYHUB_SALE, DDPROPERTY_PROJECT],
        "excludedCandidate": cross["sale"]["excludedCandidates"][0],
        "developerStartingPriceExcluded": {"url": DEVELOPER_PROJECT, "reason": "專案銷售起價，沒有可識別的二手單位及室內面積。"},
    },
    "rentSamples": [sample, rent_samples[0]],
    "yield": {"status": "not_calculated", "reason": "沒有可核實的二手出售掛牌，不能計算一房或兩房投報。"},
}
(REPORTS / "belgravia-ratchada-17-market-check-2026-10-23.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "addedRentSample": sample["id"], "saleSamples": 0, "yield": "not calculated"}, ensure_ascii=False))
