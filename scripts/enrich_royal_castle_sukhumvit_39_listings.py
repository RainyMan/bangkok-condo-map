from __future__ import annotations
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manual_path = root / 'dist' / 'bangkok-manual-market-samples.js'
app_path = root / 'dist' / 'app.js'
index_path = root / 'dist' / 'index.html'
report_path = root / 'reports' / 'royal-castle-sukhumvit-39-listings-2026-10-18.json'

hipflat_id = 3804
name = 'Royal Castle Sukhumvit 39'
sale_url = 'https://propertyhub.in.th/en/listings/2-bed-2-bath-140-sq-m-royal-castle-sukhumvit--b296096a---5890139'
rent_url = 'https://propertyhub.in.th/en/listings/lth13724-condo-for-rent-royal-castle-sukhumvit-110-sqm-2-beds-2-baths-near-bts-phrom-phong-45k-month---5627195'
sale_project_url = 'https://propertyhub.in.th/en/condo-for-sale/project-royal-castle'
rent_project_url = 'https://propertyhub.in.th/en/condo-for-rent/project-royal-castle'
sale_price, sale_area = 15_500_000, 140.0
rent_price, rent_area = 45_000, 110.0
rent_rate = rent_price / rent_area
equivalent_monthly_rent = round(rent_rate * sale_area)
net_yield_after_agent = (equivalent_monthly_rent * 11 / sale_price) * 100

text = manual_path.read_text(encoding='utf-8')
match = re.fullmatch(r'window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);\s*', text, re.S)
if not match:
    raise SystemExit('Unexpected manual market data format')
rows = json.loads(match.group(1))
row = next((item for item in rows if int(item.get('hipflatId', -1)) == hipflat_id), None)
if row is None:
    row = {'hipflatId': hipflat_id, 'name': name, 'asOf': '2026-10-18'}
    rows.append(row)

sale_sample = {
    'id': '5890139', 'price': sale_price, 'area': sale_area, 'priceSqm': round(sale_price / sale_area),
    'beds': 2, 'roomType': 'TWO_BED_ROOM',
    'title': '2 Bed 2 Bath 140 SQ.M. Royal Castle Sukhumvit', 'url': sale_url,
    'sourceName': 'PropertyHub', 'projectName': 'Royal Castle', 'updated': '2026-10-04',
    'checkedAt': '2026-10-18', 'matchedBy': 'PropertyHub exact-project sale page links the listing; direct page identifies Royal Castle, 2 bedrooms, 140 sqm, and ฿15,500,000',
    'listingStatus': 'active_as_listed',
}
rent_sample = {
    'id': '5627195', 'price': rent_price, 'area': rent_area, 'priceSqm': round(rent_rate),
    'beds': 2, 'roomType': 'TWO_BED_ROOM',
    'title': 'LTH13724 · Royal Castle Sukhumvit 39 · 2 bedrooms · 110 sqm · ฿45,000/month',
    'url': rent_url, 'sourceName': 'PropertyHub', 'projectName': 'Royal Castle', 'updated': '2026-10-10',
    'checkedAt': '2026-10-18', 'matchedBy': 'PropertyHub exact-project rent page links the listing; direct page identifies Royal Castle Sukhumvit 39, 2 bedrooms, 110 sqm, and ฿45,000/month',
    'listingStatus': 'active_as_listed',
}

def upsert_market(kind: str, sample: dict) -> None:
    market = row.setdefault(kind, {})
    samples = market.setdefault('samples', [])
    samples[:] = [item for item in samples if str(item.get('id')) != sample['id'] and item.get('url') != sample['url']]
    samples.append(sample)

upsert_market('sale', sale_sample)
upsert_market('rent', rent_sample)
row['asOf'] = '2026-10-18'
manual_path.write_text('window.BANGKOK_MANUAL_MARKET_SAMPLES = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
if "const yieldStorageKey = 'bangkokCondoYieldInputsV76';" not in app:
    raise SystemExit('Expected V76 yield storage key was not found')
app = app.replace("const yieldStorageKey = 'bangkokCondoYieldInputsV76';", "const yieldStorageKey = 'bangkokCondoYieldInputsV77';")
old_fallback = "localStorage.getItem('bangkokCondoYieldInputsV75') ||"
if old_fallback not in app:
    raise SystemExit('Expected yield migration fallback was not found')
app = app.replace(old_fallback, "localStorage.getItem('bangkokCondoYieldInputsV76') || localStorage.getItem('bangkokCondoYieldInputsV75') ||", 1)
app_path.write_text(app, encoding='utf-8')

index = index_path.read_text(encoding='utf-8')
old_cache = 'app.js?v=20261018-two-bedroom-lowest-total-roi-recalc-v76'
if old_cache not in index:
    raise SystemExit('Expected app cache key was not found')
index_path.write_text(index.replace(old_cache, 'app.js?v=20261018-two-bedroom-lowest-total-roi-recalc-v77'), encoding='utf-8')
old_data_cache = 'bangkok-manual-market-samples.js?v=20261018r-lumpini-chaopraya-individual-listings'
if old_data_cache not in index:
    raise SystemExit('Expected manual sample cache key was not found')
index_path.write_text(index_path.read_text(encoding='utf-8').replace(old_data_cache, 'bangkok-manual-market-samples.js?v=20261018s-royal-castle-2br-listings'), encoding='utf-8')

report = {
    'checkedAt': '2026-10-18', 'hipflatId': hipflat_id, 'project': name,
    'propertyHubProjectSaleUrl': sale_project_url, 'propertyHubProjectRentUrl': rent_project_url,
    'sale': {**sale_sample, 'lowestTwoBedroomObservedOnProjectPage': True, 'scopeNote': 'The exact project page showed two two-bedroom sale units at ฿15,500,000 and ฿16,200,000; this is the lower linked two-bedroom total.'},
    'rent': {**rent_sample, 'lowestTwoBedroomCurrentVisibleRentPerSqmOnProjectPage': True, 'rentPerSqmMonthExact': round(rent_rate, 2), 'scopeNote': 'The project page shows the ฿45,000 / 110 sqm two-bedroom listing updated 2026-10-10. A ฿50,000 / 140 sqm two-bedroom card is dated 2026-05-24 and is excluded from the current listing baseline due to age.'},
    'yieldEstimate': {
        'bedrooms': 2, 'purchasePriceThb': sale_price, 'purchaseAreaSqm': sale_area,
        'rentRateThbPerSqmMonth': round(rent_rate, 2), 'estimatedRentAtPurchaseAreaThbPerMonth': equivalent_monthly_rent,
        'annualRentAfterOneAgentMonthThb': equivalent_monthly_rent * 11,
        'yieldAfterOneAgentMonthBeforeUnverifiedCommonFeePercent': round(net_yield_after_agent, 2),
        'commonFeeDeducted': False,
        'formula': '(45,000 / 110 × 140 × 11) / 15,500,000 × 100',
        'limitations': ['Direct listing pages show no Last Update timestamp; project pages list the sale and rent cards as updated on 2026-10-04 and 2026-10-10 respectively.', 'Live availability is not independently confirmed with advertisers.', 'No verified project management fee was found; estimate excludes common fee, vacancy, tax, repairs, and transaction costs.']
    }
}
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'hipflatId': hipflat_id, 'salePrice': sale_price, 'saleArea': sale_area, 'rentPerSqmMonth': round(rent_rate, 2), 'estimatedRentAtSaleArea': equivalent_monthly_rent, 'netYieldAfterOneAgentMonthBeforeFee': round(net_yield_after_agent, 2), 'saleUrl': sale_url, 'rentUrl': rent_url}, ensure_ascii=False))
