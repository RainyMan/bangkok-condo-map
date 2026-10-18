from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; REPORTS=ROOT/'reports'
ID=3006; NAME='31 Residence'; DATE='2026-10-19'
DD='https://www.ddproperty.com/en/project/6787-31-residence'
PH='https://propertyhub.in.th/en/condo-for-sale/project-31-residence'
REALTOR='https://therealtors.net/project/31-residence'
RENT='https://www.ddproperty.com/en/condo-for-rent/at-31-residence-6787'
def load(path,symbol):
 m=re.search(rf'window\.{re.escape(symbol)}\s*=\s*(\[.*\]);',path.read_text(encoding='utf-8'),re.S)
 if not m: raise ValueError(path)
 return json.loads(m.group(1))
def write(path,symbol,rows): path.write_text(f'window.{symbol} = {json.dumps(rows,ensure_ascii=False,separators=(",",":"))};\n',encoding='utf-8')
p=DIST/'bangkok-market-crosschecks.js'; rows=load(p,'BANGKOK_MARKET_CROSSCHECKS')
r=next(x for x in rows if int(x['hipflatId'])==ID)
r['asOf']=DATE; r['sourceName']='DDproperty / PropertyHub'; r['projectSourceUrl']=DD
r['sale']={'activeListingCount':0,'sourceUrl':PH}
r['rent']={**(r.get('rent') or {}),'activeListingCount':3,'sourceUrl':RENT}
r['availabilitySources']=[
 {'sourceName':'DDproperty 專案出售頁','url':DD,'statusLabel':'0 間出售；截至 2026-10-19 無在架售盤'},
 {'sourceName':'PropertyHub 出售專案頁','url':PH,'statusLabel':'查無出售掛牌'},
 {'sourceName':'The Realtors 專案行情','url':REALTOR,'statusLabel':'目前 0 間出售、14 間出租；租盤行情非本次出售樣本'},
]
write(p,'BANGKOK_MARKET_CROSSCHECKS',rows)
report={'hipflatId':ID,'project':NAME,'checkedAt':DATE,'saleAvailability':{'status':'no_current_exact_project_listing','count':0,'sources':[{'url':DD,'evidence':'DDproperty project page reports 0 units for sale.'},{'url':PH,'evidence':'PropertyHub project sale page reports no listing.'},{'url':REALTOR,'evidence':'The Realtors project data reports 0 sale units.'}]},'rentAvailability':{'status':'current_rent_samples_present','directListingCount':3,'source':RENT},'roi':{'status':'not_calculable','reason':'No current verified sale price is available; rental listings alone do not support an ROI calculation.'},'note':'No area-level prices or nearby-project listings were substituted for an exact 31 Residence sale listing.'}
(REPORTS/'31-residence-sale-availability-2026-10-19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
idx=DIST/'index.html'; html=idx.read_text(encoding='utf-8'); html=re.sub(r'bangkok-market-crosschecks\.js\?v=[^"\']+','bangkok-market-crosschecks.js?v=20261019-31-residence-sale-check',html,count=1); idx.write_text(html,encoding='utf-8')
print(json.dumps({'hipflatId':ID,'sale':'zero current listings cross-checked across 3 sources','rent':'3 direct samples retained','roi':'not calculable'},ensure_ascii=False))
