"""Add source-linked sale/rent samples and project coordinates for Thana Place."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / f"thana-place-market-{date.today().isoformat()}.json"
PROJECT_ID = 3218
PROJECT_NAME = "Thana Place"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/thana-place-gkghzc"
KBT_PROJECT_URL = "https://www.kaibaanthai.com/en/projects/thailand/bangkok/lat-phrao/lat-phrao/thana-place-condominium"
AS_OF = date.today().isoformat()


def read_array(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format: {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    target = DIST / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"window.{symbol} = ")
        for chunk in json.JSONEncoder(ensure_ascii=False, separators=(",", ":")).iterencode(rows):
            stream.write(chunk)
        stream.write(";\n")
    temporary.replace(target)


catalogue = next(row for row in read_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE") if int(row["id"]) == PROJECT_ID)
if catalogue["name"] != PROJECT_NAME or catalogue.get("hipflatProjectUrl") != PROJECT_URL:
    raise RuntimeError("Hipflat catalogue identity does not match the reviewed project page")

sale_1br_url = "https://www.hipflat.co.th/ja/ads/autc0ah089a8tnlle2l3c1et3ul34434"
sale_2br_url = "https://propertyhub.in.th/en/listings/condo-for-sale-at-thana-place-building-60c-sukhonthasawat-lat-phrao-with-an-unobstructed-view---6461769"
rent_1br_url = "https://www.hipflat.co.th/en/ads/u0h2th9l88lah731214acn773u077n2t"

sale_1br = {
    "id": "CX-175650", "price": 1_150_000, "area": 42, "priceSqm": round(1_150_000 / 42, 2),
    "beds": 1, "roomType": "1BR", "title": "Thana Place · 1 房 · 42 ㎡ · ฿1,150,000", "url": sale_1br_url,
    "sourceName": "Hipflat / Connex Property", "projectName": PROJECT_NAME, "checkedAt": AS_OF,
    "updated": AS_OF, "listingStatus": "active_as_listed",
    "matchedBy": "Hipflat direct listing CX-175650 names Thana Place, 1 bedroom, 42 sqm, ฿1,150,000; its project page currently lists six sale units from ฿1,150,000 and the page reports an update 8 hours before the 2026-10-19 check.",
}
sale_2br = {
    "id": "6461769", "price": 1_290_000, "area": 60, "priceSqm": 21_500,
    "beds": 2, "roomType": "2BR", "title": "Thana Place · 2 房最低總價樣本 · 60 ㎡ · ฿1,290,000", "url": sale_2br_url,
    "sourceName": "PropertyHub / Thai Property Investor", "projectName": PROJECT_NAME, "checkedAt": AS_OF,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "PropertyHub direct listing 6461769 explicitly identifies Thana Place Building 60C, 2 bedrooms, 60 sqm, ฿1,290,000 and describes it as the best-priced unit in the project; Hipflat's project page lists this same 2BR/60sqm/8th-floor unit and price.",
}
rent_1br = {
    "id": "U1750728R", "price": 8_000, "area": 45, "priceSqm": round(8_000 / 45, 2),
    "beds": 1, "roomType": "1BR", "title": "Thana Place · 1 房 · 45 ㎡ · ฿8,000/月", "url": rent_1br_url,
    "sourceName": "Hipflat（泰文專案頁核價）", "projectName": PROJECT_NAME, "checkedAt": AS_OF,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "Hipflat direct rental listing identifies unit U1750728R in Thana Place, 1 bedroom, 45 sqm and floor 4; the current Hipflat Thai project page lists one available rental at ฿8,000/month and ฿177/sqm, while the direct unit page reports a recent update within 30 days.",
    "priceReferenceUrl": PROJECT_URL,
}
sale = {
    "count": 2, "observedCount": 2, "countKind": "manual_verified_listing", "average": 1_220_000,
    "minimum": 1_150_000, "minimumArea": 42, "averageSqm": 24_440, "minimumSqm": 21_500,
    "minimumSampleUpdated": AS_OF, "asOf": AS_OF,
    "snapshotMethod": "兩筆直接物件頁，分別核對一房最低總價與兩房最低總價；Hipflat 專案頁交叉核對在架項目及售價。",
    "sourceName": "Hipflat / PropertyHub 個別出售掛牌", "source": PROJECT_URL,
    "minimumSourceUrl": sale_1br_url, "minimumSqmSourceUrl": sale_2br_url,
    "samples": [sale_1br, sale_2br],
    "byBedroom": {
        "1": {"count": 1, "minimum": 1_150_000, "area": 42, "minimumArea": 42, "priceSqm": round(1_150_000 / 42), "minimumSqm": round(1_150_000 / 42), "minimumSourceUrl": sale_1br_url, "sourceUrl": sale_1br_url},
        "2": {"count": 1, "minimum": 1_290_000, "area": 60, "minimumArea": 60, "priceSqm": 21_500, "minimumSqm": 21_500, "minimumSourceUrl": sale_2br_url, "sourceUrl": sale_2br_url},
    },
}
rent = {
    "count": 1, "observedCount": 1, "countKind": "manual_verified_listing", "average": 8_000,
    "minimum": 8_000, "minimumArea": 45, "averageSqm": 178, "minimumSqm": round(8_000 / 45, 2),
    "minimumSampleUpdated": AS_OF, "minimumSqmSampleUpdated": AS_OF, "asOf": AS_OF,
    "snapshotMethod": "Hipflat 專案頁顯示一筆現有出租單位；個別 Hipflat 物件頁核對房型、面積及最近更新，泰文專案頁核對泰銖租金與每平方米租金。",
    "sourceName": "Hipflat 個別出租掛牌", "source": PROJECT_URL,
    "minimumSourceUrl": rent_1br_url, "minimumSqmSourceUrl": rent_1br_url,
    "samples": [rent_1br],
    "byBedroom": {"1": {"count": 1, "minimum": 8_000, "area": 45, "minimumSqm": round(8_000 / 45, 2), "minimumSourceUrl": rent_1br_url, "minimumSqmSourceUrl": rent_1br_url, "sourceUrl": rent_1br_url}},
}

manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = {int(row["hipflatId"]): row for row in manual}
entry = manual_rows.get(PROJECT_ID, {"hipflatId": PROJECT_ID, "name": PROJECT_NAME})
if entry.get("name") not in (None, PROJECT_NAME):
    raise RuntimeError("Manual market data name does not match project ID")
entry.update({
    "name": PROJECT_NAME, "completedYear": 1997, "completedYearSourceUrl": PROJECT_URL,
    "fee": {"rate": 22, "note": "PropertyHub 個別出售頁標示每平方米每月 ฿22 管理費；僅作公開刊載參考，請向管委會核實。", "source": sale_2br_url, "status": "published_indicative"},
    "asOf": AS_OF, "sale": sale, "rent": rent, "replaceSale": True, "replaceRent": True,
})
manual_rows[PROJECT_ID] = entry
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", [manual_rows[key] for key in sorted(manual_rows)])

coordinates = read_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = {int(row["hipflatId"]): row for row in coordinates}
coordinate_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": PROJECT_NAME, "lat": 13.824167, "lng": 100.6151273,
    "locationVerified": True, "sourceName": "KaiBaanThai 專案地圖",
    "sourceUrl": KBT_PROJECT_URL, "verificationSourceUrl": PROJECT_URL,
    "verificationMethod": "KaiBaanThai 專案頁結構化專案座標；以 Hipflat 同名專案及 Sukhonthasawat Road 地址核對",
    "checkedAt": AS_OF,
}
write_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", [coordinate_rows[key] for key in sorted(coordinate_rows)])

REPORT.write_text(json.dumps({
    "hipflatId": PROJECT_ID, "projectName": PROJECT_NAME, "checkedAt": AS_OF,
    "coordinates": {"lat": 13.824167, "lng": 100.6151273, "source": KBT_PROJECT_URL, "crossCheck": PROJECT_URL},
    "completedYear": {"year": 1997, "source": PROJECT_URL},
    "fee": entry["fee"], "sale": sale, "rent": rent,
    "yield": {"1BR": "可按最低 1BR 售價樣本與 1BR 最低租金單價試算", "2BR": "不估算；目前沒有可核實的同房型出租樣本"},
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"project": PROJECT_NAME, "saleSamples": len(sale["samples"]), "rentSamples": len(rent["samples"]), "feeRate": 22, "coordinates": [13.824167, 100.6151273], "report": str(REPORT)}, ensure_ascii=False, indent=2))
