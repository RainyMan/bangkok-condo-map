from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; REPORTS=ROOT/'reports'
PROJECT_ID=3738; NAME='Mano Tower'; CHECKED='2026-10-18'
PROJECT_URL='https://propertyhub.in.th/en/projects/mano-tower'
HIPFLAT_URL='https://www.hipflat.co.th/en/projects/mano-tower-ocwgrq'
RENT_URL='https://www.fazwaz.co.th/en/property-rent/3-bedroom-condo-for-rent-at-mano-tower-in-khlong-tan-nuea-bangkok-u6827524'
SALE_URL='https://propertyhub.in.th/en/listings/3-bedroom-3-bathroom-220-sq-m-mano-tower---5093826'
def read_array(filename,symbol):
 p=DIST/filename; m=re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);',p.read_text(encoding='utf-8'),re.S)
 if not m: raise ValueError(f'Missing {symbol}')
 return p,json.loads(m.group(1))
def write_array(path,symbol,rows):
 path.write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
price,area,beds=90000,326,3
rate=price/area
sample={'id':'U6827524','price':price,'area':area,'priceSqm':round(rate,2),'beds':beds,'roomType':'3BR',
 'title':'Mano Tower · 3 房 · 326 ㎡ · ฿90,000/月','url':RENT_URL,'sourceName':'FazWaz','projectName':NAME,
 'updated':'2026-10-18 (頁面顯示 2 小時前更新)','checkedAt':CHECKED,
 'matchedBy':'Exact project title Mano Tower, Khlong Tan Nuea address, and project completion year 1990',
 'availability':'Direct unit page shows 3 bedrooms, 326 sqm, ฿90,000/month, one-year contract, listed 2026-10-01 and refreshed 2 hours before check; availability date is shown as N/A.',
 'listingStatus':'availability_unconfirmed_date_unknown'}
path,rows=read_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
project=next((x for x in rows if int(x.get('hipflatId',-1))==PROJECT_ID),None)
if project is None: project={'hipflatId':PROJECT_ID,'name':NAME}; rows.append(project)
project['name']=NAME
old=project.get('rent') or {}; samples={str(x.get('url')):x for x in old.get('samples',[]) if x.get('url')}; samples[RENT_URL]=sample; items=list(samples.values())
by_bed={}
for row in items:
 key=str(row.get('beds') or '')
 if not key: continue
 r=float(row['price'])/float(row['area']); cur=by_bed.get(key)
 if cur is None or r<cur['minimumSqm']:
  by_bed[key]={'count':1,'minimum':float(row['price']),'area':float(row['area']),'minimumSqm':r,'minimumSqmSourceUrl':row['url'],'sourceUrl':row['url']}
 else: cur['count']+=1
rates=[float(x['price'])/float(x['area']) for x in items]
low_price=min(items,key=lambda x:float(x['price'])); low_rate=min(items,key=lambda x:float(x['price'])/float(x['area']))
project['rent']={'count':len(items),'observedCount':len(items),'countKind':'manual_verified_listing',
 'average':round(sum(float(x['price']) for x in items)/len(items)),'minimum':float(low_price['price']),'minimumArea':float(low_price['area']),
 'minimumSampleUpdated':low_price.get('updated'),'averageSqm':round(sum(rates)/len(rates)),'minimumSqm':round(min(rates)),
 'minimumSqmSampleUpdated':low_rate.get('updated'),'asOf':CHECKED,'sourceName':'FazWaz 個別出租掛牌',
 'source':HIPFLAT_URL,'minimumSourceUrl':low_price['url'],'minimumSqmSourceUrl':low_rate['url'],
 'snapshotMethod':'Direct current unit page identifies Mano Tower, Khlong Tan Nuea, 3 bedrooms, 326 sqm, ฿90,000/month; project name and 1990 completion year cross-check against exact PropertyHub and Hipflat project pages.',
 'byBedroom':by_bed,'samples':items}
project['replaceRent']=True; rows.sort(key=lambda x:int(x['hipflatId'])); write_array(path,'BANGKOK_MANUAL_MARKET_SAMPLES',rows)
# Lowest source-backed 3BR purchase sample already recorded in PropertyHub/legacy market data.
sale_price,sale_area=26000000,220
monthly=rate*sale_area
gross=monthly*12/sale_price*100; agent=monthly*11/sale_price*100
report={'hipflatId':PROJECT_ID,'projectName':NAME,'checkedAt':CHECKED,
 'coordinate':{'lat':13.7441503200277,'lng':100.5726899483859,'source':PROJECT_URL,'identityCheck':HIPFLAT_URL,
  'evidence':'PropertyHub exact Mano Tower project page location; project page and listing identify the same Mano Tower in Khlong Tan Nuea, Watthana.'},
 'saleListing':{'bedrooms':3,'priceTHB':sale_price,'areaSqm':sale_area,'url':SALE_URL,'asOf':'2026-10-17'},
 'rentListing':sample,
 'yieldEstimate':{'bedrooms':3,'purchasePriceTHB':sale_price,'purchaseAreaSqm':sale_area,'rentTHBPerSqmMonth':rate,
  'estimatedMonthlyRentAtPurchaseAreaTHB':monthly,'grossAnnualYieldPercent':gross,'afterOneAgentMonthPercent':agent,
  'annualCommonFeeDeductedTHB':0,'managementFee':'unknown; not deducted',
  'formula':'(3BR rent per sqm × lowest linked 3BR sale area × 12 months) ÷ lowest linked 3BR sale total; 11 months when deducting one agent month.'},
 'notes':['This project has a 3-bedroom sale/rent pairing; no two-bedroom sale baseline is shown. Select 3 bedrooms to view the matching ROI estimate.',
  'The rent page was refreshed 2 hours before checking, but availability date is N/A; availability is unconfirmed.',
  'The listing states a one-year rental contract; common fee not found and not deducted.']}
(REPORTS/'mano-tower-rent-enrichment-2026-10-18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'hipflatId':PROJECT_ID,'rentPrice':price,'rentAreaSqm':area,'rentRate':round(rate,2),'sale3BR':[sale_price,sale_area],'estimatedMonthlyRent':round(monthly,2),'grossYield':round(gross,2),'afterOneAgentMonth':round(agent,2)},ensure_ascii=False))
