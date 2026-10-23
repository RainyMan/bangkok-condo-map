from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'dist'; PID=6495; DAY='2026-10-23'
def read(file,symbol):
 text=(D/file).read_text(encoding='utf-8'); match=re.search(r'window\.'+re.escape(symbol)+r'\s*=\s*(\[.*\]);',text,re.S)
 if not match: raise ValueError(file)
 return json.loads(match.group(1))
def write(file,symbol,rows): (D/file).write_text(f'window.{symbol}='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

def upsert(file,symbol,row,key='hipflatId'):
 rows=read(file,symbol); found=next((i for i,x in enumerate(rows) if x.get(key)==PID),None)
 if found is None: rows.append(row)
 else: rows[found]=row
 write(file,symbol,rows)

hip='https://www.hipflat.co.th/projects/gladden-square-ladprao-15-0cc94l2114779ucl14812e1l94c31lul'
sale_url='https://www.hipflat.co.th/ads/9234011888e189na18t014h13u02u9la'
rent_url='https://www.hipflat.co.th/ads/c4ee449h89aa3hte3h00alac3u0heaa2'
dd_url='https://www.ddproperty.com/en/property/gladden-square-ladprao-15-bangkok-for-sale-11888829'
ph_sale='https://propertyhub.in.th/en/condo-for-sale/project-gladden-square-ladprao-15'
ph_rent='https://propertyhub.in.th/en/condo-for-rent/project-gladden-square-ladprao-15'
fazwaz='https://www.fazwaz.co.th/en/property-rent/1-bedroom-condo-for-rent-at-gladden-square-ladprao-15-in-chomphon-bangkok-u5352529'

manuals=read('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
m=next((x for x in manuals if x.get('hipflatId')==PID),None)
if m is None: raise ValueError('Expected existing sale sample')
hip_sale={'id':'9234011888e189na18t014h13u02u9la','price':3000000,'area':25,'priceSqm':120000,'beds':1,'roomType':'1BR','title':'Gladden Square Ladprao 15 · 1房 · 25㎡ · ฿3,000,000','url':sale_url,'sourceName':'Hipflat 單筆掛牌','projectName':'Gladden Square Ladprao 15','updated':DAY,'checkedAt':DAY,'matchedBy':'Hipflat project page direct listing; exact project name, bedroom, floor and completion match','listingStatus':'active_as_listed'}
hip_rent={'id':'c4ee449h89aa3hte3h00alac3u0heaa2','price':15500,'area':27.6,'priceSqm':561.5942029,'beds':1,'roomType':'1BR','title':'Gladden Square Ladprao 15 · 1房 · 27.6㎡ · ฿15,500/月','url':rent_url,'sourceName':'Hipflat 單筆掛牌','projectName':'Gladden Square Ladprao 15','updated':DAY,'checkedAt':DAY,'matchedBy':'Hipflat project page direct listing; exact project name, bedroom, floor and completion match','listingStatus':'active_as_listed'}
# Refresh/update sale sample; preserve original DDproperty listing as a separate corroborating platform result.
sale=m['sale']; existing_sale=list(sale.get('samples',[])); existing_sale=[x for x in existing_sale if x.get('url')!=sale_url]
sale['samples']=[hip_sale]+existing_sale
sale.update({'count':len(sale['samples']),'observedCount':len(sale['samples']),'countKind':'manual_verified_listing','average':sum(float(x['price']) for x in sale['samples'])/len(sale['samples']),'minimum':3000000,'minimumArea':25,'minimumSourceUrl':sale_url,'averageSqm':sum(float(x['price'])/float(x['area']) for x in sale['samples'])/len(sale['samples']),'minimumSqm':120000,'minimumSqmSourceUrl':sale_url,'minimumSampleUpdated':DAY,'minimumSqmSampleUpdated':DAY,'asOf':DAY,'sourceName':'Hipflat 單筆掛牌 + DDproperty 單筆掛牌','source':hip,'byBedroom':{'1':{'count':len(sale['samples']),'minimum':3000000,'area':25,'minimumArea':25,'priceSqm':120000,'minimumSqm':120000,'minimumSourceUrl':sale_url,'minimumSqmSourceUrl':sale_url,'sourceUrl':sale_url}}})
sale['byBedroom']['1']['count']=sum(1 for x in sale['samples'] if x.get('beds')==1)
# Hipflat shows the rental ad refreshed within the hour; the FazWaz mirror is the same unit ID and is explicitly marked stale.
rent={'count':1,'observedCount':1,'countKind':'manual_verified_listing','average':15500,'minimum':15500,'minimumArea':27.6,'minimumSampleUpdated':DAY,'averageSqm':561.59,'minimumSqm':561.59,'minimumSqmSampleUpdated':DAY,'minimumSourceUrl':rent_url,'minimumSqmSourceUrl':rent_url,'asOf':DAY,'sourceName':'Hipflat 單筆出租掛牌','source':hip,'byBedroom':{'1':{'count':1,'minimum':15500,'area':27.6,'minimumArea':27.6,'minimumSqm':561.59,'minimumSqmRate':15500/27.6,'minimumSqmArea':27.6,'minimumSqmSampleRent':15500,'minimumSourceUrl':rent_url,'minimumSqmSourceUrl':rent_url,'sourceUrl':rent_url}},'samples':[hip_rent]}
m.update({'sale':sale,'rent':rent,'replaceSale':True,'replaceRent':True})
# Existing PH project-map pin and Hipflat exact address jointly back the already plotted coordinate.
m['locationVerificationSourceUrl']=hip
m['locationVerificationNote']='座標採 PropertyHub 精確專案頁位置圖點位；Hipflat 同名專案的完整地址為 Soi Lat Phrao 15 Yaek 3，且樓層與 77 戶資料相符。'
m['completedYear']=2024;m['completedYearSourceUrl']=hip
write('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES',manuals)

# Yield rule: 27.6 sqm rent vs 25 sqm sale = 2.6 sqm difference, so scale rent/sqm to sale area.
scaled=15500/27.6*25
roi=(scaled*11)/3000000*100
cross={'hipflatId':PID,'projectName':'Gladden Square Ladprao 15','asOf':DAY,'sourceName':'Hipflat / DDproperty / PropertyHub cross-check','projectSourceUrl':hip,'sale':{'activeListingCount':2,'observedListingSamples':2,'sourceUrl':hip,'note':'Hipflat 專案頁有 1 張售屋掛牌卡並可開啟單筆；DDproperty 專案頁另列 1 筆出售。跨平台可能是同戶轉載，未將兩筆當作去重後唯一總量。','listings':[hip_sale,{'id':'11888829','price':3390000,'area':28,'priceSqm':121071.43,'bedrooms':1,'listedAt':'2026-10-16','url':dd_url,'sourceName':'DDproperty','listingStatus':'active_as_listed'}]},'rent':{'activeListingCount':1,'observedListingSamples':1,'sourceUrl':hip,'note':'Hipflat 專案頁有 1 張出租掛牌卡且單筆頁標示約 53 分鐘前更新。PropertyHub 與 DDproperty 專案頁本次顯示 0 筆；FazWaz 同 Unit ID U5352529 的鏡像頁標示一年未更新，故不另計樣本。','listings':[hip_rent]},'yieldStatus':'calculated_estimate','yieldNote':'一房最低售價 ฿3,000,000 / 25㎡；最低月租 ฿15,500 / 27.6㎡，面積差 2.6㎡ > 2㎡，按 ฿561.59/㎡/月 × 25㎡ 換算月租 ฿14,039.86。年化按收 11 個月租金估算；未扣管理費（查無可核實費率）。','yieldInputs':[{'bedrooms':1,'lowestSalePrice':3000000,'saleAreaSqm':25,'lowestMonthlyRent':15500,'lowestMonthlyRentAreaSqm':27.6,'areaDifferenceSqm':2.6,'rule':'area differs over 2 sqm; lowest rent per sqm × sale area','rentPerSqmPerMonth':round(15500/27.6,2),'estimatedMonthlyRentAtSaleArea':round(scaled,2),'deductOneAgentMonth':True,'deductManagementFee':False,'managementFeePerSqmPerMonth':None,'netAnnualYieldPercent':round(roi,2)}],'availabilitySources':[{'sourceName':'Hipflat 專案掛牌頁','url':hip,'statusLabel':'頁面顯示 1 售 1 租；兩種掛牌均能開啟對應單筆頁。'},{'sourceName':'Hipflat 出售單筆','url':sale_url,'statusLabel':'1 房、25㎡、฿3,000,000；刊登 2026-03-24，頁面顯示 2026-10-23 核對時約 2 小時前更新。'},{'sourceName':'Hipflat 出租單筆','url':rent_url,'statusLabel':'1 房、27.6㎡、฿15,500/月；刊登 2026-02-12，頁面顯示 2026-10-23 核對時約 53 分鐘前更新。'},{'sourceName':'DDproperty 專案頁','url':'https://www.ddproperty.com/en/project/14392-gladden-square-ladprao-15','statusLabel':'核對時列 1 售、0 租；出售樣本頁面更新日期 2026-10-16。'},{'sourceName':'PropertyHub 專案出租頁','url':ph_rent,'statusLabel':'本次頁面顯示沒有匹配出租物件。'},{'sourceName':'FazWaz 鏡像出租頁','url':fazwaz,'statusLabel':'相同單位 ID U5352529，฿15,500/月、27.6㎡；更新顯示一年以前，當作鏡像交叉參考，不另計新樣本。'}]}
upsert('bangkok-market-crosschecks.js','BANGKOK_MARKET_CROSSCHECKS',cross)
report={'hipflatId':PID,'name':'Gladden Square Ladprao 15','asOf':DAY,'coordinates':{'lat':13.810488006849772,'lng':100.57119485372901,'source':'https://propertyhub.in.th/en/projects/gladden-square-ladprao-15','verification':'PropertyHub 精確專案頁位置圖，Hipflat 專案同名及 Soi Lat Phrao 15 Yaek 3 地址交叉核對。'},'saleSamples':sale['samples'],'rentSample':hip_rent,'yield':cross['yieldInputs'][0],'marketChecks':cross['availabilitySources'],'limitations':['PropertyHub 與 DDproperty 專案頁本次顯示無出租掛牌；Hipflat 直接單筆頁顯示剛更新，採其為當前租金樣本。','FazWaz 同單位鏡像頁顯示一年未更新，未重複計入。','未找到可核實管理費率，投報估值不扣管理費。']}
(ROOT/'reports/gladden-square-ladprao-15-rent-enrichment-2026-10-23.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'saleMinimum':sale['minimum'],'rentMinimum':rent['minimum'],'rentAreaDifferenceSqm':2.6,'normalizedRent':round(scaled,2),'yieldPercent':round(roi,2)},ensure_ascii=False))

