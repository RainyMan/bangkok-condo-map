"""Replace invalid Belle Grand Rama 9 summary prices with verified linked listings."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "belle-grand-rama-9-listing-verification-2026-10-18.md"
PROJECT_ID = 5365
CHECKED = "2026-10-18"
SALE_URL = "https://propertyhub.in.th/en/listings/2-br-condo-for-sale-58-sqm-belle-grand-rama-9-near-mrt-phra-ram-9-id-3146118---6263032"
RENT_URL = "https://propertyscout.co.th/en/2-br-condo-belle-grand-rama-9-near-mrt-phra-ram-9-3139090/"
SALE_PAGE = "https://propertyhub.in.th/en/condo-for-sale/project-belle-grand-rama-9-belle-avenue"
RENT_PAGE = "https://propertyscout.co.th/en/bangkok/condo/belle-grand-rama-9/rentals/"
COORDINATE_URL = "https://www.condonayoo.com/belle-grand-rama-9/?v=1.0"


def load_array(filename: str, symbol: str) -> tuple[Path, str, list[dict]]:
    path = DIST / filename
    content = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*?\]);\s*$", content, re.S)
    if not match:
        raise RuntimeError(f"Could not parse {symbol} from {path}")
    return path, content, json.loads(match.group(1))


def save_array(path: Path, content: str, symbol: str, rows: list[dict]) -> None:
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


sale = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 5_790_000,
    "minimum": 5_790_000,
    "minimumArea": 58.0,
    "averageSqm": 99_828,
    "minimumSqm": 99_828,
    "minimumSampleUpdated": CHECKED,
    "minimumSqmSampleUpdated": CHECKED,
    "asOf": CHECKED,
    "sourceName": "PropertyHub 兩房單筆出售掛牌（直接物件頁）",
    "source": SALE_PAGE,
    "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL,
    "byBedroom": {
        "2": {
            "beds": 2,
            "count": 1,
            "minimum": 5_790_000,
            "minimumArea": 58.0,
            "area": 58.0,
            "priceSqm": 99_828,
            "minimumSqm": 99_828,
            "minimumSourceUrl": SALE_URL,
            "minimumSqmSourceUrl": SALE_URL,
            "sourceUrl": SALE_URL,
        }
    },
    "samples": [
        {
            "id": "6263032",
            "price": 5_790_000,
            "area": 58.0,
            "priceSqm": 99_828,
            "beds": 2,
            "roomType": "2BR",
            "title": "2-BR Condo at Belle Grand Rama 9 near MRT Phra Ram 9 (ID 3146118)",
            "url": SALE_URL,
            "sourceName": "PropertyHub",
            "projectName": "Belle Grand Rama 9",
            "updated": CHECKED,
            "checkedAt": CHECKED,
            "matchedBy": "exact_project_listing_page_and_listing_id",
            "listingStatus": "active_as_listed",
        }
    ],
}
rent_rate = 25_000 / 56
rent = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": 25_000,
    "minimum": 25_000,
    "minimumArea": 56.0,
    "averageSqm": round(rent_rate),
    "minimumSqm": round(rent_rate),
    "minimumSampleUpdated": "2026-09",
    "minimumSqmSampleUpdated": "2026-09",
    "asOf": CHECKED,
    "sourceName": "PropertyScout 確認可租的兩房單筆掛牌",
    "source": RENT_PAGE,
    "minimumSourceUrl": RENT_URL,
    "minimumSqmSourceUrl": RENT_URL,
    "byBedroom": {
        "2": {
            "beds": 2,
            "count": 1,
            "minimum": 25_000,
            "minimumArea": 56.0,
            "area": 56.0,
            "priceSqm": round(rent_rate),
            "minimumSqm": rent_rate,
            "minimumSourceUrl": RENT_URL,
            "minimumSqmSourceUrl": RENT_URL,
            "sourceUrl": RENT_URL,
        }
    },
    "samples": [
        {
            "id": "3139090",
            "price": 25_000,
            "area": 56.0,
            "priceSqm": round(rent_rate),
            "beds": 2,
            "roomType": "2BR",
            "title": "2-BR Condo for rent, Belle Grand Rama 9, near MRT Phra Ram 9",
            "url": RENT_URL,
            "sourceName": "PropertyScout",
            "projectName": "Belle Grand Rama 9",
            "updated": "2026-09",
            "checkedAt": CHECKED,
            "matchedBy": "exact_project_listing_id_and_confirmed_availability",
            "listingStatus": "availability_unconfirmed_update_over_30d",
        }
    ],
}

# Replace the polluted project-summary values: PropertyScout's prior sale
# minimum was parsed as ฿10,200. Keep counts honest as a single checked object.
manual_path, manual_content, manual_rows = load_array(
    "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
)
row = next((item for item in manual_rows if int(item["hipflatId"]) == PROJECT_ID), None)
if row is None:
    row = {"hipflatId": PROJECT_ID, "name": "Belle Grand Rama 9"}
    manual_rows.append(row)
row.update({"hipflatId": PROJECT_ID, "name": "Belle Grand Rama 9", "replaceSale": True, "replaceRent": True, "sale": sale, "rent": rent})
manual_rows.sort(key=lambda item: int(item["hipflatId"]))
save_array(manual_path, manual_content, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

coord_path, coord_content, coord_rows = load_array(
    "bangkok-propertyscout-details.js", "BANGKOK_PROPERTYSCOUT_DETAILS"
)
coord = next((item for item in coord_rows if int(item["hipflatId"]) == PROJECT_ID), None)
if coord is None:
    raise RuntimeError("Expected existing verified PropertyScout project coordinate")
coord["locationVerificationSourceUrl"] = COORDINATE_URL
coord["verificationMethod"] = "exact_project_source_crosschecked_with_google_map_coordinate"
save_array(coord_path, coord_content, "BANGKOK_PROPERTYSCOUT_DETAILS", coord_rows)

cross_path, cross_content, cross_rows = load_array(
    "bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS"
)
cross = next((item for item in cross_rows if int(item["hipflatId"]) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID, "projectName": "Belle Grand Rama 9"}
    cross_rows.append(cross)
cross.update({
    "hipflatId": PROJECT_ID,
    "projectName": "Belle Grand Rama 9",
    "asOf": CHECKED,
    "sourceName": "PropertyHub / PropertyScout",
    "projectSourceUrl": SALE_PAGE,
    "sale": {
        "activeListingCount": 1,
        "sourceUrl": SALE_PAGE,
        "minimumObservedListingUrl": SALE_URL,
        "minimumObservedPrice": 5_790_000,
        "minimumObservedArea": 58.0,
        "bedrooms": 2,
    },
    "rent": {
        "activeListingCount": 1,
        "sourceUrl": RENT_PAGE,
        "minimumObservedListingUrl": RENT_URL,
        "minimumObservedPrice": 25_000,
        "minimumObservedArea": 56.0,
        "bedrooms": 2,
        "availabilityChecked": "about one month before 2026-10-18",
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 兩房出售物件", "url": SALE_URL, "statusLabel": "售價฿5,790,000 · 58㎡ · 頁面於 2026-10-18 出現在專案結果"},
        {"sourceName": "PropertyScout 已確認可租物件", "url": RENT_URL, "statusLabel": "租金฿25,000/月 · 56㎡ · 約於核對日前一個月確認可租"},
    ],
})
cross_rows.sort(key=lambda item: int(item["hipflatId"]))
save_array(cross_path, cross_content, "BANGKOK_MARKET_CROSSCHECKS", cross_rows)

# ROI: 2BR purchase ฿5.79M / 58m²; rent rate from the lowest observed linked
# 2BR sample (฿25K / 56m²); one broker month deducted, no fee deducted because
# the current common fee is not verified.
monthly_rent = rent_rate * 58
net_yield = (monthly_rent * 11) / 5_790_000 * 100
gross_yield = (monthly_rent * 12) / 5_790_000 * 100
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(
    f"""# Belle Grand Rama 9 data correction and listing verification ({CHECKED})

- Hipflat project (ID 5365): https://www.hipflat.co.th/en/projects/belle-grand-rama-9-umlqcz
- Completed year: 2015. PropertyScout says completed in 2015 and lists 1,991 units / 43 floors.
- Coordinates currently used by the map: `13.760072, 100.569425` from the exact Belle Grand Rama 9 PropertyScout project page: https://propertyscout.co.th/en/bangkok/condo/belle-grand-rama-9/ . Condonayoo's approximate Google map point is `13.760158, 100.569434` (about 10 m away): {COORDINATE_URL}
- Corrected a corrupt PropertyScout sale minimum that had been interpreted as ฿10,200. Since the available summary did not identify an individual unit, the displayed figures now honestly show the one directly linked 2BR sale sample below.

## Verified two-bedroom samples

1. Sale: ฿5,790,000, 58 m², 2BR, or about ฿99,828/m². PropertyHub listing ID 6263032 / project unit ID 3146118: {SALE_URL}. The direct page agrees on price, area, bedrooms, and project; it appeared in the project's current results when checked on 2026-10-18.
2. Rent: ฿25,000/month, 56 m², 2BR, or about ฿446/m²/month. PropertyScout listing ID 3139090: {RENT_URL}. The direct page reports “confirmed available a month ago,” checked on 2026-10-18; availability should be rechecked before contacting the agent.

## Yield estimate

Use the 2BR sale sample's own purchase area (58 m²) and scale the 2BR rent sample's per-m² rate (`25,000 / 56`) to it, giving estimated rent of about ฿25,893/month. Gross annual yield is **{gross_yield:.2f}%**. After one month of agency fee, it is **{net_yield:.2f}%**. Common-area fee is currently unverified and therefore not deducted; transfer taxes, repairs, vacancy, and financing are also excluded.

Both market panels intentionally report one directly verified listing sample, not a project-wide average. The previous market summary's sale minimum was invalid and has been replaced rather than carried forward.
""",
    encoding="utf-8",
)
print(json.dumps({"hipflatId": PROJECT_ID, "saleSamples": 1, "rentSamples": 1, "saleMinimum": 5_790_000, "saleArea": 58, "rentMinimum": 25_000, "rentArea": 56, "estimatedMonthlyRent": round(monthly_rent), "grossAnnualYieldPercent": round(gross_yield, 2), "afterOneAgentMonthYieldPercent": round(net_yield, 2)}, ensure_ascii=False))
