from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "siri-sathorn-rents-2026-10-19.json"
PROJECT_ID = 3180
NAME = "Siri Sathorn"
PROJECT_URL = "https://www.hipflat.co.th/projects/siri-sathorn-cncjua"
CHECKED = "2026-10-19"

LISTINGS = [
    {
        "id": "9a2el0cl8te71hl9948ecl0c3u0heaa4",
        "price": 80_000,
        "area": 100,
        "beds": 2,
        "baths": 2,
        "floor": 0,
        "title": "Siri Sathorn · 2 房 · 100 ㎡ · ฿80,000/月",
        "sourceName": "FazWaz / Hipflat 個別掛牌",
    },
    {
        "id": "8a9lt9n889nh200hlunt29343u0heu72",
        "price": 60_000,
        "area": 60,
        "beds": 1,
        "baths": 1,
        "floor": 0,
        "title": "Siri Sathorn · 1 房 · 60 ㎡ · ฿60,000/月",
        "sourceName": "FazWaz / Hipflat 個別掛牌",
    },
    {
        "id": "1e9c09l2872n9cl44ac49ln33u02u918",
        "price": 50_000,
        "area": 55,
        "beds": 1,
        "baths": 1,
        "floor": 0,
        "title": "Siri Sathorn · 1 房 · 55 ㎡ · ฿50,000/月",
        "sourceName": "108Siam / Hipflat 個別掛牌",
    },
]


def load_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = DIST / filename
    match = re.search(
        rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);",
        path.read_text(encoding="utf-8"),
        re.S,
    )
    if not match:
        raise ValueError(f"Could not parse {symbol} from {path.name}")
    return path, json.loads(match.group(1))


def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(
        f"window.{symbol} = "
        + json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    samples = []
    for row in LISTINGS:
        price, area = row["price"], row["area"]
        samples.append(
            {
                **row,
                "priceSqm": round(price / area, 2),
                "roomType": f"{row['beds']} 房",
                "url": f"https://www.hipflat.co.th/ads/{row['id']}",
                "sourceName": row["sourceName"],
                "projectName": NAME,
                "checkedAt": CHECKED,
                "matchedBy": "individual_listing_linked_from_exact_Hipflat_project_page_with_matching_project_name_and_Silom_Sala_Daeng_1_address",
                "listingStatus": "active_as_listed",
            }
        )
    monthly_prices = [sample["price"] for sample in samples]
    rates = [sample["price"] / sample["area"] for sample in samples]
    min_total = min(samples, key=lambda sample: sample["price"])
    min_rate = min(samples, key=lambda sample: sample["price"] / sample["area"])
    rent_by_bedroom: dict[str, dict] = {}
    for beds in sorted({sample["beds"] for sample in samples}):
        same_bedroom = [sample for sample in samples if sample["beds"] == beds]
        lowest_total = min(same_bedroom, key=lambda sample: sample["price"])
        lowest_rate = min(same_bedroom, key=lambda sample: sample["price"] / sample["area"])
        rent_by_bedroom[str(beds)] = {
            "count": len(same_bedroom),
            "minimum": lowest_total["price"],
            "area": lowest_total["area"],
            "minimumArea": lowest_total["area"],
            "minimumSqm": round(lowest_rate["price"] / lowest_rate["area"], 2),
            "averageSqm": round(sum(item["price"] / item["area"] for item in same_bedroom) / len(same_bedroom)),
            "sourceUrl": lowest_total["url"],
            "minimumSourceUrl": lowest_total["url"],
            "minimumSqmSourceUrl": lowest_rate["url"],
        }
    rent = {
        "count": len(samples),
        "observedCount": len(samples),
        "countKind": "manual_verified_listing",
        "average": round(sum(monthly_prices) / len(monthly_prices)),
        "minimum": min_total["price"],
        "minimumArea": min_total["area"],
        "minimumSampleUpdated": None,
        "averageSqm": round(sum(rates) / len(rates)),
        "minimumSqm": round(min_rate["price"] / min_rate["area"], 2),
        "minimumSqmSampleUpdated": None,
        "asOf": CHECKED,
        "sourceName": "Hipflat 個別出租掛牌",
        "source": PROJECT_URL,
        "minimumSourceUrl": min_total["url"],
        "minimumSqmSourceUrl": min_rate["url"],
        "byBedroom": rent_by_bedroom,
        "samples": samples,
    }
    path, manual = load_array("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    project = next((row for row in manual if int(row.get("hipflatId", 0)) == PROJECT_ID), None)
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        manual.append(project)
    project.update({"asOf": CHECKED, "rent": rent, "replaceRent": True})
    save_array(path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual)

    report = {
        "hipflatId": PROJECT_ID,
        "project": NAME,
        "checkedAt": CHECKED,
        "projectSource": PROJECT_URL,
        "projectIdentity": "Hipflat project page lists Siri Sathorn at 27 Soi Sala Daeng 1, Silom, Bang Rak; this matches the catalogue project name/address and the exact-name OSM point.",
        "rentListings": [
            {
                "priceThbPerMonth": sample["price"],
                "bedrooms": sample["beds"],
                "areaSqm": sample["area"],
                "rentThbPerSqmMonth": round(sample["price"] / sample["area"], 2),
                "url": sample["url"],
            }
            for sample in samples
        ],
        "sale": "No individual sale listing found on the Hipflat project page or in exact-name DDproperty/PropertyHub/Hipflat searches. Baan Siri Sathorn results are a different project and excluded.",
        "yield": "Not calculated because no sale sample for Siri Sathorn was verified.",
        "availability": "Hipflat's project page displayed three rent units when checked; current vacancy is not independently confirmed with the advertisers.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html, count = re.subn(
        r"bangkok-manual-market-samples\.js\?v=[^\"']+",
        "bangkok-manual-market-samples.js?v=20261019-siri-sathorn-exact-rents",
        html,
    )
    if count != 1:
        raise RuntimeError("Could not update exactly one manual-market cache key")
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "rentSamples": len(samples), "lowestMonthlyRent": min_total["price"], "lowestRentPerSqm": round(min_rate["price"] / min_rate["area"], 2)}))


if __name__ == "__main__":
    main()
