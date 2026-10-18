"""Add exact PropertyHub sale and rent listings for Motive Condominium Chaengwattana."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
ID=3537
NAME='Motive Condominium Chaengwattana'
CHECKED='2026-10-18'
SALE_PROJECT='https://propertyhub.in.th/en/condo-for-sale/project-motive-condominium-chaengwattana'
RENT_PROJECT='https://propertyhub.in.th/en/condo-for-rent/project-motive-condominium-chaengwattana'
SALE_URL='https://propertyhub.in.th/en/listings/a010466-motive-condominium-chaengwattana---6428940'
RENT_URL='https://propertyhub.in.th/listings/รวมคอนโดนนนทบุรีให้เช่า️⚠️🛋️🛌motive-แจ้งวัฒนะ---4165911'
def read(path,symbol):
 m=re.search(r'window\.'+re.escape(symbol)+r' = (\[.*\]);',path.read_text(encoding='utf-8'),re.S)
 if not m: raise RuntimeError('missing '+symbol)
 return json.loads(m.group(1))
updates='2026-10-17'
sale={'id':'6428940','price':1750000,'area':27.97,'priceSqm':round(1750000/27.97),'beds':1,'roomType':'1BR','title':'A010466 Motive Condominium Chaengwattana，1 房，27.97 ㎡，3 樓，฿1,750,000','url':SALE_URL,'sourceName':'PropertyHub','projectName':NAME,'checkedAt':CHECKED,'updated':'2026-10-10','matchedBy':'exact_project_and_individual_listing_detail','listingStatus':'active_as_listed'}
rent={'id':'4165911','price':7500,'area':29,'priceSqm':round(7500/29,2),'beds':1,'roomType':'1BR','title':'Motive Condominium Chaengwattana，1 房，29 ㎡，7 樓，฿7,500/月','url':RENT_URL,'sourceName':'PropertyHub','projectName':NAME,'checkedAt':CHECKED,'updated':updates,'matchedBy':'exact_project_card_and_individual_listing_detail','listingStatus':'availability_unconfirmed_date_unknown'}
record={'hipflatId':ID,'name':NAME,'asOf':CHECKED,'replaceSale':True,'sale':{'count':1,'observedCount':1,'countKind':'manual_verified_listing','average':1750000,'minimum':1750000,'minimumArea':27.97,'minimumSampleUpdated':'2026-10-10','averageSqm':round(1750000/27.97),'minimumSqm':round(1750000/27.97),'minimumSqmSampleUpdated':'2026-10-10','asOf':CHECKED,'sourceName':'PropertyHub 已核對單筆掛牌','source':SALE_PROJECT,'minimumSourceUrl':SALE_URL,'minimumSqmSourceUrl':SALE_URL,'byBedroom':{'1':{'count':1,'minimum':1750000,'area':27.97,'minimumSqm':round(1750000/27.97),'sourceUrl':SALE_URL}},'samples':[sale]},'rent':{'count':2,'observedCount':1,'countKind':'manual_verified_listing','average':7500,'minimum':7500,'minimumArea':29,'minimumSampleUpdated':updates,'averageSqm':259,'minimumSqm':round(7500/29),'minimumSqmSampleUpdated':updates,'asOf':CHECKED,'sourceName':'PropertyHub 專案頁可見掛牌，核對一筆詳情','source':RENT_PROJECT,'minimumSourceUrl':RENT_URL,'minimumSqmSourceUrl':RENT_URL,'byBedroom':{'1':{'count':1,'minimum':7500,'area':29,'minimumSqm':round(7500/29,2),'sourceUrl':RENT_URL}},'samples':[rent]},'fee':{'rate':35,'status':'public','note':'PropertyHub 專案頁刊載管理費 ฿35/㎡/月；向管委會確認目前費率。','source':'https://propertyhub.in.th/en/projects/motive-condominium-chaengwattana'}}
p=DIST/'bangkok-manual-market-samples.js'; rows=read(p,'BANGKOK_MANUAL_MARKET_SAMPLES')
rows=[x for x in rows if int(x.get('hipflatId',0))!=ID]; rows.append(record); rows.sort(key=lambda x:int(x['hipflatId']))
p.write_text('window.BANGKOK_MANUAL_MARKET_SAMPLES = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
monthly=7500/29*27.97
fee=35*27.97*12
yield_pct=(monthly*11-fee)/1750000*100
report={'hipflatId':ID,'projectName':NAME,'checkedAt':CHECKED,'saleProjectSource':SALE_PROJECT,'saleListing':sale,'rentProjectSource':RENT_PROJECT,'rentListing':rent,'feeSource':record['fee']['source'],'defaultYieldEstimate':{'bedrooms':1,'purchasePrice':1750000,'purchaseAreaSqm':27.97,'sourceRentMonthly':7500,'sourceRentAreaSqm':29,'estimatedMonthlyRentAtPurchaseArea':round(monthly,2),'commonFeePerSqmMonthly':35,'deductAgentMonths':1,'annualRentAfterAgent':round(monthly*11,2),'annualCommonFee':round(fee,2),'netAnnualYieldPercent':round(yield_pct,4)},'notes':['PropertyHub exact project sale page showed A010466 at ฿1,750,000, 27.97 sqm, 1 bedroom and floor 3, refreshed 2026-10-10; direct listing details confirm the project and unit data.','The other lower-looking sale listing was excluded: its direct title, location, BTS Wongwian Yai, Intharaphithak Road, building A and 23rd floor identify Motif Condo Sathorn-Wongwian Yai, a distinct project that PropertyHub cross-linked to Motive Chaengwattana.','PropertyHub exact project rent page showed two listings, including a 1-bedroom, 29 sqm, ฿7,500/month card refreshed 2026-10-17. The direct listing page confirms project, rent, size, room type and floor; its own last-update field is blank, so availability remains unconfirmed. Only this one rental detail was manually verified.','The PropertyHub project page lists common fee ฿35/sqm/month, 2014 completion, 391 units and 8 floors.','Default net yield uses the lowest verified 1-bedroom sale total and its 27.97 sqm area; rent rate (฿7,500/29 sqm) is scaled to that area. It deducts one agent month and 12 months of common fee; net annual yield is approximately 3.88%.']}
(ROOT/'reports'/'motive-chaengwattana-market-2026-10-18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('saved exact Motive sale/rent samples and ROI',round(yield_pct,2),'%')
