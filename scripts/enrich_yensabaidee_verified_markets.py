from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; REPORTS=ROOT/'reports'
ID=3209; NAME='Yensabaidee Condo'; CHECKED='2026-10-19'
HIP='https://www.hipflat.co.th/en/projects/yensabaidee-condo-ocpiwe'
OFFICIAL='https://www.yensabaideecondo.com/'
SALE1='https://www.livinginsider.com/en/detail/condo-for-sale-yensabaidee-condo-ladprao-101-1bedroom-3204759'
SALE2='https://www.livinginsider.com/detail/condo-for-sale-yen-sabaidee-condo-1bedroom-3184864'
RENT='https://www.hipflat.co.th/en/ads/han8tnla82nhe89hh07718au3u0hent7'
BAD='https://www.hipflat.co.th/en/ads/7t9e41a18a3tn1443c8l9uc33u0c4uha'
def read_array(filename,symbol):
 p=DIST/filename; m=re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);',p.read_text(encoding='utf-8'),re.S)
 if not m: raise ValueError(f'Missing {symbol}')
 return p,json.loads(m.group(1))
def write_array(path,symbol,rows): path.write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
# Resale samples
sale_samples=[
 {'id':'3204759','price':1699500,'area':26,'priceSqm':round(1699500/26),'beds':1,'roomType':'1BR','title':'Yensabaidee Condo，1 房，26 ㎡，฿1,699,500','url':SALE1,'sourceName':'Livinginsider','projectName':NAME,'updated':'2026-08-27；頁面核對時顯示 8 小時前更新','checkedAt':CHECKED,'matchedBy':'exact_project_name_and_ladprao_101_project','listingStatus':'active_as_listed'},
 {'id':'3184864','price':1900000,'area':27,'priceSqm':round(1900000/27),'beds':1,'roomType':'1BR','title':'Yen Sabaidee Condo，1 房，27 ㎡，฿1,900,000','url':SALE2,'sourceName':'Livinginsider','projectName':NAME,'updated':'2026-08-13；頁面核對時顯示 1 週前更新','checkedAt':CHECKED,'matchedBy':'exact_project_name_and_ladprao_101_project','listingStatus':'active_as_listed'}]
rent_sample={'id':'han8tnla82nhe89hh07718au3u0hent7','price':14000,'area':49,'priceSqm':round(14000/49),'beds':2,'roomType':'2BR','title':'Yensabaidee Condo，2 房，49 ㎡，฿14,000/月','url':RENT,'sourceName':'Hipflat','projectName':NAME,'updated':'2026-02-12；頁面核對時顯示 1 小時前更新','checkedAt':CHECKED,'matchedBy':'exact_hipflat_project_and_direct_listing_detail','listingStatus':'active_as_listed'}
# Manual market rows
p,rows=read_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
project=next((x for x in rows if int(x.get('hipflatId',-1))==ID),None)
if project is None: project={'hipflatId':ID,'name':NAME}; rows.append(project)
project.update(name=NAME)
project['sale']={'count':2,'observedCount':2,'countKind':'manual_verified_listing','average':round(sum(x['price'] for x in sale_samples)/2),'minimum':1699500,'minimumArea':26,'minimumSampleUpdated':sale_samples[0]['updated'],'averageSqm':round(sum(x['priceSqm'] for x in sale_samples)/2),'minimumSqm':round(1699500/26),'minimumSqmSampleUpdated':sale_samples[0]['updated'],'asOf':CHECKED,'sourceName':'Livinginsider 個別出售掛牌','source':'https://www.livinginsider.com/project/yensabaidee-condo-ladprao-101-condo-buysell','minimumSourceUrl':SALE1,'minimumSqmSourceUrl':SALE1,'byBedroom':{'1':{'count':2,'minimum':1699500,'area':26,'minimumArea':26,'priceSqm':round(1699500/26),'minimumSqm':round(1699500/26),'sourceUrl':SALE1,'minimumSourceUrl':SALE1,'minimumSqmSourceUrl':SALE1}},'samples':sale_samples}
project['rent']={'count':1,'observedCount':1,'countKind':'manual_verified_listing','average':14000,'minimum':14000,'minimumArea':49,'minimumSampleUpdated':rent_sample['updated'],'averageSqm':round(14000/49),'minimumSqm':round(14000/49),'minimumSqmSampleUpdated':rent_sample['updated'],'asOf':CHECKED,'sourceName':'Hipflat 個別出租掛牌','source':HIP,'minimumSourceUrl':RENT,'minimumSqmSourceUrl':RENT,'byBedroom':{'2':{'count':1,'minimum':14000,'area':49,'minimumArea':49,'priceSqm':round(14000/49),'minimumSqm':round(14000/49),'sourceUrl':RENT,'minimumSourceUrl':RENT,'minimumSqmSourceUrl':RENT}},'samples':[rent_sample]}
rows.sort(key=lambda x:int(x['hipflatId']));write_array(p,'BANGKOK_MANUAL_MARKET_SAMPLES',rows)
# Official site embeds the Google Maps project point at 13.79396049, 100.62730791
p,coords=read_array('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES')
coords=[x for x in coords if int(x.get('hipflatId',-1))!=ID]
coords.append({'hipflatId':ID,'name':NAME,'lat':13.793960490320215,'lng':100.62730791483092,'locationVerified':True,'sourceName':'建案官方網站 Google Maps 嵌入地圖','sourceUrl':OFFICIAL,'verificationSourceUrl':HIP,'verificationMethod':'official_embedded_google_map_matches_exact_project_name_and_ladprao_101_address'})
coords.sort(key=lambda x:int(x['hipflatId']));write_array(p,'BANGKOK_VERIFIED_COORDINATES',coords)
# Independent source cross-check, including an invalid Hipflat sale card excluded from market figures.
p,cross=read_array('bangkok-market-crosschecks.js','BANGKOK_MARKET_CROSSCHECKS')
cross=[x for x in cross if int(x.get('hipflatId',-1))!=ID]
cross.append({'hipflatId':ID,'projectName':NAME,'asOf':CHECKED,'sourceName':'Livinginsider / Hipflat','projectSourceUrl':HIP,'sale':{'activeListingCount':2,'sourceUrl':'https://www.livinginsider.com/project/yensabaidee-condo-ladprao-101-condo-buysell','listings':[{'id':'3204759','bedrooms':1,'price':1699500,'area':26,'priceSqm':round(1699500/26),'listedAt':'2026-08-27','url':SALE1},{'id':'3184864','bedrooms':1,'price':1900000,'area':27,'priceSqm':round(1900000/27),'listedAt':'2026-08-13','url':SALE2}]},'rent':{'activeListingCount':1,'sourceUrl':HIP,'listings':[{'id':'han8tnla82nhe89hh07718au3u0hent7','bedrooms':2,'price':14000,'area':49,'priceSqm':round(14000/49),'url':RENT,'listedAt':'2026-02-12'}]},'availabilitySources':[{'sourceName':'Yensabaidee 官方網站','url':OFFICIAL,'statusLabel':'官方專案頁提供 26–49㎡、79 戶、8 樓；嵌入 Google Maps 座標與地址相符。'},{'sourceName':'Hipflat 錯誤關聯出售頁（已排除）','url':BAD,'statusLabel':'點入顯示 Rayong 的 D Condo 與當地地標，不是曼谷 Yensabaidee；不納入售價或投報。'},{'sourceName':'投報狀態','url':SALE1,'statusLabel':'目前僅核實到 1 房出售及 2 房出租；不跨房型計算投報，兩房最低售價尚無可信樣本。'}]})
cross.sort(key=lambda x:int(x['hipflatId']));write_array(p,'BANGKOK_MARKET_CROSSCHECKS',cross)
# Cache bust changed front-end data bundles.
idx=DIST/'index.html';html=idx.read_text(encoding='utf-8')
for old,new in [('bangkok-verified-coordinates.js?v=20261019a-wisetsuk-longdo-coordinate','bangkok-verified-coordinates.js?v=20261019-yensabaidee-official-map'),('bangkok-manual-market-samples.js?v=20261019-belgravia-ratchada-17-rent','bangkok-manual-market-samples.js?v=20261019-yensabaidee-listings'),('bangkok-market-crosschecks.js?v=20261019a-wisetsuk-no-market-and-name-collision','bangkok-market-crosschecks.js?v=20261019-yensabaidee-crosscheck')]:
 if old not in html: raise ValueError(f'Cache version not found: {old}')
 html=html.replace(old,new,1)
idx.write_text(html,encoding='utf-8')
REPORTS.mkdir(exist_ok=True)
report={'hipflatId':ID,'projectName':NAME,'checkedAt':CHECKED,'coordinate':{'lat':13.793960490320215,'lng':100.62730791483092,'source':OFFICIAL,'verificationSource':HIP},'saleSamples':sale_samples,'rentSample':rent_sample,'excludedSample':{'url':BAD,'reason':'The direct Hipflat advertisement page identifies a D Condo in Rayong and Rayong landmarks; it is mislinked and not a Yensabaidee Bangkok sample.'},'yield':{'status':'unavailable','reason':'Only 1-bedroom sale listings and a 2-bedroom rental listing were verified. A 2-bedroom yield requires the lowest verified 2-bedroom sale total and that same unit’s area; those sale data are not available. Do not combine different bedroom types.'}}
(REPORTS/'yensabaidee-coordinate-market-verification-2026-10-19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'hipflatId':ID,'saleSamples':len(sale_samples),'rentSamples':1,'lowestSale':{'price':1699500,'area':26,'sqm':round(1699500/26)},'rent':{'price':14000,'area':49,'sqm':round(14000/49)},'yield':'not calculated: bedroom types do not match','coordinate':[13.793960490320215,100.62730791483092]},ensure_ascii=False))
