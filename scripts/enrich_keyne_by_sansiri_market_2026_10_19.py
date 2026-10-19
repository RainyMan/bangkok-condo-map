"""Link Hipflat KEYNE BY SANSIRI to its exact PropertyHub project and listings."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import enrich_propertyhub_exact_project_pages as exact

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "keyne-by-sansiri-propertyhub-2026-10-19.json"
HIPFLAT_ID = 3086
PROPERTYHUB_ID = "289"
PROJECT_SLUG = "keyne"
HIPFLAT_URL = "https://www.hipflat.co.th/en/projects/keyne-by-sansiri-papeli"


def save_rows(filename: str, symbol: str, rows: list[dict]) -> None:
    exact.write(filename, symbol, rows)


def upsert(rows: list[dict], key: str, value: object, row: dict) -> list[dict]:
    for index, current in enumerate(rows):
        if str(current.get(key)) == str(value):
            rows[index] = row
            return rows
    rows.append(row)
    return rows


def main() -> None:
    catalogue = exact.arr("bangkok-catalogue.js", "BANGKOK_CONDO_CATALOGUE")
    project = next(row for row in catalogue if int(row["id"]) == HIPFLAT_ID)
    assert project["name"] == "KEYNE BY SANSIRI"
    ph_rows = exact.arr("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    ph = next(row for row in ph_rows if int(row["id"]) == HIPFLAT_ID)
    assert str(ph.get("propertyHubProjectId")) == PROPERTYHUB_ID

    kinds = {kind: exact.parse_market(HIPFLAT_ID, kind, PROJECT_SLUG, PROPERTYHUB_ID) for kind in ("sale", "rent")}
    project_data = next(row["project"] for row in kinds.values() if row.get("project"))
    alternate_names = project_data.get("projectInfo", {}).get("possibleProjectNames", [])
    assert exact.norm_full_name(project_data.get("nameEnglish") or project_data.get("name")) == "keyne"
    assert "keyne by sansiri" in {exact.norm_full_name(name) for name in alternate_names}
    assert re.search(r"\bkhlong\s+toei\b", str(project_data.get("address", "")), re.I)
    point = project_data.get("location") or {}
    lat, lng = float(point["lat"]), float(point["lng"])
    assert 13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0

    manual_rows = exact.arr("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES")
    manual = next((row for row in manual_rows if int(row["hipflatId"]) == HIPFLAT_ID), {"hipflatId": HIPFLAT_ID, "name": project["name"]})
    report_markets = {}
    for kind, data in kinds.items():
        if data.get("error") or not data.get("cards"):
            raise RuntimeError(f"No verified current PropertyHub {kind} cards: {data}")
        cards = data["cards"]
        lowest_total = min(cards, key=lambda row: row["price"])
        lowest_sqm = min(cards, key=lambda row: row["price"] / row["area"])
        by_bedroom: dict[str, dict] = {}
        for beds in sorted({int(row["beds"]) for row in cards if str(row.get("beds", "")).isdigit() and int(row["beds"]) > 0}):
            room_rows = [row for row in cards if int(row.get("beds") or 0) == beds]
            room_total = min(room_rows, key=lambda row: row["price"])
            room_sqm = min(room_rows, key=lambda row: row["price"] / row["area"])
            by_bedroom[str(beds)] = {
                "count": len(room_rows), "minimum": room_total["price"], "area": room_total["area"],
                "minimumArea": room_total["area"], "priceSqm": round(room_total["price"] / room_total["area"]),
                "minimumSqm": round(room_sqm["price"] / room_sqm["area"]),
                "sourceUrl": room_total["url"], "minimumSourceUrl": room_total["url"],
                "minimumSqmSourceUrl": room_sqm["url"],
            }
        samples = [{**row, "sourceName": "PropertyHub"} for row in cards]
        market = {
            "count": len(cards), "observedCount": len(cards), "platformCount": data["totalCount"],
            "countKind": "manual_verified_listing", "average": round(sum(row["price"] for row in cards) / len(cards)),
            "minimum": lowest_total["price"], "minimumArea": lowest_total["area"],
            "averageSqm": round(sum(row["price"] / row["area"] for row in cards) / len(cards)),
            "minimumSqm": round(lowest_sqm["price"] / lowest_sqm["area"], 2),
            "minimumSampleUpdated": lowest_total.get("updated"), "minimumSqmSampleUpdated": lowest_sqm.get("updated"),
            "asOf": date.today().isoformat(), "snapshotMethod": "Exact PropertyHub project ID 289; all paginated current cards validated against the project ID",
            "sourceName": "PropertyHub 專案單筆掛牌", "source": data["sourceUrl"],
            "minimumSourceUrl": lowest_total["url"], "minimumSqmSourceUrl": lowest_sqm["url"],
            "byBedroom": by_bedroom, "samples": samples,
        }
        ph[kind] = market
        manual[kind] = market
        manual["replace" + kind.title()] = True
        report_markets[kind] = {
            "activeListingCards": len(cards), "projectPageCount": data["totalCount"],
            "lowestTotal": {"price": lowest_total["price"], "areaSqm": lowest_total["area"], "bedrooms": lowest_total.get("beds"), "url": lowest_total["url"]},
            "lowestPricePerSqm": {"pricePerSqm": round(lowest_sqm["price"] / lowest_sqm["area"]), "url": lowest_sqm["url"]},
            "byBedroom": by_bedroom,
        }

    project_url = f"https://propertyhub.in.th/en/projects/{PROJECT_SLUG}"
    sale_url = f"https://propertyhub.in.th/en/condo-for-sale/project-{PROJECT_SLUG}"
    rent_url = f"https://propertyhub.in.th/en/condo-for-rent/project-{PROJECT_SLUG}"
    info = project_data.get("projectInfo") or {}
    project_fields = {
        "propertyHubProjectId": PROPERTYHUB_ID, "propertyHubProjectUrl": project_url,
        "propertyHubSaleUrl": sale_url, "propertyHubRentUrl": rent_url,
        "lat": lat, "lng": lng, "locationVerified": True,
        "locationSourceName": "PropertyHub 精確專案頁地圖", "locationSourceUrl": project_url,
        "locationVerificationSourceUrl": HIPFLAT_URL,
        "completedYear": int(info["completedYear"]), "completedYearSourceUrl": project_url,
        "units": int(info["totalUnits"]), "floors": int(info["buildingsFloors"]),
        "fee": {"rate": float(info["utilityFee"]), "status": "published_indicative", "note": "PropertyHub 專案頁公布管理費，請向管委會確認。", "source": project_url},
        "propertyHubMappingEvidence": "PropertyHub ID 289 names the project Keyne and lists Keyne by Sansiri as an alternate name; the exact district and Sukhumvit 36 address match Hipflat project 3086.",
    }
    ph.update(project_fields)
    map_rows = exact.arr("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    for row in map_rows:
        if int(row["id"]) == HIPFLAT_ID:
            row.update(project_fields)
            row["name"] = project["name"]

    detail_rows = exact.arr("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS")
    detail = next((row for row in detail_rows if str(row.get("propertyHubProjectId")) == PROPERTYHUB_ID), {})
    detail.update({"hipflatProjectId": HIPFLAT_ID, "propertyHubProjectId": PROPERTYHUB_ID, "name": project["name"], "projectName": "Keyne", "projectAddress": project_data.get("address"), **project_fields, "asOf": date.today().isoformat()})
    detail_rows = upsert(detail_rows, "propertyHubProjectId", PROPERTYHUB_ID, detail)

    coordinate_rows = exact.arr("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES")
    coordinate = {"hipflatId": HIPFLAT_ID, "name": project["name"], "lat": lat, "lng": lng, "locationVerified": True, "sourceName": "PropertyHub 精確專案頁地圖座標", "sourceUrl": project_url, "verificationSourceUrl": HIPFLAT_URL, "verificationMethod": "PropertyHub project ID 289 plus alternate name, exact district, and Hipflat project address"}
    coordinate_rows = upsert(coordinate_rows, "hipflatId", HIPFLAT_ID, coordinate)

    save_rows("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS", ph_rows)
    save_rows("bangkok-propertyhub-map.js", "BANGKOK_PROPERTYHUB_PROJECTS", map_rows)
    save_rows("bangkok-manual-market-samples.js", "BANGKOK_MANUAL_MARKET_SAMPLES", upsert(manual_rows, "hipflatId", HIPFLAT_ID, manual))
    save_rows("bangkok-propertyhub-details.js", "BANGKOK_PROPERTYHUB_DETAILS", detail_rows)
    save_rows("bangkok-verified-coordinates.js", "BANGKOK_VERIFIED_COORDINATES", coordinate_rows)
    sale_two = report_markets["sale"]["byBedroom"].get("2")
    rent_two = report_markets["rent"]["byBedroom"].get("2")
    yield_estimate = {"status": "not_calculated", "reason": "No matched two-bedroom sale and rent samples."}
    if sale_two and rent_two:
        purchase = float(sale_two["minimum"])
        area = float(sale_two["area"])
        monthly_rent = float(rent_two["minimumSqm"]) * area
        fee_rate = float(info.get("utilityFee") or 0)
        fee_year = fee_rate * area * 12
        yield_estimate = {
            "status": "calculated_estimate", "bedrooms": 2, "purchasePrice": purchase,
            "saleAreaSqm": area, "saleSourceUrl": sale_two["minimumSourceUrl"],
            "rentRatePerSqmMonthly": rent_two["minimumSqm"], "rentSourceUrl": rent_two["minimumSqmSourceUrl"],
            "estimatedMonthlyRent": round(monthly_rent), "managementFeeBahtPerSqmMonthly": fee_rate,
            "netAnnualPercentWithOneAgentMonth": round(((monthly_rent * 11 - fee_year) / purchase) * 100, 2),
            "netAnnualPercentWithoutAgentMonth": round(((monthly_rent * 12 - fee_year) / purchase) * 100, 2),
            "formula": "((two-bedroom minimum-rent ฿/sqm × lowest two-bedroom sale area × (12 − agent months)) − annual common fee) ÷ lowest two-bedroom sale total × 100",
        }
    REPORT.write_text(json.dumps({"hipflatId": HIPFLAT_ID, "projectName": project["name"], "propertyHubProjectId": PROPERTYHUB_ID, "propertyHubName": "Keyne", "alternateName": "Keyne by Sansiri", "projectSourceUrl": project_url, "coordinate": {"lat": lat, "lng": lng, "sourceUrl": project_url, "crossCheckUrl": HIPFLAT_URL}, "completionYear": info.get("completedYear"), "floors": info.get("buildingsFloors"), "units": info.get("totalUnits"), "feeBahtPerSqmMonthly": info.get("utilityFee"), "markets": report_markets, "yieldEstimate": yield_estimate, "checkedAt": date.today().isoformat()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    index_path = DIST / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = html.replace("bangkok-propertyhub-map.js?v=20261019-life-udomsuk-official-completion", "bangkok-propertyhub-map.js?v=20261019-keyne-exact-propertyhub-project")
    html = html.replace("bangkok-propertyhub-details.js?v=20261019-propertyhub-exact-project-matches", "bangkok-propertyhub-details.js?v=20261019-keyne-exact-propertyhub-project")
    html = html.replace("bangkok-manual-market-samples.js?v=20261019-siri-sathorn-exact-rents", "bangkok-manual-market-samples.js?v=20261019-keyne-exact-propertyhub-listings")
    index_path.write_text(html, encoding="utf-8")
    print(json.dumps({"hipflatId": HIPFLAT_ID, "name": project["name"], "coordinate": [lat, lng], "saleCards": report_markets["sale"]["activeListingCards"], "rentCards": report_markets["rent"]["activeListingCards"], "saleMin": report_markets["sale"]["lowestTotal"], "rentMin": report_markets["rent"]["lowestTotal"], "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
