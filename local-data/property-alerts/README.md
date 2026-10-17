# 本機每日房源更新

每日排程會在本機更新房源資料，不使用 AI 或模型 token。DDproperty 只讀取網站公開提供的 Condo 出售及出租 RSS；DDproperty 與 PropertyHub 的新房源提醒郵件也可從本機 Outlook、IMAP 或 `.eml` / `.html` 檔匯入。

配對成功且郵件內同時包含 Condo 名稱、房價或月租、面積與房源連結時，資料會出現在本機地圖的 Condo 卡片，並參與出售或出租每平方米最低價及平均值。掛牌以通知日期起算，超過 45 天未收到更新通知，就不再參與地圖售租價格和投報試算；再次收到該掛牌通知會更新日期。無法唯一配對或缺少價格/面積的連結會列在上層 `needs-review.json`，不會猜測所屬 Condo。

掛牌內容和本機產生的資料只保存在這台電腦，不加入版本控制。排程每日上午 08:00 執行；電腦需開機並登入 Windows。若 Outlook classic 不可用，可將提醒郵件存成 `.eml` 放入本資料夾，再執行 `scripts/run_daily_update.ps1`。更新紀錄在上層 `local-data/daily-update.log`。若 DDproperty RSS 被拒絕連線，而且沒有讀到任何提醒郵件或匯入檔，排程會回報失敗，避免把空結果記成成功。

## 啟用自動郵件同步

1. 若要由 IMAP 自動匯入，將 `scripts/mail-settings.example.json` 複製為 `local-data/mail-settings.json`，填入郵件帳號和 IMAP 主機。Gmail 使用 `imap.gmail.com`、993 埠；需在 Google 帳戶建立應用程式密碼。
2. 在 Windows「認證管理員」→「Windows 認證」新增一般認證，網際網路或網路位址填 `BangkokCondoDailyIMAP`，使用者名稱填郵件地址，密碼填郵件應用程式密碼。
3. 在 DDproperty 及 PropertyHub 設定符合目標地區、出售／出租的房源通知，寄到 Outlook/IMAP 收件匣。DDproperty 的 RSS 也由排程每日嘗試讀取；若來源限制連線，錯誤會記在更新結果，郵件提醒可繼續補入。
4. 每日排程會以唯讀方式掃描最近 45 天寄件者網域符合設定的郵件。密碼不會寫入設定檔或程式碼。PropertyHub 未提供可公開使用的房源 RSS；本工具不會自動抓取其網頁。

## 目前來源狀態

若 `local-data/daily-update.log` 顯示 DDproperty 回傳 HTTP 403，代表該次 RSS 讀取被拒絕。此電腦若也沒有 Outlook classic 設定、IMAP 設定檔或匯入的提醒郵件，就不會產生新房源；先完成上面的提醒郵件設定。掛牌逾 45 天未收到更新通知後，會從地圖和投報計算中排除。
