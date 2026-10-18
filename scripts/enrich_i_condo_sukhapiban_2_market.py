from __future__ import annotations
import csv, json
from pathlib import Path
root=Path.cwd(); dist=root/'dist'; reports=root/'reports'
project_id=3251; name='I CONDO Sukhapiban 2'; checked='2026-10-18'
project_url='https://www.hipflat.co.th/en/projects/i-condo-sukhapiban-2-sesfrg'
listing_url='https://www.hipflat.co.th/ads/8cuu0at1817110c37alacc1a3u0h14at'
coord_url='https://www.tperty.com/%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%A1%E0%B8%B4%E0%B9%80%E0%B8%99%E0%B8%B5%E0%B8%A2%E0%B8%A1-%E0%B9%80%E0%B8%99%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%97%E0%B8%B5%E0%B9%88-3105-%E0%B8%95%E0%B8%A3%E0%B8%A1-%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B9%84%E0%B8%AD%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%AA%E0%B8%B8%E0%B8%82-1520310'
corroboration='https://assets.propertyhub.in.th/listings/%E0%B8%82%E0%B8%B2%E0%B8%A2-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99%E0%B8%AA%E0%B8%B9%E0%B8%87-%E0%B8%A7%E0%B8%B4%E0%B8%A7%E0%B8%AA%E0%B8%A7%E0%B8%A2-icondo-sukhapiban-2-31-05-%E0%B8%95%E0%B8%A3%E0%B8%A1-%E0%B9%80%E0%B8%AB%E0%B9%87%E0%B8%99%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%A7%E0%B9%88%E0%B8%B2%E0%B8%A2%E0%B8%99%E0%B9%89%E0%B8%B3---6060509'
lat,lng=13.78338371,100.67113909

def arr(file,sym):
    raw=(dist/file).read_text(encoding='utf-8'); prefix=f'window.{sym} = '
    if not raw.startswith(prefix): raise ValueError(file)
    return json.loads(raw[len(prefix):].strip().rstrip(';'))
def save(file,sym,rows):
    (dist/file).write_text(f'window.{sym} = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

coords=arr('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES')
coord={"hipflatId":project_id,"name":name,"lat":lat,"lng":lng,"locationVerified":True,"sourceName":"Tperty 座標；PropertyHub Google Maps 點位交叉核對","sourceUrl":coord_url,"corroborationSourceUrl":corroboration,"verificationSourceUrl":project_url,"verificationMethod":"Tperty identifies the exact project address between Seri Thai 43 and 45 and publishes coordinates 13.78338371,100.67113909; a separate PropertyHub listing Google Maps pin is 13.783599,100.671184, about 24 m away."}
coords=[x for x in coords if int(x.get('hipflatId',-1))!=project_id]+[coord]
save('bangkok-verified-coordinates.js','BANGKOK_VERIFIED_COORDINATES',coords)

# Prefer the precisely published coordinate over the earlier approximate
# project-page pin so the application selects this verified coordinate row.
guessed=arr('bangkok-propertyhub-guessed-details.js','BANGKOK_PROPERTYHUB_GUESSED_DETAILS')
for row in guessed:
    if int(row.get('hipflatProjectId',-1))==project_id:
        row['lat']=None; row['lng']=None; row['locationVerified']=False
        row['coordinateVerificationNote']='Approximate project-page pin superseded by the direct Tperty coordinate and PropertyHub Google Maps cross-check.'
save('bangkok-propertyhub-guessed-details.js','BANGKOK_PROPERTYHUB_GUESSED_DETAILS',guessed)

routes=arr('bangkok-walk-routes.js','BANGKOK_WALK_ROUTES')
route={"id":project_id,"name":name,"originLat":lat,"originLng":lng,"distanceKm":4.133,"minutes":51,"stationId":"YL09","source":"Valhalla pedestrian routing (30 nearest stations checked)","sourceUrl":"https://valhalla1.openstreetmap.de/","networkSourceUrl":"https://www.openstreetmap.org/copyright","asOf":checked}
routes=[x for x in routes if int(x.get('id',-1))!=project_id]+[route]
save('bangkok-walk-routes.js','BANGKOK_WALK_ROUTES',routes)

rent={"count":3,"observedCount":1,"countKind":"manual_verified_listing","average":7500,"minimum":7500,"minimumArea":31.05,"minimumSampleUpdated":checked,"averageSqm":241.55,"minimumSqm":241.55,"minimumSqmSampleUpdated":checked,"asOf":checked,"sourceName":"Hipflat 已核對直接掛牌（近期更新 1 戶）","source":project_url,"minimumSourceUrl":listing_url,"minimumSqmSourceUrl":listing_url,"samples":[{"id":"U1636514","price":7500,"area":31.05,"priceSqm":241.55,"beds":1,"roomType":"1BR","title":"I CONDO Sukhapiban 2，1 房，31.05 ㎡，฿7,500/月","url":listing_url,"sourceName":"Hipflat（FazWaz Bangkok）","projectName":name,"updated":checked,"checkedAt":checked,"matchedBy":"exact_hipflat_project_and_listing_detail","listingStatus":"active_as_listed"}],"byBedroom":{"1":{"count":1,"minimum":7500,"area":31.05,"priceSqm":241.55,"minimumSqm":241.55,"sourceUrl":listing_url,"minimumSqmSourceUrl":listing_url}}}
manual=arr('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES')
old=next((x for x in manual if int(x.get('hipflatId',-1))==project_id),None)
if old:
    old['rent']=rent
else:
    manual.append({"hipflatId":project_id,"name":name,"rent":rent})
save('bangkok-manual-market-samples.js','BANGKOK_MANUAL_MARKET_SAMPLES',manual)

coord_csv=reports/'coordinate-verification-2026-10-18.csv'
coord_rows=list(csv.reader(coord_csv.open('r',encoding='utf-8-sig',newline='')))
coord_rows=[row for row in coord_rows if len(row)<1 or row[0]!=str(project_id)]
coord_rows.append([str(project_id),name,str(lat),str(lng),coord_url,corroboration,coord['verificationMethod'],''])
with coord_csv.open('w',encoding='utf-8-sig',newline='') as f: csv.writer(f).writerows(coord_rows)
listing_csv=reports/'listing-availability-checks-2026-10-18.csv'
listing_rows=list(csv.reader(listing_csv.open('r',encoding='utf-8-sig',newline='')))
listing_rows=[row for row in listing_rows if len(row)<1 or not (row[0]==str(project_id) and len(row)>3 and row[3]=='rent')]
listing_rows.append([str(project_id),name,checked,'rent','one_recent_exact_project_listing','Hipflat project page lists three rentals; direct listing U1636514 confirms exact project, one bedroom, 31.05 sqm, ฿7,500/month and update 5 hours before check. Two others last updated 2026-09-09 and were excluded. PropertyHub exact-project rental page reports no matched properties.',listing_url,project_url,'https://propertyhub.in.th/en/condo-for-rent/project-i-condo-sukhapiban-2'])
with listing_csv.open('w',encoding='utf-8-sig',newline='') as f: csv.writer(f).writerows(listing_rows)

purchase=1750000; purchase_area=47; monthly=7500/31.05*purchase_area
annual=(monthly*11)-(25*purchase_area*12)
yield_pct=annual/purchase*100
report={"hipflatId":project_id,"projectName":name,"checkedAt":checked,"coordinates":{"lat":lat,"lng":lng,"source":coord_url,"corroboration":corroboration,"method":coord['verificationMethod']},"projectRentalCheck":{"hipflatProjectUrl":project_url,"hipflatAdvertisedCount":3,"includedRecentListings":1,"excludedStaleListingLastUpdate":"2026-09-09","propertyHubRentUrl":"https://propertyhub.in.th/en/condo-for-rent/project-i-condo-sukhapiban-2","propertyHubStatus":"No matched properties for rent"},"rentListing":{"id":"U1636514","bedrooms":1,"monthlyRent":7500,"areaSqm":31.05,"rentPerSqm":round(7500/31.05,2),"url":listing_url,"listingStatus":"active_as_listed"},"twoBedroomSaleBaseline":{"price":purchase,"areaSqm":purchase_area,"bedrooms":2,"sourceUrl":"https://propertyhub.in.th/en/listings/for-sell-condo-icondo-sukhapiban-2-building-a2-floor-4-2-bed-room-room-size-47-sqm--af4a09b3---5515729","sourceCheck":"Direct detail page confirms exact project, 2 beds, 47 sqm, ฿1,750,000; project page refreshed listing 2026-10-17."},"yieldEstimate":{"rentRateFallback":"The only currently recent rent listing is one-bedroom; its per-sqm rate is used as a clearly linked fallback for the two-bedroom purchase baseline because PropertyHub and Hipflat have no recent exact two-bedroom rental sample.","estimatedMonthlyRentAtPurchaseArea":round(monthly,2),"commonFeePerSqmMonthly":25,"deductAgentMonths":1,"netAnnualYieldPercent":round(yield_pct,2)},"notes":["The two other Hipflat rent listings show last updated 2026-09-09 and were not included in current sample statistics.","PropertyHub exact-project rental page states no matched rental properties.","The yield is an estimate with a one-bedroom market rent-rate proxy; a verified two-bedroom rental listing is still needed to produce a same-room-type yield."]}
(reports/f'i-condo-sukhapiban-2-market-{checked}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({"project":name,"coord":f"{lat},{lng}","rentSamples":1,"rentPerSqm":round(7500/31.05,2),"twoBedYieldProxy":round(yield_pct,2)},ensure_ascii=False))
