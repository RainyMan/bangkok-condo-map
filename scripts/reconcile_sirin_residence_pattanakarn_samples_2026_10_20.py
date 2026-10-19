"""Replace a mismatched city-index sale record with exact-project listings."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HIPFLAT_ID = 4019
AS_OF = "2026-10-20"
PH_PROJECT = "https://propertyhub.in.th/en/projects/sirin-residence-pattanakarn"
PH_SALE_PROJECT = "https://propertyhub.in.th/en/condo-for-sale/project-sirin-residence-pattanakarn"
PH_RENT_PROJECT = "https://propertyhub.in.th/en/condo-for-rent/project-sirin-residence-pattanakarn"
WRONG_MATCH = "https://propertyhub.in.th/en/listings/great-value-condo-for-sale-at-sirin-residence-phahonyothin-area-near-bts-sai-yud---6308923"
SALE_6130985 = "https://asset-direct-v2.propertyhub.in.th/en/listings/for-sale-sirin-residence-pattanakan-near-hua-mak-station---6130985"
SALE_2173652 = "https://propertyscout.co.th/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-1-%E0%B8%AB%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%99%E0%B8%AD%E0%B8%99-%E0%B8%97%E0%B8%B5%E0%B9%88-%E0%B8%A8%E0%B8%B4%E0%B8%A3%E0%B8%B4%E0%B8%99-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%9E%E0%B8%B1%E0%B8%92%E0%B8%99%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89-arl-%E0%B8%A3%E0%B8%B2%E0%B8%A1%E0%B8%84%E0%B8%B3%E0%B9%81%E0%B8%AB%E0%B8%87-2173652/"


def load_rows(path: Path, symbol: str) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", source, re.S)
    if not match:
        raise ValueError(f"Cannot find {symbol} in {path}")
    return json.loads(match.group(1))


def save_rows(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
        newline="\n",
    )


sale_samples = [
    {
        "id": "6130985",
        "price": 1_890_000,
        "area": 29,
        "priceSqm": 65_172,
        "beds": 0,
        "roomType": "Studio",
        "title": "Sirin Residence Pattanakarn studio · 29 sqm · THB 1,890,000",
        "url": SALE_6130985,
        "sourceName": "PropertyHub",
        "projectName": "Sirin Residence Pattanakarn",
        "updated": "2026-09-28",
        "checkedAt": AS_OF,
        "matchedBy": "exact PropertyHub project page; Pattanakarn/Hua Mak listing",
        "listingStatus": "availability_unconfirmed_update_under_30d",
    },
    {
        "id": "2173652",
        "price": 1_900_000,
        "area": 37,
        "priceSqm": 51_351,
        "beds": 1,
        "roomType": "1 Bedroom",
        "title": "Sirin Residence Pattanakarn 1 bedroom · 37 sqm · THB 1,900,000",
        "url": SALE_2173652,
        "sourceName": "PropertyScout",
        "projectName": "Sirin Residence Pattanakarn",
        "updated": "2026-10-18",
        "checkedAt": AS_OF,
        "matchedBy": "exact project name and Suan Luang address; availability checked 2 days before observation",
        "listingStatus": "active_as_listed",
    },
]

sale = {
    "count": 2,
    "observedCount": 2,
    "countKind": "manual_verified_listing",
    "average": 1_895_000,
    "minimum": 1_890_000,
    "minimumArea": 29,
    "minimumSampleUpdated": "2026-09-28",
    "averageSqm": 58_262,
    "minimumSqm": 51_351,
    "minimumSqmSampleUpdated": "2026-10-18",
    "asOf": AS_OF,
    "sourceName": "PropertyHub / PropertyScout 個別出售掛牌",
    "source": PH_SALE_PROJECT,
    "minimumSourceUrl": SALE_6130985,
    "minimumSqmSourceUrl": SALE_2173652,
    "byBedroom": {
        "1": {
            "count": 1,
            "minimum": 1_900_000,
            "area": 37,
            "minimumArea": 37,
            "priceSqm": 51_351,
            "minimumSqm": 51_351,
            "sourceUrl": SALE_2173652,
            "minimumSqmSourceUrl": SALE_2173652,
        }
    },
    "samples": sale_samples,
}

rent = {
    "count": 0,
    "observedCount": 0,
    "countKind": "manual_project_availability_check",
    "minimum": 0,
    "minimumSqm": 0,
    "asOf": AS_OF,
    "sourceName": "PropertyHub exact project rental page",
    "source": PH_RENT_PROJECT,
    "samples": [],
    "availabilityNote": "The latest available PropertyHub project snapshot shows 0 rental listings; snapshot age is not stated, so rent and ROI remain unavailable until a current unit listing is verified.",
}

market_record = {
    "hipflatId": HIPFLAT_ID,
    "name": "Sirin Residence Pattanakarn",
    "asOf": AS_OF,
    "replaceSale": True,
    "replaceRent": True,
    "sale": sale,
    "rent": rent,
    "fee": {
        "rate": 28,
        "status": "public",
        "note": "PropertyHub 專案頁列管理費 ฿28/㎡/月；實際收費請向管委會確認。",
        "source": PH_PROJECT,
    },
}

manual_path = ROOT / "dist/bangkok-manual-market-samples.js"
manual_rows = load_rows(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES")
manual_rows = [row for row in manual_rows if int(row["hipflatId"]) != HIPFLAT_ID]
manual_rows.append(market_record)
save_rows(manual_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_rows)

crosschecks_path = ROOT / "dist/bangkok-market-crosschecks.js"
crosschecks = load_rows(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS")
crosscheck = {
    "hipflatId": HIPFLAT_ID,
    "projectName": "Sirin Residence Pattanakarn",
    "asOf": AS_OF,
    "yieldStatus": "not_calculable",
    "yieldNote": "未核實到可用的當前出租單筆物件；保留空租金，不計算投報率。",
    "sourceName": "PropertyHub / PropertyScout 專案與房源核對",
    "projectSourceUrl": PH_PROJECT,
    "sale": {
        "activeListingCount": 2,
        "sourceUrl": PH_SALE_PROJECT,
        "listings": [
            {"id": row["id"], "bedrooms": row["beds"], "price": row["price"], "area": row["area"], "url": row["url"], "updatedAt": row["updated"]}
            for row in sale_samples
        ],
        "note": "以兩筆 Pattanakarn/Hua Mak 個別房源取代 Phahonyothin/Sai Yud 誤配；最低總價為 Studio ฿1,890,000 / 29㎡，最低一房單價為 ฿51,351/㎡。",
    },
    "rent": {
        "activeListingCount": 0,
        "sourceUrl": PH_RENT_PROJECT,
        "listings": [],
        "note": rent["availabilityNote"],
    },
    "availabilitySources": [
        {"sourceName": "PropertyHub 專案售盤頁", "url": PH_SALE_PROJECT, "statusLabel": "明列 Pattanakarn 專案房源；1,890,000 泰銖 Studio 於 2026-09-28 刷新。"},
        {"sourceName": "PropertyScout 個別一房掛牌", "url": SALE_2173652, "statusLabel": "Suan Luang Pattanakarn 專案，37㎡、1 房、1,900,000 泰銖；頁面標示 2026-10-18 可售確認。"},
        {"sourceName": "排除的 PropertyHub 誤配樣本", "url": WRONG_MATCH, "statusLabel": "詳情地址為 Phahonyothin Road、Anusawari、Bang Khen，非 Pattanakarn 的 Suan Luang；不納入專案售價與投報。"},
        {"sourceName": "PropertyHub 專案租盤頁", "url": PH_RENT_PROJECT, "statusLabel": "來源快照未列租盤，快照年齡未註明；不推算租金或投報率。"},
    ],
    "yield": {
        "status": "not_calculable",
        "reason": "未核實到有可用租金與同房型對應的當前出租物件；不以歷史或異專案租盤代算。",
    },
}
crosschecks = [row for row in crosschecks if int(row["hipflatId"]) != HIPFLAT_ID]
crosschecks.append(crosscheck)
save_rows(crosschecks_path, "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": HIPFLAT_ID,
    "project": "Sirin Residence Pattanakarn",
    "checkedAt": AS_OF,
    "identity": {
        "hipflatProjectUrl": "https://www.hipflat.co.th/en/projects/sirin-residence-pattanakarn-fgphiu",
        "propertyHubProjectUrl": PH_PROJECT,
        "propertyHubProjectName": "Sirin Residence Pattanakarn",
        "propertyHubAddress": "Suan Luang, Bangkok",
        "floors": 8,
        "units": 77,
    },
    "excludedMismatchedListing": {
        "url": WRONG_MATCH,
        "listedProjectLabel": "Sirin Residence Pattanakarn",
        "detailsAddress": "Phahonyothin Road, Anusawari, Bang Khen, Bangkok",
        "reason": "Bang Khen / Sai Yud location conflicts with the exact Pattanakarn project location in Suan Luang.",
    },
    "saleSamples": sale_samples,
    "rent": {
        "status": "no_confirmed_current_unit_sample",
        "projectPage": PH_RENT_PROJECT,
        "note": rent["availabilityNote"],
    },
    "yield": {"status": "not_calculable", "reason": crosscheck["yield"]["reason"]},
    "sources": {
        "propertyHubProject": PH_PROJECT,
        "propertyHubSale": PH_SALE_PROJECT,
        "propertyHubRent": PH_RENT_PROJECT,
        "lowestTotalSale": SALE_6130985,
        "lowestOneBedroomRate": SALE_2173652,
        "excludedMismatchedSale": WRONG_MATCH,
    },
}
(ROOT / "reports/sirin-residence-pattanakarn-market-reconciliation-2026-10-20.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print("Updated manual sale/rent override, market crosscheck, and reconciliation report for Hipflat 4019.")
