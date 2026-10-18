from __future__ import annotations
import csv, json, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
REPORTS = ROOT / 'reports'
PROJECT_ID = 4064
NAME = 'D.D. Tower'
CHECKED = '2026-10-18'
COORD = (13.7740501, 100.5613139)
OSM_URL = 'https://www.openstreetmap.org/way/333223536'
PH_URL = 'https://propertyhub.in.th/en/projects/d-d-tower'
HIPFLAT_URL = 'https://www.hipflat.co.th/en/projects/dd-tower-pkedkj'
RENT_URL = 'https://www.ddproperty.com/en/property/d-d-tower-bangkok-for-rent-500560873'

def load_array(filename: str, symbol: str) -> tuple[Path, list[dict]]:
    path = DIST / filename
    match = re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);', path.read_text(encoding='utf-8'), re.S)
    if not match:
        raise ValueError(f'Missing {symbol} in {path}')
    return path, json.loads(match.group(1))

def save_array(path: Path, symbol: str, rows: list[dict]) -> None:
    path.write_text(f'window.{symbol} = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')

# Coordinate evidence: OSM's named building point resolves to D.D. Tower, Soi Prachasongkhro 20, Din Daeng 10400.
coord_path, coords = load_array('bangkok-verified-coordinates.js', 'BANGKOK_VERIFIED_COORDINATES')
coord_record = {
    'hipflatId': PROJECT_ID, 'name': NAME, 'lat': COORD[0], 'lng': COORD[1], 'locationVerified': True,
    'sourceName': 'OpenStreetMap 具名建築點位', 'sourceUrl': OSM_URL,
    'verificationSourceUrl': PH_URL,
    'verificationMethod': 'OSM_named_building_DD_Tower_address_Soi_Prachasongkhro_20_Din_Daeng_cross_checked_against_exact_PropertyHub_project_and_Hipflat_project_address',
}
coords = [row for row in coords if int(row.get('hipflatId', -1)) != PROJECT_ID] + [coord_record]
coords.sort(key=lambda row: int(row['hipflatId']))
save_array(coord_path, 'BANGKOK_VERIFIED_COORDINATES', coords)

# A current individual DDproperty listing has matching project name and Prachasongkhro 20 address.
price, area, beds = 75000, 240, 3
sample = {
    'id': '500560873', 'price': price, 'area': area, 'priceSqm': round(price / area, 2),
    'beds': beds, 'roomType': '3BR',
    'title': 'D.D. Tower · 3 房 · 240 ㎡ · ฿75,000/月',
    'url': RENT_URL, 'sourceName': 'DDproperty', 'projectName': NAME,
    'updated': '2026-09-16', 'checkedAt': CHECKED,
    'matchedBy': 'DDproperty_direct_listing_project_name_and_Prachasongkhro_20_address_cross_checked_against_project_detail',
    'listingStatus': 'availability_unconfirmed_update_over_30d',
    'availability': 'DDproperty individual listing remains published as checked 2026-10-18; listing date 2026-09-16. PropertyHub exact-project rent page currently reports zero matched rental units, so confirm availability and project association before relying on this estimate.',
}
market_path, markets = load_array('bangkok-manual-market-samples.js', 'BANGKOK_MANUAL_MARKET_SAMPLES')
project = next((row for row in markets if int(row.get('hipflatId', -1)) == PROJECT_ID), None)
if project is None:
    project = {'hipflatId': PROJECT_ID, 'name': NAME}
    markets.append(project)
project['name'] = NAME
rent = project.get('rent') or {}
samples = {str(row.get('url')): row for row in rent.get('samples', []) if row.get('url')}
samples[RENT_URL] = sample
all_samples = list(samples.values())
by_bedroom = {}
for row in all_samples:
    b = str(row.get('beds') or '')
    if not b: continue
    old = by_bedroom.get(b)
    rate = float(row['price']) / float(row['area'])
    if old is None or rate < old['minimumSqm']:
        by_bedroom[b] = {'count': 1, 'minimum': row['price'], 'area': row['area'], 'minimumSqm': rate,
                          'minimumSqmSourceUrl': row['url'], 'sourceUrl': row['url']}
    else:
        old['count'] += 1
rates = [float(row['price']) / float(row['area']) for row in all_samples]
lowest_price = min(all_samples, key=lambda row: float(row['price']))
lowest_rate = min(all_samples, key=lambda row: float(row['price']) / float(row['area']))
project['rent'] = {
    'count': len(all_samples), 'observedCount': len(all_samples), 'countKind': 'manual_verified_listing',
    'average': round(sum(float(row['price']) for row in all_samples) / len(all_samples)),
    'minimum': float(lowest_price['price']), 'minimumArea': float(lowest_price['area']),
    'minimumSampleUpdated': lowest_price.get('updated'),
    'averageSqm': round(sum(rates) / len(rates)), 'minimumSqm': round(min(rates)),
    'minimumSqmSampleUpdated': lowest_rate.get('updated'), 'asOf': CHECKED,
    'sourceName': 'DDproperty 個別出租掛牌', 'source': HIPFLAT_URL,
    'minimumSourceUrl': lowest_price['url'], 'minimumSqmSourceUrl': lowest_rate['url'],
    'snapshotMethod': 'Direct individual listing matched by exact D.D. Tower name and Prachasongkhro 20 address; PropertyHub project page currently shows no matched rentals, so the sample is dated and availability is unconfirmed.',
    'byBedroom': by_bedroom, 'samples': all_samples,
}
project['replaceRent'] = True
markets.sort(key=lambda row: int(row['hipflatId']))
save_array(market_path, 'BANGKOK_MANUAL_MARKET_SAMPLES', markets)

sale_price, sale_area = 2_899_000, 71
rent_rate = price / area
monthly_estimate = rent_rate * sale_area
gross_yield = monthly_estimate * 12 / sale_price * 100
agent_adjusted = monthly_estimate * 11 / sale_price * 100
report = {
    'hipflatId': PROJECT_ID, 'projectName': NAME, 'checkedAt': CHECKED,
    'coordinate': {'lat': 13.77476678633347, 'lng': 100.56165651720289, 'point': PH_URL,
                   'independentOSMCrossCheck': {'lat': COORD[0], 'lng': COORD[1], 'url': OSM_URL},
                   'identityCrossChecks': [PH_URL, HIPFLAT_URL],
                   'evidence': 'The live map coordinate is the exact PropertyHub project page location; OpenStreetMap independently maps a named D.D. Tower building at the matching Soi Prachasongkhro 20 address in Din Daeng.'},
    'rentListing': sample,
    'rentStatusCrossCheck': {'propertyHubProjectPage': PH_URL, 'status': '0 matched rentals at check', 'note': 'External direct listing remains shown, but freshness and exact association are not fully confirmed.'},
    'twoBedroomYieldBaseline': {'salePriceTHB': sale_price, 'saleAreaSqm': sale_area,
        'saleSourceUrl': 'https://propertyhub.in.th/en/listings/for-sell-condo-d-d-tower-building-1-floor-16-2-bed-room-room-size-71-sqm--9b280866---6210412',
        'rentalRoomType': '3BR fallback; no verified 2BR rent found', 'rentalRateTHBPerSqmMonth': rent_rate,
        'estimatedMonthlyRentAtSaleAreaTHB': monthly_estimate, 'grossAnnualYieldPercent': gross_yield,
        'afterOneAgentMonthPercent': agent_adjusted,
        'formula': '3BR rent listing monthly rate × lowest 2BR sale area; annualize by 12 (or 11 months after one agent month), divided by lowest 2BR sale price.'},
    'limitations': ['PropertyHub exact-project rental page shows zero matched listings.', 'The DDproperty listing is dated 2026-09-16 and is over 30 days old at check time.', 'Three-bedroom listing area (240 sqm) exceeds this project source’s typical range; treat cross-room yield as indicative and confirm listing association and current availability.'],
}
(REPORTS / 'dd-tower-coordinate-rent-enrichment-2026-10-18.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'hipflatId': PROJECT_ID, 'coordinates': COORD, 'rentSample': sample, 'twoBedroomPurchase': [sale_price, sale_area], 'rentRatePerSqm': rent_rate, 'grossYield': round(gross_yield, 2), 'afterOneAgentMonth': round(agent_adjusted, 2), 'verifiedCoordinateCount': len(coords)}, ensure_ascii=False))
