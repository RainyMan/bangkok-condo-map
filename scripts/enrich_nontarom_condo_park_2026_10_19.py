from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "nontarom-condo-park-enrichment-2026-10-19.json"
PROJECT_ID = 3583
NAME = "Nontarom Condo Park"
CHECKED = "2026-10-19"
HIPFLAT_URL = "https://www.hipflat.co.th/projects/nontarom-condo-park-yslcxr"
SALE_URL = "https://www.hipflat.co.th/ads/t393ll8a81a2aaca7t7nahn43u04u42e"
RENT_URL = "https://www.hipflat.co.th/ads/99484t1u814a0tu7h7897ne83u0h14a3"
COORD_URL = "https://homestock.co.th/place/the-walk-ratchaphruek"
ADDRESS_CHECK_URL = "https://www.ddproperty.com/en/project/1435-nontarom-condo-park-talingchun"


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


def sample(url: str, price: int, area: int, room_type: str, source: str) -> dict:
    return {
        "id": url.rsplit("/", 1)[-1],
        "price": price,
        "area": area,
        "priceSqm": round(price / area, 2),
        "beds": 1,
        "roomType": room_type,
        "title": f"{NAME} · {room_type} · {area} ㎡ · ฿{price:,}{' / 月' if source == 'rent' else ''}",
        "url": url,
        "sourceName": "Hipflat 個別掛牌",
        "projectName": NAME,
        "checkedAt": CHECKED,
        "matchedBy": "individual_listing_linked_from_exact_Hipflat_project_page_with_matching_project_name_and_address",
        "listingStatus": "active_as_listed",
    }


def market(source: str, unit: dict) -> dict:
    price = unit["price"]
    area = unit["area"]
    rate = round(price / area, 2)
    return {
        "count": 1,
        "observedCount": 1,
        "countKind": "manual_verified_listing",
        "average": price,
        "minimum": price,
        "minimumArea": area,
        "minimumSampleUpdated": None,
        "averageSqm": round(rate),
        "minimumSqm": rate,
        "minimumSqmSampleUpdated": None,
        "asOf": CHECKED,
        "sourceName": "Hipflat 個別出售掛牌" if source == "sale" else "Hipflat 個別出租掛牌",
        "source": unit["url"],
        "minimumSourceUrl": unit["url"],
        "minimumSqmSourceUrl": unit["url"],
        "byBedroom": {
            "1": {
                "count": 1,
                "minimum": price,
                "area": area,
                "minimumArea": area,
                "minimumSqm": rate,
                "averageSqm": round(rate),
                "sourceUrl": unit["url"],
                "minimumSourceUrl": unit["url"],
                "minimumSqmSourceUrl": unit["url"],
            }
        },
        "samples": [unit],
    }


def main() -> None:
    # HomeStock supplies coordinates on its nearby-condo map; Hipflat's exact
    # project page and DDproperty confirm this is the same 120-unit complex.
    coordinate_path, coordinates = load_array(
        "bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES"
    )
    coordinate = {
        "hipflatId": PROJECT_ID,
        "name": NAME,
        "lat": 13.77909,
        "lng": 100.45626,
        "locationVerified": True,
        "sourceName": "HomeStock 專案座標",
        "sourceUrl": COORD_URL,
        "verificationSourceUrl": HIPFLAT_URL,
        "corroborationSourceUrl": ADDRESS_CHECK_URL,
        "verificationMethod": "exact_project_name_coordinate_listing_cross_checked_with_Hipflat_and_DDproperty_project_address_and_120_unit_complex",
    }
    coordinates = [row for row in coordinates if int(row.get("hipflatId", 0)) != PROJECT_ID]
    coordinates.append(coordinate)
    save_array(coordinate_path, "BANGKOK_VERIFIED_COORDINATES", coordinates)

    # The app currently takes this project's approximate PropertyHub point
    # before consulting the verified-coordinate table. Replace that point in
    # the loaded record too, so the map actually uses the stronger evidence.
    guessed_path, guessed_rows = load_array(
        "bangkok-propertyhub-guessed-details.js", "BANGKOK_PROPERTYHUB_GUESSED_DETAILS"
    )
    guessed = next(
        (row for row in guessed_rows if int(row.get("hipflatProjectId", 0)) == PROJECT_ID),
        None,
    )
    if guessed is None:
        raise ValueError("Expected the existing matched PropertyHub project record")
    guessed.update(
        {
            "lat": coordinate["lat"],
            "lng": coordinate["lng"],
            "locationVerified": True,
            "locationSourceName": coordinate["sourceName"],
            "locationSourceUrl": coordinate["sourceUrl"],
            "locationVerificationSourceUrl": HIPFLAT_URL,
        }
    )
    save_array(guessed_path, "BANGKOK_PROPERTYHUB_GUESSED_DETAILS", guessed_rows)

    # Hipflat's project page linked one 1-bedroom unit per market: ฿1.29M / 32
    # sqm for sale and ฿5,000 / 24 sqm for rent. Do not pair the unlike units;
    # ROI will apply the rent rate per sqm to the sale unit's 32 sqm area.
    sale_unit = sample(SALE_URL, 1_290_000, 32, "1 房", "sale")
    rent_unit = sample(RENT_URL, 5_000, 24, "1 房", "rent")
    market_path, manual_markets = load_array(
        "bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES"
    )
    project = next(
        (row for row in manual_markets if int(row.get("hipflatId", 0)) == PROJECT_ID),
        None,
    )
    if project is None:
        project = {"hipflatId": PROJECT_ID, "name": NAME}
        manual_markets.append(project)
    project.update(
        {
            "asOf": CHECKED,
            "sale": market("sale", sale_unit),
            "rent": market("rent", rent_unit),
            "replaceSale": True,
            "replaceRent": True,
        }
    )
    save_array(market_path, "BANGKOK_MANUAL_MARKET_SAMPLES", manual_markets)

    monthly_rent_estimate = round(rent_unit["price"] / rent_unit["area"] * sale_unit["area"])
    net_rent_after_agent = monthly_rent_estimate * 11
    roi_after_agent = net_rent_after_agent / sale_unit["price"] * 100
    report = {
        "hipflatId": PROJECT_ID,
        "project": NAME,
        "checkedAt": CHECKED,
        "coordinates": {
            "lat": coordinate["lat"],
            "lng": coordinate["lng"],
            "source": COORD_URL,
            "projectIdentitySource": HIPFLAT_URL,
            "addressCorroboration": ADDRESS_CHECK_URL,
            "evidence": "HomeStock lists Nontarom Condo Park at 13.77909, 100.45626. Hipflat identifies the project as 14/1 Soi Chak Phra 26 with 120 units; DDproperty describes the same Nontarom 3-building, 120-unit complex at 314 Chak Phra Road, Taling Chan.",
        },
        "sale": {
            "priceThb": sale_unit["price"],
            "areaSqm": sale_unit["area"],
            "pricePerSqmThb": sale_unit["priceSqm"],
            "bedrooms": sale_unit["beds"],
            "url": SALE_URL,
        },
        "rent": {
            "monthlyThb": rent_unit["price"],
            "areaSqm": rent_unit["area"],
            "rentPerSqmMonthThb": rent_unit["priceSqm"],
            "bedrooms": rent_unit["beds"],
            "url": RENT_URL,
        },
        "roiEstimate": {
            "monthlyRentAtSaleUnitAreaThb": monthly_rent_estimate,
            "assumption": "Apply the 1-bedroom rent listing's per-sqm rate to the 32 sqm sale listing; the sale and rent are distinct units.",
            "afterOneAgentMonthPercent": round(roi_after_agent, 2),
            "managementFee": "Not verified; excluded from this estimate.",
        },
        "sourceNote": "The Hipflat project page showed and linked one sale and one rental unit when checked. Availability is not independently confirmed with the advertisers.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html, coord_count = re.subn(
        r"bangkok-verified-coordinates\.js\?v=[^\"']+",
        "bangkok-verified-coordinates.js?v=20261019-nontarom-coordinate",
        html,
    )
    html, market_count = re.subn(
        r"bangkok-manual-market-samples\.js\?v=[^\"']+",
        "bangkok-manual-market-samples.js?v=20261019-nontarom-direct-sale-rent",
        html,
    )
    if coord_count != 1 or market_count != 1:
        raise RuntimeError("Could not update exactly one cache key for each changed data file")
    html, guessed_count = re.subn(
        r"bangkok-propertyhub-guessed-details\.js\?v=[^\"']+",
        "bangkok-propertyhub-guessed-details.js?v=20261019-nontarom-coordinate-crosscheck",
        html,
    )
    if guessed_count != 1:
        raise RuntimeError("Could not update the PropertyHub matched-coordinate cache key")
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({"hipflatId": PROJECT_ID, "coordinates": [coordinate["lat"], coordinate["lng"]], "salePrice": sale_unit["price"], "saleArea": sale_unit["area"], "rentPrice": rent_unit["price"], "rentArea": rent_unit["area"], "roiAfterAgentPercent": round(roi_after_agent, 2)}))


if __name__ == "__main__":
    main()
