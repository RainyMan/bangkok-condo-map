"""Refresh verified 31 Residence rents from Hipflat's live project listings."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_PATH = ROOT / "dist" / "bangkok-manual-market-samples.js"
INDEX_PATH = ROOT / "dist" / "index.html"
REPORT_PATH = ROOT / "reports" / "31-residence-rent-samples-2026-10-18.json"
PROJECT_ID = 3006
CHECKED_AT = "2026-10-18"
PROJECT_URL = "https://www.hipflat.co.th/en/projects/31-residence-krkcne"

RENT_SAMPLES = [
    {
        "id": "U37158", "price": 75_000, "area": 170, "priceSqm": 441,
        "beds": 2, "roomType": "2BR",
        "title": "31 Residence，2 房，170 ㎡，฿75,000/月",
        "url": "https://www.hipflat.co.th/en/ads/le7at2e78l17nthcu7ucta073u02u980",
        "sourceName": "Hipflat", "projectName": "31 Residence",
        "updated": CHECKED_AT, "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_and_listing_detail",
        "listingStatus": "active_as_listed",
    },
    {
        "id": "BR0684AP", "price": 95_000, "area": 270, "priceSqm": 352,
        "beds": 3, "roomType": "3BR",
        "title": "31 Residence，3 房，270 ㎡，฿95,000/月",
        "url": "https://www.hipflat.co.th/en/ads/928n422n88a2c28hh1t1hul33u0l0ehn",
        "sourceName": "Hipflat", "projectName": "31 Residence",
        "updated": "2026-09-09", "checkedAt": CHECKED_AT,
        "matchedBy": "exact_hipflat_project_and_listing_detail",
        "listingStatus": "availability_unconfirmed_update_over_30d",
    },
]


def load_rows() -> list[dict]:
    text = MANUAL_PATH.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError("Unexpected manual market sample data format")
    return json.loads(match.group(1))


rows = load_rows()
project = next(row for row in rows if int(row.get("hipflatId", 0)) == PROJECT_ID)
existing_rent = project.get("rent", {}).get("samples", [])
samples_by_url = {row["url"]: row for row in existing_rent if row.get("url")}
samples_by_url.update({row["url"]: row for row in RENT_SAMPLES})
samples = sorted(samples_by_url.values(), key=lambda row: (int(row["price"]), row["area"]))
rates = [row["price"] / row["area"] for row in samples]
lowest_total = min(samples, key=lambda row: row["price"])
lowest_rate = min(samples, key=lambda row: row["price"] / row["area"])
by_bedroom = {}
for beds in sorted({int(row["beds"]) for row in samples}):
    room_samples = [row for row in samples if int(row["beds"]) == beds]
    low_total = min(room_samples, key=lambda row: row["price"])
    low_rate = min(room_samples, key=lambda row: row["price"] / row["area"])
    by_bedroom[str(beds)] = {
        "count": len(room_samples),
        "minimum": low_total["price"],
        "area": low_total["area"],
        "minimumArea": low_total["area"],
        "priceSqm": round(low_rate["price"] / low_rate["area"]),
        "minimumSqm": round(low_rate["price"] / low_rate["area"]),
        "averageSqm": round(sum(row["price"] / row["area"] for row in room_samples) / len(room_samples)),
        "sourceUrl": low_total["url"],
        "minimumSourceUrl": low_total["url"],
        "minimumSqmSourceUrl": low_rate["url"],
    }

project["rent"] = {
    "count": 18,
    "observedCount": len(samples),
    "countKind": "manual_verified_listing",
    "average": round(sum(row["price"] for row in samples) / len(samples)),
    "minimum": lowest_total["price"],
    "minimumArea": lowest_total["area"],
    "minimumSampleUpdated": lowest_total.get("updated"),
    "averageSqm": round(sum(rates) / len(rates)),
    "minimumSqm": round(lowest_rate["price"] / lowest_rate["area"]),
    "minimumSqmSampleUpdated": lowest_rate.get("updated"),
    "asOf": CHECKED_AT,
    "snapshotMethod": "Hipflat exact project page lists 18 available rental units; three direct unit pages checked, including the lowest-total two-bedroom unit and lowest-rate sampled unit.",
    "sourceName": "Hipflat 個別租賃掛牌",
    "source": PROJECT_URL,
    "minimumSourceUrl": lowest_total["url"],
    "minimumSqmSourceUrl": lowest_rate["url"],
    "byBedroom": by_bedroom,
    "samples": samples,
}

MANUAL_PATH.write_text(
    "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
    + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)

index = INDEX_PATH.read_text(encoding="utf-8")
index = index.replace(
    "bangkok-manual-market-samples.js?v=20261018z-aspire-vibha-victory",
    "bangkok-manual-market-samples.js?v=20261018a-31-residence-direct-rents",
    1,
)
INDEX_PATH.write_text(index, encoding="utf-8")

REPORT_PATH.write_text(
    json.dumps(
        {
            "hipflatId": PROJECT_ID,
            "condo": "31 Residence",
            "checkedAt": CHECKED_AT,
            "projectSource": PROJECT_URL,
            "projectListingCount": 18,
            "verifiedRentSamples": samples,
            "rentSummary": project["rent"],
            "saleSearch": {
                "propertyhubProject": "https://propertyhub.in.th/en/condo-for-sale/project-31-residence",
                "propertyhubResult": "No matched properties for Sale",
                "ddpropertyProject": "https://www.ddproperty.com/en/project/6787-31-residence",
                "ddpropertyResult": "For Sale (0)",
                "decision": "No sale listing added; no project-matched active resale unit was found on the checked DDproperty or PropertyHub project pages.",
            },
            "roi": {
                "status": "unavailable",
                "reason": "No verified sale sample for this project; an investment yield would require inventing a purchase price.",
            },
            "notes": [
                "The lowest-total two-bedroom rent is ฿75,000/month for 170 sqm (฿441/sqm/month), refreshed on the Hipflat page within about one hour of checking.",
                "The 3-bedroom ฿95,000 / 270 sqm listing is included as a direct sample, but its 2026-09-09 update is over 30 days old and current availability is unconfirmed.",
                "The existing direct PropertyHub sample (฿77,000 / 160 sqm) is retained; observedCount counts the three directly checked units while count reflects the 18-unit Hipflat project page.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

print(json.dumps({"hipflatId": PROJECT_ID, "verifiedRentSamples": len(samples), "twoBedroom": by_bedroom["2"], "lowestSampleRate": round(lowest_rate["price"] / lowest_rate["area"], 2), "sale": "not found on checked PropertyHub/DDproperty project pages", "roi": "unavailable"}, ensure_ascii=False))
