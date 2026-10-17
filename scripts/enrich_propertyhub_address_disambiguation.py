from __future__ import annotations
import concurrent.futures, json, pathlib, re, sys, threading, time, unicodedata
from datetime import date
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import geocode_propertyhub_guess as base

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
RESEARCH = pathlib.Path(r'C:\Users\j654v\Desktop\codex\condo_research\bangkok')
CACHE = RESEARCH / 'propertyhub-guessed-project-details.jsonl'
OUTPUT = DIST / 'bangkok-propertyhub-guessed-details.js'
LOG = RESEARCH / 'propertyhub-address-disambiguation.log'
DISTRICTS = [
 'Pom Prap Sattru Phai','Thawi Watthana','Khlong Sam Wa','Bang Khun Thian','Bang Kho Laem','Saphan Sung',
 'Bangkok Yai','Bangkok Noi','Phaya Thai','Phra Khanong','Ratchathewi','Samphanthawong','Wang Thonglang',
 'Huai Khwang','Khan Na Yao','Lat Krabang','Bueng Kum','Chom Thong','Don Mueang','Nong Chok','Nong Khaem',
 'Pathum Wan','Phasi Charoen','Phra Nakhon','Rat Burana','Taling Chan','Thung Khru','Bang Kapi','Bang Khae',
 'Bang Khen','Bang Na','Bang Phlat','Bang Rak','Bang Sue','Chatuchak','Din Daeng','Dusit','Khlong San','Khlong Toei',
 'Lak Si','Lat Phrao','Min Buri','Prawet','Sai Mai','Sathon','Suan Luang','Thon Buri','Yan Nawa'
]
ALIASES = {'vadhana':'watthana','watthana':'watthana','khet watthana':'watthana','bkk':'bangkok'}

def title_norm(value: str) -> str:
    value = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode().lower()
    value = value.replace('&', ' and ').replace('@', ' at ')
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()

def district(value: str) -> str | None:
    text = title_norm(value)
    for label in sorted(DISTRICTS, key=len, reverse=True):
        needle = title_norm(label)
        if re.search(rf'\b{re.escape(needle)}\b', text):
            return ALIASES.get(needle, needle)
    if re.search(r'\b(vadhana|watthana)\b', text): return 'watthana'
    return None

def resolve(target: dict, source: dict, all_projects: list[dict]) -> bool:
    found_name = source.get('nameEnglish') or source.get('name') or ''
    target_title = title_norm(target.get('name', ''))
    found_title = title_norm(found_name)
    target_district = district(target.get('address', ''))
    found_district = district(source.get('address', ''))
    exact = [p for p in all_projects if title_norm(p.get('name', '')) == found_title]
    if exact:
        candidates = exact
    else:
        actual = base.tokens(found_name)
        if not actual: return False
        scored = []
        for p in all_projects:
            wanted = base.tokens(p.get('name', ''))
            if not wanted: continue
            score = len(wanted & actual) / max(1, len(wanted | actual))
            scored.append((score, p))
        if not scored: return False
        best = max(score for score, _ in scored)
        if best < 0.8: return False
        candidates = [p for score, p in scored if score >= best - 0.02]
    if len(candidates) > 1:
        if not found_district: return False
        candidates = [p for p in candidates if district(p.get('address', '')) == found_district]
    if len(candidates) != 1 or int(candidates[0]['id']) != int(target['id']): return False
    if target_district and found_district and target_district != found_district: return False
    return True

def fetch(row: dict, projects: list[dict]) -> dict:
    target = next((p for p in projects if int(p['id']) == int(row['hipflatProjectId'])), None)
    if not target: return {'id': row['hipflatProjectId'], 'status': 'project_missing'}
    url = f"{base.BASE}/en/projects/{base.slugify(target['name'])}"
    try:
        response = base.requests.get(url, headers=base.HEADERS, timeout=(8, 25))
        if response.status_code != 200: return {'id': int(target['id']), 'status': f'http_{response.status_code}'}
        project = base.find_project(response.text)
        if not project: return {'id': int(target['id']), 'status': 'project_data_missing'}
        point = project.get('location') or {}
        try: lat, lng = float(point.get('lat')), float(point.get('lng'))
        except (TypeError, ValueError): return {'id': int(target['id']), 'status': 'coordinates_missing'}
        if not (13.4 <= lat <= 14.1 and 100.2 <= lng <= 101.0): return {'id': int(target['id']), 'status': 'outside_bangkok'}
        if not resolve(target, project, projects): return {'id': int(target['id']), 'status': 'identity_ambiguous', 'foundName': project.get('nameEnglish') or project.get('name'), 'foundDistrict': district(project.get('address',''))}
        info = project.get('projectInfo') or {}
        result = {'hipflatProjectId': int(target['id']), 'propertyHubProjectId': str(project.get('id') or ''), 'name': target['name'],
            'projectName': project.get('nameEnglish') or project.get('name'), 'projectSlug': project.get('slug') or base.slugify(target['name']),
            'projectAddress': project.get('address'), 'lat': lat, 'lng': lng, 'locationVerified': True,
            'locationSourceName': 'PropertyHub 專案頁（名稱＋行政區核對）', 'locationSourceUrl': url,
            'completedYearSourceUrl': url, 'asOf': date.today().isoformat()}
        if str(info.get('completedYear','')).isdigit(): result['completedYear'] = int(info['completedYear'])
        if str(info.get('totalUnits','')).isdigit(): result['units'] = int(info['totalUnits'])
        if str(info.get('buildingsFloors','')).isdigit(): result['floors'] = int(info['buildingsFloors'])
        fee = re.search(r'(\d+(?:\.\d+)?)', str(info.get('utilityFee') or ''))
        if fee and 1 <= float(fee.group(1)) <= 1000:
            result['fee'] = {'rate': float(fee.group(1)), 'note': 'PropertyHub 專案頁公布數值；現行費率請向管委會確認。', 'source': url, 'status': 'published_indicative'}
        return result
    except base.requests.RequestException:
        return {'id': int(target['id']), 'status': 'request_failed'}

def main() -> int:
    projects = base.read_array(base.CATALOGUE, 'BANGKOK_CONDO_CATALOGUE')
    rows = [json.loads(line) for line in CACHE.read_text(encoding='utf-8').splitlines() if line.strip()]
    targets_by_id = {}
    for row in rows:
        if row.get('status') == 'name_not_unique': targets_by_id[int(row['hipflatProjectId'])] = row
    pending = list(targets_by_id.values())
    print(f'Name-ambiguous PropertyHub project pages to recheck: {len(pending)}', flush=True)
    results=[]; lock=threading.Lock(); done=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(fetch,row,projects) for row in pending]
        for future in concurrent.futures.as_completed(futures):
            item=future.result()
            with lock:
                results.append(item); done+=1
                if done % 50 == 0: print(f'Rechecked {done}/{len(pending)}; uniquely resolved {sum(bool(x.get("locationVerified")) for x in results)}', flush=True)
    accepted=[x for x in results if x.get('locationVerified')]
    existing={int(x['hipflatProjectId']):x for x in base.read_array(OUTPUT,'BANGKOK_PROPERTYHUB_GUESSED_DETAILS')} if OUTPUT.exists() else {}
    for x in accepted: existing[int(x['hipflatProjectId'])]=x
    ordered=sorted(existing.values(),key=lambda x:int(x['hipflatProjectId']))
    tmp=OUTPUT.with_suffix('.js.tmp')
    tmp.write_text('window.BANGKOK_PROPERTYHUB_GUESSED_DETAILS = '+json.dumps(ordered,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    tmp.replace(OUTPUT)
    counts={}
    for x in results: counts[x.get('status','verified')]=counts.get(x.get('status','verified'),0)+1
    summary={'rechecked':len(results),'added':len(accepted),'totalVerified':len(ordered),'statuses':counts}
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    LOG.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0
if __name__ == '__main__': raise SystemExit(main())
