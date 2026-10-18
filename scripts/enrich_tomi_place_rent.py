from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
PROJECT_ID=3010
NAME='Tomi Place'
URL='https://www.renthub.in.th/en/tomi-place'
PROJECT_URL='https://www.hipflat.co.th/en/projects/tomi-place-vyeasl'
PRICE=5900
AREA=25
SAMPLE={'id':'39112','price':PRICE,'area':AREA,'priceSqm':round(PRICE/AREA),'beds':0,'roomType':'STUDIO','title':'Tomi Place，STUDIO，25 ㎡，฿5,900/月','url':URL,'sourceName':'RentHub','projectName':NAME,'checkedAt':'2026-10-18','matchedBy':'exact_project_name_and_bangkok_district_cross_checked_Hipflat_project','listingStatus':'active_as_listed'}
path=DIST/'bangkok-manual-market-samples.js'
m=re.search(r'window\.BANGKOK_MANUAL_MARKET_SAMPLES\s*=\s*(\[.*\]);',path.read_text(encoding='utf-8'),re.S)
rows=json.loads(m.group(1))
project=next((row for row in rows if int(row.get('hipflatId',0))==PROJECT_ID),None)
if project is None:
 project={'hipflatId':PROJECT_ID,'name':NAME};rows.append(project)
rent=project.setdefault('rent',{})
samples=[x for x in rent.get('samples',[]) if x.get('url')!=URL]+[SAMPLE]
rent.update({'count':len(samples),'observedCount':len(samples),'countKind':'manual_verified_listing','average':PRICE,'minimum':PRICE,'minimumArea':AREA,'minimumSampleUpdated':None,'averageSqm':round(PRICE/AREA),'minimumSqm':round(PRICE/AREA),'minimumSqmSampleUpdated':None,'asOf':'2026-10-18','sourceName':'RentHub 個別租賃房源（公寓 Studio；Hipflat 同名專案核對）','source':URL,'minimumSourceUrl':URL,'minimumSqmSourceUrl':URL,'samples':samples})
path.write_text('window.BANGKOK_MANUAL_MARKET_SAMPLES = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
report={'hipflatId':PROJECT_ID,'projectName':NAME,'checkedAt':'2026-10-18','listing':{'source':URL,'hipflatProject':PROJECT_URL,'monthlyRentThb':PRICE,'roomType':'Studio','areaSqm':AREA,'rentThbPerSqmMonth':PRICE/AREA,'RentHubStatus':'Available','RentHubBadges':['Verified listing','Verified structure inspection listing']},'matchingEvidence':'RentHub listing is titled Tomi place in Din Daeng; Hipflat catalogue has the unique Tomi Place project in Din Daeng and describes address 20 Sutthisan Winitchai Rd. Classified as apartment Studio listing because RentHub categorizes this listing as a room/apartment.', 'saleMarket':{'status':'no verified sale listing found; no yield calculated'},'availabilityCaveat':'RentHub reports Available when checked on 2026-10-18; vacancy has not been independently confirmed with the property.'}
(ROOT/'reports'/'tomi-place-rent-enrichment-2026-10-18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'projectId':PROJECT_ID,'monthlyRent':PRICE,'area':AREA,'rentPerSqm':round(PRICE/AREA),'source':URL},ensure_ascii=False))
