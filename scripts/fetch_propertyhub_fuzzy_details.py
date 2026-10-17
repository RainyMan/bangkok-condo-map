from __future__ import annotations
import concurrent.futures,json,pathlib,re,sys,threading,time,unicodedata
from datetime import date
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import geocode_propertyhub_guess as base
ROOT=pathlib.Path(__file__).resolve().parents[1]; RESEARCH=pathlib.Path(r'C:\Users\j654v\Desktop\codex\condo_research\bangkok'); TARGETS=RESEARCH/'propertyhub-fuzzy-project-targets.json'; CACHE=RESEARCH/'propertyhub-fuzzy-project-details.jsonl'; OUTPUT=ROOT/'dist/bangkok-propertyhub-guessed-details.js'
def norm(value):return re.sub(r'[^a-z0-9]+',' ',str(value or '').lower()).strip()
DISTRICTS=['pom prap sattru phai','thawi watthana','khlong sam wa','bang khun thian','bang kho laem','saphan sung','bangkok yai','bangkok noi','phaya thai','phra khanong','ratchathewi','samphanthawong','wang thonglang','huai khwang','khan na yao','lat krabang','bueng kum','chom thong','don mueang','nong chok','nong khaem','pathum wan','phasi charoen','phra nakhon','rat burana','taling chan','thung khru','bang kapi','bang khae','bang khen','bang na','bang phlat','bang rak','bang sue','chatuchak','din daeng','dusit','khlong san','khlong toei','lak si','lat phrao','min buri','prawet','sai mai','sathon','suan luang','thon buri','yan nawa','bang bon','watthana']
def district(value):
 text=norm(unicodedata.normalize('NFKD',str(value or '')).encode('ascii','ignore').decode())
 for label in sorted(DISTRICTS,key=len,reverse=True):
  if re.search(rf'\b{re.escape(label)}\b',text):return 'watthana' if label=='watthana' else label
 return None
def fetch(row):
 url=row['candidateSourceUrl']
 for attempt in range(3):
  try:
   res=base.requests.get(url,headers=base.HEADERS,timeout=(8,25))
   if res.status_code in (429,500,502,503,504):time.sleep(3*(attempt+1));continue
   if res.status_code!=200:return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':f'http_{res.status_code}'}
   project=base.find_project(res.text)
   if not project:return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'project_data_missing'}
   if str(project.get('id'))!=str(row['propertyHubProjectId']):return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'project_id_mismatch'}
   found=project.get('nameEnglish') or project.get('name') or ''
   if norm(found)!=norm(row['propertyHubName']):return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'page_name_mismatch','foundName':found}
   # The project page district, when supplied, must agree with the Hipflat
   # project's district and the 80% majority district in citywide listing cards.
   page_district=district(project.get('address')); target_district=row['district']
   if page_district and page_district!=target_district:return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'page_district_mismatch','pageDistrict':page_district,'targetDistrict':target_district}
   point=project.get('location') or {}
   try:lat,lng=float(point.get('lat')),float(point.get('lng'))
   except (TypeError,ValueError):return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'coordinates_missing'}
   if not (13.4<=lat<=14.1 and 100.2<=lng<=101.0):return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'outside_bangkok'}
   info=project.get('projectInfo') or {}; result={'hipflatProjectId':int(row['hipflatProjectId']),'propertyHubProjectId':str(row['propertyHubProjectId']),'name':row['hipflatName'],'projectName':found,'propertyHubListingProjectName':row['propertyHubName'],'projectSlug':project.get('slug') or url.rstrip('/').rsplit('/',1)[-1],'projectAddress':project.get('address'),'lat':lat,'lng':lng,'locationVerified':True,'coordinateSourceVerified':True,'identityMatchMethod':'exact_propertyhub_id_plus_high_confidence_name_and_listing_district','identityMatchScore':row['nameScore'],'listingDistrictShare':row['districtShare'],'locationSourceName':'PropertyHub 專案頁（ID＋樓盤名近似度＋掛牌行政區核對）','locationSourceUrl':url,'completedYearSourceUrl':url,'asOf':date.today().isoformat()}
   if str(info.get('completedYear','')).isdigit():result['completedYear']=int(info['completedYear'])
   if str(info.get('totalUnits','')).isdigit():result['units']=int(info['totalUnits'])
   if str(info.get('buildingsFloors','')).isdigit():result['floors']=int(info['buildingsFloors'])
   fee=re.search(r'(\d+(?:\.\d+)?)',str(info.get('utilityFee') or ''))
   if fee and 1<=float(fee.group(1))<=1000:result['fee']={'rate':float(fee.group(1)),'note':'PropertyHub 專案頁公布數值；現行費率請向管委會確認。','source':url,'status':'published_indicative'}
   return result
  except Exception as e:
   if attempt==2:return {'hipflatProjectId':row['hipflatProjectId'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['hipflatName'],'status':'fetch_error','error':type(e).__name__}
   time.sleep(2*(attempt+1))
def main():
 targets=json.loads(TARGETS.read_text(encoding='utf8'));cache={}
 if CACHE.exists():
  for line in CACHE.open(encoding='utf8'):
   try:
    x=json.loads(line);cache[str(x['propertyHubProjectId'])]=x
   except (ValueError,KeyError):pass
 pending=[x for x in targets if str(x['propertyHubProjectId']) not in cache];print('fuzzy candidates',len(targets),'cached',len(cache),'pending',len(pending),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool,CACHE.open('a',encoding='utf8') as out:
  futures=[pool.submit(fetch,x) for x in pending]
  for i,f in enumerate(concurrent.futures.as_completed(futures),1):
   item=f.result();cache[str(item['propertyHubProjectId'])]=item;out.write(json.dumps(item,ensure_ascii=False,separators=(',',':'))+'\n');out.flush()
   if i%15==0:print('fetched',i,'verified',sum(bool(x.get('locationVerified')) for x in cache.values()),flush=True)
 verified={int(x['hipflatProjectId']):x for x in base.read_array(OUTPUT,'BANGKOK_PROPERTYHUB_GUESSED_DETAILS')}
 added=0
 for x in cache.values():
  if not x.get('locationVerified'):continue
  pid=int(x['hipflatProjectId']);previous=verified.get(pid,{})
  # Preserve prior source facts where the verified page omits them.
  verified[pid]={**previous,**x};added+=1
 rows=sorted(verified.values(),key=lambda x:int(x['hipflatProjectId']));tmp=OUTPUT.with_suffix('.js.tmp');tmp.write_text('window.BANGKOK_PROPERTYHUB_GUESSED_DETAILS = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8');tmp.replace(OUTPUT)
 statuses={}
 for x in cache.values():statuses[x.get('status','verified')]=statuses.get(x.get('status','verified'),0)+1
 report={'fuzzyCandidates':len(targets),'checked':len(cache),'verifiedFuzzy':sum(bool(x.get('locationVerified')) for x in cache.values()),'verifiedTotalDetails':sum(bool(x.get('locationVerified')) for x in verified.values()),'statuses':statuses,'appRowsWritten':len(rows)}
 (RESEARCH/'propertyhub-fuzzy-project-details-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
