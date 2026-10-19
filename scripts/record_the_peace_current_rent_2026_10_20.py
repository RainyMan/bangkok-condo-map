"""Record the removed The Peace listing and its current zero-rent check."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3093
AS_OF = "2026-10-20"
PROJECT_URL = "https://propertyhub.in.th/en/projects/the-peace"
RENT_URL = "https://propertyhub.in.th/en/listings/peace-private-place-2-bedrooms-for-rent---4583413"
SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-the-peace"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-the-peace"


def read_array(filename: str, symbol: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"(window\.{symbol}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Cannot parse {symbol}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def write_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


candidate = {
    "id": "4583413",
    "price": 25_000,
    "area": 76,
    "priceSqm": 328.95,
    "beds": 2,
    "roomType": "2BR",
    "title": "Peace Private Place 2 bedrooms, for rent",
    "url": RENT_URL,
    "sourceName": "PropertyHub",
    "projectName": "The Peace",
    "updated": "2026-09-24",
    "checkedAt": AS_OF,
    "matchedBy": "exact_propertyhub_project_listing_page",
    "listingStatus": "confirmed_unavailable_redirects_to_empty_project_page",
    "verificationNote": "搜尋快取曾列 2 房、76㎡、฿25,000/月；2026-10-20 個別網址已轉到本案出租專案頁，而專案頁顯示 No matched properties for Rent，故不作為現行樣本。",
}

prefix, manual_rows, suffix = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual = next((row for row in manual_rows if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if manual is not None:
    rent = manual.get("rent") or {}
    rent["samples"] = [row for row in rent.get("samples", []) if str(row.get("id")) != candidate["id"]]
    if not rent["samples"] and rent.get("minimumSourceUrl") == RENT_URL:
        manual.pop("rent", None)
    if not manual.get("sale") and not manual.get("rent"):
        manual_rows.remove(manual)
write_array("bangkok-manual-market-samples.js", prefix, manual_rows, suffix)

prefix, checks, suffix = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
check = next((row for row in checks if int(row.get("hipflatId", -1)) == PROJECT_ID), None)
if check is None:
    check = {"hipflatId": PROJECT_ID, "projectName": "The Peace"}
    checks.append(check)
check.update({
    "asOf": AS_OF,
    "sourceName": "PropertyHub 個別掛牌與專案頁",
    "projectSourceUrl": PROJECT_URL,
})
check["sale"] = {
    "activeListingCount": 0,
    "displayedResultCount": 0,
    "sourceUrl": SALE_URL,
    "checkedAt": AS_OF,
    "note": "PropertyHub 專案出售頁查核顯示 0 筆。",
}
check["rent"] = {
    "activeListingCount": 0,
    "displayedResultCount": 0,
    "sourceUrl": RENT_PROJECT_URL,
    "checkedAt": AS_OF,
    "listings": [],
    "unavailableCandidates": [candidate],
    "note": "PropertyHub 現行出租專案頁顯示 0 筆。搜尋快取中的掛牌網址現已轉到無匹配物件的專案頁，故不列為可用樣本。",
}
check["availabilitySources"] = [
    {"sourceName": "PropertyHub 專案頁", "url": PROJECT_URL, "statusLabel": "目前專案資訊頁；出租列表另行核對。"},
    {"sourceName": "PropertyHub 出售專案頁", "url": SALE_URL, "statusLabel": "查核時 0 筆出售掛牌。"},
    {"sourceName": "PropertyHub 出租專案頁", "url": RENT_PROJECT_URL, "statusLabel": "目前顯示 No matched properties for Rent。"},
    {"sourceName": "PropertyHub 舊掛牌網址", "url": RENT_URL, "statusLabel": "網址已轉到本案出租專案頁，現行頁面無匹配掛牌；搜尋快取舊資料不納入行情。"},
]
check["yieldStatus"] = "not_calculated"
check["yieldNote"] = "目前沒有本案出售掛牌，無購入價格樣本，故不計投報率。"
write_array("bangkok-market-crosschecks.js", prefix, checks, suffix)

report = {
    "hipflatId": PROJECT_ID,
    "project": "The Peace",
    "checkedAt": AS_OF,
    "historicalSearchCandidate": candidate,
    "projectPage": PROJECT_URL,
    "currentRentPage": {"url": RENT_PROJECT_URL, "result": "No matched properties for Rent", "checkedAt": AS_OF},
    "candidateListingUrlOutcome": "The old listing URL canonicalizes to the empty project rental page; not counted as a current listing.",
    "saleAvailability": {"count": 0, "sourceUrl": SALE_URL, "checkedAt": AS_OF},
    "yieldStatus": "not_calculated_no_current_sale_or_rent_listing",
}
(ROOT / "reports" / "the-peace-stale-rent-candidate-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
