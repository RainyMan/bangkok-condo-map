from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
ID=3022
DATE='2026-10-19'
HIPFLAT='https://www.hipflat.co.th/projects/condare-maneeya-vmdoxl'
PH_PROJECT='https://propertyhub.in.th/en/projects/condare-maneeya'
PH_SALE='https://propertyhub.in.th/en/condo-for-sale/project-condare-maneeya'
PH_RENT='https://propertyhub.in.th/en/condo-for-rent/project-condare-maneeya'
OLD='https://www.rightmove.condothai.co.th/room/60158/Condare%20Maneeya/0/?distance=3'

def read_array(file,symbol):
    p=DIST/file; text=p.read_text(encoding='utf-8')
    m=re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);',text,re.S)
    if not m: raise RuntimeError(f'missing {symbol}')
    return json.loads(m.group(1))
def write_array(file,symbol,rows):
    (DIST/file).write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
manual=read_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
record=next(x for x in manual if int(x['hipflatId'])==ID)
sale=record['sale']; old=next(x for x in sale['samples'] if x.get('url')==OLD)
old['listingStatus']='availability_unconfirmed_update_over_30d'
old['statusCheckedAt']=DATE
old['statusNote']='No refresh date was available. Hipflat currently reports no available units; retain this listing as an unconfirmed historical lead and exclude it from current sale pricing and ROI.'
sale.update({'count':0,'observedCount':0,'countKind':'no_current_verified_listings','average':None,'minimum':None,'minimumArea':None,'averageSqm':None,'minimumSqm':None,'minimumSourceUrl':None,'minimumSqmSourceUrl':None,'minimumSampleUpdated':None,'minimumSqmSampleUpdated':None,'byBedroom':{},'asOf':DATE,'source':PH_PROJECT,'note':'A Condothai two-bedroom listing remains as an unconfirmed historical reference, with no update date. Hipflat currently shows no available units; it is excluded from active price metrics and yield.'})
record['replaceSale']=True; record['asOf']=DATE
write_array('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES',manual)
crosses=read_array('bangkok-market-crosschecks.js','BANGKOK_MARKET_CROSSCHECKS')
cross=next(x for x in crosses if int(x['hipflatId'])==ID)
cross.update({'asOf':DATE,'projectSourceUrl':PH_PROJECT,
 'sale':{'activeListingCount':0,'displayedResultCount':1,'historicalSamples':[{'price':3811000,'area':88.05,'beds':2,'url':OLD,'statusLabel':'來源沒有近期更新日期；Hipflat 現在顯示無可用房源，故只作歷史參考，不納入現行最低售價或投報。'}],'sourceUrl':PH_SALE,'note':'Hipflat currently reports no available property; PropertyHub listing is historical and lacks a current update date.'},
 'rent':{'activeListingCount':0,'sourceUrl':PH_RENT,'note':'PropertyHub rent page reports no matched properties, and Hipflat currently reports no available property.'},
 'availabilitySources':[{'sourceName':'Hipflat 專案頁','url':HIPFLAT,'statusLabel':'核對時頁面顯示目前沒有可用物件。'}, {'sourceName':'PropertyHub 出售專案頁','url':PH_SALE,'statusLabel':'目前沒有可核實的現行出售單筆掛牌。'}, {'sourceName':'PropertyHub 出租專案頁','url':PH_RENT,'statusLabel':'目前沒有配對的出租房源。'}, {'sourceName':'PropertyHub 專案資訊','url':PH_PROJECT,'statusLabel':'專案頁與清單的舊掛牌狀態不一致；不視為現行掛牌。'}, {'sourceName':'Condothai 歷史出售樣本','url':OLD,'statusLabel':'兩房 88.05㎡、฿3,811,000；無近期更新證據，僅保留歷史參考。'}],
 'yieldStatus':'not_calculated','yieldNote':'目前沒有可核實的現行租金樣本，出售樣本亦無法確認現行有效；不計算投報率。'})
write_array('bangkok-market-crosschecks.js','BANGKOK_MARKET_CROSSCHECKS',crosses)
report={'hipflatId':ID,'project':'Condare Maneeya','checkedAt':DATE,'location':{'coordinates':'13.80257439278313,100.5627697443388','source':'https://propertyhub.in.th/en/projects/condare-maneeya','status':'verified_project_map'},'sale':{'status':'no_current_verified_listing','displayedOldResultCount':1,'historicalSample':{'priceTHB':3811000,'areaSqm':88.05,'bedrooms':2,'url':OLD,'updated':'not provided'},'treatment':'Retained for traceability only; excluded from current market baseline.'},'rent':{'status':'no_current_verified_listing','source':PH_RENT},'yield':{'status':'not_calculable','reason':'No current verified rent listing; sale sample has unconfirmed current availability.'},'sources':[HIPFLAT,PH_SALE,PH_RENT,PH_PROJECT,OLD]}
(ROOT/'reports'/'condare-maneeya-current-availability-2026-10-19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':record['name'],'activeSale':sale['count'],'activeRent':cross['rent']['activeListingCount'],'yield':cross['yieldStatus']},ensure_ascii=False))
