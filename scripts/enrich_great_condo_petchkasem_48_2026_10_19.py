from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3175
PROJECT_NAME = "The Great Condo Petchkasem 48"
CHECKED_AT = "2026-10-19"
PH_PROJECT = "https://propertyhub.in.th/en/projects/the-great-condo"
PH_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-the-great-condo"
PH_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-the-great-condo"
SALE_LISTING = "https://assets.propertyhub.in.th/listings/a033746-the-great-condo-petchkasem-48---6005471"
HIPFLAT = "https://www.hipflat.co.th/en/projects/the-great-condo-petchkasem-48-jvfwpo"
COORDINATE_SOURCE = "https://www.thaigerproperty.com/projects/thailand/bangkok/phasi-charoen/bang-duan/the-great-condo-petchkasem-48"


def read_js_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not find {symbol} in {path}")
    return json.loads(match.group(1))


def write_js_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        f"{json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


sample = {
    "id": "6005471",
    "price": 1_899_000,
    "area": 57,
    "priceSqm": 33_316,
    "beds": 2,
    "roomType": "2 Bedroom",
    "url": SALE_LISTING,
    "title": "A033746 The Great Condo Petchkasem 48 · 2 Bedroom · 57 sqm · ฿1,899,000",
    "sourceName": "PropertyHub",
    "projectName": PROJECT_NAME,
    "updated": "2026-10-17",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_alias_and_direct_listing_page",
    "listingStatus": "active_as_listed",
}

market_path = DIST / "bangkok-manual-market-samples.js"
markets = read_js_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
sale = {
    "count": 4,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 1_899_000,
    "minimum": 1_899_000,
    "minimumArea": 57,
    "minimumSampleUpdated": "2026-10-17",
    "averageSqm": 33_316,
    "minimumSqm": 33_316,
    "minimumSqmSampleUpdated": "2026-10-17",
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub",
    "source": PH_SALE,
    "minimumSourceUrl": SALE_LISTING,
    "minimumSqmSourceUrl": SALE_LISTING,
    "byBedroom": {
        "2": {
            "count": 1,
            "minimum": 1_899_000,
            "area": 57,
            "minimumArea": 57,
            "priceSqm": 33_316,
            "minimumSqm": 33_316,
            "sourceUrl": SALE_LISTING,
            "minimumSourceUrl": SALE_LISTING,
            "minimumSqmSourceUrl": SALE_LISTING,
        }
    },
    "samples": [sample],
}
entry = {
    "hipflatId": PROJECT_ID,
    "name": PROJECT_NAME,
    "asOf": CHECKED_AT,
    "sale": sale,
    "fee": {
        "rate": 15,
        "status": "published_indicative",
        "note": "PropertyHub 專案頁刊載的公用費為 15 THB/㎡/月；現行費率請向管委會確認。",
        "source": PH_PROJECT,
    },
    "completedYear": 2011,
    "completedYearSourceUrl": PH_PROJECT,
    "availabilitySources": [
        {
            "sourceName": "PropertyHub 兩房直售物件 A033746",
            "url": SALE_LISTING,
            "statusLabel": "2 房 · 57㎡ · ฿1,899,000；專案頁標示於 2026-10-17 更新。",
        },
        {
            "sourceName": "PropertyHub 出租專案頁",
            "url": PH_RENT,
            "statusLabel": "核對時顯示 0 筆出租；未找到可核實的現行租盤。",
        },
        {
            "sourceName": "PropertyHub 專案資料",
            "url": PH_PROJECT,
            "statusLabel": "核對專案別名、2011 完工、203 戶、8 層及 15 THB/㎡ 公用費。",
        },
        {
            "sourceName": "座標來源 Thaiger Property",
            "url": COORDINATE_SOURCE,
            "statusLabel": "與 Hipflat 同名專案頁交叉核對；地圖座標已由現有座標資料列驗證。",
        },
        {
            "sourceName": "Hipflat 專案頁",
            "url": HIPFLAT,
            "statusLabel": "以 Hipflat 專案識別頁核對專案名稱。",
        },
    ],
}
markets = [row for row in markets if int(row.get("hipflatId", -1)) != PROJECT_ID]
markets.append(entry)
markets.sort(key=lambda row: int(row.get("hipflatId", 0)))
write_js_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES", markets)

crosschecks_path = DIST / "bangkok-market-crosschecks.js"
crosschecks = read_js_array(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": PROJECT_ID,
    "projectName": PROJECT_NAME,
    "asOf": CHECKED_AT,
    "sourceName": "PropertyHub",
    "projectSourceUrl": PH_PROJECT,
    "sale": {
        "activeListingCount": 4,
        "listings": [sample],
        "sourceUrl": PH_SALE,
    },
    "rent": {"activeListingCount": 0, "sourceUrl": PH_RENT, "listings": []},
    "availabilitySources": entry["availabilitySources"],
    "roi": {
        "status": "not_calculable",
        "reason": "目前沒有可核實的現行出租掛牌；不以鄰近專案或區域租金代替。",
    },
}
crosschecks = [row for row in crosschecks if int(row.get("hipflatId", -1)) != PROJECT_ID]
crosschecks.append(crosscheck)
crosschecks.sort(key=lambda row: int(row.get("hipflatId", 0)))
write_js_array(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "project": PROJECT_NAME,
    "checkedAt": CHECKED_AT,
    "coordinates": {
        "status": "previously_verified",
        "source": COORDINATE_SOURCE,
        "crossCheck": HIPFLAT,
    },
    "sale": {
        "status": "verified_individual_listing",
        "priceTHB": 1_899_000,
        "areaSqm": 57,
        "pricePerSqmTHB": 33_316,
        "bedrooms": 2,
        "listingId": "A033746 / 6005471",
        "updatedAt": "2026-10-17",
        "source": SALE_LISTING,
        "projectSource": PH_SALE,
    },
    "rent": {
        "status": "no_current_listing_found",
        "count": 0,
        "source": PH_RENT,
        "evidence": "The PropertyHub project rent page showed 0 listings on 2026-10-19.",
    },
    "fee": {"rateTHBPerSqmPerMonth": 15, "source": PH_PROJECT},
    "yield": {
        "status": "not_calculable",
        "reason": "沒有可核實現行租盤，不計算投報率。",
    },
    "limitations": "只將可點開的單筆售盤納入售價樣本；出租頁目前為 0 筆，不使用附近專案代填。",
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "the-great-condo-petchkasem-48-market-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index_path = DIST / "index.html"
html = index_path.read_text(encoding="utf-8")
html, changed = re.subn(
    r"bangkok-manual-market-samples\.js\?v=[^\"']+",
    "bangkok-manual-market-samples.js?v=20261019-great-condo-petchkasem-48-market",
    html,
    count=1,
)
html, changed_crosscheck = re.subn(
    r"bangkok-market-crosschecks\.js\?v=[^\"']+",
    "bangkok-market-crosschecks.js?v=20261019-great-condo-petchkasem-48-market",
    html,
    count=1,
)
if changed != 1 or changed_crosscheck != 1:
    raise ValueError("Could not update the manual market source cache keys")
index_path.write_text(html, encoding="utf-8")

print(json.dumps({"hipflatId": PROJECT_ID, "sale": "2BR listing verified", "rent": "0 current listings; no yield imputed"}, ensure_ascii=False))
