"""Add a recently updated A-Pa Place individual sale listing and availability check."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
AS_OF = "2026-10-19"
LISTING_URL = "https://www.livinginsider.com/detail/condo-for-sale-sapankwaijatujak-1bedroom-3086008"
PROPERTYHUB_PROJECT_URL = "https://propertyhub.in.th/projects/arpa-place"
PROPERTYHUB_SALE_URL = "https://propertyhub.in.th/ขายคอนโด/โครงการ-arpa-place"
PROPERTYHUB_RENT_URL = "https://propertyhub.in.th/เช่าคอนโด/โครงการ-arpa-place"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/apa-place-ufwlfe"


def load_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = DIST / filename
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise ValueError(f"Missing {symbol} in {filename}")
    return path, json.loads(match.group(1))


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    price, area = 550_000, 26.85
    price_sqm = round(price / area, 2)
    sample = {
        "id": "T-141273",
        "kind": "sale",
        "price": price,
        "area": area,
        "priceSqm": price_sqm,
        "beds": 1,
        "roomType": "1BR",
        "title": "A-Pa Place Ratchada 32 · 1 房 · 26.85 ㎡ · ฿550,000",
        "url": LISTING_URL,
        "sourceName": "LivingInsider 直接出售掛牌",
        "projectName": "A-Pa Place",
        "checkedAt": AS_OF,
        "updated": "2026-10-12",
        "matchedBy": "exact_project_name_and_listing_map_pin_approximately_55m_from_verified_project_pin",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    }

    path, rows = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in rows if row.get("hipflatId") == 3073), None)
    if project is None:
        project = {"hipflatId": 3073, "name": "A-Pa Place"}
        rows.append(project)
    project["sale"] = {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "averageSqm": price_sqm,
        "minimumSqm": price_sqm,
        "minimumSqmSampleUpdated": "2026-10-12",
        "minimumSampleUpdated": "2026-10-12",
        "asOf": AS_OF,
        "sourceName": "LivingInsider 直接房源",
        "source": LISTING_URL,
        "minimumSourceUrl": LISTING_URL,
        "minimumSqmSourceUrl": LISTING_URL,
        "samples": [sample],
        "note": "單筆房源標示 1 房、26.85㎡、฿550,000；頁面顯示 2026-05-24 建立、於核對日前約一週更新。座標連結與已核實專案點相距約 55 公尺；在架狀態仍請向刊登者確認。",
    }
    project["replaceSale"] = True
    save_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", rows)

    path, rows = load_array("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
    check = next((row for row in rows if row.get("hipflatId") == 3073), None)
    if check is None:
        check = {"hipflatId": 3073, "projectName": "A-Pa Place"}
        rows.append(check)
    check.update({
        "asOf": AS_OF,
        "sourceName": "LivingInsider / PropertyHub / Hipflat",
        "projectSourceUrl": HIPFLAT_URL,
        "sale": {
            "activeListingCount": 1,
            "listings": [{
                "id": "T-141273", "price": price, "area": area, "priceSqm": price_sqm,
                "bedrooms": 1, "checkedAt": AS_OF, "url": LISTING_URL,
                "sourceName": "LivingInsider", "listingStatus": "availability_unconfirmed_update_under_30d",
            }],
            "sourceUrl": LISTING_URL,
            "note": "PropertyHub 專案出售頁顯示無掛牌；另核到 LivingInsider 單筆 1 房出售頁，顯示約一週前更新，現況請向刊登者確認。",
        },
        "rent": {
            "activeListingCount": 0,
            "sourceUrl": PROPERTYHUB_RENT_URL,
            "note": "PropertyHub 的 Arpa Place 專案出租頁顯示目前沒有出租掛牌；Hipflat 專案頁亦顯示無可用物件。",
        },
        "availabilitySources": [
            {"sourceName": "LivingInsider 單筆出售頁", "url": LISTING_URL, "statusLabel": "1 房、26.85㎡、฿550,000；頁面顯示約一週前更新，現況待向仲介確認。"},
            {"sourceName": "PropertyHub 出售專案頁", "url": PROPERTYHUB_SALE_URL, "statusLabel": "專案頁目前顯示無出售掛牌；與最近更新的 LivingInsider 單筆頁資料並列，未據此將其判定為已售。"},
            {"sourceName": "PropertyHub 出租專案頁", "url": PROPERTYHUB_RENT_URL, "statusLabel": "專案頁顯示目前沒有出租掛牌。"},
            {"sourceName": "PropertyHub 專案定位", "url": PROPERTYHUB_PROJECT_URL, "statusLabel": "專案名稱 Arpa Place、จตุจักร；地圖點與房源頁 Google Maps 點位相距約 55 公尺。"},
            {"sourceName": "Hipflat 專案頁", "url": HIPFLAT_URL, "statusLabel": "專案頁顯示目前無可用物件；完工年 1996、8 層、121 戶。"},
        ],
        "yieldStatus": "not_calculated",
        "yieldNote": "已核對一筆近期更新出售掛牌，但 PropertyHub 與 Hipflat 沒有找到本案現行出租掛牌；缺少本案租金樣本，不計投報率。",
    })
    save_array(path, "BANGKOK_MARKET_CROSSCHECKS", rows)


if __name__ == "__main__":
    main()
