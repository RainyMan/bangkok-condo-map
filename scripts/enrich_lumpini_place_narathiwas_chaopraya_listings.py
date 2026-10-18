"""Attach verified two-bedroom sale and rent listings to both Hipflat aliases."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "dist" / "bangkok-manual-market-samples.js"
REPORT_FILE = ROOT / "reports" / "lumpini-place-narathiwas-chaopraya-listings-2026-10-18.json"
CHECKED_AT = "2026-10-18"
SALE_URL = (
    "https://propertyhub.in.th/en/listings/"
    "2-br-condo-at-lumpini-place-narathiwat-chaopraya-close-to-phra-ram-3-"
    "id-3260053---6352799"
)
RENT_URL = (
    "https://propertyhub.in.th/en/listings/"
    "for-rent-condo-lumpini-place-narathiwas-chaopraya-chong-nonsi-yannawa-"
    "bangkok-cx-52999-live-chat-with-us-add-line-connexproperty--a6ed096d---4397609"
)
PROJECT_SALE_URL = "https://propertyhub.in.th/en/condo-for-sale/project-lumpini-place-narathiwas-chaopraya"
PROJECT_RENT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-lumpini-place-narathiwas-chaopraya"
PROJECT_IDS = (3848, 5521)

SALE_SAMPLE = {
    "id": "6352799",
    "price": 4_600_000,
    "area": 68,
    "priceSqm": 67_647,
    "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Lumpini Place Narathiwat-Chaopraya，2 房，68 ㎡，฿4,600,000",
    "url": SALE_URL,
    "sourceName": "PropertyHub（PropertyScout 掛牌）",
    "projectName": "Lumpini Place Narathiwas - Chaopraya",
    "updated": "2026-10-16",
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_unit_details",
    "listingStatus": "active_as_listed",
}
RENT_SAMPLE = {
    "id": "4397609",
    "price": 20_000,
    "area": 68,
    "priceSqm": 294,
    "beds": 2,
    "roomType": "TWO_BED_ROOM",
    "title": "Lumpini Place Narathiwas - Chaopraya，2 房，68 ㎡，฿20,000／月",
    "url": RENT_URL,
    "sourceName": "PropertyHub（Connex Property）",
    "projectName": "Lumpini Place Narathiwas - Chaopraya",
    "updated": CHECKED_AT,
    "checkedAt": CHECKED_AT,
    "matchedBy": "exact_project_name_and_unit_details",
    "listingStatus": "active_as_listed",
}


def load_array(path: Path, variable: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"\s*window\.{re.escape(variable)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise ValueError(f"Could not parse {variable} from {path}")
    return json.loads(match.group(1))


def main() -> None:
    rows = load_array(DATA_FILE, "BANGKOK_MANUAL_MARKET_SAMPLES")
    by_id = {int(row["hipflatId"]): row for row in rows}
    additions = []
    for project_id in PROJECT_IDS:
        if project_id in by_id:
            row = by_id[project_id]
            if any(sample.get("url") in {SALE_URL, RENT_URL} for market in (row.get("sale"), row.get("rent")) if market for sample in market.get("samples", [])):
                continue
        else:
            row = {
                "hipflatId": project_id,
                "name": "Lumpini Place Narathiwas-Chaopraya" if project_id == 3848 else "Lumpini Place Narathiwas - Chaopraya",
                "asOf": CHECKED_AT,
            }
            rows.append(row)
            by_id[project_id] = row
        row["asOf"] = CHECKED_AT
        for kind, sample in (("sale", SALE_SAMPLE), ("rent", RENT_SAMPLE)):
            market = row.setdefault(kind, {})
            samples = market.setdefault("samples", [])
            if not any(existing.get("url") == sample["url"] for existing in samples):
                samples.append(sample.copy())
        additions.append(project_id)

    DATA_FILE.write_text(
        "window.BANGKOK_MANUAL_MARKET_SAMPLES = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    report = {
        "checkedAt": CHECKED_AT,
        "hipflatProjectIds": list(PROJECT_IDS),
        "projectAliases": ["Lumpini Place Narathiwas-Chaopraya", "Lumpini Place Narathiwas - Chaopraya"],
        "aliasEvidence": "Both Hipflat entries resolve to the same verified PropertyScout project coordinate (13.683371, 100.548909) and the exact PropertyHub project name, address district, and 68 sqm two-bedroom unit type.",
        "coordinateSource": "https://propertyscout.co.th/en/bangkok/condo/lumpini-place-narathiwat-chaopraya/",
        "sale": {
            "projectPage": PROJECT_SALE_URL,
            "listing": SALE_SAMPLE,
            "verification": "The exact-project PropertyHub sale page shows 2-bedroom listings at 68 sqm; the linked individual PropertyHub listing confirms the project, 2 bedrooms, 68 sqm, THB 4,600,000, and was refreshed 2026-10-16. It is the lowest total price among the two-bedroom listings shown on the exact-project sale page when checked.",
        },
        "rent": {
            "projectPage": PROJECT_RENT_URL,
            "listing": RENT_SAMPLE,
            "verification": "The exact-project PropertyHub rent page shows two-bedroom listings at 68 sqm; the linked individual listing confirms the project, 2 bedrooms, 68 sqm, THB 20,000/month, and an update timestamp of 2026-10-18. It is the lowest two-bedroom monthly rent shown on the exact-project rent page when checked.",
        },
        "yieldBaseline": {
            "bedrooms": 2,
            "purchasePriceThb": SALE_SAMPLE["price"],
            "purchaseAreaSqm": SALE_SAMPLE["area"],
            "rentRateThbPerSqmMonth": round(RENT_SAMPLE["price"] / RENT_SAMPLE["area"], 2),
            "estimatedMonthlyRentThb": RENT_SAMPLE["price"],
            "annualYieldAfterOneAgentMonthBeforeUnverifiedCommonFeePercent": round(
                RENT_SAMPLE["price"] * 11 / SALE_SAMPLE["price"] * 100, 2
            ),
            "note": "The estimate uses 11 rent months after a one-month agent fee. The available source labels a 25 THB/sqm charge as Utility Fee; it is not treated as a confirmed common-area management fee and is not deducted.",
            "saleSourceUrl": SALE_URL,
            "rentSourceUrl": RENT_URL,
        },
        "manualSamplesAddedToHipflatIds": additions,
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"projectIds": PROJECT_IDS, "saleUrl": SALE_URL, "rentUrl": RENT_URL, "report": str(REPORT_FILE)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
