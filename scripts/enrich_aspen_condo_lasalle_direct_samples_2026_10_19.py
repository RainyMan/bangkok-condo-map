from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKED = "2026-10-19"
ID = 4315
NAME = "Aspen Condo Lasalle"
SALE_PRICE, SALE_AREA = 1_300_000, 24.0
RENT_PRICE, RENT_AREA = 7_500, 24.0
SALE_URL = "https://propertyhub.in.th/en/listings/huge-loss-sale-below-market-priceonly-1-3-million-aspen-lasalle-opposite-sikarin-hospital-sri-lasalle-mrt---6340897"
RENT_URL = "https://propertyhub.in.th/en/listings/%EF%B8%8F-dm-us-on-line-multiple-units-available-aspen-available-sizes-24-27-35-sq-m-bts-bearing-mrt-sri-la-salle--ac9109a8---6468860"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-aspen-lasalle-phase-a"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-aspen-lasalle-phase-a"


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{symbol}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot parse {symbol}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


sale_rate = round(SALE_PRICE / SALE_AREA)
rent_rate = int(RENT_PRICE / RENT_AREA + 0.5)
sale_sample = {
    "id": "6340897", "price": SALE_PRICE, "area": SALE_AREA, "priceSqm": sale_rate,
    "beds": 1, "roomType": "1BR", "title": "Aspen Condo Lasalle Phase A，1 房，24 ㎡，฿1,300,000",
    "url": SALE_URL, "sourceName": "PropertyHub", "projectName": NAME,
    "updated": "2026-10-14", "checkedAt": CHECKED,
    "matchedBy": "PropertyHub_project_feed_names_Aspen_Lasalle_Phase_A_and_direct_listing_names_project_and_gives_1BR_24sqm_price",
    "listingStatus": "active_as_listed",
}
rent_sample = {
    "id": "6468860", "price": RENT_PRICE, "area": RENT_AREA, "priceSqm": rent_rate,
    "beds": 1, "roomType": "1BR", "title": "Aspen Lasalle Phase A，多種面積可選；1 房 24 ㎡，฿7,500/月",
    "url": RENT_URL, "sourceName": "PropertyHub", "projectName": NAME,
    "updated": "2026-10-06", "checkedAt": CHECKED,
    "matchedBy": "PropertyHub_A_phase_project_feed_and_direct_multi_unit_listing_match_24sqm_1BR_option_at_7500_month",
    "listingStatus": "active_as_listed",
}

manual_rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == ID), None)
if record is None:
    record = {"hipflatId": ID, "name": NAME}
    manual_rows.append(record)
record.update({
    "asOf": CHECKED,
    "fee": {"rate": 35, "unit": "THB/sqm/month", "source": RENT_PROJECT_URL,
            "note": "PropertyHub 專案頁列出管理費 ฿35/㎡；實際費率請向管委會確認。"},
    "sale": {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": SALE_PRICE, "minimum": SALE_PRICE, "minimumArea": SALE_AREA,
        "minimumSampleUpdated": sale_sample["updated"], "averageSqm": sale_rate, "minimumSqm": sale_rate,
        "minimumSqmSampleUpdated": sale_sample["updated"], "asOf": CHECKED,
        "sourceName": "PropertyHub 直接出售掛牌", "source": SALE_PROJECT_URL,
        "minimumSourceUrl": SALE_URL, "minimumSqmSourceUrl": SALE_URL,
        "byBedroom": {"1": {"count": 1, "minimum": SALE_PRICE, "area": SALE_AREA,
                             "minimumArea": SALE_AREA, "priceSqm": sale_rate, "minimumSqm": sale_rate,
                             "sourceUrl": SALE_URL, "minimumSourceUrl": SALE_URL,
                             "minimumSqmSourceUrl": SALE_URL}},
        "samples": [sale_sample],
    },
    "rent": {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": RENT_PRICE, "minimum": RENT_PRICE, "minimumArea": RENT_AREA,
        "minimumSampleUpdated": rent_sample["updated"], "averageSqm": rent_rate, "minimumSqm": rent_rate,
        "minimumSqmSampleUpdated": rent_sample["updated"], "asOf": CHECKED,
        "sourceName": "PropertyHub 直接出租掛牌", "source": RENT_PROJECT_URL,
        "minimumSourceUrl": RENT_URL, "minimumSqmSourceUrl": RENT_URL,
        "byBedroom": {"1": {"count": 1, "minimum": RENT_PRICE, "area": RENT_AREA,
                             "minimumArea": RENT_AREA, "priceSqm": rent_rate, "minimumSqm": rent_rate,
                             "sourceUrl": RENT_URL, "minimumSourceUrl": RENT_URL,
                             "minimumSqmSourceUrl": RENT_URL}},
        "samples": [rent_sample],
    },
})
manual_rows.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

crosschecks = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = next((row for row in crosschecks if int(row.get("hipflatId", -1)) == ID), None)
if crosscheck is None:
    crosscheck = {"hipflatId": ID, "projectName": NAME}
    crosschecks.append(crosscheck)
crosscheck.update({
    "projectName": NAME, "asOf": CHECKED, "sourceName": "PropertyHub",
    "projectSourceUrl": SALE_PROJECT_URL,
    "sale": {"activeListingCount": 26, "sourceUrl": SALE_PROJECT_URL,
             "listings": [{"id": sale_sample["id"], "price": SALE_PRICE, "area": SALE_AREA,
                           "priceSqm": sale_rate, "bedrooms": 1, "title": sale_sample["title"],
                           "url": SALE_URL, "listedAt": sale_sample["updated"]}]},
    "rent": {"activeListingCount": 27, "sourceUrl": RENT_PROJECT_URL,
             "listings": [{"id": rent_sample["id"], "price": RENT_PRICE, "area": RENT_AREA,
                           "priceSqm": rent_rate, "bedrooms": 1, "title": rent_sample["title"],
                           "url": RENT_URL, "listedAt": rent_sample["updated"]}]},
    "availabilitySources": [{"sourceName": "PropertyHub 出售專案頁", "url": SALE_PROJECT_URL,
                              "statusLabel": "26 筆公開掛牌；已核對最低所見 1 房樣本"},
                             {"sourceName": "PropertyHub 出租專案頁", "url": RENT_PROJECT_URL,
                              "statusLabel": "27 筆公開掛牌；已核對最低所見 1 房樣本"}],
})
crosschecks.sort(key=lambda row: int(row["hipflatId"]))
save_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": ID, "project": NAME, "checkedAt": CHECKED,
    "sale": sale_sample, "rent": rent_sample,
    "saleProjectPage": {"url": SALE_PROJECT_URL, "visibleListings": 26},
    "rentProjectPage": {"url": RENT_PROJECT_URL, "visibleListings": 28},
    "commonFee": {"thbPerSqmMonth": 35, "sourceUrl": RENT_PROJECT_URL},
    "yield": {"status": "not_calculated", "reason": "核對到的直接出售／出租樣本都是 1 房；此站點的投報基準要求同房型最低兩房售價與租金，不能混用一房行情。"},
    "limitations": ["PropertyHub 專案結果卡顯示出售掛牌於 2026-10-14 更新，出租選項於 2026-10-06 更新；未聯絡刊登者再次確認空置或售出狀態。", "出租掛牌列出多種面積；PropertyHub 專案結果列明 ฿7,500/月對應 24 ㎡的一房選項。"],
    "sources": {"saleProject": SALE_PROJECT_URL, "saleListing": SALE_URL,
                "rentProject": RENT_PROJECT_URL, "rentListing": RENT_URL},
}
(ROOT / "reports" / "aspen-condo-lasalle-direct-samples-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

availability_path = ROOT / "reports" / "listing-availability-checks-2026-10-18.csv"
if availability_path.exists():
    with availability_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        rows = [row for row in reader if not (row.get("hipflat_id") == str(ID) and row.get("market") in {"sale", "rent"})]
    rows.extend([
        {"hipflat_id": str(ID), "condo": NAME, "checked_at": CHECKED, "market": "sale",
         "status": "active_as_listed", "verification_note": "PropertyHub project feed shows the linked 1BR/24sqm/฿1.3m listing refreshed on 14 Oct 2026. Current availability has not been confirmed with the advertiser.",
         "source_1": SALE_URL, "source_2": SALE_PROJECT_URL, "source_3": RENT_PROJECT_URL},
        {"hipflat_id": str(ID), "condo": NAME, "checked_at": CHECKED, "market": "rent",
         "status": "active_as_listed", "verification_note": "PropertyHub Phase A project feed shows the linked multi-unit listing refreshed on 6 Oct 2026 and gives the 24sqm 1-bedroom option at ฿7,500/month. Current availability has not been confirmed with the advertiser.",
         "source_1": RENT_URL, "source_2": RENT_PROJECT_URL, "source_3": SALE_PROJECT_URL},
    ])
    with availability_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

print(json.dumps({"hipflatId": ID, "saleTHB": SALE_PRICE, "saleTHBPerSqm": sale_rate,
                  "rentTHBPerMonth": RENT_PRICE, "rentTHBPerSqmMonth": rent_rate,
                  "twoBedroomYield": "not calculated: no linked two-bedroom comparables"}))
