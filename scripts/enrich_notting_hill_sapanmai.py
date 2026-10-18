from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PROJECT_ID = 3205
PROJECT = "NOTTING HILL Hydepark-Sapanmai"
AS_OF = "2026-10-19"
HIPFLAT = "https://www.hipflat.co.th/en/projects/notting-hill-hydeparksapanmai-mjwjbh"
DDPROPERTY = "https://www.ddproperty.com/en/project/6734-notting-hill-hyde-park-sapanmai"
COORD_SOURCE = "https://www.homenayoo.com/the-origin-phahol-sapanmai/"
GOOGLE_MAPS = "https://www.google.com/maps/place/13.888451,100.610435"


def read_array(path: Path, symbol: str) -> list[dict]:
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Could not parse {symbol} from {path.name}")
    return json.loads(match.group(1))


def write_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n", encoding="utf-8")


def main() -> None:
    coords_path = DIST / "bangkok-verified-coordinates.js"
    coords = [r for r in read_array(coords_path, "BANGKOK_VERIFIED_COORDINATES") if int(r.get("hipflatId", -1)) != PROJECT_ID]
    coords.append({
        "hipflatId": PROJECT_ID, "name": PROJECT, "lat": 13.888451, "lng": 100.610435,
        "locationVerified": True, "sourceName": "Homenayoo 專案地圖座標／Hipflat 地址交叉核對",
        "sourceUrl": COORD_SOURCE, "verificationSourceUrl": HIPFLAT,
        "verificationMethod": "Homenayoo identifies The Origin Phahol-Saphanmai as a complete redesign of Notting Hill Hyde Park-Sapanmai and publishes its map point; DDproperty confirms the exact former project name and the same Thepharak Road, Khlong Thanon address. The project is plotted at the successor development site.",
        "addressMatch": "439/1 Theppharak Rd, Khlong Thanon, Sai Mai, Bangkok 10220",
        "mapUrl": GOOGLE_MAPS,
    })
    coords.sort(key=lambda r: int(r.get("hipflatId", 0)))
    write_array(coords_path, "BANGKOK_VERIFIED_COORDINATES", coords)

    manual_path = DIST / "bangkok-manual-market-samples.js"
    manual = [r for r in read_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES") if int(r.get("hipflatId", -1)) != PROJECT_ID]
    manual.append({"hipflatId": PROJECT_ID, "name": PROJECT, "completedYear": 2019, "completedYearSourceUrl": DDPROPERTY})
    manual.sort(key=lambda r: int(r.get("hipflatId", 0)))
    write_array(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

    cross_path = DIST / "bangkok-market-crosschecks.js"
    cross = [r for r in read_array(cross_path, "BANGKOK_MARKET_CROSSCHECKS") if int(r.get("hipflatId", -1)) != PROJECT_ID]
    cross.append({
        "hipflatId": PROJECT_ID, "projectName": PROJECT, "asOf": AS_OF,
        "sourceName": "Hipflat", "projectSourceUrl": HIPFLAT,
        "sale": {"activeListingCount": 0, "sourceUrl": HIPFLAT},
        "rent": {"activeListingCount": 0, "sourceUrl": HIPFLAT},
        "availabilitySources": [
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT, "statusLabel": "目前顯示無可用房源；未納入售租或投報樣本"},
            {"sourceName": "DDproperty 專案頁", "url": DDPROPERTY, "statusLabel": "成交／租售交易資料未提供；僅用於核對完工年與地址"},
        ],
    })
    cross.sort(key=lambda r: int(r.get("hipflatId", 0)))
    write_array(cross_path, "BANGKOK_MARKET_CROSSCHECKS", cross)

    csv_path = REPORTS / "listing-availability-checks-2026-10-18.csv"
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f); fields = reader.fieldnames
            rows = [r for r in reader if not (r.get("hipflat_id") == str(PROJECT_ID) and r.get("market") in {"sale", "rent"})]
        note = "Hipflat exact-project page checked 2026-10-19 states no properties are currently available. DDproperty provides no transaction-price data for this project page. No nearby project listing was substituted; no current sale/rent sample or ROI is asserted."
        for market in ("sale", "rent"):
            rows.append({"hipflat_id": str(PROJECT_ID), "condo": PROJECT, "checked_at": AS_OF, "market": market, "status": "no_current_matching_listing", "verification_note": note, "source_1": HIPFLAT, "source_2": DDPROPERTY, "source_3": ""})
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(sorted(rows, key=lambda r: (int(r["hipflat_id"]), r["market"])))

    report = {
        "hipflatId": PROJECT_ID, "project": PROJECT, "checkedAt": AS_OF,
        "coordinates": {"status": "verified_successor_project_site", "lat": 13.888451, "lng": 100.610435, "coordinateSource": COORD_SOURCE, "googleMapsPoint": GOOGLE_MAPS, "identityCrosscheck": HIPFLAT, "method": "The Origin Phahol-Saphanmai is documented as the full redesign/successor of Notting Hill Hyde Park-Sapanmai; DDproperty confirms the former project name, 439/1 Thepharak Road, and 2019 completion."},
        "projectDetails": {"completedYear": 2019, "floors": 14, "units": 536, "detailsSource": DDPROPERTY},
        "marketAvailability": {"sale": {"status": "no_current_matching_listing", "sampleCount": 0, "source": HIPFLAT}, "rent": {"status": "no_current_matching_listing", "sampleCount": 0, "source": HIPFLAT}},
        "roi": {"status": "not_calculable", "reason": "No current exact-project sale or rental listings were available on the check date."},
    }
    (REPORTS / "notting-hill-hydepark-sapanmai-verification-2026-10-19.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(r"bangkok-verified-coordinates\.js\?v=[^\"']+", "bangkok-verified-coordinates.js?v=20261019-notting-hill-successor-site", html, count=1)
    html = re.sub(r"bangkok-manual-market-samples\.js\?v=[^\"']+", "bangkok-manual-market-samples.js?v=20261019-notting-hill-completion", html, count=1)
    html = re.sub(r"bangkok-market-crosschecks\.js\?v=[^\"']+", "bangkok-market-crosschecks.js?v=20261019-notting-hill-no-current-listings", html, count=1)
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinate": [13.888451, 100.610435], "completedYear": 2019, "currentSaleSamples": 0, "currentRentSamples": 0, "roi": "not_calculable"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
