from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
ID=3453
SOURCE='https://yusabuy.com/2017/03/09/poly-place-%E0%B8%9E%E0%B8%AB%E0%B8%A5%E0%B9%82%E0%B8%A2%E0%B8%98%E0%B8%B4%E0%B8%99-23-preview/'
ENTRY={
 'hipflatId':ID,'name':'23 Poly Place @ Phaholyothin 23',
 'lat':13.826450,'lng':100.560900,'locationVerified':True,
 'sourceName':'Yusabuy 專案預覽 GPS 座標', 'sourceUrl':SOURCE,
 'verificationSourceUrl':'https://www.hipflat.co.th/en/projects/23-poly-place-at-phaholyothin-23-jsoslk',
 'verificationMethod':'exact_project_name_and_project_description_match; published_gps_coordinate',
 'asOf':'2026-10-20'
}
path=DIST/'bangkok-verified-coordinates.js'; text=path.read_text(encoding='utf-8')
m=re.fullmatch(r'(\s*window\.BANGKOK_VERIFIED_COORDINATES\s*=\s*)(\[.*\])(\s*;?\s*)',text,re.S)
if not m: raise RuntimeError('Cannot parse verified coordinate source')
rows=json.loads(m.group(2)); old=next((r for r in rows if int(r.get('hipflatId',-1))==ID),None)
if old: rows.remove(old)
rows.append(ENTRY); rows.sort(key=lambda r:int(r['hipflatId']))
path.write_text(m.group(1)+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+m.group(3),encoding='utf-8')
report=ROOT/'reports'/'23-poly-place-coordinate-verification-2026-10-20.json'
report.write_text(json.dumps({'hipflatId':ID,'project':ENTRY['name'],'checkedAt':'2026-10-20','coordinates':{'lat':ENTRY['lat'],'lng':ENTRY['lng']},'source':SOURCE,'crosscheck':ENTRY['verificationSourceUrl'],'method':ENTRY['verificationMethod'],'marketData':'No current direct sale or rent listing was verified in this pass; no ROI calculated.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':ENTRY['name'],'coordinates':[ENTRY['lat'],ENTRY['lng']],'coordinateCount':len(rows)},ensure_ascii=False))
