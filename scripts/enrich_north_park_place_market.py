from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
CHECKED = '2026-10-18'
HIPFLAT_SALE_RENT = 'https://www.hipflat.co.th/en/ads/4t8eth498ae12a9t904c3t243ul33ah0'
THAIHOME_SALE = 'https://www.thaihometown.com/%EF%BF%BD%CD%B9%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%CA%B9%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD-%EF%BF%BD%EF%BF%BD%EF%BF%BD%C3%B6%E4%BF%BF%EF%BF%BD%EF%BF%BD-%EF%BF%BD%CD%B9%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%D4%B7%EF%BF%BD%EF%BF%BD%EF%BF%BD-%EF%BF%BD%EF%BF%BD%EF%BF%BD%C3%B6%E4%BF%BF%EF%BF%BD%EF%BF%BD-5239010.html'
PH_PROJECT = 'https://propertyhub.in.th/en/projects/north-park-place'
PROJECT_ID = 6498
PROJECT_NAME = 'North Park Place'


def load_array(filename: str, symbol: str) -> list[dict]:
    path = DIST / filename
    match = re.search(rf'window\.{symbol}\s*=\s*(\[.*\]);', path.read_text(encoding='utf-8'), re.S)
    if not match:
        raise RuntimeError(f'Could not parse {symbol}')
    return json.loads(match.group(1))


def save_array(filename: str, symbol: str, rows: list[dict]) -> None:
    (DIST / filename).write_text(
        f'window.{symbol} = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n',
        encoding='utf-8',
    )

# Include both the lower legacy listing and the more recently refreshed Hipflat unit.
# The lower item is retained as an observation, but explicitly marked stale/unconfirmed.
old_listing = {
    'id': '5239010', 'price': 13_900_000, 'area': 175.36,
    'priceSqm': round(13_900_000 / 175.36), 'beds': 2, 'roomType': '2BR',
    'title': 'ขายคอนโด North Park Place 2 ห้องนอน 175.36 ตร.ม. (ประกาศ 13 ก.ค. 2569)',
    'url': THAIHOME_SALE, 'sourceName': 'ThaiHometown', 'projectName': PROJECT_NAME,
    'updated': '2026-07-13', 'checkedAt': CHECKED,
    'matchedBy': 'listing_text_names_North_Park_Place_and_address_Tha_Sai_1_Thung_Song_Hong_Lak_Si',
    'listingStatus': 'availability_unconfirmed_update_over_30d',
}
current_sale = {
    'id': 'U6680163', 'price': 18_500_000, 'area': 167,
    'priceSqm': round(18_500_000 / 167), 'beds': 2, 'roomType': '2BR',
    'title': 'For sale and for rent 2 bedrooms condo in Lak Si, Bangkok · U6680163',
    'url': HIPFLAT_SALE_RENT, 'sourceName': 'Hipflat', 'projectName': PROJECT_NAME,
    'updated': CHECKED, 'checkedAt': CHECKED,
    'matchedBy': 'Hipflat_direct_ad_names_North_Park_Place_and_lists_2_bed_167_sqm_sale_price_and_rent',
    'listingStatus': 'active_as_listed',
}
current_rent = {
    'id': 'U6680163', 'price': 55_000, 'area': 167,
    'priceSqm': round(55_000 / 167), 'beds': 2, 'roomType': '2BR',
    'title': 'For sale and for rent 2 bedrooms condo in Lak Si, Bangkok · U6680163',
    'url': HIPFLAT_SALE_RENT, 'sourceName': 'Hipflat', 'projectName': PROJECT_NAME,
    'updated': CHECKED, 'checkedAt': CHECKED,
    'matchedBy': 'Hipflat_direct_ad_names_North_Park_Place_and_lists_2_bed_167_sqm_rent_55000_per_month',
    'listingStatus': 'active_as_listed',
}

sales = [old_listing, current_sale]
lowest = min(sales, key=lambda row: row['price'])
rate_low = round(lowest['price'] / lowest['area'])
sale_market = {
    'count': len(sales), 'observedCount': len(sales),
    'countKind': 'manual_verified_individual_listing_with_stale_status_flagged',
    'average': round(sum(row['price'] for row in sales) / len(sales)),
    'minimum': lowest['price'], 'minimumArea': lowest['area'],
    'minimumSampleUpdated': lowest['updated'],
    'averageSqm': round(sum(row['priceSqm'] for row in sales) / len(sales)),
    'minimumSqm': rate_low, 'minimumSqmSampleUpdated': lowest['updated'],
    'asOf': CHECKED, 'sourceName': 'Hipflat 與 ThaiHometown 個別出售掛牌',
    'source': 'https://www.hipflat.co.th/en/projects/north-park-place-iqoecm',
    'minimumSourceUrl': lowest['url'], 'minimumSqmSourceUrl': lowest['url'],
    'byBedroom': {'2': {
        'count': 2, 'minimum': lowest['price'], 'area': lowest['area'],
        'priceSqm': rate_low, 'minimumSqm': rate_low,
        'sourceUrl': lowest['url'], 'minimumSqmSourceUrl': lowest['url'],
    }},
    'samples': sales,
}

manual_path = DIST / 'bangkok-manual-market-samples.js'
manual = load_array(manual_path.name, 'BANGKOK_MANUAL_MARKET_SAMPLES')
record = next((row for row in manual if int(row.get('hipflatId', -1)) == PROJECT_ID), None)
if record is None:
    record = {'hipflatId': PROJECT_ID, 'name': PROJECT_NAME}
    manual.append(record)
record.update({
    'asOf': CHECKED, 'replaceSale': True, 'sale': sale_market,
    'rent': {'samples': [current_rent]},
})
manual.sort(key=lambda row: int(row['hipflatId']))
save_array(manual_path.name, 'BANGKOK_MANUAL_MARKET_SAMPLES', manual)

# The PropertyHub project page directly states common fee of 45 THB/sqm and 2010 completion.
ph_details_path = DIST / 'bangkok-propertyhub-details.js'
ph_details = load_array(ph_details_path.name, 'BANGKOK_PROPERTYHUB_DETAILS')
ph_project = next(row for row in ph_details if str(row.get('propertyHubProjectId')) == '204')
ph_project['fee'] = {
    'rate': 45, 'note': 'PropertyHub 專案頁公開管理費數值；目前費率仍請向管委會確認。',
    'source': PH_PROJECT, 'status': 'published_indicative',
}
save_array(ph_details_path.name, 'BANGKOK_PROPERTYHUB_DETAILS', ph_details)

availability_path = ROOT / 'reports' / 'listing-availability-checks-2026-10-18.csv'
with availability_path.open('r', newline='', encoding='utf-8-sig') as source:
    reader = csv.DictReader(source)
    fields = reader.fieldnames or []
    rows = [row for row in reader if not (row.get('hipflat_id') == str(PROJECT_ID) and row.get('market') in {'sale', 'rent'})]
rows.extend([
    {'hipflat_id': str(PROJECT_ID), 'condo': PROJECT_NAME, 'checked_at': CHECKED, 'market': 'sale',
     'status': 'availability_unconfirmed_update_over_30d',
     'verification_note': 'ThaiHometown listing #5239010 states 2 bedrooms, 175.36 sqm, THB 13.9m and was posted 13 July 2026. Page remains available but is over 30 days old; availability is unconfirmed. A Hipflat direct listing U6680163, 2 bedrooms, 167 sqm, THB 18.5m, was refreshed within the last day.',
     'source_1': THAIHOME_SALE, 'source_2': HIPFLAT_SALE_RENT, 'source_3': PH_PROJECT},
    {'hipflat_id': str(PROJECT_ID), 'condo': PROJECT_NAME, 'checked_at': CHECKED, 'market': 'rent',
     'status': 'active_as_listed',
     'verification_note': 'Hipflat direct listing U6680163 explicitly offers the same 2-bedroom, 167 sqm unit for rent at THB 55,000/month and showed an update within the last day. PropertyHub also has separate 2-bedroom rental listings; their individual pages omit a last-update date.',
     'source_1': HIPFLAT_SALE_RENT, 'source_2': 'https://propertyhub.in.th/en/listings/condo-for-rent-north-park-place-live-like-5-star-hotel-free-wi-fi-and-maid-099-998-3897---2966490', 'source_3': PH_PROJECT},
])
with availability_path.open('w', newline='', encoding='utf-8-sig') as output:
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader(); writer.writerows(rows)

# Keep the source evidence and transparent ROI calculation alongside coverage reports.
# Rent low per sqm comes from the existing 2BR PropertyHub source (85,000 / 269 = 316).
rent_sqm_low = 316
purchase = lowest['price']; area = lowest['area']
monthly_rent_estimate = round(rent_sqm_low * area)
net_yield = round(((monthly_rent_estimate * 11) - (45 * area * 12)) / purchase * 100, 2)
report = {
    'hipflatId': PROJECT_ID, 'project': PROJECT_NAME, 'checkedAt': CHECKED,
    'sources': {'project': 'https://www.hipflat.co.th/en/projects/north-park-place-iqoecm', 'managementFee': PH_PROJECT,
                'saleLowest': THAIHOME_SALE, 'saleRecent': HIPFLAT_SALE_RENT, 'rentRecent': HIPFLAT_SALE_RENT,
                'rentLowestPerSqm': 'https://propertyhub.in.th/en/listings/condo-168-sq-m-for-rent-north-park-place-live-like-5-star-hotel-free-wi-fi-and-maid--ac3a091a---2966511'},
    'saleSamples': sales,
    'rentSample': current_rent,
    'yieldEstimate': {'bedrooms': 2, 'purchasePrice': purchase, 'purchaseAreaSqm': area,
                      'rentLowPerSqmPerMonth': rent_sqm_low, 'estimatedMonthlyRent': monthly_rent_estimate,
                      'annualRentAfterOneAgentMonth': monthly_rent_estimate * 11,
                      'annualCommonFee': round(45 * area * 12), 'netYieldPercent': net_yield,
                      'note': 'Uses the lowest observed linked two-bedroom sale listing; its availability is unconfirmed because the posted listing is over 30 days old.'},
}
(ROOT / 'reports' / 'north-park-place-enrichment-2026-10-18.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'project': PROJECT_NAME, 'saleSamples': len(sales), 'lowestSale': lowest['price'], 'lowestSaleArea': lowest['area'], 'saleBahtPerSqm': rate_low, 'rentSample': current_rent['price'], 'rentBahtPerSqm': current_rent['priceSqm'], 'estimatedNetYieldPercent': net_yield}, ensure_ascii=False))
