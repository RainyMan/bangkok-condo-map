from __future__ import annotations
import json,re,requests
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'; PID=3336
HEAD={'User-Agent':'Mozilla/5.0 (compatible; BangkokCondoMapResearch/1.0)'}
def load(file,symbol):
 p=DIST/file; t=p.read_text(encoding='utf-8'); m=re.search(r'window\.'+re.escape(symbol)+r'\s*=\s*(\[.*\]);',t,re.S); return p,json.loads(m.group(1))
markets={}
for kind in ('sale','rent'):
 allads=[]; page=1; total=1
 while page<=total:
  url=f'https://propertyhub.in.th/en/condo-for-{kind}/project-metro-park-sathorn-phase-3c?page={page}'
  resp=requests.get(url,headers=HEAD,timeout=30); resp.raise_for_status()
  data=json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',resp.text,re.S).group(1))['props']['pageProps']
  if page==1: project=data['project']; total=int(data['listings']['pagination'].get('totalPages') or 1)
  allads += data['listings']['listings']; page+=1
 cards=[]
 for ad in allads:
  room=ad.get('roomInformation') or {}; area=float(room.get('roomArea') or 0); beds=room.get('numberOfBed')
  pr=ad.get('price') or {}; amount=(pr.get('forSale') or {}).get('price') if kind=='sale' else ((pr.get('forRent') or {}).get('monthly') or {}).get('price')
  try: amount=float(amount)
  except (TypeError,ValueError): continue
  if not (area>0 and amount>0): continue
  slug=ad.get('slug'); lid=ad.get('id')
  if not slug or not lid: continue
  updated=ad.get('updatedAt') or ad.get('refreshedAt') or ''
  cards.append({'id':str(lid),'price':amount,'area':area,'priceSqm':round(amount/area),'beds':beds,'roomType':room.get('roomType'),'title':str(ad.get('title') or '')[:240],'url':f'https://propertyhub.in.th/en/listings/{slug}---{lid}','updated':updated[:10] if updated else None})
 if not cards: continue
 bybed={}
 for bed in {x['beds'] for x in cards if isinstance(x['beds'],(int,float)) and x['beds']>0}:
  group=[x for x in cards if x['beds']==bed]; lo=min(group,key=lambda x:x['price'])
  bybed[str(int(bed))]={'count':len(group),'minimum':lo['price'],'area':lo['area'],'priceSqm':lo['priceSqm'],'minimumSqm':round(min(x['priceSqm'] for x in group)),'sourceUrl':lo['url']}
 totalcount=int(data['listings']['pagination'].get('totalCount') or len(cards))
 byrate=min(cards,key=lambda x:x['price']/x['area']); byprice=min(cards,key=lambda x:x['price'])
 markets[kind]={'count':totalcount,'observedCount':len(cards),'countKind':'manual_verified_listing','average':round(sum(x['price'] for x in cards)/len(cards)),'minimum':byprice['price'],'minimumArea':byprice['area'],'averageSqm':round(sum(x['priceSqm'] for x in cards)/len(cards)),'minimumSqm':round(byrate['priceSqm']),'asOf':'2026-10-18','snapshotMethod':'PropertyHub exact project page, all available paginated listings','sourceName':'PropertyHub 單筆房源','source':f'https://propertyhub.in.th/en/condo-for-{kind}/project-metro-park-sathorn-phase-3c','minimumSourceUrl':byprice['url'],'minimumSqmSourceUrl':byrate['url'],'minimumSampleUpdated':byprice.get('updated'),'minimumSqmSampleUpdated':byrate.get('updated'),'byBedroom':bybed,'samples':cards}
# add to manual market layer
p,rows=load('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES'); row=next((x for x in rows if int(x['hipflatId'])==PID),None)
if row is None: row={'hipflatId':PID,'name':'Metro Park Sathorn Phase 3'}; rows.append(row)
row.update(markets); p.write_text('window.BANGKOK_MANUAL_MARKET_SAMPLES = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
# verified map pin from PropertyHub embedded project map, cross-checked against project identity/name
lat=float(project['location']['lat']); lng=float(project['location']['lng'])
p,coords=load('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES'); rec={'hipflatId':PID,'name':'Metro Park Sathorn Phase 3','lat':lat,'lng':lng,'locationVerified':True,'sourceName':'PropertyHub 專案頁地圖座標','sourceUrl':'https://propertyhub.in.th/en/projects/metro-park-sathorn-phase-3c','verificationSourceUrl':'https://www.hipflat.co.th/en/projects/metro-park-sathorn-phase-3-qzvubr','verificationMethod':'PropertyHub exact project page embedded map point and project name cross-checked against Hipflat'}
old=next((x for x in coords if int(x['hipflatId'])==PID),None)
if old: coords[coords.index(old)]=rec
else: coords.append(rec)
p.write_text('window.BANGKOK_VERIFIED_COORDINATES = '+json.dumps(coords,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
# project completion year, fee, coordinates in research layer (browser copy)
p,props=load('bangkok-propertyhub.js','BANGKOK_PROPERTYHUB_PROJECTS'); base=next(x for x in props if int(x['id'])==PID)
base.update({'lat':lat,'lng':lng,'locationVerified':True,'locationSourceName':'PropertyHub 專案頁地圖座標','locationSourceUrl':'https://propertyhub.in.th/en/projects/metro-park-sathorn-phase-3c','locationVerificationSourceUrl':'https://www.hipflat.co.th/en/projects/metro-park-sathorn-phase-3-qzvubr','propertyHubProjectId':str(project['id']),'propertyHubProjectUrl':'https://propertyhub.in.th/en/projects/metro-park-sathorn-phase-3c','completedYear':int(project['projectInfo']['completedYear']),'completedYearSourceUrl':'https://propertyhub.in.th/en/projects/metro-park-sathorn-phase-3c','fee':({'rate':float(project['projectInfo']['utilityFee']),'status':'public','note':'PropertyHub project page lists this common fee; confirm with juristic office.','source':'https://propertyhub.in.th/en/projects/metro-park-sathorn-phase-3c'} if project['projectInfo'].get('utilityFee') else None)})
for kind in ('sale','rent'): base[kind]=None
p.write_text('window.BANGKOK_PROPERTYHUB_PROJECTS = '+json.dumps(props,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(json.dumps({'project':'Metro Park Sathorn Phase 3C (Hipflat Metro Park Sathorn Phase 3)','hipflatId':PID,'coords':[lat,lng],'completedYear':base['completedYear'],'fee':base.get('fee'),'saleCount':markets['sale']['count'],'rentCount':markets['rent']['count'],'saleMin2BR':markets['sale']['byBedroom'].get('2'),'rentMinRate2BR':min((x['price']/x['area'] for x in markets['rent']['samples'] if x.get('beds')==2),default=None),'salePages':total},ensure_ascii=False,indent=2))






