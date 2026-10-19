from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECT_ID = 3038
NAME = "Ussakan Place Twin Condo"
AS_OF = "2026-10-19"
BAM_URL = "https://www.bam.co.th/en/npa/property/66293"
RENT_URL = "https://www.hipflat.co.th/ads/2a0a0aa081tl8cnn841984eu3ul38t9u"
PROJECT_URL = "https://www.hipflat.com/projects/ussakan-place-twin-condo-uprazd"


def load(filename: str, symbol: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", text, re.S)
    if not match:
        raise RuntimeError(f"Missing {symbol} in {filename}")
    return json.loads(match.group(1))


def save(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f"window.{symbol} = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


asset = {
    "id": "HBKKCU4862001",
    "price": 1467000,
    "area": 48.17,
    "priceSqm": 30455,
    "beds": 1,
    "roomType": "1 Bedroom",
    "title": "BAM bank-owned condo asset · 1 bedroom · 48.17 sqm · ฿1,467,000",
    "url": BAM_URL,
    "sourceName": "Bangkok Commercial Asset Management (BAM)",
    "projectName": NAME,
    "updated": AS_OF,
    "checkedAt": AS_OF,
    "matchedBy": "exact_project_name_and_address_ramkhamhaeng_105_1_on_official_BAM_asset_page",
    "listingStatus": "active_as_listed",
    "specialAsset": True,
}

manual = load("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
entry = next((item for item in manual if int(item.get("hipflatId", -1)) == PROJECT_ID), None)
if entry is None:
    entry = {"hipflatId": PROJECT_ID, "name": NAME}
    manual.append(entry)
sale = entry.setdefault("sale", {})
samples = sale.setdefault("samples", [])
samples[:] = [item for item in samples if item.get("url") != BAM_URL]
samples.append(asset)
entry["asOf"] = AS_OF
manual.sort(key=lambda item: int(item["hipflatId"]))
save("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

crosschecks = load("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS")
cross = next((item for item in crosschecks if int(item.get("hipflatId", -1)) == PROJECT_ID), None)
if cross is None:
    cross = {"hipflatId": PROJECT_ID, "projectName": NAME}
    crosschecks.append(cross)
cross.update(
    {
        "projectName": NAME,
        "asOf": AS_OF,
        "sourceName": "BAM bank-owned asset",
        "sale": {
            "activeListingCount": 1,
            "sourceUrl": BAM_URL,
            "listings": [
                {
                    "listingId": asset["id"],
                    "bedrooms": 1,
                    "price": asset["price"],
                    "area": asset["area"],
                    "priceSqm": asset["priceSqm"],
                    "listedAt": "Checked 2026-10-19",
                    "url": BAM_URL,
                }
            ],
        },
        "availabilitySources": [
            {
                "sourceName": "BAM 官方銀行資產出售物件",
                "url": BAM_URL,
                "statusLabel": "頁面目前可查到資產代碼 HBKKCU4862001：1 房、48.17㎡、฿1,467,000；銀行註明價格可能依條件變動。此為銀行資產，單獨列示，不納入一般市場均價與投報。",
            },
            {
                "sourceName": "Hipflat 專案出租物件",
                "url": RENT_URL,
                "statusLabel": "另有 1 房、38㎡、฿8,000/月的 Hipflat 租盤；與銀行出售資產不是同一間物件，故不把它與特惠資產配對計算投報。",
            },
        ],
        "roi": {
            "status": "not_calculable",
            "reason": "可核實出售來源屬銀行特惠資產；一般市場未有配對的同房型出售樣本，不以特惠價與一般租盤計算投報。",
        },
        "note": "BAM listing price is subject to change; retain this separately from ordinary market samples.",
    }
)
crosschecks.sort(key=lambda item: int(item["hipflatId"]))
save("bangkok-market-crosschecks.js", "BANGKOK_MARKET_CROSSCHECKS", crosschecks)

report = {
    "hipflatId": PROJECT_ID,
    "project": NAME,
    "checkedAt": AS_OF,
    "sale": asset,
    "rent": {
        "status": "direct_project_sample_present",
        "price": 8000,
        "areaSqm": 38,
        "bedrooms": 1,
        "url": RENT_URL,
        "source": PROJECT_URL,
    },
    "roi": {
        "status": "not_calculable",
        "reason": "The BAM property is a special bank-owned asset and is kept out of ordinary market-yield calculations; the existing project rental listing is another unit.",
    },
    "identityCheck": "BAM page names Ussakan Place Twin Condo and gives an exact Ramkhamhaeng 105/1 address, matching the Hipflat project; nearby Asakan Place listings were excluded.",
    "sources": {"bamAsset": BAM_URL, "hipflatProject": PROJECT_URL, "hipflatRent": RENT_URL},
}
(ROOT / "reports" / "ussakan-place-bam-asset-2026-10-19.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

index = (DIST / "index.html").read_text(encoding="utf-8")
index, count = re.subn(
    r"bangkok-manual-market-samples\.js\?v=[^\"']+",
    "bangkok-manual-market-samples.js?v=20261019-ussakan-bam-asset",
    index,
    count=1,
)
if count != 1:
    raise RuntimeError("Could not update market sample cache key")
(DIST / "index.html").write_text(index, encoding="utf-8")
print(json.dumps({"project": NAME, "specialSaleAsset": asset["id"], "generalMarketAndROI": "unchanged", "report": "reports/ussakan-place-bam-asset-2026-10-19.json"}, ensure_ascii=False))
