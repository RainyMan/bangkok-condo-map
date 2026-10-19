from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3105
NAME = "Picha Pavilion"
AS_OF = "2026-10-20"
PH_PROJECT = "https://propertyhub.in.th/en/projects/picha-pavilion"
PH_RENT = "https://propertyhub.in.th/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-picha-pavilion"
ZM_RENT = "https://zmyhome.com/property/V181621"
SALE_SAMPLE = "https://propertyhub.in.th/en/listings/picha-pavilian-condo-selling-condo---6350508"


def load(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def save(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


crosschecks = load("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
row = next((item for item in crosschecks if int(item.get("hipflatId", -1)) == PROJECT_ID), None)
if row is None:
    row = {"hipflatId": PROJECT_ID, "projectName": NAME}
    crosschecks.append(row)
row.update(
    {
        "projectName": NAME,
        "asOf": AS_OF,
        "sourceName": "PropertyHub / ZMyHome",
        "projectSourceUrl": PH_PROJECT,
        "sale": {"displayedListingCount": 2, "sourceUrl": PH_PROJECT, "note": "PropertyHub project page currently displays two exact-project listings; lowest linked item is 6350508, ฿680,000 / 27㎡. The individual page does not show a recent last-updated date."},
        "rent": {"activeListingCount": 0, "sourceUrl": PH_RENT, "listings": [], "note": "PropertyHub currently shows zero exact-project rentals. An older ZMyHome lead is reported rented in September 2026 and is excluded from current rent and ROI."},
        "availabilitySources": [
            {
                "sourceName": "PropertyHub 出租專案頁",
                "url": PH_RENT,
                "statusLabel": "2026-10-20 核對顯示沒有出租掛牌；未找到可核實的現行出租物件。",
            },
            {
                "sourceName": "ZMyHome 出租房源線索 V181621",
                "url": ZM_RENT,
                "statusLabel": "頁面列 ฿3,500/月、32㎡ studio；搜尋索引標示 2026-09 已出租，單筆頁未提供可核實的最新狀態。僅保留歷史線索，不納入現行租金或投報。",
            },
            {
                "sourceName": "PropertyHub 出售物件 6350508",
                "url": SALE_SAMPLE,
                "statusLabel": "PropertyHub 專案頁目前顯示本案兩筆出售；直接物件頁列 1 房、27㎡、฿680,000，但單筆最後更新日期為空白；保留為在架觀察樣本，售方仍待確認。",
            },
        ],
        "roi": {
            "status": "not_calculable",
            "reason": "PropertyHub 專案頁於 2026-10-20 顯示零筆出租。ZMyHome ฿3,500/月線索已有 2026-09 已出租紀錄，不能代表現行租金。",
        },
        "note": "以 PropertyHub 同案零出租數和 ZMyHome 已出租歷史線索確認缺少現行租盤；未以附近專案或區域租金代替。",
    }
)
crosschecks.sort(key=lambda item: int(item["hipflatId"]))
save("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": AS_OF,
    "coordinate": {
        "status": "verified",
        "source": PH_PROJECT,
        "lat": 13.69287115746202,
        "lng": 100.6435012489693,
    },
    "sale": {
        "status": "project_page_displays_direct_sale_listing_but_unit_last_updated_date_missing",
        "price": 680000,
        "areaSqm": 27,
        "roomType": "Studio",
        "url": SALE_SAMPLE,
        "updatedAt": None,
        "projectPageObservedAt": AS_OF,
        "projectPageDisplayedSaleCount": 2,
    },
    "rent": {
        "status": "no_current_sample; propertyhub_exact_project_count_zero",
        "availabilityPage": PH_RENT,
        "availabilityEvidence": "PropertyHub exact-project page shows 0 rentals and 2 sale listings when checked 2026-10-20.",
        "historicalRentedLead": {
            "url": ZM_RENT,
            "price": 3500,
            "areaSqm": 32,
            "roomType": "studio",
            "listingStatus": "reported_rented_2026-09; current status unconfirmed on individual page",
            "reasonExcluded": "The listing is reported rented in September 2026 and the individual page does not verify current availability.",
        },
    },
    "roi": {
        "status": "not_calculable",
        "reason": "No confirmed current rental listing supports an annual rent estimate.",
    },
    "sources": {"propertyHubProject": PH_PROJECT, "propertyHubRent": PH_RENT, "historicalRentedLead": ZM_RENT, "saleListing": SALE_SAMPLE},
    "identityCheck": "The ZMyHome address identifies Srinakarin 40 / Supapong 3 and names Picha Pavilion; its ฿3,500 / 32㎡ studio record is retained as historical after a September 2026 rented report, not a current sample.",
}
(ROOT / "reports" / "picha-pavilion-rent-availability-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index = (DIST / "index.html").read_text(encoding="utf-8")
index, count = re.subn(
    r"bangkok-market-crosschecks\.js\?v=[^\"']+",
    "bangkok-market-crosschecks.js?v=20261020-picha-rent-availability",
    index,
    count=1,
)
if count != 1:
    raise RuntimeError("Could not update market crosscheck cache key")
(DIST / "index.html").write_text(index, encoding="utf-8")
print(json.dumps({"project": NAME, "currentRentSample": "none confirmed", "observedSaleListings": 2, "roi": "not calculable", "report": "reports/picha-pavilion-rent-availability-2026-10-20.json"}, ensure_ascii=False))
