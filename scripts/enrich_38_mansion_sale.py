from __future__ import annotations
import csv, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
CHECKED='2026-10-18'
ID=4675
NAME='38 Mansion'
SALE_URL='https://www.ddproperty.com/en/property/38-mansion-bangkok-for-sale-500402398'
DD_PROJECT='https://www.ddproperty.com/en/project/324-38-mansion'
PH_RENT='https://propertyhub.in.th/en/listings/aa689638-1bed-1bath-bts-thong-lo-57sqm-thb-25-000-mo-fl-1-38-mansion-thonglor---6423582'
PRICE=5_990_000
AREA=68.44
RATE=round(PRICE/AREA)
RENT_RATE=439
MONTHLY_RENT=round(RENT_RATE*AREA)
YIELD=round(MONTHLY_RENT*11/PRICE*100,2)

def load_array(filename,symbol):
 p=DIST/filename
 m=re.search(rf'window\.{symbol}\s*=\s*(\[.*\]);',p.read_text(encoding='utf-8'),re.S)
 if not m: raise RuntimeError(f'cannot parse {symbol}')
 return json.loads(m.group(1))
def save_array(filename,symbol,rows):
 (DIST/filename).write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

sample={
 'id':'500402398','price':PRICE,'area':AREA,'priceSqm':RATE,'beds':1,'roomType':'1BR',
 'title':'38 Mansion 1-bedroom serviced apartment · 68.44 sqm · THB 5,990,000',
 'url':SALE_URL,'sourceName':'DDproperty','projectName':NAME,'updated':'2026-09-02','checkedAt':CHECKED,
 'matchedBy':'DDproperty_individual_listing_names_38_Mansion_and_identifies_1992_building_near_Thong_Lo_BTS',
 'listingStatus':'availability_unconfirmed_update_over_30d'
}
sale={
 'count':1,'observedCount':1,'countKind':'manual_verified_listing_availability_unconfirmed',
 'average':PRICE,'minimum':PRICE,'minimumArea':AREA,'minimumSampleUpdated':'2026-09-02',
 'averageSqm':RATE,'minimumSqm':RATE,'minimumSqmSampleUpdated':'2026-09-02','asOf':CHECKED,
 'sourceName':'DDproperty 直接出售掛牌（500402398）','source':DD_PROJECT,
 'minimumSourceUrl':SALE_URL,'minimumSqmSourceUrl':SALE_URL,
 'byBedroom':{'1':{'count':1,'minimum':PRICE,'area':AREA,'priceSqm':RATE,'minimumSqm':RATE,'sourceUrl':SALE_URL,'minimumSqmSourceUrl':SALE_URL}},
 'samples':[sample]
}
manual=load_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
record=next((r for r in manual if int(r.get('hipflatId',-1))==ID),None)
if record is None:
 record={'hipflatId':ID,'name':NAME}; manual.append(record)
record.update({'asOf':CHECKED,'replaceSale':True,'sale':sale})
manual.sort(key=lambda r:int(r['hipflatId']))
save_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES',manual)

path=ROOT/'reports'/'listing-availability-checks-2026-10-18.csv'
with path.open('r',newline='',encoding='utf-8-sig') as f:
 reader=csv.DictReader(f); fields=reader.fieldnames or []; rows=[r for r in reader if not(r.get('hipflat_id')==str(ID) and r.get('market')=='sale')]
rows.append({'hipflat_id':str(ID),'condo':NAME,'checked_at':CHECKED,'market':'sale','status':'availability_unconfirmed_update_over_30d',
 'verification_note':'DDproperty direct listing 500402398 lists 1 bedroom, 68.44 sqm, THB 5.99m, listed 2 Sep 2026. The DDproperty project page currently reports 0 listings for sale, so current availability is unconfirmed.',
 'source_1':SALE_URL,'source_2':DD_PROJECT,'source_3':PH_RENT})
with path.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

report={'hipflatId':ID,'project':NAME,'checkedAt':CHECKED,'sale':sample,
 'rentBaseline':{'bedrooms':1,'pricePerSqmPerMonth':RENT_RATE,'sourceUrl':PH_RENT},
 'yieldEstimate':{'purchasePrice':PRICE,'purchaseAreaSqm':AREA,'estimatedMonthlyRent':MONTHLY_RENT,
                   'annualRentAfterOneAgentMonth':MONTHLY_RENT*11,'yieldBeforeCommonFee':YIELD,
                   'commonFee':'not verified; excluded','note':'The linked DDproperty unit was listed over 30 days ago; current availability is unconfirmed.'},
 'sources':{'DDpropertyProject':DD_PROJECT,'DDpropertyListing':SALE_URL,'PropertyHubRent':PH_RENT}}
(ROOT/'reports'/'38-mansion-sale-enrichment-2026-10-18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':NAME,'salePrice':PRICE,'areaSqm':AREA,'priceSqm':RATE,'rentEstimatePerMonth':MONTHLY_RENT,'yieldBeforeFeePercent':YIELD},ensure_ascii=False))
