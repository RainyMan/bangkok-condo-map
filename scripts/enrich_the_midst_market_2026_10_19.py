from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PROJECT_ID = 3087
NAME = 'The Midst Condo'
AS_OF = '2026-10-19'
PH_PROJECT = 'https://propertyhub.in.th/en/projects/the-midst-condo'
PH_SALE = 'https://propertyhub.in.th/en/condo-for-sale/project-the-midst-condo'
PH_RENT = 'https://propertyhub.in.th/en/condo-for-rent/project-the-midst-condo'
RENT_URL = 'https://www.fazwaz.com/property-rent/1-bedroom-condo-for-rent-at-the-midst-condo-in-chantharakasem-bangkok-u6729242'
DD_OLDER_SALE = 'https://www.ddproperty.com/property/%25E0%25B9%2580%25E0%25B8%2594%25E0%25B8%25AD%25E0%25B8%25B0-%25E0%25B8%25A1%25E0%25B8%25B4%25E0%25B8%25AA%25E0%25B8%2597%25E0%25B9%258C-%25E0%25B8%2584%25E0%25B8%25AD%25E0%25B8%2599%25E0%25B9%2582%25E0%25B8%2594-%25E0%25B8%2581%25E0%25B8%25A3%25E0%25B8%25B8%25E0%25B8%2587%25E0%25B9%2580%25E0%25B8%2597%25E0%25B8%259E-%25E0%25B8%2582%25E0%25B8%25B2%25E0%25B8%25A2-500277870'
def load(name, symbol):
    p = DIST / name
    m = re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);', p.read_text(encoding='utf-8'), re.S)
    if not m: raise RuntimeError(f'Missing {symbol}')
    return json.loads(m.group(1))
def save(name, symbol, rows):
    (DIST / name).write_text(f'window.{symbol} = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
rent_sample = {
    'id': 'U6729242', 'price': 10000, 'area': 28.8, 'priceSqm': 347,
    'beds': 1, 'roomType': '1 Bedroom',
    'title': '1 Bedroom Condo for rent at The Midst Condo · 28.80 sqm · ฿10,000/month',
    'url': RENT_URL, 'sourceName': 'FazWaz', 'projectName': NAME,
    'updated': AS_OF, 'checkedAt': AS_OF,
    'matchedBy': 'direct_listing_names_The_Midst_Condo_and_identifies_Chantharakasem_project_and_28_80sqm_unit',
    'listingStatus': 'availability_unconfirmed_update_under_30d',
}
manual = load('bangkok-manual-market-samples.js', 'BANGKOK_MANUAL_MARKET_SAMPLES')
entry = next((row for row in manual if int(row.get('hipflatId', -1)) == PROJECT_ID), None)
if entry is None:
    entry = {'hipflatId': PROJECT_ID, 'name': NAME}
    manual.append(entry)
rent = entry.setdefault('rent', {})
samples = rent.setdefault('samples', [])
samples[:] = [sample for sample in samples if sample.get('url') != RENT_URL]
samples.append(rent_sample)
rent.update({
    'count': max(1, int(rent.get('count') or 0)), 'observedCount': max(1, int(rent.get('observedCount') or 0)),
    'countKind': 'manual_verified_listing', 'minimum': 10000, 'minimumArea': 28.8,
    'minimumSampleUpdated': AS_OF, 'minimumSqm': 347, 'minimumSqmSampleUpdated': AS_OF,
    'average': 10000, 'averageSqm': 347, 'asOf': AS_OF,
    'sourceName': 'FazWaz 直接出租掛牌（U6729242）', 'source': PH_RENT,
    'minimumSourceUrl': RENT_URL, 'minimumSqmSourceUrl': RENT_URL,
})
entry['asOf'] = AS_OF
manual.sort(key=lambda row: int(row['hipflatId']))
save('bangkok-manual-market-samples.js', 'BANGKOK_MANUAL_MARKET_SAMPLES', manual)
crosschecks = load('bangkok-market-crosschecks.js', 'BANGKOK_MARKET_CROSSCHECKS')
cross = next((row for row in crosschecks if int(row.get('hipflatId', -1)) == PROJECT_ID), None)
if cross is None:
    cross = {'hipflatId': PROJECT_ID, 'projectName': NAME}
    crosschecks.append(cross)
cross.update({
    'projectName': NAME, 'asOf': AS_OF, 'sourceName': 'PropertyHub', 'projectSourceUrl': PH_PROJECT,
    'sale': {'activeListingCount': 0, 'sourceUrl': PH_SALE, 'listings': []},
    'rent': {'activeListingCount': 2, 'sourceUrl': PH_RENT, 'listings': [rent_sample]},
    'availabilitySources': [
        {'sourceName': 'PropertyHub 出售專案頁', 'url': PH_SALE, 'statusLabel': '目前顯示 0 筆出售物件'},
        {'sourceName': 'PropertyHub 出租專案頁', 'url': PH_RENT, 'statusLabel': '頁面列有 2 筆出租物件'},
        {'sourceName': 'FazWaz 直接出租物件 U6729242', 'url': RENT_URL, 'statusLabel': '1 房、28.80㎡、฿10,000/月；本次查核可開啟，頁面顯示可立即入住'},
        {'sourceName': 'DDproperty 較早出售物件頁', 'url': DD_OLDER_SALE, 'statusLabel': '頁面列 22㎡、฿2,826,240，刊登日期 2026-04-29；超過 30 日且現售狀態未確認，未納入現售行情與投報'},
    ],
})
crosschecks.sort(key=lambda row: int(row['hipflatId']))
save('bangkok-market-crosschecks.js', 'BANGKOK_MARKET_CROSSCHECKS', crosschecks)
report = {
    'hipflatId': PROJECT_ID, 'project': NAME, 'checkedAt': AS_OF,
    'rent': rent_sample,
    'sale': {
        'status': 'no_confirmed_current_listing', 'source': PH_SALE,
        'historicalLead': {'price': 2826240, 'area': 22, 'priceSqm': 128465, 'url': DD_OLDER_SALE, 'listedAt': '2026-04-29', 'listingStatus': 'availability_unconfirmed_update_over_30d'},
        'note': 'DDproperty item is retained as an older lead only; the current PropertyHub sale project page shows no matched properties. It is excluded from current ROI inputs.',
    },
    'yield': {'status': 'not_calculable', 'reason': 'No confirmed current sale listing for the project; the older DDproperty item has unconfirmed availability.'},
    'sources': {'propertyHubProject': PH_PROJECT, 'propertyHubSale': PH_SALE, 'propertyHubRent': PH_RENT, 'directRentListing': RENT_URL},
    'identityCheck': 'The direct rent page identifies The Midst Condo in Chantharakasem; nearby condo listings and unrelated The Midst projects were excluded.',
}
(ROOT / 'reports' / 'the-midst-market-enrichment-2026-10-19.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
index = (DIST / 'index.html').read_text(encoding='utf-8')
index, n1 = re.subn(r'bangkok-manual-market-samples\.js\?v=[^"\']+', 'bangkok-manual-market-samples.js?v=20261019-the-midst-rent-sample', index, count=1)
index, n2 = re.subn(r'bangkok-market-crosschecks\.js\?v=[^"\']+', 'bangkok-market-crosschecks.js?v=20261019-the-midst-availability', index, count=1)
if n1 != 1 or n2 != 1: raise RuntimeError('Could not update cache keys')
(DIST / 'index.html').write_text(index, encoding='utf-8')
print(json.dumps({'project': NAME, 'rent': '1 direct sample added', 'currentSale': 'no confirmed listings', 'yield': 'not calculable', 'report': 'reports/the-midst-market-enrichment-2026-10-19.json'}, ensure_ascii=False))
