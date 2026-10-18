"""Correct Uea Pracha Building 7's address and record its linked SAM asset listing."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "uea-pracha-building-7-2026-10-18.json"
PROJECT_ID = 3119
PROJECT_NAME = "Uea Pracha Condo Town Building 7"
SAM_URL = "https://npa.sam.or.th/site/index.php/npa/map_preview/13636/"
HIPFLAT_URL = "https://www.hipflat.co.th/projects/uea-pracha-condo-town-building-7-sqnbxh"
BAANFINDER_URL = "https://www.baanfinder.com/en/project/uea-pracha-condotown-7--33427"
CORRECT_ADDRESS = "Soi Nak Niwat 48 Yaek 18, Lat Phrao, Bangkok 10230, THA"


def load_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Could not parse {symbol} from {path.name}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    # Hipflat's catalogue address for this building conflicts with the exact
    # building/unit address on the Thai asset manager's linked sale record.
    for filename, symbol in (
        ("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE"),
        ("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"),
    ):
        path = DIST / filename
        rows = load_array(path, symbol)
        row = next((item for item in rows if int(item.get("id", -1)) == PROJECT_ID), None)
        if not row:
            raise ValueError(f"Hipflat project {PROJECT_ID} missing from {filename}")
        row.update({
            "address": CORRECT_ADDRESS,
            "addressSourceUrl": SAM_URL,
            "addressCrossCheckUrl": BAANFINDER_URL,
            "addressVerificationNote": "SAM's unit record identifies Building 7 at Soi Nak Niwat 48 Yaek 18, Lat Phrao; BaanFinder independently lists Uea Pracha Condotown 7 at the same soi. Hipflat's Srinagarindra address conflicts with these exact-building sources.",
            "units": 103,
            "floors": 5,
            "locationVerified": False,
            "lat": None,
            "lng": None,
            "locationSourceUrl": None,
        })
        write_array(path, symbol, rows)

    manual_path = DIST / "bangkok-manual-market-samples.js"
    manual_rows = load_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
    project_row = next((item for item in manual_rows if int(item.get("hipflatId", -1)) == PROJECT_ID), None)
    if project_row is None:
        project_row = {"hipflatId": PROJECT_ID, "name": PROJECT_NAME}
        manual_rows.append(project_row)
    sample = {
        "id": "SAM-8Z4427",
        "price": 259000,
        "area": 30.48,
        "priceSqm": round(259000 / 30.48),
        "beds": 0,
        "roomType": "STUDIO",
        "title": "SAM 銀行資產出售 · Building 7 unit 41/209 · Studio · 30.48 ㎡；SAM 頁面未列更新日",
        "url": SAM_URL,
        "sourceName": "SAM（泰國資產管理公司銀行資產出售）",
        "projectName": PROJECT_NAME,
        "matchedBy": "exact_building_7_unit_address_and_name_cross_checked_with_Hipflat_and_BaanFinder",
        "sampleType": "bank_asset_sale",
        "specialAsset": True,
        "checkedAt": date.today().isoformat(),
        "listingStatus": "availability_unconfirmed_date_unknown",
    }
    sale = project_row.setdefault("sale", {"samples": []})
    sale["samples"] = [item for item in sale.get("samples", []) if item.get("id") != sample["id"]]
    sale["samples"].append(sample)
    sale["asOf"] = date.today().isoformat()
    sale["sourceName"] = "SAM 特殊銀行資產單筆掛牌（不納入一般行情／投報）"
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

    # Bust browser caches for all changed datasets. The PropertyHub detail file
    # also received one new page from the just-completed 14-page incremental run.
    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    replacements = {
        r"bangkok-catalogue\.js\?v=[^\"']+": "bangkok-catalogue.js?v=20261018c-uea-pracha-building-7-address-correction",
        r"bangkok-propertyhub-map\.js\?v=[^\"']+": "bangkok-propertyhub-map.js?v=20261018h-uea-pracha-building-7-address-correction",
        r"bangkok-manual-market-samples\.js\?v=[^\"']+": "bangkok-manual-market-samples.js?v=20261018h-uea-pracha-building-7-special-asset",
        r"bangkok-propertyhub-details\.js\?v=[^\"']+": "bangkok-propertyhub-details.js?v=20261018d-propertyhub-incremental-details",
    }
    for pattern, replacement in replacements.items():
        html, count = re.subn(pattern, replacement, html, count=1)
        if count != 1:
            raise ValueError(f"Could not update index cache reference: {pattern}")
    index_path.write_text(html, encoding="utf-8")

    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT_NAME,
        "address": CORRECT_ADDRESS,
        "addressSource": SAM_URL,
        "identityCrossCheck": {"hipflat": HIPFLAT_URL, "baanfinder": BAANFINDER_URL},
        "addressEvidence": "SAM record 8Z4427 identifies unit 41/209 in Condominium Uea Pracha Condo Town Building 7 at Soi Nak Niwat 48 Yaek 18, Lat Phrao. BaanFinder separately lists Uea Pracha Condotown 7 at Nak Niwat 48 Yaek 18. Hipflat's 169 Srinagarindra address conflicts with both exact-building sources.",
        "saleSample": {"price": 259000, "areaSqm": 30.48, "pricePerSqm": round(259000 / 30.48), "source": SAM_URL, "specialAsset": True, "listingStatus": "SAM page displays for sale; source page does not provide an update date."},
        "rentSample": None,
        "coordinates": None,
        "coordinateStatus": "pending; no building-level map point verified yet",
        "checkedAt": date.today().isoformat(),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "address": CORRECT_ADDRESS, "specialSaleSample": sample, "coordinatesVerified": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
