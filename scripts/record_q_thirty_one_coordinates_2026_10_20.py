from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
ID=3351
ENTRY={
  'hipflatId':ID,
  'name':'Q Thirty One',
  'lat':13.734928244081472,
  'lng':100.56678363065794,
  'locationVerified':True,
  'sourceName':'PropertyHub 專案頁地圖座標',
  'sourceUrl':'https://propertyhub.in.th/en/projects/q-thirty-one---17310',
  'verificationMethod':'exact_project_name_match_propertyhub_project_detail_location; coordinate_from_project_location_object',
  'asOf':'2026-10-20'
}
path=DIST/'bangkok-verified-coordinates.js'
text=path.read_text(encoding='utf-8')
pattern=r'(\s*window\.BANGKOK_VERIFIED_COORDINATES\s*=\s*)(\[.*\])(\s*;?\s*)'
m=re.fullmatch(pattern,text,re.S)
if not m: raise RuntimeError('Cannot parse verified coordinate source')
rows=json.loads(m.group(2))
old=next((r for r in rows if int(r.get('hipflatId',-1))==ID),None)
if old:
  if old.get('locationVerified') and (old.get('lat'),old.get('lng'))==(ENTRY['lat'],ENTRY['lng']):
    print('already present'); raise SystemExit(0)
  rows.remove(old)
rows.append(ENTRY); rows.sort(key=lambda r:int(r['hipflatId']))
path.write_text(m.group(1)+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+m.group(3),encoding='utf-8')
report=ROOT/'reports'/'q-thirty-one-coordinate-verification-2026-10-20.json'
report.write_text(json.dumps({'hipflatId':ID,'project':'Q Thirty One','checkedAt':'2026-10-20','coordinates':{'lat':ENTRY['lat'],'lng':ENTRY['lng']},'source':ENTRY['sourceUrl'],'method':ENTRY['verificationMethod'],'marketData':'No direct current sale or rent listing was verified in this pass; do not calculate yield from this coordinate-only update.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':ENTRY['name'],'lat':ENTRY['lat'],'lng':ENTRY['lng'],'previous':old,'coordinateCount':len(rows)},ensure_ascii=False))
