from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';REPORTS=ROOT/'reports'
PROJECT_ID=3697;NAME='Green Point Condominium';CHECKED='2026-10-18'
HIPFLAT_URL='https://www.hipflat.co.th/projects/green-point-condominium-e3l1te0a11nl0elc47t1u189nn083u02'
PH_URL='https://propertyhub.in.th/en/projects/green-point-condo'
RENT_URL='https://www.hipflat.co.th/ja/ads/739209ch8ctu7l1804732nnt3u0h14ue'
ALT_RENT_URL='https://www.samuitimes.com/th/เช่าบ้าน/คอนโดให้เช่า-สตูดิโอ-ที่-กรีน-พ้อยท์-คอนโดมิเนี่ยม-ใน-โคกแฝด-กรุงเทพมหานคร-u1827480'
DOT_URL='https://www.thailand-property.com/condo/39481/green-point-condominium'
def read_array(filename,symbol):
 p=DIST/filename;m=re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);',p.read_text(encoding='utf-8'),re.S)
 if not m:raise ValueError(f'Missing {symbol}')
 return p,json.loads(m.group(1))
def write_array(path,symbol,rows):path.write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
price,area,beds=3000,21.19,1; rate=price/area
sample={'id':'U1827480','price':price,'area':area,'priceSqm':round(rate,2),'beds':beds,'roomType':'STUDIO',
 'title':'Green Point Condominium · studio · 21.19 ㎡ · ฿3,000/月',
 'url':RENT_URL,'sourceName':'Hipflat','projectName':NAME,'updated':'2026-02-11 (最後更新顯示 16 小時前)',
 'checkedAt':CHECKED,'matchedBy':'Hipflat direct ad U1827480 names Green Point Condominium and states 21.19 sqm, studio and THB 3,000/month; PropertyHub and Hipflat project pages corroborate identity.',
 'availability':'Hipflat direct listing says available for rent; posted 2026-02-11 and refreshed 16 hours before check. Thailand-Property exact-project page also shows one rental unit from ฿2,999.',
 'listingStatus':'active_as_listed'}
path,rows=read_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
project=next((x for x in rows if int(x.get('hipflatId',-1))==PROJECT_ID),None)
if project is None:project={'hipflatId':PROJECT_ID,'name':NAME};rows.append(project)
project['name']=NAME
old=project.get('rent') or {}; samples={str(x.get('url')):x for x in old.get('samples',[]) if x.get('url')};samples[RENT_URL]=sample;items=list(samples.values())
by={}
for row in items:
 b=str(row.get('beds') or '')
 if not b:continue
 r=float(row['price'])/float(row['area']);cur=by.get(b)
 if cur is None or r<cur['minimumSqm']:by[b]={'count':1,'minimum':float(row['price']),'area':float(row['area']),'minimumSqm':r,'minimumSqmSourceUrl':row['url'],'sourceUrl':row['url']}
 else:cur['count']+=1
rates=[float(x['price'])/float(x['area']) for x in items];low_p=min(items,key=lambda x:float(x['price']));low_r=min(items,key=lambda x:float(x['price'])/float(x['area']))
project['rent']={'count':len(items),'observedCount':len(items),'countKind':'manual_verified_listing','average':round(sum(float(x['price']) for x in items)/len(items)),
 'minimum':float(low_p['price']),'minimumArea':float(low_p['area']),'minimumSampleUpdated':low_p.get('updated'),'averageSqm':round(sum(rates)/len(rates)),
 'minimumSqm':round(min(rates)),'minimumSqmSampleUpdated':low_r.get('updated'),'asOf':CHECKED,'sourceName':'Hipflat 個別出租掛牌',
 'source':HIPFLAT_URL,'minimumSourceUrl':low_p['url'],'minimumSqmSourceUrl':low_r['url'],
 'snapshotMethod':'Direct Hipflat unit U1827480 confirms the project, studio type, 21.19 sqm and ฿3,000 monthly rent; project identity cross-checked against exact PropertyHub and Hipflat pages.',
 'byBedroom':by,'samples':items}
project['replaceRent']=True
common_fee_monthly=500
project['fee']={'rate':common_fee_monthly/area,'status':'listing_indicated',
 'note':'Hipflat listing description states common fee ฿500/month for this 21.19㎡ unit; converted to ฿/㎡/month for calculator. Verify the current project fee with the juristic office.',
 'source':RENT_URL}
rows.sort(key=lambda x:int(x['hipflatId']));write_array(path,'BANGKOK_MANUAL_MARKET_SAMPLES',rows)
sale_price,sale_area=719100,21.15
rent_scaled=rate*sale_area;fee_rate=common_fee_monthly/area
annual_after_agent=rent_scaled*11;annual_fee=fee_rate*sale_area*12
report={'hipflatId':PROJECT_ID,'projectName':NAME,'checkedAt':CHECKED,
 'coordinate':{'lat':13.841357155876963,'lng':100.85076428780098,'source':PH_URL,'identityCheck':HIPFLAT_URL,'evidence':'Exact PropertyHub Green Point Condo page and Hipflat Green Point Condominium page identify the same project in Nong Chok.'},
 'saleListing':{'bedrooms':1,'priceTHB':sale_price,'areaSqm':sale_area,'url':'https://propertyhub.in.th/en/listings/great-value-condo-for-sale-at-green-poin-near-min-buri---6309349','updated':'2026-10-16'},
 'rentListing':sample,
 'managementFee':{'monthlyPerUnitTHB':500,'unitAreaSqm':area,'rateTHBPerSqmMonth':fee_rate,'source':RENT_URL,'note':'As stated in the direct listing description; not independently confirmed by the juristic office.'},
 'yieldEstimate':{'bedrooms':1,'purchasePriceTHB':sale_price,'purchaseAreaSqm':sale_area,'rentTHBPerSqmMonth':rate,
  'estimatedMonthlyRentAtPurchaseAreaTHB':rent_scaled,'grossAnnualYieldPercent':rent_scaled*12/sale_price*100,
  'afterOneAgentMonthAndManagementFeePercent':(annual_after_agent-annual_fee)/sale_price*100,
  'annualCommonFeeDeductedTHB':annual_fee,'formula':'((monthly rent per sqm × paired 1BR purchase area × 11 months) − (฿500 monthly common fee scaled by purchase area × 12)) ÷ lowest 1BR sale price.'},
 'crossChecks':{'secondaryExactProjectRentPage':DOT_URL,'status':'one rental unit from ฿2,999 per month'},
 'notes':['Same-room 1BR/studio sample pair. Listing is currently shown as available and refreshed 16 hours before checking.',
  'The listing description states a ฿500 monthly common fee for the unit; the juristic office should confirm current fee.']}
(REPORTS/'green-point-condominium-rent-enrichment-2026-10-18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'hipflatId':PROJECT_ID,'rentRate':round(rate,2),'sale1BR':[sale_price,sale_area],
 'monthlyRentEstimate':round(rent_scaled,2),'grossYieldPercent':round(rent_scaled*12/sale_price*100,2),
 'netYieldAfterAgentAndFeePercent':round((annual_after_agent-annual_fee)/sale_price*100,2),'feePerSqmMonth':round(fee_rate,2)},ensure_ascii=False))
