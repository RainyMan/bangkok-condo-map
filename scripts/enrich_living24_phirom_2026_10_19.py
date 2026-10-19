import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rent_samples = {
    4423: {
        "name": "Living @ 24", "price": 65000, "area": 90, "beds": 2,
        "updated": "2026-09-25",
        "url": "https://www.ddproperty.com/property/living-24-%E0%B8%A5%E0%B8%B4%E0%B8%9F%E0%B8%A7%E0%B8%B4%E0%B9%88%E0%B8%87-%E0%B9%81%E0%B8%AD%E0%B8%97-%E0%B8%97%E0%B9%80%E0%B8%A7%E0%B8%99%E0%B8%95%E0%B8%B5%E0%B9%89%E0%B9%82%E0%B8%9F%E0%B8%A3%E0%B9%8C-%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E-%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2-11408941",
        "project_url": "https://www.ddproperty.com/en/project/7572-living-24",
        "rent_url": "https://www.ddproperty.com/en/condo-for-rent/at-living-24-7572",
        "sale_url": "https://www.ddproperty.com/en/condo-for-sale/at-living-24-7572",
        "propertyhub_url": "https://propertyhub.in.th/en/projects/living-24---14524",
        "project_source": "https://www.hipflat.co.th/en/projects/living-at-24-dbjaxq",
        "active_rent_count": 11,
    },
    4445: {
        "name": "Phirom Garden Residence", "price": 150000, "area": 280, "beds": 3,
        "updated": "2026-09-25",
        "url": "https://www.ddproperty.com/en/property/phirom-garden-residence-bangkok-for-rent-11372336",
        "project_url": "https://www.ddproperty.com/en/project/6788-phirom-garden-residence",
        "rent_url": "https://www.ddproperty.com/en/condo-for-rent/at-phirom-garden-residence-6788",
        "sale_url": "https://www.ddproperty.com/en/condo-for-sale/at-phirom-garden-residence-6788",
        "propertyhub_url": "https://propertyhub.in.th/en/projects/phirom-garden-residence",
        "project_source": "https://www.hipflat.co.th/en/projects/phirom-garden-residence-uuvcvx",
        "active_rent_count": 7,
    },
}

def load_window(name):
    path = ROOT / "dist" / name
    prefix, payload = path.read_text(encoding="utf-8").split("=", 1)
    return path, prefix, json.loads(payload.strip().rstrip(";"))

manual_path, manual_prefix, manual = load_window("bangkok-manual-market-samples.js")
manual_by_id = {row["hipflatId"]: row for row in manual}
cross_path, cross_prefix, crosschecks = load_window("bangkok-market-crosschecks.js")
cross_by_id = {row["hipflatId"]: row for row in crosschecks}
evidence = {"asOf": "2026-10-19", "projects": [], "method": "Only direct project-matched listings refreshed within 30 days are used as current rental samples. Sale counts are recorded as zero only where both DDproperty and PropertyHub project sale pages show no units."}

for hipflat_id, row in rent_samples.items():
    rate = row["price"] / row["area"]
    source = {
        "id": row["url"].rsplit("-", 1)[-1], "price": row["price"], "area": row["area"],
        "priceSqm": round(rate, 2), "beds": row["beds"], "roomType": f'{row["beds"]}BR',
        "title": f'{row["name"]}，{row["beds"]}房，{row["area"]}㎡，฿{row["price"]:,}/月',
        "url": row["url"], "sourceName": "DDproperty", "projectName": row["name"],
        "updated": row["updated"], "checkedAt": "2026-10-19",
        "matchedBy": "exact_project_name_and_address",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }
    market = {
        "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
        "average": row["price"], "minimum": row["price"], "minimumArea": row["area"],
        "minimumSampleUpdated": row["updated"], "averageSqm": round(rate, 2),
        "minimumSqm": round(rate, 2), "minimumSqmSampleUpdated": row["updated"],
        "asOf": "2026-10-19", "sourceName": "DDproperty 個別房源",
        "source": row["rent_url"], "minimumSourceUrl": row["url"],
        "minimumSqmSourceUrl": row["url"], "samples": [source],
        "byBedroom": {str(row["beds"]): {
            "count": 1, "minimum": row["price"], "area": row["area"],
            "priceSqm": round(rate, 2), "minimumSqm": round(rate, 2),
            "averageSqm": round(rate, 2), "sourceUrl": row["url"],
            "minimumSqmSourceUrl": row["url"],
        }},
    }
    manual_by_id[hipflat_id] = {
        "hipflatId": hipflat_id, "name": row["name"], "rent": market, "replaceRent": True,
    }
    cross_by_id[hipflat_id] = {
        "hipflatId": hipflat_id, "projectName": row["name"], "asOf": "2026-10-19",
        "sourceName": "DDproperty / PropertyHub 專案與個別房源核對",
        "projectSourceUrl": row["project_source"],
        "sale": {
            "activeListingCount": 0, "sourceUrl": row["sale_url"],
            "note": "DDproperty 與 PropertyHub 專案出售頁目前均列 0 筆；未找到可核實的現行出售單筆掛牌，因此不填售價、不估投報。",
        },
        "rent": {
            "activeListingCount": row["active_rent_count"], "sourceUrl": row["rent_url"],
            "note": f'DDproperty 專案出租頁列有 {row["active_rent_count"]} 筆；另以 30 日內更新的個別房源建立租金樣本。',
        },
        "availabilitySources": [
            {"sourceName": "DDproperty 專案出售頁", "url": row["sale_url"], "statusLabel": "目前顯示 0 筆出售房源。"},
            {"sourceName": "PropertyHub 專案頁", "url": row["propertyhub_url"], "statusLabel": "目前顯示 0 筆出售房源；租金行情以個別房源核對。"},
            {"sourceName": "DDproperty 專案出租頁", "url": row["rent_url"], "statusLabel": f'DDproperty 專案頁顯示 {row["active_rent_count"]} 筆出租房源。'},
            {"sourceName": "DDproperty 個別出租房源", "url": row["url"], "statusLabel": f'{row["beds"]} 房，฿{row["price"]:,}/月，{row["area"]}㎡；刊登更新 {row["updated"]}，目前可租狀態待刊登者確認。'},
        ],
        "yieldStatus": "not_calculated",
        "yieldNote": "目前未找到本案可核實的出售單筆掛牌，缺少購入價基準，不計投報率。",
    }
    evidence["projects"].append({
        "hipflatId": hipflat_id, "name": row["name"],
        "coordinateSource": row["propertyhub_url"],
        "saleStatus": "No active project-matched listings on DDproperty and PropertyHub project sale pages.",
        "saleSources": [row["sale_url"], row["propertyhub_url"]],
        "rent": {
            "priceTHBPerMonth": row["price"], "areaSqm": row["area"],
            "bedrooms": row["beds"], "rateTHBPerSqmPerMonth": round(rate, 2),
            "updated": row["updated"], "individualListing": row["url"],
        },
        "projectRentSource": row["rent_url"],
    })

manual = sorted(manual_by_id.values(), key=lambda row: row["hipflatId"])
crosschecks = sorted(cross_by_id.values(), key=lambda row: row["hipflatId"])
manual_path.write_text(manual_prefix + "=" + json.dumps(manual, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
cross_path.write_text(cross_prefix + "=" + json.dumps(crosschecks, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
(ROOT / "reports" / "living24-phirom-current-market-2026-10-19.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

