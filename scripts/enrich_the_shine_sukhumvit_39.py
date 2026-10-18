"""Verify The Shine Sukhumvit 39's map point and listing availability."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3172
PROJECT = "The shine sukhumvit 39"
AS_OF = "2026-10-18"
LAT, LNG = 13.7377054, 100.5743707
HIPFLAT = "https://www.hipflat.co.th/en/projects/the-shine-sukhumvit-39-aucpzr"
GOOGLE_MAPS = "https://www.google.com/maps/place/The+Shine/data=!4m7!3m6!1s0x30e29eff599772a9:0x78c8d032011e0dd3!8m2!3d13.7377054!4d100.5743707"
NESTOPA = "https://nestopa.com/th-en/project/%E0%B9%80%E0%B8%94%E0%B8%AD%E0%B8%B0%E0%B9%84%E0%B8%8A%E0%B8%99-%E0%B8%AA%E0%B8%82%E0%B8%A1%E0%B8%A7%E0%B8%97-39-3011"
YOSHIDA = "https://yoshida.co.th/the-shine/"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Unexpected asset format: {path.name}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict], compact: bool = True) -> None:
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":") if compact else None, indent=None if compact else 2)
    path.write_text(f"window.{symbol} = {payload};\n", encoding="utf-8")


def update_coordinates() -> None:
    path = DIST / "bangkok-propertyhub-map.js"
    rows = read_array(path, "BANGKOK_PROPERTYHUB_PROJECTS")
    row = next(row for row in rows if int(row["id"]) == PROJECT_ID)
    row.update({
        "lat": LAT,
        "lng": LNG,
        "address": "12 Phrom Si 2 Alley, Sukhumvit 39, Khlong Tan Nuea, Watthana, Bangkok 10110, Thailand",
        "locationVerified": True,
        "locationSourceUrl": GOOGLE_MAPS,
        "locationSourceName": "Google Maps 同址 The Shine 點位",
        "locationVerificationSourceUrl": YOSHIDA,
        "locationVerificationMethod": "Google Maps place 'The Shine' is pinned at 12 Phrom Si 2 Alley (13.7377054, 100.5743707); Yoshida's The Shine Sukhumvit 39 property profile gives the matching 12 Sukhumvit Soi 39 (Promsri 2) address; Hipflat identifies this project as The shine sukhumvit 39 at 39 Boutique Suites&Spa, Soi Sukhumvit 49/13. Identity and location cross-checked across the sources.",
        "asOf": AS_OF,
    })
    write_array(path, "BANGKOK_PROPERTYHUB_PROJECTS", rows)

    path = DIST / "bangkok-verified-coordinates.js"
    rows = [row for row in read_array(path, "BANGKOK_VERIFIED_COORDINATES") if int(row.get("hipflatId", -1)) != PROJECT_ID]
    rows.append({
        "hipflatId": PROJECT_ID,
        "name": PROJECT,
        "lat": LAT,
        "lng": LNG,
        "locationVerified": True,
        "sourceName": "Google Maps 同址 The Shine 點位",
        "sourceUrl": GOOGLE_MAPS,
        "verificationSourceUrl": YOSHIDA,
        "projectSourceUrl": HIPFLAT,
        "verificationMethod": "Google Maps exact-name place at 12 Phrom Si 2 Alley, corroborated by Yoshida property profile for The Shine Sukhumvit 39 at 12 Sukhumvit Soi 39 (Promsri 2) and Hipflat project identity/address.",
        "asOf": AS_OF,
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_VERIFIED_COORDINATES", rows)


def update_market_status() -> None:
    path = DIST / "bangkok-market-crosschecks.js"
    rows = [row for row in read_array(path, "BANGKOK_MARKET_CROSSCHECKS") if int(row.get("hipflatId", -1)) != PROJECT_ID]
    rows.append({
        "hipflatId": PROJECT_ID,
        "projectName": PROJECT,
        "asOf": AS_OF,
        "sourceName": "Hipflat",
        "projectSourceUrl": HIPFLAT,
        "sale": {"activeListingCount": 0, "sourceUrl": HIPFLAT},
        "rent": {"activeListingCount": 0, "sourceUrl": HIPFLAT},
        "availabilitySources": [
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "目前無出售或出租房源"},
            {"sourceName": "Nestopa 專案頁", "url": NESTOPA, "statusLabel": "專案頁顯示出售 0 筆、出租 0 筆"},
            {"sourceName": "Yoshida 房型租金表", "url": YOSHIDA, "statusLabel": "列出 1–2 房租金區間，未列現行單筆空房，不作掛牌樣本"},
        ],
    })
    rows.sort(key=lambda row: int(row.get("hipflatId", 0)))
    write_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows, compact=False)

    path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        existing = [row for row in reader if not (row["hipflat_id"] == str(PROJECT_ID) and row["market"] in {"sale", "rent"})]
    note = "Hipflat exact-project page states no properties are currently available; Nestopa exact-name project page reports 0 for sale and 0 for rent. Yoshida's project profile provides room-type rent ranges but no current unit listing, so those ranges are not counted as a sample or used in ROI."
    for market in ("sale", "rent"):
        existing.append({
            "hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF,
            "market": market, "status": "no_current_matching_listing",
            "verification_note": note,
            "source_1": HIPFLAT, "source_2": NESTOPA, "source_3": YOSHIDA,
        })
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(existing, key=lambda row: (int(row["hipflat_id"]), row["market"])))


def update_cache_keys() -> None:
    path = DIST / "index.html"
    html = path.read_text(encoding="utf-8")
    keys = {
        r"bangkok-propertyhub-map\.js\?v=[^\"']+": "bangkok-propertyhub-map.js?v=20261018s-the-shine-verified-google-pin",
        r"bangkok-verified-coordinates\.js\?v=[^\"']+": "bangkok-verified-coordinates.js?v=20261018v-the-shine-verified-google-pin",
        r"bangkok-market-crosschecks\.js\?v=[^\"']+": "bangkok-market-crosschecks.js?v=20261018u-the-shine-availability",
        r"bangkok-walk-routes\.js\?v=[^\"']+": "bangkok-walk-routes.js?v=20261018v-the-shine-walking-route",
    }
    for pattern, replacement in keys.items():
        html = re.sub(pattern, replacement, html, count=1)
    path.write_text(html, encoding="utf-8")


def write_report() -> None:
    report = {
        "hipflatId": PROJECT_ID,
        "project": PROJECT,
        "checkedAt": AS_OF,
        "location": {
            "latitude": LAT,
            "longitude": LNG,
            "verified": True,
            "coordinateSource": GOOGLE_MAPS,
            "identityCrosschecks": [YOSHIDA, HIPFLAT],
            "method": "Google Maps identifies The Shine at 12 Phrom Si 2 Alley; Yoshida names The Shine Sukhumvit 39 at 12 Sukhumvit Soi 39 (Promsri 2); Hipflat links The shine sukhumvit 39 to 39 Boutique Suites&Spa, Soi Sukhumvit 49/13.",
        },
        "marketAvailability": {
            "sale": {"status": "no_current_matching_listing", "sampleCount": 0, "sources": [HIPFLAT, NESTOPA]},
            "rent": {"status": "no_current_matching_listing", "sampleCount": 0, "sources": [HIPFLAT, NESTOPA]},
        },
        "excludedPriceReference": {"url": YOSHIDA, "detail": "The source lists room-type monthly rent ranges, not currently available unit-level listings; excluded from samples and yield."},
        "roi": {"status": "not_calculable", "reason": "No current exact-project unit listings for sale or rent."},
        "projectFacts": {"note": "Completion year and floor count omitted because sources disagree (2016/2017 and 7/8/9 floors)."},
    }
    (REPORTS / "the-shine-sukhumvit-39-enrichment-2026-10-18.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    update_coordinates()
    update_market_status()
    update_cache_keys()
    write_report()
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinatesVerified": True, "sale": "no_current_matching_listing", "rent": "no_current_matching_listing", "roi": "not_calculable"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
