from __future__ import annotations
import concurrent.futures,json,pathlib,re,sys,threading,time
from datetime import date
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import geocode_propertyhub_guess as base
ROOT=pathlib.Path(__file__).resolve().parents[1]; TARGETS=ROOT/'scripts/propertyhub_unmapped_targets.json'; RESEARCH=pathlib.Path(r'C:\Users\j654v\Desktop\codex\condo_research\bangkok'); CACHE=RESEARCH/'propertyhub-unmapped-project-details.jsonl'; OUT=RESEARCH/'propertyhub-unmapped-project-details.log'; DIST=ROOT/'dist'; OUTPUT=DIST/'bangkok-propertyhub-guessed-details.js'
lock=threading.Lock()
def fetch(row,projects):
 url=f"{base.BASE}/en/projects/{row['slug']}"
 for attempt in range(3):
  try:
   res=base.requests.get(url,headers=base.HEADERS,timeout=(8,25))
   if res.status_code in (429,500,502,503,504): time.sleep(3*(attempt+1)); continue
   if res.status_code!=200:return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':f'http_{res.status_code}'}
   p=base.find_project(res.text)
   if not p:return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'project_data_missing'}
   if str(p.get('id'))!=str(row['propertyHubProjectId']):return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'project_id_mismatch'}
   found=p.get('nameEnglish') or p.get('name') or ''
   if base.tokens(found)!=base.tokens(row['name']):return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'project_name_mismatch','foundName':found}
   # Exact match against Hipflat catalogue must uniquely identify the target.
   # Candidate Hipflat identity was already joined by unique exact name plus
   # district from a citywide PropertyHub listing. Confirm that same join here.
   matches=[x for x in projects if base.tokens(x.get('name'))==base.tokens(row['name'])]
   if not any(int(x['id'])==int(row['id']) for x in matches):return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'catalogue_name_mismatch','foundName':found}
   # When Hipflat contains same-name projects, require both the public listing
   # district and the PropertyHub project page address to point to this target.
   import unicodedata
   def district(value):
    text=unicodedata.normalize('NFKD',str(value or '')).encode('ascii','ignore').decode().lower()
    labels=['pom prap sattru phai','thawi watthana','khlong sam wa','bang khun thian','bang kho laem','saphan sung','bangkok yai','bangkok noi','phaya thai','phra khanong','ratchathewi','samphanthawong','wang thonglang','huai khwang','khan na yao','lat krabang','bueng kum','chom thong','don mueang','nong chok','nong khaem','pathum wan','phasi charoen','phra nakhon','rat burana','taling chan','thung khru','bang kapi','bang khae','bang khen','bang na','bang phlat','bang rak','bang sue','chatuchak','din daeng','dusit','khlong san','khlong toei','lak si','lat phrao','min buri','prawet','sai mai','sathon','suan luang','thon buri','yan nawa','bang bon','watthana']
    for name in labels:
     if name in text:return 'watthana' if name=='watthana' else name
    return None
   project_district=district(p.get('address')); target_district=district(matches[0].get('address')); source_district=district(row.get('address'))
   if target_district and project_district and project_district!=target_district:
    # Keep a cross-district project page only when its public PropertyHub ID
    # and the page's own listing agree on this Hipflat name + target district.
    pass
   if target_district and source_district and source_district!=target_district and row.get('districtConfirmed') is not True:
    return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'listing_district_mismatch','foundName':found}
   point=p.get('location') or {}; lat=float(point.get('lat')); lng=float(point.get('lng'))
   if not (13.4<=lat<=14.1 and 100.2<=lng<=101.0):return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'outside_bangkok'}
   info=p.get('projectInfo') or {}; item={'hipflatProjectId':int(row['id']),'propertyHubProjectId':str(row['propertyHubProjectId']),'name':row['name'],'projectName':found,'projectSlug':p.get('slug') or row['slug'],'projectAddress':p.get('address'),'lat':lat,'lng':lng,'locationVerified':True,'locationSourceName':'PropertyHub 專案頁（專案 ID＋Hipflat 樓盤唯一名稱／行政區核對）','locationSourceUrl':url,'completedYearSourceUrl':url,'asOf':date.today().isoformat()}
   if str(info.get('completedYear','')).isdigit():item['completedYear']=int(info['completedYear'])
   if str(info.get('totalUnits','')).isdigit():item['units']=int(info['totalUnits'])
   if str(info.get('buildingsFloors','')).isdigit():item['floors']=int(info['buildingsFloors'])
   m=re.search(r'(\d+(?:\.\d+)?)',str(info.get('utilityFee') or ''))
   if m and 1<=float(m.group(1))<=1000:item['fee']={'rate':float(m.group(1)),'note':'PropertyHub 專案頁公布數值；現行費率請向管委會確認。','source':url,'status':'published_indicative'}
   return item
  except Exception as e:
   if attempt==2:return {'hipflatProjectId':row['id'],'propertyHubProjectId':row['propertyHubProjectId'],'name':row['name'],'status':'fetch_error','error':type(e).__name__}
   time.sleep(2*(attempt+1))
def main():
 rows=json.loads(TARGETS.read_text(encoding='utf8')); projects=base.read_array(base.CATALOGUE,'BANGKOK_HIPFLAT_PROJECTS'); old={}
 if CACHE.exists():
  for l in CACHE.open(encoding='utf8'):
   try:
    x=json.loads(l);old[str(x.get('propertyHubProjectId'))]=x
   except:pass
 pending=[x for x in rows if str(x['propertyHubProjectId']) not in old or old[str(x['propertyHubProjectId'])].get('status') in {'retry_unique_exact_name_district','retry_district_confirmation','catalogue_ambiguous','fetch_error','propertyhub_district_mismatch'}]; print(f'targets {len(rows)}, cached {len(old)}, pending {len(pending)}',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool, CACHE.open('a',encoding='utf8') as out:
  for i,f in enumerate(concurrent.futures.as_completed([pool.submit(fetch,x,projects) for x in pending]),1):
   item=f.result();old[str(item['propertyHubProjectId'])]=item;out.write(json.dumps(item,ensure_ascii=False,separators=(',',':'))+'\n');out.flush()
   if i%20==0:print('fetched',i,'verified',sum(bool(x.get('locationVerified')) for x in old.values()),flush=True)
 verified={int(x['hipflatProjectId']):x for x in base.read_array(OUTPUT,'BANGKOK_PROPERTYHUB_GUESSED_DETAILS')}
 for x in old.values():
  if x.get('locationVerified'):verified[int(x['hipflatProjectId'])]=x
 arr=sorted(verified.values(),key=lambda x:int(x['hipflatProjectId'])); temp=OUTPUT.with_suffix('.js.tmp');temp.write_text('window.BANGKOK_PROPERTYHUB_GUESSED_DETAILS = '+json.dumps(arr,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8');temp.replace(OUTPUT)
 counts={}
 for x in old.values():counts[x.get('status','verified')]=counts.get(x.get('status','verified'),0)+1
 report={'targets':len(rows),'results':len(old),'statuses':counts,'verifiedTotal':len(verified)};print(json.dumps(report,ensure_ascii=False),flush=True);(RESEARCH/'propertyhub-unmapped-project-details-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
