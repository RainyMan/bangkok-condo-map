"""Record source-level availability conflicts for SiriMetro Ratchada-Vipawadee."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3228
AS_OF = "2026-10-20"
PH_SALE = "https://propertyhub.in.th/en/condo-for-sale/project-sirimetro-ratchada-vipawadee"
PH_RENT = "https://propertyhub.in.th/en/condo-for-rent/project-sirimetro-ratchada-vipawadee"
SALE_URL = "https://propertyhub.in.th/en/listings/a045611-sirimetro-ratchada-vipawadee---6187051"
DD_PROJECT = "https://www.ddproperty.com/en/project/136-sirimetro-ratchada-vipawadee-condominium"
IBANGKOK_RENT = "https://www.ibangkokcondo.com/index.php/rent-condo/Sirimetro-Ratchada-Vipawadee"
SCANCONDO_RENT = "https://www.scancondo.com/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%AA%E0%B8%B4%E0%B8%A3%E0%B8%B4%E0%B9%80%E0%B8%A1%E0%B9%82%E0%B8%97%E0%B8%A3-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2-%E0%B8%A7%E0%B8%B4%E0%B8%A0%E0%B8%B2%E0%B8%A7%E0%B8%94%E0%B8%B5"
RENTCONDO_LISTING = "https://www.rentcondobkk.com/%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/134639/SRV10-0007/%E0%B8%9B%E0%B8%A5%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%AA%E0%B8%B4%E0%B8%A3%E0%B8%B4%E0%B9%80%E0%B8%A1%E0%B9%82%E0%B8%97%E0%B8%A3-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2-%E0%B8%A7%E0%B8%B4%E0%B8%A0%E0%B8%B2%E0%B8%A7%E0%B8%94%E0%B8%B5-%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99-2-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%95%E0%B8%B9%E0%B8%94%E0%B8%B4%E0%B9%82%E0%B8%AD-%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%AA%E0%B8%B4%E0%B9%88%E0%B8%87%E0%B8%AD%E0%B8%B3%E0%B8%99%E0%B8%A7%E0%B8%A2%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B8%B0%E0%B8%94%E0%B8%A7%E0%B8%81-%E0%B8%9A%E0%B8%AD%E0%B8%81%E0%B9%80%E0%B8%A5%E0%B8%A2%E0%B8%AB%E0%B9%89%E0%B8%B2%E0%B8%A1%E0%B8%9E%E0%B8%A5%E0%B8%B2%E0%B8%94"


def read_crosschecks() -> tuple[str, list[dict], str]:
    text = (DIST / "bangkok-market-crosschecks.js").read_text(encoding="utf-8")
    match = re.fullmatch(r"(window\.BANGKOK_MARKET_CROSSCHECKS\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError("Cannot parse BANGKOK_MARKET_CROSSCHECKS")
    return match.group(1), json.loads(match.group(2)), match.group(3)


prefix, rows, suffix = read_crosschecks()
row = next((item for item in rows if int(item.get("hipflatId", -1)) == PROJECT_ID), None)
if row is None:
    row = {"hipflatId": PROJECT_ID, "projectName": "SiriMetro Ratchada-Vipawadee"}
    rows.append(row)

row.update({
    "asOf": AS_OF,
    "sourceName": "PropertyHub / DDproperty / iBangkokCondo / Scancondo / RentCondoBKK",
    "projectSourceUrl": "https://www.hipflat.co.th/en/projects/sirimetro-ratchada-vipawadee-eqciom",
    "sale": {
        "activeListingCount": 2,
        "displayedResultCount": 2,
        "sourceUrl": PH_SALE,
        "listings": [{
            "listingId": "6187051",
            "price": 1_390_000,
            "area": 23,
            "priceSqm": 60_435,
            "bedrooms": 0,
            "listedAt": "2026-10-17",
            "url": SALE_URL,
            "sourceName": "PropertyHub",
            "listingStatus": "active_as_listed",
            "statusLabel": "Studio，23㎡，฿1,390,000；PropertyHub 曼谷出售結果刷新日 2026-10-17。",
        }],
        "note": "PropertyHub 專案出售頁列 2 筆；最低可核對的直接房源為 Studio、23㎡、฿1,390,000。",
    },
    "rent": {
        "activeListingCount": 0,
        "displayedResultCount": 0,
        "sourceUrl": PH_RENT,
        "listings": [],
        "note": "PropertyHub 專案頁目前無匹配出租物件；DDproperty 與 iBangkokCondo 亦未列出現行出租。另一個租屋頁仍顯示 ฿8,000/月、24㎡ 的 SRV10-0007，但 Scancondo 將該房標為已租，且該頁發布日期未核實；不納入現行租金或投報。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": "https://www.hipflat.co.th/en/projects/sirimetro-ratchada-vipawadee-eqciom", "statusLabel": "專案資料列 2011 完工、79 戶、8 層；本次搜尋未找到可確認現況的租盤。"},
        {"sourceName": "PropertyHub 出租專案頁", "url": PH_RENT, "statusLabel": "目前沒有匹配出租掛牌。"},
        {"sourceName": "DDproperty 專案頁", "url": DD_PROJECT, "statusLabel": "本次核對未找到現行出租掛牌。"},
        {"sourceName": "iBangkokCondo 出租專案頁", "url": IBANGKOK_RENT, "statusLabel": "頁面標示 0 筆現行出租。"},
        {"sourceName": "Scancondo 出租專案頁", "url": SCANCONDO_RENT, "statusLabel": "列出 3 筆出租歷史項目；其中 SRV10-0007 明確標示已租，不能當作現行可租。"},
        {"sourceName": "RentCondoBKK 待確認房源 SRV10-0007", "url": RENTCONDO_LISTING, "statusLabel": "頁面顯示 Studio、24㎡、฿8,000/月並稱可看房，但發布/更新日期未核實；與 Scancondo 已租狀態矛盾，暫不納入租金基準。"},
    ],
    "yieldStatus": "not_calculated_rent_availability_conflict",
    "yieldNote": "已有 Studio 出售樣本，但找不到現行且狀態一致的租盤。SRV10-0007 的租金為候選歷史線索，來源狀態衝突，因此不得用於現行租金或投報率。",
})

(DIST / "bangkok-market-crosschecks.js").write_text(
    prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
    encoding="utf-8",
)

report = {
    "hipflatId": PROJECT_ID,
    "projectName": "SiriMetro Ratchada-Vipawadee",
    "asOf": AS_OF,
    "verifiedSaleSample": {"listingId": "6187051", "roomType": "Studio", "priceTHB": 1_390_000, "areaSqm": 23, "url": SALE_URL},
    "rentAvailability": "conflicted; excluded from current rent and yield",
    "rentCandidate": {"roomType": "Studio", "priceTHBPerMonth": 8_000, "areaSqm": 24, "listingId": "SRV10-0007", "url": RENTCONDO_LISTING},
    "crossChecks": [
        {"source": "PropertyHub", "url": PH_RENT, "result": "0 matched rent listings"},
        {"source": "iBangkokCondo", "url": IBANGKOK_RENT, "result": "0 current rentals"},
        {"source": "Scancondo", "url": SCANCONDO_RENT, "result": "SRV10-0007 marked rented"},
        {"source": "RentCondoBKK", "url": RENTCONDO_LISTING, "result": "฿8,000/month; availability/date not independently established"},
    ],
    "yield": "not calculated because rental availability is contradictory",
}
(ROOT / "reports" / "sirimetro-market-crosscheck-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "sale": "one directly linked studio sample", "rent": "conflicted and excluded from ROI"}, ensure_ascii=False))
