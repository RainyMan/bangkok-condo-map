"""Verify several unresolved Bangkok Condo map pins and record listing gaps."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
CHECKED_AT = "2026-10-19"
HIPFLAT = {
    3248: "https://www.hipflat.co.th/en/projects/dusit-condominium-yyjuao",
    3343: "https://www.hipflat.co.th/en/projects/pannup-2-wyabco",
    3363: "https://www.hipflat.co.th/en/projects/nontarom-condo-park-building-b-suljbp",
    3583: "https://www.hipflat.co.th/en/projects/nontarom-condo-park-yslcxr",
    5278: "https://www.hipflat.co.th/en/projects/nontarom-talingchan-xizstv",
}
ESRI_BASE = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?"


def load_js_array(filename: str, variable: str) -> tuple[str, list[dict], str]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.fullmatch(rf"({re.escape(variable)}\s*=\s*)(\[.*\])(\s*;?\s*)", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected JavaScript array format: {filename}")
    return match.group(1), json.loads(match.group(2)), match.group(3)


def save_js_array(filename: str, prefix: str, rows: list[dict], suffix: str) -> None:
    (DIST / filename).write_text(
        prefix + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + suffix,
        encoding="utf-8",
    )


def upsert_by(rows: list[dict], key: str, value: int, record: dict) -> None:
    index = next((i for i, row in enumerate(rows) if int(row.get(key, -1)) == value), None)
    if index is None:
        rows.append(record)
    else:
        rows[index] = record


def esri_url(query: str) -> str:
    return ESRI_BASE + urlencode(
        {"SingleLine": query, "f": "json", "outFields": "*", "maxLocations": 1}
    )


def google_maps_url(lat: float, lng: float) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lng}"


# These points come from high-confidence ArcGIS World Geocoding Service POI or
# PointAddress matches against Hipflat's exact project addresses. Nontarom's
# umbrella project also has a Google Maps point embedded in its linked unit
# page; ArcGIS returns the matching project POI within approximately 80 m.
coordinate_records = [
    {
        "hipflatId": 3248,
        "name": "Dusit Condominium",
        "lat": 13.778310388,
        "lng": 100.522663339,
        "locationVerified": True,
        "sourceName": "Google Maps 點位（ArcGIS 專案 POI 核對）",
        "sourceUrl": google_maps_url(13.778310388, 100.522663339),
        "verificationSourceUrl": esri_url("Dusit Condominium Nakhon Chai Si Dusit Bangkok"),
        "corroborationSourceUrl": HIPFLAT[3248],
        "verificationMethod": "ArcGIS POI result score 97.8; Hipflat detail text identifies Soi Dusit Condo, Nakhon Chai Si Road, Dusit and the 8-floor, 114-unit property. Hipflat's header incorrectly labels it at Victory Monument in Ratchathewi; corrected the map address from its detailed project description.",
        "asOf": CHECKED_AT,
    },
    {
        "hipflatId": 3343,
        "name": "Pannup 2",
        "lat": 13.746408882433,
        "lng": 100.462267697073,
        "locationVerified": True,
        "sourceName": "Google Maps 點位（ArcGIS 門牌座標核對）",
        "sourceUrl": google_maps_url(13.746408882433, 100.462267697073),
        "verificationSourceUrl": esri_url("409/4 Soi Charan Sanitwong 25, Charan Sanitwong Rd, Bang Khun Si, Bangkok Noi, Bangkok 10700"),
        "corroborationSourceUrl": HIPFLAT[3343],
        "verificationMethod": "ArcGIS exact PointAddress result score 98.89 for Hipflat's full street address 409/4 Soi Charan Sanitwong 25; confirmed project name/address on the Hipflat project page.",
        "asOf": CHECKED_AT,
    },
    {
        "hipflatId": 3363,
        "name": "Nontarom Condo Park Building B",
        "lat": 13.763033088186,
        "lng": 100.453337365973,
        "locationVerified": True,
        "sourceName": "Google Maps 點位（ArcGIS 門牌座標核對）",
        "sourceUrl": google_maps_url(13.763033088186, 100.453337365973),
        "verificationSourceUrl": esri_url("634 Soi Kaeo Ngoen Thong 14, Kaeo Ngoen Thong Rd, Khlong Chak Phra, Taling Chan, Bangkok 10170"),
        "corroborationSourceUrl": HIPFLAT[3363],
        "verificationMethod": "ArcGIS exact PointAddress result score 100 for Hipflat's stated address 634 Soi Kaeo Ngoen Thong 14. Kept this Building B record distinct from the umbrella Nontarom Condo Park entry, whose separate Chak Phra address geocodes approximately 1.8 km away.",
        "asOf": CHECKED_AT,
    },
    {
        "hipflatId": 3583,
        "name": "Nontarom Condo Park",
        "lat": 13.7784358,
        "lng": 100.4564521,
        "locationVerified": True,
        "sourceName": "Google Maps 點位（ArcGIS 專案 POI 核對）",
        "sourceUrl": google_maps_url(13.7784358, 100.4564521),
        "verificationSourceUrl": esri_url("Nontarom Condo Park, Taling Chan, Bangkok"),
        "corroborationSourceUrl": HIPFLAT[3583],
        "verificationMethod": "ArcGIS returned the named Nontharom Condo Park POI. The Google Maps link embedded in the linked ZmyHome unit page identifies 13.7791414261,100.4562606812, approximately 80 m from this project point; Hipflat's page independently matches the name, Chak Phra address, 2010 completion, 120 units, and linked unit listings.",
        "asOf": CHECKED_AT,
    },
    {
        "hipflatId": 5278,
        "name": "Nontarom Talingchan",
        "lat": 13.778848272645,
        "lng": 100.455296216745,
        "locationVerified": True,
        "sourceName": "Google Maps 點位（ArcGIS 門牌座標核對）",
        "sourceUrl": google_maps_url(13.778848272645, 100.455296216745),
        "verificationSourceUrl": esri_url("44/16 Soi Chakphra 30, Chak Phra Rd, Taling Chan, Bangkok 10170"),
        "corroborationSourceUrl": HIPFLAT[5278],
        "verificationMethod": "ArcGIS exact PointAddress result score 96.84 for Hipflat's listed address 44/16 Soi Chakphra 30; Hipflat page confirms the Nontarom Talingchan project and five-floor completion details.",
        "asOf": CHECKED_AT,
    },
]

catalogue_prefix, catalogue, catalogue_suffix = load_js_array("bangkok-catalogue.js", "window.BANGKOK_CONDO_CATALOGUE")
coordinates_prefix, coordinates, coordinates_suffix = load_js_array("bangkok-verified-coordinates.js", "window.BANGKOK_VERIFIED_COORDINATES")
cross_prefix, crosschecks, cross_suffix = load_js_array("bangkok-market-crosschecks.js", "window.BANGKOK_MARKET_CROSSCHECKS")
manual_prefix, manual_markets, manual_suffix = load_js_array("bangkok-manual-market-samples.js", "window.BANGKOK_MANUAL_MARKET_SAMPLES")

coordinate_summary = []
for record in coordinate_records:
    upsert_by(coordinates, "hipflatId", record["hipflatId"], record)
    project = next(row for row in catalogue if int(row["id"]) == record["hipflatId"])
    project.update(
        {
            "lat": record["lat"],
            "lng": record["lng"],
            "locationVerified": True,
            "locationSourceUrl": record["sourceUrl"],
            "addressSourceUrl": record.get("corroborationSourceUrl") or record["verificationSourceUrl"],
        }
    )
    completeness = dict(project.get("dataCompleteness") or {})
    completeness["coordinates"] = True
    project["dataCompleteness"] = completeness
    coordinate_summary.append(
        {"hipflatId": record["hipflatId"], "name": record["name"], "lat": record["lat"], "lng": record["lng"], "source": record["sourceUrl"]}
    )

# Repair Hipflat's conflicting generic header for Dusit Condominium using its
# own detailed address and facts rather than preserving the incorrect district.
dusit = next(row for row in catalogue if int(row["id"]) == 3248)
dusit.update(
    {
        "address": "Soi Dusit Condominium, Nakhon Chai Si Road, Dusit, Bangkok 10300, Thailand",
        "completedYear": 1983,
        "floors": 8,
        "units": 114,
        "sourceDescription": "Hipflat 的專案詳細說明將 Dusit Condominium 定位於 Dusit 區 Nakhon Chai Si Road 的 Soi Dusit Condo，並列出 1983 年完工、8 層、114 戶。Hipflat 頁首錯誤標成 Victory Monument / Ratchathewi；地圖位置採用詳細說明地址並由 ArcGIS POI 核對。",
    }
)
sale_url = "https://www.bam.co.th/th/npa/property/141563"
sale_price = 3_564_000
sale_area = 271.5
sale_sample = {
    "id": "HBKKCU5615001",
    "price": sale_price,
    "area": sale_area,
    "priceSqm": round(sale_price / sale_area, 2),
    "beds": 3,
    "roomType": "3BR",
    "title": "Dusit Condominium · 3 房 · 271.5 ㎡ · ฿3,564,000",
    "url": sale_url,
    "sourceName": "BAM 資產管理公司直售",
    "projectName": "Dusit Condominium",
    "checkedAt": CHECKED_AT,
    "matchedBy": "listing_project_name_building_and_address_match",
    "listingStatus": "active_as_listed",
}
sale_market = {
    "count": 1,
    "observedCount": 1,
    "countKind": "manual_verified_listing",
    "average": sale_price,
    "minimum": sale_price,
    "minimumArea": sale_area,
    "minimumSampleUpdated": CHECKED_AT,
    "averageSqm": round(sale_price / sale_area),
    "minimumSqm": round(sale_price / sale_area, 2),
    "minimumSqmSampleUpdated": CHECKED_AT,
    "asOf": CHECKED_AT,
    "sourceName": "BAM 資產管理公司直售掛牌",
    "source": sale_url,
    "minimumSourceUrl": sale_url,
    "minimumSqmSourceUrl": sale_url,
    "byBedroom": {
        "3": {
            "count": 1,
            "minimum": sale_price,
            "area": sale_area,
            "minimumArea": sale_area,
            "minimumSqm": round(sale_price / sale_area, 2),
            "averageSqm": round(sale_price / sale_area),
            "sourceUrl": sale_url,
            "minimumSourceUrl": sale_url,
            "minimumSqmSourceUrl": sale_url,
        }
    },
    "samples": [sale_sample],
}
manual_index = next((i for i, row in enumerate(manual_markets) if int(row.get("hipflatId", -1)) == 3248), None)
if manual_index is None:
    manual_markets.append({"hipflatId": 3248, "name": "Dusit Condominium", "asOf": CHECKED_AT, "sale": sale_market, "rent": {}})
else:
    manual_markets[manual_index] = {**manual_markets[manual_index], "asOf": CHECKED_AT, "sale": sale_market}
completeness = dict(dusit.get("dataCompleteness") or {})
completeness.update({"saleSample": True, "rentSample": False, "yield": False})
dusit["dataCompleteness"] = completeness
dusit["marketDataStatus"] = "verified_sale_sample_rent_pending"
upsert_by(
    crosschecks,
    "hipflatId",
    3248,
    {
        "hipflatId": 3248,
        "projectName": "Dusit Condominium",
        "asOf": CHECKED_AT,
        "sourceName": "Hipflat 專案頁核對",
        "projectSourceUrl": HIPFLAT[3248],
        "sale": {"activeListingCount": 1, "sourceUrl": sale_url, "note": "BAM 資產管理公司現行 NPA 直售：3 房、271.5㎡、要價 ฿3,564,000。"},
        "rent": {"activeListingCount": 0, "sourceUrl": HIPFLAT[3248], "note": "Hipflat 專案頁顯示目前沒有可用物件；未核實到本案現行出租單筆掛牌。"},
        "availabilitySources": [
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT[3248], "statusLabel": "目前頁面顯示沒有可用物件；Hipflat 以外核對到 BAM 現行出售單筆。"},
            {"sourceName": "BAM 資產管理公司直售", "url": sale_url, "statusLabel": "現行 NPA 3 房掛牌：฿3,564,000／271.5㎡；頁面列明 Dusit Condominium A 棟、8 樓。"},
        ],
        "yieldStatus": "not_calculated",
        "yieldNote": "已核實一筆本案 3 房出售掛牌，但尚無可核實的現行出租樣本，無法計算投報率。",
    },
)

for project_id, project_name, hipflat_url, note in [
    (3343, "Pannup 2", HIPFLAT[3343], "Hipflat 專案頁顯示目前沒有可用物件；未取得可核實的本案出售或出租單筆掛牌。"),
    (3363, "Nontarom Condo Park Building B", HIPFLAT[3363], "Hipflat 的 Building B 專案頁顯示目前沒有可用物件。Nontarom Condo Park umbrella entry 是不同地址的獨立記錄，未把其售租掛牌移植至本 Building B。"),
    (5278, "Nontarom Talingchan", HIPFLAT[5278], "Hipflat 專案頁顯示目前沒有可用物件；未取得可核實的本案出售或出租單筆掛牌。"),
]:
    upsert_by(
        crosschecks,
        "hipflatId",
        project_id,
        {
            "hipflatId": project_id,
            "projectName": project_name,
            "asOf": CHECKED_AT,
            "sourceName": "Hipflat 專案頁核對",
            "projectSourceUrl": hipflat_url,
            "sale": {"activeListingCount": 0, "sourceUrl": hipflat_url, "note": note},
            "rent": {"activeListingCount": 0, "sourceUrl": hipflat_url, "note": note},
            "availabilitySources": [{"sourceName": "Hipflat 專案頁", "url": hipflat_url, "statusLabel": "目前頁面顯示沒有可用物件；沒有將附近或相似名稱專案的房源併入。"}],
            "yieldStatus": "not_calculated",
            "yieldNote": "沒有本案可核實的現行出售與出租單筆樣本，不能建立購入價與租金基準，因此未計算投報率。",
        },
    )

save_js_array("bangkok-catalogue.js", catalogue_prefix, catalogue, catalogue_suffix)
save_js_array("bangkok-verified-coordinates.js", coordinates_prefix, coordinates, coordinates_suffix)
save_js_array("bangkok-market-crosschecks.js", cross_prefix, crosschecks, cross_suffix)
save_js_array("bangkok-manual-market-samples.js", manual_prefix, manual_markets, manual_suffix)

report = {
    "checkedAt": CHECKED_AT,
    "work": "Verified five unresolved coordinates, corrected one conflicting address, and recorded project-specific no-current-listing evidence without inventing prices or ROI.",
    "coordinates": coordinate_summary,
    "market": {
        "currentDirectSaleSamplesAdded": 1,
        "currentDirectRentSamplesAdded": 0,
        "noHipflatInventoryProjectPages": [3248, 3343, 3363, 5278],
        "saleSampleAdded": {"projectId": 3248, "priceTHB": sale_price, "areaSqm": sale_area, "bedrooms": 3, "pricePerSqm": round(sale_price / sale_area, 2), "source": sale_url},
        "notCalculatedYield": [3248, 3343, 3363, 5278],
        "existingCurrentSamplesPreserved": {
            "projectId": 3583,
            "saleUrl": "https://www.hipflat.co.th/ads/t393ll8a81a2aaca7t7nahn43u04u42e",
            "rentUrl": "https://www.hipflat.co.th/ads/99484t1u814a0tu7h7897ne83u0h14a3",
            "note": "The umbrella Nontarom Condo Park listing samples remain attached only to project 3583; no samples were copied to the separate Building B record 3363 or Nontarom Talingchan 5278.",
        },
    },
    "limitations": [
        "Tamarind Tree Residence (3171) has only a street-level geocode match; it was left unmapped pending a project-specific point.",
        "Tropical Garden (3315) resolves only to Soi Phrom Chit rather than the exact condominium footprint; it was left unmapped pending a project-specific point.",
    ],
    "sources": [
        {"hipflatId": row["hipflatId"], "name": row["name"], "mapPoint": row["sourceUrl"], "geocoder": row["verificationSourceUrl"], "project": row.get("corroborationSourceUrl")}
        for row in coordinate_records
    ],
}
REPORTS.mkdir(exist_ok=True)
(REPORTS / "talingchan-dusit-coordinate-enrichment-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

# Invalidate the browser's catalog and evidence bundles without touching other
# caches; these files are consumed as static JavaScript arrays.
index_path = DIST / "index.html"
index = index_path.read_text(encoding="utf-8")
for old, new in [
    ("bangkok-catalogue.js?v=20261019-ava-garden-address-completion", "bangkok-catalogue.js?v=20261019-talingchan-dusit-coordinate-batch"),
    ("bangkok-verified-coordinates.js?v=20261019-ava-garden-thinkofliving-point", "bangkok-verified-coordinates.js?v=20261019-talingchan-dusit-coordinate-batch"),
    ("bangkok-market-crosschecks.js?v=20261019-ava-garden-market-audit", "bangkok-market-crosschecks.js?v=20261019-talingchan-dusit-coordinate-batch"),
]:
    if old in index:
        index = index.replace(old, new)
    elif new not in index:
        raise RuntimeError(f"Expected cache tag missing: {old}")
index_path.write_text(index, encoding="utf-8")

print(json.dumps({"coordinatesVerified": len(coordinate_records), "currentDirectSaleSamplesAdded": 1, "currentDirectRentSamplesAdded": 0, "marketCrosschecksAdded": 4, "report": "reports/talingchan-dusit-coordinate-enrichment-2026-10-19.json"}, ensure_ascii=False))
