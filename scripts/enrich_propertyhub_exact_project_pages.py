from __future__ import annotations
import concurrent.futures,csv,json,re,sys,time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
import requests
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'; REPORT=ROOT/'reports'/f'propertyhub-project-page-backfill-{date.today().isoformat()}.json'
HEAD={'User-Agent':'BangkokCondoMapResearch/1.0 (public project listing verification)','Accept':'text/html,application/xhtml+xml','Accept-Language':'en,th;q=0.8'}
EXCLUDED={}

def arr(file,symbol):
 t=(DIST/file).read_text(encoding='utf-8'); m=re.search(r'window\.'+re.escape(symbol)+r'\s*=\s*(\[.*\]);',t,re.S)
 if not m: raise RuntimeError(f'Cannot read {symbol}')
 return json.loads(m.group(1))
def write(file,symbol,rows): (DIST/file).write_text(f'window.{symbol} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
def fetch_page(url):
 for n in range(3):
  try:
   r=requests.get(url,headers=HEAD,timeout=(10,35))
   if r.status_code in (429,500,502,503,504): time.sleep(1.5*(n+1)); continue
   r.raise_for_status(); m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',r.text,re.S)
   if not m: return None
   return json.loads(m.group(1))['props']['pageProps']
  except Exception:
   if n<2: time.sleep(1.25*(n+1))
 return None
def parse_market(pid,kind,slug,expected_ph_id):
 allcards=[]; project=None; pages=1; total_count=0
 for page in range(1,11):
  u=f'https://propertyhub.in.th/en/condo-for-{kind}/project-{slug}'+(f'?page={page}' if page>1 else '')
  data=fetch_page(u)
  if not data: return {'kind':kind,'error':'page_unavailable','url':u}
  p=data.get('project') or {}; current_id=str(p.get('id') or '')
  if not project:
   if expected_ph_id and current_id != str(expected_ph_id): return {'kind':kind,'error':'project_id_mismatch','seenProjectId':current_id,'expectedProjectId':str(expected_ph_id)}
   project=p; pagination=(data.get('listings') or {}).get('pagination') or {}; pages=int(pagination.get('totalPages') or 0); total_count=int(pagination.get('totalCount') or 0)
   if pages>10: return {'kind':kind,'error':'too_many_pages','totalPages':pages}
  elif current_id != str(project.get('id')): return {'kind':kind,'error':'pagination_project_mismatch'}
  ads=(data.get('listings') or {}).get('listings') or []
  for a in ads:
   room=a.get('roomInformation') or {}; info=a.get('price') or {}; area=room.get('roomArea'); price=(((info.get('forSale') or {}).get('price')) if kind=='sale' else (((info.get('forRent') or {}).get('monthly') or {}).get('price')))
   listing_id=str(a.get('id') or '')
   if listing_id in EXCLUDED.get((pid,kind),set()): continue
   try: price=float(price); area=float(area)
   except (ValueError,TypeError): continue
   if not (15<=area<=1000 and price>0): continue
   if kind=='sale' and not (10_000<=price<=500_000_000 and 10_000<=price/area<=2_000_000): continue
   if kind=='rent' and not (500<=price<=5_000_000 and 50<=price/area<=20_000): continue
   lid=listing_id; listing_slug=str(a.get('slug') or '')
   if not lid or not listing_slug: continue
   allcards.append({'id':lid,'price':price,'area':area,'priceSqm':round(price/area),'beds':room.get('numberOfBed'),'roomType':room.get('roomType'),'title':str(a.get('title') or '')[:220],'url':f'https://propertyhub.in.th/en/listings/{listing_slug}---{lid}','updated':str(a.get('updatedAt') or a.get('refreshedAt') or '')[:10] or None})
  if page>=max(1,pages): break
 if not project: return {'kind':kind,'error':'missing_project'}
 # Exact property id is the primary identity check; all cards must refer to the same PH project.
 project_ids={str((a.get('project') or {}).get('id') or '') for a in ((data.get('listings') or {}).get('listings') or [])}
 if project_ids and project_ids != {str(project.get('id'))}: return {'kind':kind,'error':'listing_project_id_mismatch'}
 return {'kind':kind,'project':project,'cards':allcards,'totalCount':total_count,'sourceUrl':f'https://propertyhub.in.th/en/condo-for-{kind}/project-{slug}'}
def norm(s): return set(re.findall(r'[a-z0-9]+',str(s or '').lower()))-{'the','condo','condominium','project','residence','residences','apartment','place','tower','bangkok'}
def main():
 global EXCLUDED
 for item in json.loads((ROOT/'scripts'/'propertyhub_listing_exclusions.json').read_text(encoding='utf-8')):
  EXCLUDED.setdefault((int(item['hipflatProjectId']),str(item['kind'])),set()).add(str(item['listingId']))
 projects=arr('bangkok-catalogue.js','BANGKOK_CONDO_CATALOGUE'); project_by_id={int(x['id']):x for x in projects}
 ph=arr('bangkok-propertyhub.js','BANGKOK_PROPERTYHUB_PROJECTS'); ph_by_id={int(x['id']):x for x in ph}
 manual=arr('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES'); manual_by={int(x['hipflatId']):x for x in manual}
 report_rows={int(x['hipflat_id']):x for x in csv.DictReader(open(ROOT/'reports'/f'bangkok-coverage-{date.today().isoformat()}.csv',encoding='utf-8-sig'))}
 tasks=[]
 for pid,row in ph_by_id.items():
  coverage=report_rows.get(pid); project=project_by_id.get(pid); manual_row=manual_by.get(pid,{})
  if not coverage or not project or not row.get('propertyHubProjectUrl'): continue
  slug=urlparse(row['propertyHubProjectUrl']).path.rstrip('/').split('/')[-1]
  if not slug: continue
  kinds=[]
  for kind,label in [('sale','sale_sample'),('rent','rent_sample')]:
   if coverage.get(label)=='no' and not manual_row.get(kind): kinds.append(kind)
  if kinds: tasks.append((pid,slug,str(row.get('propertyHubProjectId') or ''),kinds))
 print(f'Exact PropertyHub project pages to inspect: {len(tasks)}; eligible markets: {sum(len(x[3]) for x in tasks)}',flush=True)
 results=[]
 def work(task):
  pid,slug,expected,kinds=task; out={'pid':pid,'slug':slug,'markets':{},'project':None}
  for kind in kinds:
   data=parse_market(pid,kind,slug,expected)
   if data.get('project'): out['project']=data['project']
   out['markets'][kind]=data
  return out
 done=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  futures=[pool.submit(work,t) for t in tasks]
  for future in concurrent.futures.as_completed(futures):
   item=future.result(); results.append(item); done+=1
   if done%20==0 or done==len(tasks): print(f'Inspected {done}/{len(tasks)} project pages',flush=True)
 good=[]; rejected=[]
 for result in results:
  pid=result['pid']; base=ph_by_id[pid]; cat=project_by_id[pid]; expected=str(base.get('propertyHubProjectId') or '')
  success={k:v for k,v in result['markets'].items() if not v.get('error') and v.get('cards')}
  # If a PropertyHub ID is absent, require a distinctive project-name match before using its data.
  pname=str((result.get('project') or {}).get('nameEnglish') or (result.get('project') or {}).get('name') or '')
  a,b=norm(cat.get('name')),norm(pname)
  overlap=a&b
  identity_ok=bool(expected and str((result.get('project') or {}).get('id'))==expected) or (len(overlap)>=2 or any(len(x)>=7 for x in overlap))
  if result.get('project') and not identity_ok:
   rejected.append({'hipflatId':pid,'hipflatName':cat.get('name'),'propertyHubName':pname,'overlap':sorted(overlap)}); continue
  if result.get('project'): good.append((result,success))
 # Consolidate each direct source market with sample-level links and linked lowest records.
 new_count={'sale':0,'rent':0}; coordinate_count=0; details=arr('bangkok-propertyhub-details.js','BANGKOK_PROPERTYHUB_DETAILS'); detail_by={str(x.get('propertyHubProjectId')):x for x in details if x.get('propertyHubProjectId')}
 verified=arr('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES'); verified_by={int(x['hipflatId']):x for x in verified}
 for result,markets in good:
  pid=result['pid']; cat=project_by_id[pid]; base=ph_by_id[pid]; mm=manual_by.get(pid) or {'hipflatId':pid,'name':cat['name']}; project=result.get('project') or {}
  slug=result['slug']; project_url=f'https://propertyhub.in.th/en/projects/{slug}'
  for kind,data in markets.items():
   cards=data['cards']; low_price=min(cards,key=lambda x:x['price']); low_rate=min(cards,key=lambda x:x['price']/x['area'])
   bybed={}
   for beds in sorted({int(x['beds']) for x in cards if isinstance(x.get('beds'),(int,float)) and x['beds']>0}):
    group=[x for x in cards if x.get('beds')==beds]; lo=min(group,key=lambda x:x['price'])
    bybed[str(beds)]={'count':len(group),'minimum':lo['price'],'area':lo['area'],'priceSqm':lo['priceSqm'],'minimumSqm':round(min(x['price']/x['area'] for x in group)),'sourceUrl':lo['url']}
   mm[kind]={'count':len(cards),'platformCount':data['totalCount'],'observedCount':len(cards),'countKind':'manual_verified_listing','average':round(sum(x['price'] for x in cards)/len(cards)),'minimum':low_price['price'],'minimumArea':low_price['area'],'averageSqm':round(sum(x['priceSqm'] for x in cards)/len(cards)),'minimumSqm':round(low_rate['price']/low_rate['area']),'minimumSampleUpdated':low_price.get('updated'),'minimumSqmSampleUpdated':low_rate.get('updated'),'asOf':date.today().isoformat(),'snapshotMethod':'PropertyHub exact project page, all available listing pages with validated project ID; known exclusions removed','sourceName':'PropertyHub 專案單筆掛牌','source':data['sourceUrl'],'minimumSourceUrl':low_price['url'],'minimumSqmSourceUrl':low_rate['url'],'byBedroom':bybed,'samples':cards}
   mm['replace'+kind.title()]=True; new_count[kind]+=1
  if markets: manual_by[pid]=mm
  p=project or {}; point=p.get('location') or {}; info=p.get('projectInfo') or {}
  try: lat,lng=float(point['lat']),float(point['lng'])
  except (TypeError,ValueError,KeyError): lat=lng=None
  if lat and lng and 13.4<=lat<=14.1 and 100.2<=lng<=101.0:
   base.update({'lat':lat,'lng':lng,'locationVerified':True,'locationSourceName':'PropertyHub 精確專案頁地圖','locationSourceUrl':project_url,'locationVerificationSourceUrl':cat.get('hipflatProjectUrl')})
   verified_by[pid]={'hipflatId':pid,'name':cat['name'],'lat':lat,'lng':lng,'locationVerified':True,'sourceName':'PropertyHub 精確專案頁地圖座標','sourceUrl':project_url,'verificationSourceUrl':cat.get('hipflatProjectUrl'),'verificationMethod':'PropertyHub project ID validated against the catalogue mapping; embedded project point'}
   coordinate_count+=1
  if str(info.get('completedYear','')).isdigit(): base['completedYear']=int(info['completedYear']); base['completedYearSourceUrl']=project_url
  if str(info.get('totalUnits','')).isdigit(): base['units']=int(info['totalUnits'])
  if str(info.get('buildingsFloors','')).isdigit(): base['floors']=int(info['buildingsFloors'])
  try:
   fee=float(info.get('utilityFee'))
   if 1<=fee<=1000: base['fee']={'rate':fee,'status':'published_indicative','note':'PropertyHub 專案頁公布的管理費數值，請向管委會確認。','source':project_url}
  except (ValueError,TypeError): pass
  phid=str(base.get('propertyHubProjectId') or p.get('id') or '')
  if phid:
   detail=detail_by.get(phid,{'propertyHubProjectId':phid,'name':cat['name']}); detail.update({'sourceUrl':project_url,'projectName':p.get('nameEnglish') or p.get('name'),'projectAddress':p.get('address'),'asOf':date.today().isoformat()})
   if lat and lng: detail.update({'lat':lat,'lng':lng,'locationVerified':True,'locationSourceUrl':project_url,'locationSourceName':'PropertyHub 精確專案頁'})
   if base.get('completedYear'): detail.update({'completedYear':base['completedYear'],'completedYearSourceUrl':project_url})
   if base.get('units'): detail['units']=base['units']
   if base.get('floors'): detail['floors']=base['floors']
   if base.get('fee'): detail['fee']=base['fee']
   detail_by[phid]=detail
 manual_out=[manual_by[k] for k in sorted(manual_by)]
 write('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES',manual_out)
 write('bangkok-propertyhub.js','BANGKOK_PROPERTYHUB_PROJECTS',ph)
 write('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES',[verified_by[k] for k in sorted(verified_by)])
 write('bangkok-propertyhub-details.js','BANGKOK_PROPERTYHUB_DETAILS',[detail_by[k] for k in sorted(detail_by)])
 REPORT.write_text(json.dumps({'projectPagesChecked':len(results),'projectsWithMatchedProjectPage':len(good),'projectsWithNewListings':sum(bool(m) for _,m in good),'newSaleMarkets':new_count['sale'],'newRentMarkets':new_count['rent'],'projectCoordinatesFromPropertyHubPages':coordinate_count,'identityMismatchesRejected':rejected,'checkedAt':date.today().isoformat(),'examples':[{'hipflatId':r['pid'],'slug':r['slug'],'sale':('sale' in m),'rent':('rent' in m)} for r,m in good if m][:80]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'checked':len(results),'projectsWithSamples':len(good),'newSaleMarkets':new_count['sale'],'newRentMarkets':new_count['rent'],'verifiedCoordinateSourceCount':coordinate_count,'rejectedIdentityCount':len(rejected),'report':str(REPORT)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
