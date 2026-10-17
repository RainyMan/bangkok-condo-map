"""Download BMA's public type-6 building/address attributes by district."""
from __future__ import annotations

import json
import pathlib
import time

import requests

URL = "http://3d-cpd.bangkok.go.th/ArcGIS/rest/services/BMA3D_3DService/MapServer/25/query"
OUTPUT = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok\bma-type6-addresses.jsonl")
FIELDS = ",".join((
    "OBJECTID", "BLDG_ID", "BL_TYPE", "BL_ACT_NAME", "BL_NSTOREY", "BL_NUNIT", "BL_NAME",
    "BL_HOUSENUM", "BL_VILLNUM", "BL_VILLAGE", "BL_ROAD", "BL_SOI", "BL_SUB_DISTRICT",
    "BL_DISTRICT", "BL_CHANGWAT", "BL_POSTCODE", "BL_ADDRESS", "BL_DATE", "UPDATE_YEAR",
))
DISTRICTS = {
    "Pom Prap Sattru Phai": "ป้อมปราบศัตรูพ่าย", "Thawi Watthana": "ทวีวัฒนา", "Khlong Sam Wa": "คลองสามวา",
    "Bang Khun Thian": "บางขุนเทียน", "Bang Kho Laem": "บางคอแหลม", "Saphan Sung": "สะพานสูง",
    "Bangkok Yai": "บางกอกใหญ่", "Bangkok Noi": "บางกอกน้อย", "Phaya Thai": "พญาไท", "Phra Khanong": "พระโขนง",
    "Ratchathewi": "ราชเทวี", "Samphanthawong": "สัมพันธวงศ์", "Wang Thonglang": "วังทองหลาง",
    "Huai Khwang": "ห้วยขวาง", "Khan Na Yao": "คันนายาว", "Lat Krabang": "ลาดกระบัง", "Bueng Kum": "บึงกุ่ม",
    "Chom Thong": "จอมทอง", "Don Mueang": "ดอนเมือง", "Nong Chok": "หนองจอก", "Nong Khaem": "หนองแขม",
    "Pathum Wan": "ปทุมวัน", "Phasi Charoen": "ภาษีเจริญ", "Phra Nakhon": "พระนคร", "Rat Burana": "ราษฎร์บูรณะ",
    "Taling Chan": "ตลิ่งชัน", "Thung Khru": "ทุ่งครุ", "Bang Kapi": "บางกะปิ", "Bang Khae": "บางแค",
    "Bang Khen": "บางเขน", "Bang Na": "บางนา", "Bang Phlat": "บางพลัด", "Bang Rak": "บางรัก",
    "Bang Sue": "บางซื่อ", "Chatuchak": "จตุจักร", "Din Daeng": "ดินแดง", "Dusit": "ดุสิต",
    "Khlong San": "คลองสาน", "Khlong Toei": "คลองเตย", "Lak Si": "หลักสี่", "Lat Phrao": "ลาดพร้าว",
    "Min Buri": "มีนบุรี", "Prawet": "ประเวศ", "Sai Mai": "สายไหม", "Sathon": "สาทร",
    "Suan Luang": "สวนหลวง", "Thon Buri": "ธนบุรี", "Yan Nawa": "ยานนาวา", "Bang Bon": "บางบอน",
    "Watthana": "วัฒนา", "Bangkok": "กรุงเทพมหานคร",
}


def request(session: requests.Session, params: dict) -> dict:
    for attempt in range(4):
        try:
            response = session.get(URL, params={**params, "f": "json"}, timeout=(10, 40))
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data
        except (requests.RequestException, ValueError, RuntimeError):
            if attempt == 3:
                raise
            time.sleep(1 + attempt)
    raise RuntimeError("request attempts exhausted")


def fetch_range(session: requests.Session, district: str, low: int, high: int, output: list[dict]) -> int:
    where = f"BL_TYPE='6' AND BL_DISTRICT='{district}' AND OBJECTID > {low} AND OBJECTID <= {high}"
    count = int(request(session, {"where": where, "returnCountOnly": "true"}).get("count", 0))
    if not count:
        return 0
    if count <= 950:
        rows = request(session, {"where": where, "outFields": FIELDS, "returnGeometry": "false"}).get("features", [])
        output.extend(row["attributes"] for row in rows)
        return len(rows)
    midpoint = (low + high) // 2
    return fetch_range(session, district, low, midpoint, output) + fetch_range(session, district, midpoint, high, output)


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = "BangkokCondoMapResearch/1.0 (public BMA GIS data)"
    rows: dict[int, dict] = {}
    for index, (english, thai) in enumerate(DISTRICTS.items(), 1):
        district_rows: list[dict] = []
        count = fetch_range(session, thai, 0, 3_000_000, district_rows)
        for row in district_rows:
            rows[int(row["OBJECTID"])] = row
        print(f"{index}/{len(DISTRICTS)} {english}: {count} buildings; total {len(rows)}", flush=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows.values()), encoding="utf-8")
    print(f"Saved {len(rows)} unique building/address records to {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
