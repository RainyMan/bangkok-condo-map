from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

def load_array(filename: str, var: str):
    path = DIST / filename
    text = path.read_text(encoding='utf-8')
    match = re.search(rf'window\.{re.escape(var)}\s*=\s*(\[.*\]);', text)
    if not match:
        raise RuntimeError(f'Cannot parse {filename}')
    return path, text[:match.start(1)], json.loads(match.group(1)), text[match.end(1):]

def save_array(data):
    path, prefix, rows, suffix = data
    path.write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + suffix, encoding='utf-8')

sale_url = 'https://propertyscout.co.th/en/bangkok/bts/nana/sales/condo/1-bedroom/page-2/'
sale_detail = 'https://propertyscout.co.th/en/1-br-condo-nana-condo-near-bts-nana-2778746/'
rent_url = 'https://propertyscout.co.th/en/1-br-condo-nana-condo-near-bts-nana-3224759/'
ph_sale = 'https://propertyhub.in.th/en/condo-for-sale/project-nana-condo'
ph_rent = 'https://propertyhub.in.th/en/condo-for-rent/project-nana-condo'

sample_sale = {
    'id': '2778746', 'price': 1890000, 'area': 29, 'priceSqm': 65172, 'beds': 1, 'roomType': '1BR',
    'title': 'Nana Condo 1 bedroom 29 sqm ฿1,890,000', 'url': sale_detail, 'sourceName': 'PropertyScout',
    'projectName': 'Nana Condo', 'updated': '2026-08', 'checkedAt': '2026-10-19',
    'matchedBy': 'exact_project_name_and_listing_detail', 'listingStatus': 'availability_unconfirmed_update_over_30d'
}
sample_rent = {
    'id': '3224759', 'price': 13000, 'area': 28, 'priceSqm': 464, 'beds': 1, 'roomType': '1BR',
    'title': 'Nana Condo 1 bedroom 28 sqm ฿13,000/month', 'url': rent_url, 'sourceName': 'PropertyScout',
    'projectName': 'Nana Condo', 'updated': '2026-10-14', 'checkedAt': '2026-10-19',
    'matchedBy': 'exact_project_name_and_listing_detail', 'listingStatus': 'confirmed_available_within_7d'
}
manual = load_array('bangkok-manual-market-samples.js', 'BANGKOK_MANUAL_MARKET_SAMPLES')
manual_rows = manual[2]
record = next((row for row in manual_rows if int(row['hipflatId']) == 3127), None)
if not record:
    raise RuntimeError('Nana Condo record not found')
record['replaceSale'] = True
record['sale'] = {
    'count': 0, 'observedCount': 0, 'countKind': 'availability_unconfirmed', 'asOf': '2026-10-19',
    'sourceName': 'PropertyScout / PropertyHub 專案核對', 'source': sale_url,
    'samples': [], 'byBedroom': {}
}
record['replaceRent'] = True
record['rent'] = {
    'count': 1, 'observedCount': 1, 'countKind': 'manual_verified_listing', 'average': 13000,
    'minimum': 13000, 'minimumArea': 28, 'minimumSampleUpdated': '2026-10-14', 'averageSqm': 464,
    'minimumSqm': 464, 'minimumSqmSampleUpdated': '2026-10-14', 'asOf': '2026-10-19',
    'sourceName': 'PropertyScout 單筆房源', 'source': rent_url, 'minimumSourceUrl': rent_url,
    'minimumSqmSourceUrl': rent_url, 'samples': [sample_rent],
    'byBedroom': {'1': {'count': 1, 'minimum': 13000, 'area': 28, 'priceSqm': 464,
                        'minimumSqm': 464, 'sourceUrl': rent_url, 'minimumSqmSourceUrl': rent_url}}
}
save_array(manual)

cross = load_array('bangkok-market-crosschecks.js', 'BANGKOK_MARKET_CROSSCHECKS')
rows = cross[2]
cc = {
    'hipflatId': 3127, 'projectName': 'Nana Condo', 'asOf': '2026-10-19',
    'sourceName': 'PropertyScout / PropertyHub 多平台核對', 'projectSourceUrl': 'https://www.hipflat.co.th/en/projects/nana-condo-setbyl',
    'sale': {'activeListingCount': 0, 'listings': [{'url': sale_detail, 'price': 1890000, 'area': 29, 'bedrooms': 1,
              'priceSqm': 65172, 'listedAt': '2026-03-01', 'statusLabel': '直接房源頁顯示約 2 個月前確認；列作過期樣本，不用於投報'}],
             'sourceUrl': sale_url, 'note': '目前未取得可直接核實現行狀態的 2 房出售物件頁；可追溯的 1 房 ฿1.89M 樣本頁約 2 個月前更新，保留歷史參考但不作投報基準。PropertyHub 專案頁未列目前出售物件。'},
    'rent': {'activeListingCount': 1, 'listings': [{'url': rent_url, 'price': 13000, 'area': 28, 'bedrooms': 1,
              'priceSqm': 464, 'listedAt': '2026-07-23', 'statusLabel': 'PropertyScout 5 天前確認仍可出租'}],
             'sourceUrl': rent_url, 'note': '保留直接房源頁確認仍可出租的 1 房樣本。PropertyHub 頁另外列出 2 筆租盤，其中一筆標示 11 樓，與專案資料 8 樓不符，未併入樣本。'},
    'availabilitySources': [
        {'sourceName': 'PropertyScout 出售頁', 'url': sale_url, 'statusLabel': '有 1 房掛牌；尚無現行可核實 2 房售價。'},
        {'sourceName': 'PropertyScout 出售單筆', 'url': sale_detail, 'statusLabel': '฿1,890,000 · 29㎡ · 1 房；頁面約 2 個月前更新，僅供歷史參考。'},
        {'sourceName': 'PropertyScout 出租單筆', 'url': rent_url, 'statusLabel': '฿13,000／月 · 28㎡ · 1 房；5 天前確認可租。'},
        {'sourceName': 'PropertyHub 出售專案頁', 'url': ph_sale, 'statusLabel': '目前頁面未列出售物件。'},
        {'sourceName': 'PropertyHub 出租專案頁', 'url': ph_rent, 'statusLabel': '頁面列 2 筆；其中 11 樓資料與 8 層樓專案資訊矛盾，未納入本次樣本。'},
    ],
    'yieldStatus': 'two_bedroom_sale_missing',
    'yieldNote': '目前沒有可核實的現行 2 房出售樣本，因此預設兩房年投報率不計算；不可使用過期的 2 房售價摘要。若切換到有現行售租樣本的房型，可另行估算。'
}
rows = [row for row in rows if int(row['hipflatId']) != 3127]
rows.append(cc)
rows.sort(key=lambda row: int(row['hipflatId']))
cross = (cross[0], cross[1], rows, cross[3])
save_array(cross)

index = DIST / 'index.html'
text = index.read_text(encoding='utf-8')
text = re.sub(r'bangkok-manual-market-samples\.js\?v=[^"\']+', 'bangkok-manual-market-samples.js?v=20261019-nana-current-samples-v2', text, count=1)
text = re.sub(r'bangkok-market-crosschecks\.js\?v=[^"\']+', 'bangkok-market-crosschecks.js?v=20261019-nana-sale-rent-check-v2', text, count=1)
text = re.sub(r'app\.js\?v=[^"\']+', 'app.js?v=20261019-yield-recalculation-v178', text, count=1)
index.write_text(text, encoding='utf-8')

app = DIST / 'app.js'
text = app.read_text(encoding='utf-8')
text = text.replace("bangkokCondoYieldInputsV173", "bangkokCondoYieldInputsV174")
text = text.replace("for (let version = 172; version >= 5; version--)", "for (let version = 173; version >= 5; version--)")
app.write_text(text, encoding='utf-8')

print(json.dumps({'project': record['name'], 'saleSample': sample_sale, 'rentSample': sample_rent, 'crosscheck': cc}, ensure_ascii=True))

