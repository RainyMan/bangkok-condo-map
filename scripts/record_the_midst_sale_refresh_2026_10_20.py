"""Record the refreshed direct sale evidence for Hipflat project 3087."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3087
AS_OF = "2026-10-20"
SALE_URL = "https://www.livinginsider.com/detail/condo-for-sale-ladprao-central-ladprao-1bedroom-3057798"
RENT_URL = "https://www.fazwaz.com/property-rent/1-bedroom-condo-for-rent-at-the-midst-condo-in-chantharakasem-bangkok-u6729242"
PH_SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-the-midst-condo"
DD_OLD_URL = "https://www.ddproperty.com/property/%25E0%25B8%2594%25E0%25B8%25AD%25E0%25B8%25B0-%25E0%25B8%25A1%25E0%25B8%25B4%25E0%25B8%25AA%25E0%25B8%2597%25E0%25B9%258C-%25E0%25B8%2584%25E0%25B8%25AD%25E0%25B8%2599%25E0%25B9%2582%25E0%25B8%2594-%25E0%25B8%2581%25E0%25B8%25A3%25E0%25B8%25B8%25E0%25B8%2597-%25E0%25B8%25A2-%25E0%25B8%2582%25E0%25B8%25B2%25E0%25B8%25A2-500277870"


def read_array(filename: str, symbol: str) -> tuple[Path, str, list[dict], str]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{re.escape(symbol)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot parse {symbol} from {filename}")
    return path, match.group(1), json.loads(match.group(2)), match.group(3)


def write_array(path: Path, prefix: str, rows: list[dict], suffix: str) -> None:
    path.write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix, encoding="utf-8")


_, sale_prefix, manual_rows, sale_suffix = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is None:
    manual = {"hipflatId": PROJECT_ID, "name": "The Midst Condo"}
    manual_rows.append(manual)

sale_sample = {
    "id": "3057798",
    "price": 2_826_240,
    "area": 22,
    "priceSqm": 128_465,
    "beds": 1,
    "roomType": "ONE_BED_ROOM",
    "title": "ประกาศขายคอนโด THE MIDST Condo รัชดา-ลาดพร้าว · 1 房 · 22㎡ · ฿2,826,240",
    "url": SALE_URL,
    "sourceName": "LivingInsider",
    "projectName": "The Midst Condo Ratchada-Lat Phrao",
    "updated": AS_OF,
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "matchedBy": "direct_listing_title_and_description_name_The_Midst_Condo_Ratchada_Lat_Phrao_and_Chan_Kasem; listing_page_project_field_is_unspecified",
    "note": "Listing created 2026-04-29 and was bumped about one week before the 2026-10-20 check. Price and 22 sqm area are explicit; project name appears in title/description, but listing page's project field is unspecified. Treat as a current candidate with availability and project match to confirm.",
}
sale = manual.setdefault("sale", {})
samples = [sample for sample in sale.get("samples", []) if str(sample.get("id")) != sale_sample["id"]]
samples.append(sale_sample)
sale.update({
    "samples": samples,
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "minimum": 2_826_240,
    "minimumArea": 22,
    "minimumSampleUpdated": AS_OF,
    "minimumSqm": 128_465,
    "minimumSqmSampleUpdated": AS_OF,
    "average": 2_826_240,
    "averageSqm": 128_465,
    "asOf": AS_OF,
    "sourceName": "LivingInsider 直接出售掛牌",
    "source": SALE_URL,
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "note": "目前只有一筆一房候選出售掛牌；頁面標示約一週前重新刊登，但專案欄空白。以標題和描述的本案名稱及地區配對，仍待向刊登者確認；不視為兩房樣本。",
})
manual["asOf"] = AS_OF
write_array(DIST / "bangkok-manual-market-samples.js", sale_prefix, manual_rows, sale_suffix)

_, cross_prefix, cross_rows, cross_suffix = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next((row for row in cross_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if cross is None:
    raise RuntimeError("Expected current The Midst cross-check record")
cross["asOf"] = AS_OF
cross["sourceName"] = "PropertyHub / DDproperty / LivingInsider / FazWaz"
sale_check = cross.setdefault("sale", {})
sale_check["activeListingCount"] = 1
sale_check["displayedResultCount"] = 1
sale_check["sourceUrl"] = SALE_URL
sale_check["listings"] = [{
    "listingId": "3057798",
    "price": 2_826_240,
    "area": 22,
    "priceSqm": 128_465,
    "bedrooms": 1,
    "listedAt": "2026-04-29",
    "url": SALE_URL,
    "sourceName": "LivingInsider",
    "listingStatus": "availability_unconfirmed_update_under_30d",
    "statusLabel": "頁面約一週前重新刊登；標題和描述指向 The Midst Ratchada-Lat Phrao，但專案欄未指定，房型 1 房、22㎡、฿2,826,240。需向刊登者確認在架狀態與專案歸屬。",
    "alternateSourceUrls": [DD_OLD_URL],
}]
sale_check["note"] = "PropertyHub 專案出售頁仍顯示 0 筆。LivingInsider 另有約一週前重新刊登的 1 房、22㎡、฿2,826,240 掛牌，與 DDproperty 2026-04-29 的同價同面積歷史頁相符，可能為同一房源的跨平台重刊；只計一筆候選樣本。專案欄未指定，現況及歸屬需確認。"
availability = cross.setdefault("availabilitySources", [])
availability = [row for row in availability if row.get("url") not in {SALE_URL, DD_OLD_URL}]
availability.extend([
    {"sourceName": "PropertyHub 出售專案頁", "url": PH_SALE_PROJECT, "statusLabel": "目前顯示 0 筆出售物件。"},
    {"sourceName": "LivingInsider 一房出售掛牌", "url": SALE_URL, "statusLabel": "1 房、22㎡、฿2,826,240；約一週前重新刊登，專案欄未指定，歸屬及在架狀態待確認。"},
    {"sourceName": "DDproperty 歷史出售掛牌", "url": DD_OLD_URL, "statusLabel": "同為 22㎡、฿2,826,240，刊登日期 2026-04-29；可能與 LivingInsider 為同一房源，保留作交叉來源，不另計樣本。"},
])
cross["availabilitySources"] = availability
cross["yieldStatus"] = "one_bedroom_candidate_yield_unconfirmed"
cross["yieldNote"] = "沒有可核實兩房出售樣本。若接受這筆一房候選售盤及目前 1 房租盤，試算只能標示一房估算；售盤專案欄未指定且現況待確認，暫不把候選值當作確定市場投報。"
write_array(DIST / "bangkok-market-crosschecks.js", cross_prefix, cross_rows, cross_suffix)

report = {
    "hipflatId": PROJECT_ID,
    "project": "The Midst Condo",
    "asOf": AS_OF,
    "saleCandidate": sale_sample,
    "rentSample": {
        "id": "U6729242", "price": 10_000, "area": 28.8, "bedrooms": 1,
        "url": RENT_URL, "status": "availability_unconfirmed_update_under_30d",
    },
    "treatment": "One-bedroom cross-platform candidate only; no two-bedroom sale evidence. Crosswalk uncertainty and availability remain visible. Existing two-bedroom ROI must not be inferred.",
}
(ROOT / "reports" / "the-midst-sale-refresh-2026-10-20.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "salePrice": sale_sample["price"], "area": sale_sample["area"], "bedrooms": sale_sample["beds"], "status": sale_sample["listingStatus"]}, ensure_ascii=False))
