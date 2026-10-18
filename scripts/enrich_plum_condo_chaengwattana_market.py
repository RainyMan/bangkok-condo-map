from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
PID=6317
NAME='Plum Condo Chaengwattana - Donmuang'
CHECKED='2026-10-18'
HIPFLAT='https://www.hipflat.co.th/en/projects/plum-condo-chaengwattana-donmuang-ncryth'
PH='https://propertyhub.in.th/en/projects/plum-condo-chaengwattana-donmueang'
SALE=[
 {'id':'U1931771','price':1650000,'area':23.0,'beds':1,'roomType':'1BR','updated':CHECKED,'title':'Plum Condo Chaengwattana - Donmuang · 1 房 · 23 ㎡ · ฿1,650,000','url':'https://www.hipflat.co.th/en/ads/844803148e3l1t93993lc9h03u02u94l'},
 {'id':'U6663063','price':2270000,'area':26.0,'beds':1,'roomType':'1BR','updated':CHECKED,'title':'Plum Condo Chaengwattana - Donmuang · 1 房 · 26 ㎡ · ฿2,270,000','url':'https://www.hipflat.co.th/en/ads/ula809ca8cl8tlu8311cteu43u092h0a'},
 {'id':'U1402086','price':1600000,'area':22.94,'beds':1,'roomType':'1BR','updated':CHECKED,'title':'Plum Condo Chaengwattana - Donmuang · 1 房 · 22.94 ㎡ · ฿1,600,000','url':'https://www.hipflat.co.th/en/ads/3h4aln998tleuctua7n0e41l3u0h1440'},
 {'id':'CX-135704','price':2580000,'area':35.38,'beds':1,'roomType':'1BR','updated':CHECKED,'title':'Plum Condo Chaengwattana - Donmuang · 1 房 · 35.38 ㎡ · ฿2,580,000','url':'https://www.hipflat.co.th/en/ads/a09lt8t78n332u72c941uteu3u0l1e9n'},
 {'id':'CX-135707','price':1860000,'area':26.39,'beds':1,'roomType':'1BR','updated':CHECKED,'title':'Plum Condo Chaengwattana - Donmuang · 1 房 · 26.39 ㎡ · ฿1,860,000','url':'https://www.hipflat.co.th/en/ads/9e1h49e08t0n2h438el4a2e73u0c4ac4'},
]
RENT=[{'id':'CX-161398','price':9500,'area':26.5,'beds':1,'roomType':'1BR','updated':CHECKED,'title':'Plum Condo Chaengwattana - Donmuang · 1 房 · 26.5 ㎡ · ฿9,500/月','url':'https://www.hipflat.co.th/en/ads/1ac90l0a8ht4e8u2n4tel9a23ul38t9l'}]
def read_array(file,symbol):
 p=DIST/file; m=re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);',p.read_text(encoding='utf-8'),re.S)
 if not m: raise RuntimeError(f'missing {symbol}')
 return p,json.loads(m.group(1))
def write_array(path,symbol,rows):
 path.write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
def annotate(rows):
 for row in rows:
  row.update(priceSqm=round(row['price']/row['area']),sourceName='Hipflat 個別掛牌',projectName=NAME,checkedAt=CHECKED,matchedBy='Hipflat exact project listing and project name; same Thung Song Hong/Lak Si district',listingStatus='active_as_listed')
 return rows
SALE=annotate(SALE); RENT=annotate(RENT)
low_total=min(SALE,key=lambda x:x['price']); low_sqm=min(SALE,key=lambda x:x['price']/x['area'])
rent_low=min(RENT,key=lambda x:x['price']/x['area'])
sale={'count':len(SALE),'observedCount':len(SALE),'countKind':'manual_verified_listing','average':round(sum(x['price'] for x in SALE)/len(SALE)),'minimum':low_total['price'],'minimumArea':low_total['area'],'minimumSampleUpdated':CHECKED,'averageSqm':round(sum(x['price']/x['area'] for x in SALE)/len(SALE)),'minimumSqm':round(low_sqm['price']/low_sqm['area']),'minimumSqmSampleUpdated':CHECKED,'asOf':CHECKED,'snapshotMethod':'Hipflat project page and individual listing detail pages; listings were visible as active and refreshed on 2026-10-18','sourceName':'Hipflat 個別出售掛牌','source':HIPFLAT,'minimumSourceUrl':low_total['url'],'minimumSqmSourceUrl':low_sqm['url'],'byBedroom':{'1':{'count':len(SALE),'minimum':low_total['price'],'area':low_total['area'],'minimumArea':low_total['area'],'minimumSqm':low_total['price']/low_total['area'],'priceSqm':round(low_total['price']/low_total['area']),'sourceUrl':low_total['url'],'minimumSourceUrl':low_total['url'],'minimumSqmSourceUrl':low_sqm['url']}},'samples':SALE}
rent={'count':len(RENT),'observedCount':len(RENT),'countKind':'manual_verified_listing','average':rent_low['price'],'minimum':rent_low['price'],'minimumArea':rent_low['area'],'minimumSampleUpdated':CHECKED,'averageSqm':round(rent_low['price']/rent_low['area']),'minimumSqm':round(rent_low['price']/rent_low['area']),'minimumSqmSampleUpdated':CHECKED,'asOf':CHECKED,'snapshotMethod':'Hipflat project page and directly linked rental detail page; listing detail confirms 9500 THB/month, 26.5 sqm, 1 bedroom, updated 2026-10-18','sourceName':'Hipflat 個別出租掛牌','source':HIPFLAT,'minimumSourceUrl':rent_low['url'],'minimumSqmSourceUrl':rent_low['url'],'byBedroom':{'1':{'count':1,'minimum':rent_low['price'],'area':rent_low['area'],'minimumArea':rent_low['area'],'minimumSqm':rent_low['price']/rent_low['area'],'averageSqm':rent_low['price']/rent_low['area'],'sourceUrl':rent_low['url'],'minimumSourceUrl':rent_low['url'],'minimumSqmSourceUrl':rent_low['url']}},'samples':RENT}
manual_path,manual=read_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
entry=next((r for r in manual if int(r.get('hipflatId',0))==PID),None)
if entry is None: entry={'hipflatId':PID,'name':NAME}; manual.append(entry)
entry.update(name=NAME,asOf=CHECKED,sale=sale,rent=rent,replaceSale=True,replaceRent=True)
write_array(manual_path,'BANGKOK_MANUAL_MARKET_SAMPLES',manual)
# Hipflat's exact project and listing pages specify completion in September 2023; replace the conflicting 2024 fallback from the portal's generic project metadata.
detail_path,details=read_array('bangkok-propertyhub-guessed-details.js','BANGKOK_PROPERTYHUB_GUESSED_DETAILS')
detail=next((r for r in details if int(r.get('hipflatProjectId',0))==PID),None)
if detail:
 detail['completedYear']=2023; detail['completedYearSourceUrl']=HIPFLAT
 detail['completionYearMethod']='Hipflat exact project page and individual unit page both state completion in Sep 2023; use the project-specific completion statement rather than PropertyHub year-built metadata.'
 detail['locationSourceName']='PropertyHub 專案頁（專案 ID、樓盤名與掛牌行政區核對）'
 if detail.get('fee'):
  detail['fee']['note']='PropertyHub 專案頁公布管理費 45 THB/㎡/月；現行費率請再向管委會確認。'
write_array(detail_path,'BANGKOK_PROPERTYHUB_GUESSED_DETAILS',details)
# Repair source attribution for the already verified embedded PropertyHub project point.
coord_path,coords=read_array('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES')
coord=next((r for r in coords if int(r.get('hipflatId',0))==PID),None)
if coord:
 coord['sourceName']='PropertyHub 專案頁（專案 ID、樓盤名與掛牌行政區核對）'
 coord['verificationSourceUrl']=HIPFLAT
 coord['verificationMethod']='PropertyHub embedded project point checked against exact PropertyHub project ID, exact Hipflat project name and address district; Hipflat project page corroborates the same condo identity and address.'
write_array(coord_path,'BANGKOK_VERIFIED_COORDINATES',coords)
price=low_total['price']; area=low_total['area']; rent_rate=rent_low['price']/rent_low['area']
monthly=rent_rate*area; agent_annual=monthly*11; fee_annual=45*area*12
report={'hipflatId':PID,'project':NAME,'checkedAt':CHECKED,'coordinates':{'lat':coord['lat'],'lng':coord['lng'],'source':coord['sourceUrl'],'verification':HIPFLAT},'completionYear':{'year':2023,'source':HIPFLAT,'discrepancy':'PropertyHub project metadata shows 2024; Hipflat project and individual unit pages state Sep 2023.'},'managementFee':{'thbPerSqmMonth':45,'source':PH},'sale':{'count':len(SALE),'minimumTotal':price,'minimumAreaSqm':area,'minimumPricePerSqm':round(price/area),'minimumUrl':low_total['url'],'lowestPricePerSqmUrl':low_sqm['url'],'allSamples':SALE},'rent':{'count':len(RENT),'monthly':rent_low['price'],'areaSqm':rent_low['area'],'pricePerSqmMonth':round(rent_rate),'url':rent_low['url'],'allSamples':RENT},'yieldEstimate':{'bedrooms':1,'purchasePriceThb':price,'purchaseAreaSqm':area,'rentRateThbPerSqmMonth':rent_rate,'estimatedMonthlyRentThb':round(monthly),'annualRentAfterOneAgentMonthThb':round(agent_annual),'annualCommonFeeDeductedThb':round(fee_annual),'netYieldPercentAfterOneAgentMonthAndManagementFee':round((agent_annual-fee_annual)/price*100,2),'purchaseSource':low_total['url'],'rentSource':rent_low['url'],'formula':'((monthly rent × purchase area × 11 months) − (45 THB/㎡/month × purchase area × 12)) ÷ purchase price × 100'}}
report_path=ROOT/'reports'/'plum-condo-chaengwattana-market-2026-10-18.json'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':NAME,'saleSamples':len(SALE),'rentSamples':len(RENT),'minimumSale':price,'minimumArea':area,'rentPerSqm':round(rent_rate),'netYield':report['yieldEstimate']['netYieldPercentAfterOneAgentMonthAndManagementFee'],'coordinate':(coord['lat'],coord['lng']),'completedYear':2023},ensure_ascii=False))
