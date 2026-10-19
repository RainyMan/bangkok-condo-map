from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3105
NAME = "Picha Pavilion"
AS_OF = "2026-10-19"
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
        "sale": {"sourceUrl": PH_PROJECT},
        "rent": {"activeListingCount": 0, "sourceUrl": PH_RENT, "listings": []},
        "availabilitySources": [
            {
                "sourceName": "PropertyHub 出租專案頁",
                "url": PH_RENT,
                "statusLabel": "核對時顯示沒有出租掛牌；未找到可核實的現行出租物件。",
            },
            {
                "sourceName": "ZMyHome 出租房源線索 V181621",
                "url": ZM_RENT,
                "statusLabel": "頁面列 ฿3,500/月、32㎡ studio，但未提供刊登更新日期，且明示屋主尚未驗證；僅作待確認線索，不納入租金樣本或投報。",
            },
            {
                "sourceName": "PropertyHub 出售物件 6350508",
                "url": SALE_SAMPLE,
                "statusLabel": "直接物件頁列 Picha Pavilion studio、27㎡、฿680,000；頁面顯示 2026-09-03 更新，已在出售樣本中。",
            },
        ],
        "roi": {
            "status": "not_calculable",
            "reason": "目前沒有可核實的現行出租樣本；ZMyHome 租屋頁未確認刊登仍有效。",
        },
        "note": "未以附近專案、區域租金或日期不明的房源線索代替 Picha Pavilion 現行租盤。",
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
        "status": "direct_listing_sample_present",
        "price": 680000,
        "areaSqm": 27,
        "roomType": "Studio",
        "url": SALE_SAMPLE,
        "updatedAt": "2026-09-03",
    },
    "rent": {
        "status": "no_confirmed_current_sample",
        "availabilityPage": PH_RENT,
        "availabilityEvidence": "PropertyHub rental project page showed no rental listings at review.",
        "unconfirmedLead": {
            "url": ZM_RENT,
            "price": 3500,
            "areaSqm": 32,
            "roomType": "studio",
            "reasonExcluded": "No listing update date; page says the owner's identity has not been verified.",
        },
    },
    "roi": {
        "status": "not_calculable",
        "reason": "No confirmed current rental listing supports an annual rent estimate.",
    },
    "sources": {"propertyHubProject": PH_PROJECT, "propertyHubRent": PH_RENT, "unconfirmedRentLead": ZM_RENT, "saleListing": SALE_SAMPLE},
    "identityCheck": "The ZMyHome address identifies Srinakarin 40 / Supapong 3 and names Picha Pavilion; it is retained only as an unverified lead, not a current sample.",
}
(ROOT / "reports" / "picha-pavilion-rent-availability-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index = (DIST / "index.html").read_text(encoding="utf-8")
index, count = re.subn(
    r"bangkok-market-crosschecks\.js\?v=[^\"']+",
    "bangkok-market-crosschecks.js?v=20261019-picha-rent-availability",
    index,
    count=1,
)
if count != 1:
    raise RuntimeError("Could not update market crosscheck cache key")
(DIST / "index.html").write_text(index, encoding="utf-8")
print(json.dumps({"project": NAME, "currentRentSample": "none confirmed", "roi": "not calculable", "report": "reports/picha-pavilion-rent-availability-2026-10-19.json"}, ensure_ascii=False))
