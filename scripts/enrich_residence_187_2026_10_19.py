"""Verify the Residence 187 location and refresh its exact-project sale/rent samples."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "residence-187-location-market-2026-10-19.json"
PROJECT_ID = 3515
NAME = "Residence 187 By Ariva"
HIPFLAT = "https://www.hipflat.co.th/en/projects/residence-187-by-ariva-prlqmu"
PROPERTYHUB = "https://propertyhub.in.th/en/projects/dazzle-sukhumvit-7"
PROPERTYHUB_FEE = "https://propertyhub.in.th/ขายคอนโด/โครงการ-dazzle-sukhumvit-7"
DD_PROJECT = "https://www.ddproperty.com/en/project/6131-residence-187"
OSM = "https://www.openstreetmap.org/way/1457578466"
SALE_URL = "https://www.ddproperty.com/en/property/residence-187-bangkok-for-sale-500030491"
RENT_52_URL = "https://www.ddproperty.com/en/property/residence-187-bangkok-for-rent-500544595"
RENT_51_URL = "https://www.ddproperty.com/en/property/residence-187-bangkok-for-rent-500583076"
AS_OF = "2026-10-19"


def load_array(filename: str, symbol: str) -> tuple[Path, str, list[dict]]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);\s*", text, re.S)
    if not match:
        raise RuntimeError(f"Unexpected array format in {filename}")
    return path, text[:match.start(1)], json.loads(match.group(1))


def save_array(path: Path, prefix: str, rows: list[dict], *, pretty: bool = False) -> None:
    suffix = json.dumps(rows, ensure_ascii=False, indent=2) if pretty else json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(prefix + suffix + ";\n", encoding="utf-8", newline="\n")


def sample(sample_id: str, kind: str, price: int, area: float, beds: int, title: str, url: str, updated: str) -> dict:
    return {
        "id": sample_id, "kind": kind, "price": price, "area": area,
        "priceSqm": round(price / area, 2), "beds": beds, "roomType": f"{beds}BR",
        "title": title, "url": url, "sourceName": "DDproperty",
        "projectName": NAME, "updated": updated, "checkedAt": AS_OF,
        "matchedBy": "exact_project_name_address_and_direct_listing_page",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }


catalogue_path, _, catalogue = load_array("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
project = next(row for row in catalogue if int(row["id"]) == PROJECT_ID)
if project.get("name") != NAME or project.get("hipflatProjectUrl") != HIPFLAT:
    raise RuntimeError("Hipflat project identity does not match the reviewed Residence 187 page")

sale_sample = sample(
    "500030491", "sale", 23_990_000, 64, 1,
    "Residence 187，1 房，64㎡，฿23,990,000",
    SALE_URL, "2026-10-01",
)
rent_samples = [
    sample("500544595", "rent", 120_000, 52, 1,
           "Residence 187，1 房，52㎡，฿120,000/月",
           RENT_52_URL, "2026-09-27"),
    sample("500583076", "rent", 120_000, 51, 1,
           "Residence 187，1 房，51㎡，฿120,000/月",
           RENT_51_URL, "2026-09-24"),
]
low_rent_rate = min(row["priceSqm"] for row in rent_samples)
low_rent = next(row for row in rent_samples if row["priceSqm"] == low_rent_rate)
sale_market = {
    "count": 1, "observedCount": 1, "countKind": "manual_verified_listing",
    "average": 23_990_000, "minimum": 23_990_000, "minimumArea": 64,
    "minimumSampleUpdated": "2026-10-01", "averageSqm": sale_sample["priceSqm"],
    "minimumSqm": sale_sample["priceSqm"], "minimumSqmSampleUpdated": "2026-10-01",
    "asOf": AS_OF, "sourceName": "DDproperty 個別房源",
    "source": DD_PROJECT, "minimumSourceUrl": SALE_URL,
    "minimumSqmSourceUrl": SALE_URL, "samples": [sale_sample],
    "byBedroom": {"1": {
        "count": 1, "minimum": 23_990_000, "area": 64,
        "minimumArea": 64, "priceSqm": sale_sample["priceSqm"],
        "minimumSqm": sale_sample["priceSqm"], "averageSqm": sale_sample["priceSqm"],
        "sourceUrl": SALE_URL, "minimumSourceUrl": SALE_URL,
        "minimumSqmSourceUrl": SALE_URL,
    }},
}
rent_market = {
    "count": 2, "observedCount": 2, "countKind": "manual_verified_listings",
    "average": 120_000, "minimum": 120_000, "minimumArea": low_rent["area"],
    "minimumSampleUpdated": low_rent["updated"],
    "averageSqm": round(sum(row["priceSqm"] for row in rent_samples) / len(rent_samples), 2),
    "minimumSqm": low_rent_rate, "minimumSqmSampleUpdated": low_rent["updated"],
    "asOf": AS_OF, "sourceName": "DDproperty 個別房源",
    "source": DD_PROJECT, "minimumSourceUrl": RENT_52_URL,
    "minimumSqmSourceUrl": low_rent["url"], "samples": rent_samples,
    "byBedroom": {"1": {
        "count": 2, "minimum": 120_000, "area": low_rent["area"],
        "minimumArea": low_rent["area"], "priceSqm": low_rent_rate,
        "minimumSqm": low_rent_rate,
        "averageSqm": round(sum(row["priceSqm"] for row in rent_samples) / len(rent_samples), 2),
        "sourceUrl": low_rent["url"], "minimumSourceUrl": RENT_52_URL,
        "minimumSqmSourceUrl": low_rent["url"],
    }},
}

coordinates_path, coordinates_prefix, coordinates = load_array("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
coordinate_rows = {int(row["hipflatId"]): row for row in coordinates}
coordinate_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": NAME,
    "lat": 13.7433990, "lng": 100.5555585, "locationVerified": True,
    "sourceName": "OpenStreetMap 建物點位（Dazzle，18 Sukhumvit 7）",
    "sourceUrl": OSM, "verificationSourceUrl": HIPFLAT,
    "corroborationSourceUrl": PROPERTYHUB,
    "verificationMethod": "OSM 建物 Dazzle 標示 18 Sukhumvit 7；PropertyHub 將 Residence 187 列為 Dazzle Sukhumvit 7 別名，DDproperty 個別掛牌與 Hipflat 專案地址均為 18 Sukhumvit 7。",
    "checkedAt": AS_OF,
}
save_array(coordinates_path, coordinates_prefix, [coordinate_rows[key] for key in sorted(coordinate_rows)])

manual_path, manual_prefix, manual = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = {int(row["hipflatId"]): row for row in manual}
manual_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "name": NAME,
    "sale": sale_market, "rent": rent_market,
    "replaceSale": True, "replaceRent": True,
    "fee": {"rate": 50, "status": "public", "note": "PropertyHub 專案頁標示管理費每㎡฿50；實際收費仍請向管委會確認。", "source": PROPERTYHUB_FEE},
}
save_array(manual_path, manual_prefix, [manual_rows[key] for key in sorted(manual_rows)])

cross_path, cross_prefix, crosschecks = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross_rows = {int(row["hipflatId"]): row for row in crosschecks}
cross_rows[PROJECT_ID] = {
    "hipflatId": PROJECT_ID, "projectName": NAME, "asOf": AS_OF,
    "sourceName": "DDproperty / PropertyHub / OpenStreetMap",
    "projectSourceUrl": DD_PROJECT,
    "sale": {"activeListingCount": 1, "listings": [sale_sample], "sourceUrl": DD_PROJECT,
             "note": "DDproperty 專案頁列 1 筆出售；個別掛牌為 1 房、64㎡、฿23,990,000，標示 2026-10-01 刊登。"},
    "rent": {"activeListingCount": 2, "listings": rent_samples, "sourceUrl": "https://www.ddproperty.com/en/condo-for-rent/at-residence-187-6131",
             "note": "DDproperty 租屋結果列兩筆近期更新掛牌，皆為 1 房、月租 ฿120,000；兩筆可能是同單位重複刊登，分別保留來源，不將筆數當成獨立成交量。"},
    "availabilitySources": [
        {"sourceName": "DDproperty 出售物件", "url": SALE_URL, "statusLabel": "1 房、64㎡、฿23,990,000；頁面列 2026-10-01。"},
        {"sourceName": "DDproperty 出租物件 500544595", "url": RENT_52_URL, "statusLabel": "1 房、約 52㎡、฿120,000/月；搜尋結果列 2026-09-27 更新。"},
        {"sourceName": "DDproperty 出租物件 500583076", "url": RENT_51_URL, "statusLabel": "1 房、51㎡、฿120,000/月；頁面列 2026-09-24。"},
        {"sourceName": "PropertyHub 專案別名", "url": PROPERTYHUB, "statusLabel": "Residence 187 列為 DAZZLE Sukhumvit 7 別名。"},
        {"sourceName": "PropertyHub 管理費資料", "url": PROPERTYHUB_FEE, "statusLabel": "專案頁列管理費 ฿50/㎡/月；實際收費請向管委會確認。"},
        {"sourceName": "OpenStreetMap 建物點位", "url": OSM, "statusLabel": "建物名稱 Dazzle、門牌 18 Sukhumvit 7；與 Hipflat、PropertyHub 專案別名及 DDproperty 掛牌地址相符。"},
    ],
    "yieldStatus": "calculated_from_lowest_1br_sale_and_rent_per_sqm",
    "yieldNote": "以最低可核實 1 房售價及同房型最低租金/㎡計算；售盤為 64㎡，租盤最低單價樣本約 52㎡。依 PropertyHub 列示的 ฿50/㎡/月管理費試算，實際收費請向管委會確認。",
}
save_array(cross_path, cross_prefix, [cross_rows[key] for key in sorted(cross_rows)], pretty=True)

(DIST / "index.html").write_text(
    (DIST / "index.html").read_text(encoding="utf-8")
    .replace("bangkok-verified-coordinates.js?v=20261019-arcadia-suite-osm-point", "bangkok-verified-coordinates.js?v=20261019-residence187-osm-point")
    .replace("bangkok-manual-market-samples.js?v=20261019-living24-phirom-direct-rent", "bangkok-manual-market-samples.js?v=20261019-residence187-ddproperty-sale-rent")
    .replace("bangkok-walk-routes.js?v=20261019-v-one-tower-3433", "bangkok-walk-routes.js?v=20261019-residence187-route")
    .replace("bangkok-market-crosschecks.js?v=20261019-living24-phirom-sale-status", "bangkok-market-crosschecks.js?v=20261019-residence187-exact-listings"),
    encoding="utf-8", newline="\n",
)

REPORT.write_text(json.dumps({
    "hipflatId": PROJECT_ID, "projectName": NAME, "checkedAt": AS_OF,
    "identity": {"hipflat": HIPFLAT, "ddProperty": DD_PROJECT, "propertyHubAlias": PROPERTYHUB},
    "coordinate": {"lat": 13.7433990, "lng": 100.5555585, "osmBuilding": OSM,
                    "evidence": "OSM way 1457578466 is named Dazzle at 18 Sukhumvit 7; PropertyHub lists Residence 187 as a project alias for Dazzle Sukhumvit 7; DDproperty and Hipflat use the same Soi Sukhumvit 7 address."},
    "sale": {"bedrooms": 1, "priceTHB": 23_990_000, "areaSqm": 64, "priceTHBPerSqm": sale_sample["priceSqm"], "updated": sale_sample["updated"], "url": SALE_URL},
    "rentSamples": [{"bedrooms": row["beds"], "priceTHBPerMonth": row["price"], "areaSqm": row["area"], "priceTHBPerSqmPerMonth": row["priceSqm"], "updated": row["updated"], "url": row["url"]} for row in rent_samples],
    "maintenanceFeeTHBPerSqmPerMonth": {"value": 50, "source": PROPERTYHUB_FEE, "status": "public_project_detail_requires_juristic_confirmation"},
    "yieldMethod": "lowest current 1BR sale total with its own area; same-room lowest rent per sqm multiplied by sale area; deduct 50 THB/sqm/month fee and one month of rent for agent management by default.",
    "duplicateRisk": "Two 120,000 THB rent posts may refer to the same unit; shown as two source records but not treated as independent transactions.",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"hipflatId": PROJECT_ID, "saleSamples": 1, "rentSamples": 2,
                  "coordinates": [13.7433990, 100.5555585], "report": str(REPORT)}, ensure_ascii=False))
