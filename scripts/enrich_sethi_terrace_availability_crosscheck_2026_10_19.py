from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'

def load(name,var):
 p=DIST/name; text=p.read_text(encoding='utf-8'); m=re.search(rf'window\.{re.escape(var)}\s*=\s*(\[.*\]);',text)
 if not m: raise RuntimeError(f'Cannot read {name}')
 return p,text[:m.start(1)],json.loads(m.group(1)),text[m.end(1):]

def save(data):
 p,prefix,rows,suffix=data
 p.write_text(prefix+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+suffix,encoding='utf-8')

listing='https://propertyhub.in.th/en/listings/for-rent-spacious-2-bedroom-200-sqm-near-emsphere---6380539'
rent_project='https://propertyhub.in.th/en/condo-for-rent/project-sethi-terrace'
sale_project='https://propertyhub.in.th/en/condo-for-sale/project-sethi-terrace'
hipflat='https://www.hipflat.co.th/en/projects/sethi-terrace-gkwojp'
record={
 'hipflatId':3039,'projectName':'Sethi Terrace','asOf':'2026-10-19','sourceName':'PropertyHub / Hipflat 多平台核對','projectSourceUrl':hipflat,
 'sale':{'activeListingCount':0,'sourceUrl':sale_project,'note':'PropertyHub 專案出售頁目前顯示 No matched properties for Sale；未找到可核實的現行單筆出售物件，因此不填售價、不計投報。'},
 'rent':{'activeListingCount':1,'listings':[{'id':'6380539','price':50000,'area':200,'priceSqm':250,'bedrooms':2,'url':listing,'listedAt':'2026-09-08','statusLabel':'專案頁目前列 1 筆；房源頁符合 Sethi Terrace／2 房／200㎡／฿50,000，但頁面未提供最近更新日，請向刊登者確認'}],'sourceUrl':rent_project,'note':'PropertyHub 專案出租頁列 1 筆；直接房源頁核對專案名、房型、面積與租金。房源頁的 Last Update 欄未提供日期，故在架狀態尚待刊登者確認。'},
 'availabilitySources':[
  {'sourceName':'PropertyHub 出售專案頁','url':sale_project,'statusLabel':'目前顯示 0 筆出售，No matched properties for Sale。'},
  {'sourceName':'Hipflat 專案頁','url':hipflat,'statusLabel':'核對本案專案頁；未找到可核實的出售單筆來源。'},
  {'sourceName':'PropertyHub 出租專案頁','url':rent_project,'statusLabel':'列 1 筆出租；2026-09-08 更新列表。'},
  {'sourceName':'PropertyHub 出租單筆','url':listing,'statusLabel':'฿50,000／月 · 200㎡ · 2 房；房源頁沒有最近更新日期，需向刊登者確認。'},
  {'sourceName':'DotProperty 專案頁','url':'https://www.dotproperty.co.th/en/condo/18182/sethi-terrace','statusLabel':'較舊專案頁列 3 筆出租（฿40,000–50,000／月），不作出售依據。'}
 ],
 'yieldStatus':'no_current_sale_listing','yieldNote':'PropertyHub 目前沒有匹配出售掛牌；沒有可核實購入價，因此不計算年投報率。'
}
data=load('bangkok-market-crosschecks.js','BANGKOK_MARKET_CROSSCHECKS')
rows=[x for x in data[2] if int(x['hipflatId'])!=3039]
rows.append(record); rows.sort(key=lambda x:int(x['hipflatId']))
data=(data[0],data[1],rows,data[3]);save(data)
index=DIST/'index.html'; html=index.read_text(encoding='utf-8')
html=re.sub(r'bangkok-market-crosschecks\.js\?v=[^"\']+','bangkok-market-crosschecks.js?v=20261019-sethi-terrace-no-sale',html,count=1)
index.write_text(html,encoding='utf-8')
report=ROOT/'reports/bangkok-coverage-2026-10-19.csv'
with report.open(encoding='utf-8-sig',newline='') as f:
 import csv
 rows=list(csv.DictReader(f)); fields=list(rows[0])
for r in rows:
 if r['hipflat_id']=='3039':
  r['sale_source']=sale_project
  r['missing']='出售（已核對：目前無現行掛牌）'
with report.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(json.dumps(record,ensure_ascii=True))
