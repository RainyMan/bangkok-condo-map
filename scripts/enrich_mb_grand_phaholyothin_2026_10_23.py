"""Verify MB Grand Phaholyothin's duplicate Hipflat record and linked rent evidence."""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
AS_OF = date.today().isoformat()
PROJECT_ID = 3516
PROPERTYHUB_PROJECT_ID = "894"
PROJECT_URL = "https://propertyhub.in.th/en/projects/mb-grand"
RENT_PROJECT_URL = "https://propertyhub.in.th/en/condo-for-rent/project-mb-grand"
LISTING_URL = "https://propertyhub.in.th/en/listings/condo-in-high-potential-central-city-location-mb-grand-phaholyothin-near-bts-sena-ruam---6326328"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/mb-grand-phaholyothin-iquejg"
HOME_URL = "https://www.home.co.th/condo/mb-grand-phaholyothin-2934"


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Cannot read {symbol} from {filename}")
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def by_int_id(rows: list[dict], key: str) -> dict[int, dict]:
    return {int(row[key]): row for row in rows if row.get(key) is not None}


def main() -> None:
    coordinates = by_int_id(load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"), "hipflatId")
    details = {str(row.get("propertyHubProjectId")): row for row in load_array("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")}
    canonical = details[PROPERTYHUB_PROJECT_ID]
    lat, lng = float(canonical["lat"]), float(canonical["lng"])
    coordinate = {
        "hipflatId": PROJECT_ID,
        "name": "MB GRAND Phaholyothin",
        "lat": lat,
        "lng": lng,
        "locationVerified": True,
        "sourceName": "PropertyHub 精確專案頁地圖座標；Home.co.th 與 Hipflat 專案描述交叉核對",
        "sourceUrl": PROJECT_URL,
        "verificationSourceUrl": HIPFLAT_URL,
        "corroborationSourceUrl": HOME_URL,
        "verificationMethod": "PropertyHub exact MB Grand project map point and project ID; 151 units/19 floors/2010 and Phaholyothin address cross-checked against Hipflat description and Home.co.th. Hipflat top-level district address is inconsistent and was not used for geocoding.",
        "asOf": AS_OF,
    }
    coordinates[PROJECT_ID] = coordinate
    save_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", [coordinates[key] for key in sorted(coordinates)])

    catalogue = by_int_id(load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE"), "id")
    project = catalogue[PROJECT_ID]
    project.update({
        "lat": lat, "lng": lng, "locationVerified": True,
        "address": "1345 Phahon Yothin Road, Samsen Nai, Phaya Thai, Bangkok 10400, Thailand",
        "locationSourceUrl": PROJECT_URL, "locationSourceName": "PropertyHub 精確專案頁地圖",
        "completedYear": 2010, "units": 151, "floors": 19,
        "fee": {"rate": 30, "status": "published_indicative", "note": "PropertyHub 專案頁公布的管理費數值，簽約前請向管委會確認。", "source": PROJECT_URL},
        "propertyHubProjectId": PROPERTYHUB_PROJECT_ID,
        "propertyHubProjectUrl": PROJECT_URL,
        "dataCompleteness": {**project.get("dataCompleteness", {}), "coordinates": True},
        "locationVerificationNote": "Hipflat 頂層地址誤列 Ratchathewi；Hipflat 專案描述、PropertyHub 及 Home.co.th 均指向 Phaholyothin/Samsen Nai, Phaya Thai。",
    })
    save_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE", [catalogue[key] for key in sorted(catalogue)])

    ph_map = by_int_id(load_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS"), "id")
    ph_row = ph_map[PROJECT_ID]
    ph_row.update({
        "lat": lat, "lng": lng, "locationVerified": True,
        "completedYear": 2010, "units": 151, "floors": 19,
        "address": "1345 Phahon Yothin Road, Samsen Nai, Phaya Thai, Bangkok 10400, Thailand",
        "locationSourceUrl": PROJECT_URL, "locationSourceName": "PropertyHub 精確專案頁地圖",
        "propertyHubProjectId": PROPERTYHUB_PROJECT_ID,
        "propertyHubProjectUrl": PROJECT_URL,
        "fee": {"rate": 30, "status": "published_indicative", "note": "PropertyHub 專案頁公布的管理費數值，簽約前請向管委會確認。", "source": PROJECT_URL},
        "locationVerificationNote": "同一 PropertyHub 專案另以 MB Grand / MB GRAND Phaholyothin 列名；Hipflat 專案描述與 Home.co.th 的名稱、Phaholyothin 地址、151 戶、19 層、2010 年資料一致。",
    })
    save_array("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", [ph_map[key] for key in sorted(ph_map)])

    rent_sample = {
        "id": "6326328", "kind": "rent", "price": 29000, "area": 66,
        "priceSqm": round(29000 / 66, 2), "beds": 2, "roomType": "TWO_BED_ROOM",
        "title": "MB Grand Phaholyothin，2 房，66 ㎡，฿29,000/月",
        "url": LISTING_URL, "sourceName": "PropertyHub 單筆出租掛牌",
        "projectName": "MB Grand / MB GRAND Phaholyothin", "updated": None,
        "checkedAt": AS_OF, "projectPageRefreshedAt": AS_OF,
        "matchedBy": "exact_propertyhub_project_alias_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_date_unknown",
        "statusNote": "PropertyHub 專案出租頁仍列此單筆房源；個別頁核對 2 房、66㎡、฿29,000/月，但更新日期未提供，現況待刊登者確認。",
    }
    rent = {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": 29000, "minimum": 29000, "minimumArea": 66,
        "averageSqm": round(29000 / 66), "minimumSqm": round(29000 / 66),
        "asOf": AS_OF, "sourceName": "PropertyHub 專案出租頁＋單筆掛牌",
        "source": RENT_PROJECT_URL, "minimumSourceUrl": LISTING_URL,
        "minimumSqmSourceUrl": LISTING_URL,
        "samples": [rent_sample],
        "byBedroom": {"2": {
            "count": 1, "minimum": 29000, "area": 66, "minimumArea": 66,
            "priceSqm": round(29000 / 66), "minimumSqm": round(29000 / 66),
            "sourceUrl": LISTING_URL, "minimumSourceUrl": LISTING_URL,
            "minimumSqmSourceUrl": LISTING_URL,
        }},
        "note": rent_sample["statusNote"],
    }
    manual = by_int_id(load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"), "hipflatId")
    manual[PROJECT_ID] = {"hipflatId": PROJECT_ID, "name": "MB GRAND Phaholyothin", "asOf": AS_OF, "rent": rent, "replaceRent": True}
    save_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", [manual[key] for key in sorted(manual)])

    REPORTS.mkdir(exist_ok=True)
    report = {
        "checkedAt": AS_OF,
        "hipflatId": PROJECT_ID,
        "project": "MB GRAND Phaholyothin",
        "identity": {
            "propertyHubProjectId": PROPERTYHUB_PROJECT_ID,
            "coordinates": [lat, lng],
            "address": project["address"],
            "completionYear": 2010, "units": 151, "floors": 19,
            "commonFee": {"rate": 30, "unit": "THB/sqm/month", "status": "published_indicative"},
            "sources": [PROJECT_URL, HIPFLAT_URL, HOME_URL],
            "note": project["locationVerificationNote"],
        },
        "sale": {"status": "no_current_project_listing_found", "source": PROJECT_URL,
                 "hipflatProjectPage": HIPFLAT_URL,
                 "note": "PropertyHub 專案頁列 0 筆出售，Hipflat 專案頁亦顯示目前無房源；不填售價或投報率。"},
        "rent": {"price": 29000, "area": 66, "beds": 2, "source": LISTING_URL,
                 "projectPage": RENT_PROJECT_URL, "availability": "unconfirmed_date_unknown",
                 "note": rent_sample["statusNote"]},
        "yield": {"status": "not_calculated", "reason": "沒有本案可核實出售樣本，沒有購入總價基準。"},
    }
    (REPORTS / "mb-grand-phaholyothin-verification-2026-10-23.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (REPORTS / f"bangkok-coverage-{AS_OF}.csv").open(encoding="utf-8-sig", newline="") as handle:
        coverage = next(row for row in csv.DictReader(handle) if row["hipflat_id"] == str(PROJECT_ID))
    print(json.dumps({"hipflatId": PROJECT_ID, "name": project["name"], "coordinate": [lat, lng],
                      "previousCoverage": coverage, "rentSample": rent_sample, "yield": "not_calculated"}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
