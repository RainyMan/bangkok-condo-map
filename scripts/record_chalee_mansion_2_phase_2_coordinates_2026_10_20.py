from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'; ID=3446
MAP='https://www.google.com/maps/search/?api=1&query=13.7651596069%2C100.6227645874'
ENTRY={'hipflatId':ID,'name':'Chalee Mansion 2 Phase 2','lat':13.7651596069,'lng':100.6227645874,'locationVerified':True,'sourceName':'ZmyHome 專案物件頁 Google Maps 點位','sourceUrl':MAP,'verificationSourceUrl':'https://www.ddproperty.com/en/project/15480-chalee-mansion-2-phase-2','verificationMethod':'exact_project_listing_map_pin_crosschecked_with_same_name_DDproperty_project_and_address','asOf':'2026-10-20'}
path=DIST/'bangkok-verified-coordinates.js'; text=path.read_text(encoding='utf-8'); m=re.fullmatch(r'(\s*window\.BANGKOK_VERIFIED_COORDINATES\s*=\s*)(\[.*\])(\s*;?\s*)',text,re.S)
if not m: raise RuntimeError('Cannot parse coordinate file')
rows=json.loads(m.group(2)); rows=[r for r in rows if int(r.get('hipflatId',-1))!=ID]; rows.append(ENTRY); rows.sort(key=lambda r:int(r['hipflatId']))
path.write_text(m.group(1)+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+m.group(3),encoding='utf-8')
(ROOT/'reports'/'chalee-mansion-2-phase-2-coordinate-verification-2026-10-20.json').write_text(json.dumps({'hipflatId':ID,'project':ENTRY['name'],'checkedAt':'2026-10-20','coordinates':{'lat':ENTRY['lat'],'lng':ENTRY['lng']},'mapPointSource':MAP,'projectIdentityCrosscheck':ENTRY['verificationSourceUrl'],'method':ENTRY['verificationMethod'],'marketData':'No direct current sale or rent sample verified. Older ZmyHome sale records were not treated as active listings; no yield calculated.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'project':ENTRY['name'],'coordinates':[ENTRY['lat'],ENTRY['lng']],'coordinateCount':len(rows)},ensure_ascii=False))
