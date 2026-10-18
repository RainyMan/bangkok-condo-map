from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PID = 3362
NAME = 'Haven Luxe Phaholyothin'
HIPFLAT = 'https://www.hipflat.co.th/en/projects/haven-luxe-phaholyothin-imqgji'
SALE_PROJECT = 'https://assets3.propertyhub.in.th/en/condo-for-sale/project-haven-luxe'
SALE_ONE = 'https://propertyhub.in.th/en/listings/md-26067199-rare-find-beautiful-unit-at-a-below-market-price-at-haven-luxe-phaholyothinbook-now-before-it-s-gone---6389907'
SALE_TWO = 'https://www.ddproperty.com/en/property/haven-luxe-for-sale-500166264'
RENT_ONE = 'https://www.hipflat.co.th/en/ads/t0e3leu08u203cuch12a7nnt3ul3t9ln'
RENT_TWO = "https://www.ddproperty.com/property/haven-luxe-%25E0%25B8%25AE%25E0%25B8%25B2%25E0%25B9%2580%25E0%25B8%25A7%25E0%25B9%2588%25E0%25B8%2599-%25E0%25B8%25A5%25E0%25B8%25B8%25E0%25B8%2584%25E0%25B8%258B%25E0%25B8%258C-%25E0%25B8%2581%25E0%25B8%25A3%25E0%25B8%25B8%25E0%25B8%2587-%25E0%25B8%2597%25E0%25B8%259E-%25E0%25B9%2583%25E0%25B8%25AB%25E0%25B9%2589%25E0%25B8%258A%25E0%25B9%2588%25E0%25B8%25B2-500278250"
RENT_PROJECT = 'https://www.ddproperty.com/en/condo-for-rent/at-haven-luxe-4309'
MAP_URL = 'https://www.google.com/maps/place/Haven+luxe/@13.7879637,100.5529549,17z/'


def read_js(path: Path):
    return json.loads(path.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))


def write_js(path: Path, name: str, rows):
    path.write_text(f'window.{name} = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')

sale = [
    {'id':'6389907','price':3450000,'area':37.5,'priceSqm':92000,'beds':1,'roomType':'ONE_BED_ROOM','title':'Haven Luxe Phaholyothin, 1 bedroom, 37.5 sqm','url':SALE_ONE,'updated':'2026-09-13','sourceName':'PropertyHub','projectName':NAME,'matchedBy':'Exact project result and direct listing; 1 bedroom, 37.5 sqm and THB 3,450,000. Older than 30 days.','listingStatus':'availability_unconfirmed_update_over_30d'},
    {'id':'500166264','price':4990000,'area':50,'priceSqm':99800,'beds':2,'roomType':'TWO_BED_ROOM','title':'Haven Luxe, 2 bedrooms, 50 sqm, THB 4,990,000','url':SALE_TWO,'updated':'2026-02-23','sourceName':'DDproperty','projectName':NAME,'matchedBy':'Direct DDproperty listing states Haven Luxe at 39 Soi Inthamara 4, 2 bedrooms, 50 sqm and THB 4,990,000. Older than 30 days.','listingStatus':'availability_unconfirmed_update_over_30d'},
]
rent = [
    {'id':'CX-78207','price':14000,'area':35,'priceSqm':400,'beds':1,'roomType':'ONE_BED_ROOM','title':'Haven Luxe Phaholyothin, 1 bedroom, 35 sqm, THB 14,000/month','url':RENT_ONE,'updated':'2026-09-12','sourceName':'Hipflat','projectName':NAME,'matchedBy':'Direct Hipflat listing states exact project, Soi Inthamara 4, 1 bedroom, 35 sqm and THB 14,000/month; refresh date conflicts with page header.','listingStatus':'availability_unconfirmed_date_conflict'},
    {'id':'500278250','price':23000,'area':50,'priceSqm':460,'beds':2,'roomType':'TWO_BED_ROOM','title':'Haven Luxe, 2 bedrooms, 50 sqm, THB 23,000/month','url':RENT_TWO,'updated':'2026-04-30','sourceName':'DDproperty','projectName':NAME,'matchedBy':'Direct DDproperty listing identifies Haven Luxe, 2 bedrooms, 50 sqm and THB 23,000/month; older than 30 days.','listingStatus':'availability_unconfirmed_update_over_30d'},
]

manual_path = ROOT / 'dist/bangkok-manual-market-samples.js'
manual_rows = [r for r in read_js(manual_path) if r.get('hipflatId') != PID]
manual_rows.append({
    'hipflatId':PID,'name':NAME,'asOf':'2026-10-19','completedYear':2014,
    'fee':{'rate':40,'status':'published_indicative','note':'PropertyHub 專案頁列 40 THB/㎡ utility fee；月收週期尚未向管委會核實。','source':SALE_PROJECT},
    'sale':{'count':5,'observedCount':2,'countKind':'manual_verified_individual_listing_with_stale_status_flagged','average':4220000,'minimum':3450000,'minimumArea':37.5,'minimumSampleUpdated':'2026-09-13','averageSqm':95900,'minimumSqm':92000,'minimumSqmSampleUpdated':'2026-09-13','asOf':'2026-10-19','sourceName':'PropertyHub 個別掛牌與 DDproperty 兩房掛牌','source':SALE_PROJECT,'minimumSourceUrl':SALE_ONE,'minimumSqmSourceUrl':SALE_ONE,'byBedroom':{'1':{'count':1,'minimum':3450000,'area':37.5,'priceSqm':92000,'minimumSqm':92000,'sourceUrl':SALE_ONE},'2':{'count':1,'minimum':4990000,'area':50,'priceSqm':99800,'minimumSqm':99800,'sourceUrl':SALE_TWO}},'samples':sale},
    'rent':{'count':7,'observedCount':2,'countKind':'manual_verified_individual_listing_with_stale_status_flagged','average':18500,'minimum':14000,'minimumArea':35,'minimumSampleUpdated':'2026-09-12','averageSqm':430,'minimumSqm':400,'minimumSqmSampleUpdated':'2026-09-12','asOf':'2026-10-19','sourceName':'Hipflat 個別掛牌與 DDproperty 兩房租盤','source':HIPFLAT,'minimumSourceUrl':RENT_ONE,'minimumSqmSourceUrl':RENT_ONE,'byBedroom':{'1':{'count':1,'minimum':14000,'area':35,'priceSqm':400,'minimumSqm':400,'sourceUrl':RENT_ONE},'2':{'count':1,'minimum':23000,'area':50,'priceSqm':460,'minimumSqm':460,'sourceUrl':RENT_TWO}},'samples':rent},
    'replaceSale':True,'replaceRent':True,
})
write_js(manual_path,'BANGKOK_MANUAL_MARKET_SAMPLES',manual_rows)

coords_path = ROOT / 'dist/bangkok-verified-coordinates.js'
coords_rows = [r for r in read_js(coords_path) if r.get('hipflatId') != PID]
coords_rows.append({'hipflatId':PID,'name':NAME,'lat':13.7879637,'lng':100.5529549,'locationVerified':True,'sourceName':'Google Maps 精確地點 / Hipflat 街址交叉核對','sourceUrl':MAP_URL,'verificationSourceUrl':HIPFLAT,'verificationMethod':'Google Maps lists Haven luxe at 39 Soi Inthamara 4, matching Hipflat project location on Sutthisan Winitchai Road (Soi Inthamara 4), Sam Sen Nai. Excluded neighboring Haven Condominium and unrelated Phahon Yothin 8 name match.','addressMatch':'39 Soi Inthamara 4, Sam Sen Nai, Phaya Thai, Bangkok 10400'})
write_js(coords_path,'BANGKOK_VERIFIED_COORDINATES',coords_rows)

report = {'hipflatId':PID,'projectName':NAME,'asOf':'2026-10-19','coordinate':{'lat':13.7879637,'lng':100.5529549,'googleMaps':MAP_URL,'projectAddress':'Sutthisan Winitchai Road (Soi Inthamara 4), Sam Sen Nai, Phaya Thai','verification':'Google Maps point at 39 Soi Inthamara 4 matches Hipflat project description.'},'completionYear':{'year':2014,'source':HIPFLAT},'saleSamples':sale,'rentSamples':rent,'twoBedroomRent':{'priceThbPerMonth':23000,'areaSqm':50,'rentThbPerSqmMonth':460,'url':RENT_TWO,'projectIndexUrl':RENT_PROJECT,'listedDate':'2026-04-30','status':'availability_unconfirmed_update_over_30d'},'fee':{'rateThbPerSqm':40,'source':SALE_PROJECT,'note':'Utility-fee billing period not confirmed; deducting it remains indicative.'},'yield':'Two-bedroom sale and rent references both exceed 30 days. Kept as clickable historical asking prices; excluded from automatic current-yield estimate until availability is reconfirmed.'}
(ROOT/'reports/haven-luxe-phaholyothin-verification-2026-10-19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':NAME,'saleSamples':len(sale),'rentSamples':len(rent),'coordinate':[13.7879637,100.5529549]},ensure_ascii=False))
