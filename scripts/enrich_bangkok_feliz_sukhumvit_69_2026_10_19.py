"""Attach verified coordinates, direct listings, fee, and ROI evidence for Bangkok Feliz Sukhumvit 69."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKED = "2026-10-19"
PROJECT_ID = 4474
NAME = "Bangkok Feliz Sukhumvit 69"
HIPFLAT = "https://www.hipflat.co.th/en/projects/bangkok-feliz-sukhumvit-69-xugzqu"
DD_SALE_PAGE = "https://www.ddproperty.com/en/property-for-sale/at-bangkok-feliz-sukhumvit-69-1801"
PH_PROJECT = "https://propertyhub.in.th/en/projects/bangkok-feliz-sukhumvit-69"
PH_RENT_PAGE = "https://propertyhub.in.th/en/condo-for-rent/project-bangkok-feliz-sukhumvit-69"
GOOGLE_PIN_SOURCE = "https://www.homenayoo.com/bangkok-feliz-sukhumvit-69/"
OSM_CORROBORATION = "https://mapcarta.com/W320277882"

SALE_1BR = "https://www.ddproperty.com/en/property/bangkok-feliz-sukhumvit-69-bangkok-for-sale-500223483"
SALE_2BR = "https://www.ddproperty.com/en/property/bangkok-feliz-sukhumvit-69-bangkok-for-sale-500482934"
SALE_2BR_CONFLICT = "https://www.ddproperty.com/en/property/bangkok-feliz-sukhumvit-69-bangkok-for-sale-500637932"
RENT_1BR = "https://propertyhub.in.th/en/listings/for-rent-bangkok-feliz-sukhumvit-69-bts-prakhanong-210-m-3-min-walk-call-061-354-4246-negotiable-line-id-condobkk-with-code-h1273---4948577"
RENT_2BR_OLD = "https://www.ddproperty.com/en/property/bangkok-feliz-sukhumvit-69-bangkok-for-rent-500208051"


def read_array(filename: str, symbol: str):
    path = DIST / filename
    content = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*?\]);\s*$", content, re.S)
    if not match:
        raise RuntimeError(f"Could not parse {symbol} from {path}")
    return path, content, json.loads(match.group(1))


def write_array(path: Path, content: str, symbol: str, rows):
    replacement = f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};"
    updated, count = re.subn(
        rf"window\.{re.escape(symbol)}\s*=\s*\[.*?\];\s*$",
        replacement,
        content,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"Could not update {symbol} in {path}")
    path.write_text(updated, encoding="utf-8", newline="")


def listing(listing_id, kind, price, area, beds, title, url, updated, source_name):
    return {
        "id": str(listing_id),
        "kind": kind,
        "price": price,
        "area": area,
        "priceSqm": round(price / area),
        "beds": beds,
        "roomType": f"{beds}BR",
        "title": title,
        "url": url,
        "sourceName": source_name,
        "projectName": NAME,
        "updated": updated,
        "checkedAt": CHECKED,
        "matchedBy": "exact_project_page_card_and_direct_listing_id",
        "listingStatus": "active_as_listed",
    }


sale_samples = [
    listing("500223483", "sale", 3_200_000, 45, 1,
            "Bangkok Feliz Sukhumvit 69 1-bedroom, 45 sqm, ฿3,200,000",
            SALE_1BR, "2026-10-09", "DDproperty"),
    listing("500482934", "sale", 9_900_000, 104.48, 2,
            "Bangkok Feliz Sukhumvit 69 2-bedroom, 104.48 sqm, ฿9,900,000",
            SALE_2BR, "2026-09-27", "DDproperty"),
]
rent_samples = [
    listing("4948577", "rent", 13_000, 36, 1,
            "For Rent Bangkok Feliz Sukhumvit 69 near BTS Phra Khanong, 1-bedroom, 36 sqm, ฿13,000/month",
            RENT_1BR, "2026-10-09", "PropertyHub"),
]

manual_path, manual_content, manual_rows = read_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": NAME}
    manual_rows.append(manual)
manual["fee"] = {
    "rate": 45,
    "status": "published_project_fee",
    "note": "PropertyHub 專案頁明列 Common Fee ฿45/㎡/月。計算仍可由使用者勾選是否扣除。",
    "source": PH_PROJECT,
}

for market_name, new_samples in (("sale", sale_samples), ("rent", rent_samples)):
    market = manual.setdefault(market_name, {})
    by_url = {sample.get("url"): sample for sample in market.get("samples", []) if sample.get("url")}
    by_url.update({sample["url"]: sample for sample in new_samples})
    market["samples"] = list(by_url.values())
    market["asOf"] = CHECKED
    market["sourceName"] = "DDproperty / PropertyHub 精確專案掛牌"

coord_path, coord_content, coord_rows = read_array(
    "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"
)
coord = next((row for row in coord_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if coord is None:
    coord = {"hipflatId": PROJECT_ID, "name": NAME}
    coord_rows.append(coord)
coord.update({
    "name": NAME,
    "lat": 13.715842,
    "lng": 100.591972,
    "locationVerified": True,
    "sourceName": "Homenayoo 專案頁 Google Maps 點位",
    "sourceUrl": GOOGLE_PIN_SOURCE,
    "verificationSourceUrl": OSM_CORROBORATION,
    "verificationMethod": "exact_project_name_and_address_google_maps_pin_crosschecked_against_osm_building_way",
})

cross_path, cross_content, cross_rows = read_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
cross = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID, "projectName": NAME}
    cross_rows.append(cross)
cross.update({
    "projectName": NAME,
    "asOf": CHECKED,
    "sourceName": "DDproperty / PropertyHub",
    "projectSourceUrl": HIPFLAT,
    "sale": {
        "activeListingCount": 11,
        "sourceUrl": DD_SALE_PAGE,
        "listings": [
            {"listingId": row["id"], "price": row["price"], "area": row["area"], "priceSqm": row["priceSqm"], "bedrooms": row["beds"], "listedAt": row["updated"], "url": row["url"], "sourceName": row["sourceName"], "status": "active_as_listed"}
            for row in sale_samples
        ],
    },
    "rent": {
        "sourceUrl": PH_RENT_PAGE,
        "listings": [
            {"listingId": row["id"], "price": row["price"], "area": row["area"], "priceSqm": row["priceSqm"], "bedrooms": row["beds"], "listedAt": row["updated"], "url": row["url"], "sourceName": row["sourceName"], "status": "active_as_listed"}
            for row in rent_samples
        ] + [{
            "listingId": "500208051", "price": 34_000, "area": 92,
            "priceSqm": round(34_000 / 92), "bedrooms": 2,
            "listedAt": "2026-09-03", "url": RENT_2BR_OLD,
            "sourceName": "DDproperty", "status": "availability_unconfirmed_update_over_30d",
        }],
        "statusNote": "現行專案頁所見掛牌沒有可核對的兩房出租。DDproperty 兩房฿34,000/92㎡掛牌最後刊登於2026-09-03，超過30日，僅保留歷史線索，不納入當前投報。",
    },
    "availabilitySources": [
        {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "Bangkok Feliz Sukhumvit 69 專案識別；列售租數量與專案摘要。"},
        {"sourceName": "售盤專案頁與直接掛牌", "url": DD_SALE_PAGE, "statusLabel": "DDproperty 專案頁顯示 11 筆在售；2房目前顯示฿9,900,000/104.48㎡（刊登2026-09-27），1房最低總價掛牌฿3,200,000/45㎡（刊登2026-10-09）。"},
        {"sourceName": "低價兩房售盤待確認衝突", "url": SALE_2BR_CONFLICT, "statusLabel": "DDproperty 搜尋索引曾顯示另一筆฿8,000,000/104.48㎡、刊登2026-10-13；目前直接網址導回專案售盤頁，該頁列出的兩房是฿9,900,000，故8M資料保留為衝突線索、不覆蓋目前可見掛牌。"},
        {"sourceName": "租盤專案頁", "url": PH_RENT_PAGE, "statusLabel": "PropertyHub 專案出租頁顯示現行掛牌；最低已核對的一房掛牌為฿13,000/月、36㎡，刷新2026-10-09。未找到現行可核對兩房出租。"},
        {"sourceName": "過期兩房租盤（排除投報）", "url": RENT_2BR_OLD, "statusLabel": "DDproperty 直接兩房租盤฿34,000/月、92㎡，刊登於2026-09-03；截至2026-10-19已超過30日，現況未確認，不納入現行行情或投報。"},
        {"sourceName": "管理費", "url": PH_PROJECT, "statusLabel": "PropertyHub 專案資料明列 Common Fee ฿45/㎡/月。"},
        {"sourceName": "Google Maps 專案點", "url": GOOGLE_PIN_SOURCE, "statusLabel": "Homenayoo 專案頁列 Google Maps 座標13.715842, 100.591972。"},
        {"sourceName": "OSM 建物交叉核對", "url": OSM_CORROBORATION, "statusLabel": "Mapcarta 的 OpenStreetMap way 320277882 標為 Bangkok Feliz 建物，點位13.71558, 100.59196，與 Google Maps 專案點相距約29公尺。"},
    ],
})

write_array(manual_path, manual_content, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)
write_array(coord_path, coord_content, "BANGKOK_VERIFIED_COORDINATES", coord_rows)
write_array(cross_path, cross_content, "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

purchase = 3_200_000
sale_area = 45
rent_rate = 13_000 / 36
monthly_rent_at_sale_area = rent_rate * sale_area
annual_net_after_agent_and_fee = monthly_rent_at_sale_area * 11 - 45 * sale_area * 12
annual_net_without_agent = monthly_rent_at_sale_area * 12 - 45 * sale_area * 12
roi_after_agent_and_fee = annual_net_after_agent_and_fee / purchase * 100
roi_without_agent = annual_net_without_agent / purchase * 100
report = f"""# Bangkok Feliz Sukhumvit 69 market and location verification ({CHECKED})

- Hipflat project: {HIPFLAT} (Hipflat ID {PROJECT_ID}).
- Coordinates: Homenayoo gives Google Maps point 13.715842, 100.591972. Mapcarta's OSM building way point is 13.71558, 100.59196, about 29 m away. The project pin is now in the verified-coordinate layer.
- Project page: PropertyHub lists one 8-floor building, 71 units, completion 2014 and common fee ฿45/㎡/month. Hipflat's completion year differs; the data source conflict remains visible.

## Direct market evidence

- 1-bedroom sale: [DDproperty listing 500223483]({SALE_1BR}) — ฿3,200,000, 45㎡, listed 2026-10-09. This is the lowest-total 1-bedroom sale shown in the exact project's DDproperty results reviewed on {CHECKED}.
- 2-bedroom sale: [DDproperty listing 500482934]({SALE_2BR}) — ฿9,900,000, 104.48㎡, listed 2026-09-27. The current project page displays this as its one 2-bedroom result.
- 1-bedroom rent: [PropertyHub listing 4948577]({RENT_1BR}) — ฿13,000/month, 36㎡, refreshed 2026-10-09; the rate is ฿361.11/㎡/month.
- 2-bedroom rent: [DDproperty listing 500208051]({RENT_2BR_OLD}) — ฿34,000/month, 92㎡, listed 2026-09-03. It is over 30 days old as of the check date, so availability is unconfirmed and it is excluded from the current 2-bedroom ROI baseline.
- Conflict check: DDproperty search indexed listing 500637932 at ฿8,000,000/104.48㎡, but its direct URL currently redirects to the project results page, where the visible 2-bedroom listing is ฿9,900,000. The unresolvable lower-price record is retained as a conflict lead and not treated as an active sample.

## One-bedroom annual yield estimate

- Purchase baseline: ฿3,200,000 and the same listing's 45㎡.
- Rent baseline: ฿13,000 ÷ 36㎡ × 45㎡ = about ฿16,250/month.
- Common fee: ฿45 × 45㎡ × 12 = ฿24,300/year.
- With one month of agent management deducted: (฿16,250 × 11 − ฿24,300) ÷ ฿3,200,000 = **{roi_after_agent_and_fee:.2f}% net annual yield**.
- Without the one-month agent deduction, keeping the same common fee: **{roi_without_agent:.2f}%**.
- A current 2-bedroom rental was not found, so no current two-bedroom ROI is claimed. The app can calculate the one-bedroom case when that room type is selected.
"""
(ROOT / "reports/bangkok-feliz-sukhumvit-69-market-2026-10-19.md").write_text(report, encoding="utf-8", newline="")
print(json.dumps({
    "project": NAME,
    "coordinates": [13.715842, 100.591972],
    "saleSamplesAdded": len(sale_samples),
    "rentSamplesAdded": len(rent_samples),
    "oneBedroomYieldAfterFeeAndAgentPercent": round(roi_after_agent_and_fee, 2),
    "twoBedroomYield": "not calculated; current 2-bedroom rent not verified",
    "report": "reports/bangkok-feliz-sukhumvit-69-market-2026-10-19.md",
}, ensure_ascii=False))
