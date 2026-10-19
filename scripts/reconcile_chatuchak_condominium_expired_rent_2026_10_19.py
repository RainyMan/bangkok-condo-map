"""Reconcile an expired rent listing and clear its active rent baseline."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3005
LISTING_ID = "6242213"
AS_OF = "2026-10-19"
LISTING_URL = "https://propertyhub.in.th/en/listings/%EF%B8%8F-64-2-sq-m-condo-for-rent-high-floor-stunning-chatuchak-park-view-fully-furnished-move-in-ready---6242213"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-chatuchak-condominium"
SALE_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-sale/project-chatuchak-condominium"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/chatuchak-condominium-cpdwry"


def read_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Could not read {symbol} from {filename}")
    return json.loads(match.group(1))


def write_array(filename: str, symbol: str, rows: list[dict]) -> None:
    text = f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (DIST / filename).write_text(text, encoding="utf-8")


manual = read_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
record = next(row for row in manual if int(row["hipflatId"]) == PROJECT_ID)
rent = record["rent"]
sample = next(row for row in rent["samples"] if str(row.get("id")) == LISTING_ID)
sample["listingStatus"] = "confirmed_unavailable"
sample["availableUntil"] = "2026-06-30"
sample["statusCheckedAt"] = AS_OF
sample["statusNote"] = "PropertyHub direct page says available for rent through 2026-06-30; this date has passed."
rent.update({
    "count": 0,
    "observedCount": 0,
    "countKind": "no_current_verified_listings",
    "average": None,
    "minimum": None,
    "minimumArea": None,
    "minimumSampleUpdated": None,
    "averageSqm": None,
    "minimumSqm": None,
    "minimumSqmSampleUpdated": None,
    "asOf": AS_OF,
    "source": RENT_PROJECT_URL,
    "minimumSourceUrl": None,
    "minimumSqmSourceUrl": None,
    "byBedroom": {},
})
record["replaceRent"] = True
record["asOf"] = AS_OF
write_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

crosschecks = read_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next(row for row in crosschecks if int(row["hipflatId"]) == PROJECT_ID)
cross["asOf"] = AS_OF
cross["projectSourceUrl"] = SALE_PROJECT_URL
cross["sale"] = {"activeListingCount": 0, "sourceUrl": SALE_PROJECT_URL}
cross["rent"] = {
    "activeListingCount": 0,
    "displayedResultCount": 1,
    "sourceUrl": RENT_PROJECT_URL,
    "note": "The project page displays one result, but the linked listing's stated availability ended 2026-06-30.",
}
cross["availabilitySources"] = [
    {
        "sourceName": "Hipflat",
        "url": HIPFLAT_URL,
        "statusLabel": "專案頁目前沒有可用出售／出租掛牌。",
    },
    {
        "sourceName": "PropertyHub 出售專案頁",
        "url": SALE_PROJECT_URL,
        "statusLabel": "核對日顯示 No matched properties for Sale。",
    },
    {
        "sourceName": "PropertyHub 租屋單筆頁",
        "url": LISTING_URL,
        "statusLabel": "頁面顯示租期至 2026-06-30，已過期；保留為歷史樣本，不列目前租金或投報。",
    },
]
write_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "project": "Chatuchak Condominium",
    "checkedAt": AS_OF,
    "sources": {
        "propertyhubRentProject": RENT_PROJECT_URL,
        "propertyhubSaleProject": SALE_PROJECT_URL,
        "rentListing": LISTING_URL,
        "hipflatProject": HIPFLAT_URL,
    },
    "rent": {
        "status": "historical_listing_expired",
        "projectPageDisplayedResults": 1,
        "priceTHBPerMonth": 33000,
        "areaSqm": 64,
        "bedrooms": 2,
        "priceTHBPerSqmPerMonth": 515.625,
        "availableUntil": "2026-06-30",
        "treatment": "Retained as a directly linked historical sample. Excluded from current rent metrics and yield calculations.",
    },
    "sale": {
        "status": "no_current_project_listing",
        "projectPageDisplayedResults": 0,
        "treatment": "No sale basis; do not calculate ROI.",
    },
    "yield": {"status": "not_calculable", "reason": "No verified current sale and rent listing pair."},
}
(ROOT / "reports" / "chatuchak-condominium-market-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"hipflatId": PROJECT_ID, "activeRentSamples": 0, "saleListings": 0, "yield": "not calculable"}))
