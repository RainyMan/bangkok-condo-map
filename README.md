# Bangkok condo map

繁體中文｜[English](README.en.md)｜[ภาษาไทย](README.th.md)

曼谷 Condo 地圖與房產資料探索工具。使用互動地圖瀏覽曼谷 Condo、交通站點、可查證的房源樣本與投資報酬估算。

## 功能

- 在地圖上查看曼谷 Condo 與 BTS、MRT、機場快線及交通船站點。
- 依房型、總價、售價／租金每平方米、年投報率、完工年份、公寓樓高和交通距離篩選及排序。
- 查看 Condo 完工資訊、座標來源、房源樣本與原始來源連結。
- 依一房、兩房的低價與低租金估算年投報率；面積差超過 2 ㎡時，以最低租金每平方米乘最低售價物件面積估算。
- 依地圖縮放範圍載入附近 Condo，並提供步行距離估算。

## 資料與估算

專案資料彙整自 Hipflat、PropertyHub、DDproperty、OpenStreetMap 等來源，並在 Condo 資訊中提供可用的來源連結。座標、房源與完工年份的資料完整度會因專案而異；地圖上的價格和投報率是依可取得的樣本計算，應查看來源頁面核對最新狀態。投報估算不構成投資建議。

OpenStreetMap 地圖資料 © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)。

## 本機預覽

網站是靜態前端，建置後的檔案位於 `dist/`。在專案根目錄執行：

```powershell
cd dist
py -m http.server 4173
```

接著開啟 <http://127.0.0.1:4173/>。

## 資料建置

`scripts/` 收錄瀏覽器資料、交通站點、步行路線及資料覆核的 Python 腳本。更新資料時，請依目標腳本內的說明執行，再使用：

```powershell
py scripts/build_fast_browser_data.py
```

網站部署設定位於 `.openai/hosting.json`，靜態網站目錄為 `dist/`。
