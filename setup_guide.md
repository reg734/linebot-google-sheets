# LINE Bot 設定指南 - 支援儲存控制與圖片上傳

## 功能特色
- ✅ `/save` 命令開始儲存模式
- ✅ `/end` 命令停止儲存模式  
- ✅ 文字訊息儲存到 Google Sheets
- ✅ 圖片自動上傳到 Google Drive 並將連結存到 Google Sheets
- ✅ 只有在儲存模式下才會儲存訊息

## 1. 環境變數設定

建立 `.env` 檔案並填入您的 LINE Bot 資訊：

```
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
LINE_CHANNEL_ID=你的_Channel_ID
GOOGLE_SPREADSHEET_ID=你的_Google_Spreadsheet_ID
GOOGLE_DRIVE_FOLDER_ID=你的_Google_Drive_資料夾_ID (可選)
```

## 2. Google APIs 設定

### 2.1 建立 Google Cloud Project
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用以下 APIs:
   - **Google Sheets API**
   - **Google Drive API**

### 2.2 建立服務帳戶
1. 在 Google Cloud Console 中，前往「API 和服務」>「憑證」
2. 點擊「建立憑證」>「服務帳戶」
3. 填寫服務帳戶詳細資訊
4. 在「金鑰」分頁中，建立新的 JSON 金鑰
5. 下載 JSON 檔案並重新命名為 `credentials.json`，放在專案根目錄

### 2.3 建立 Google Sheets
1. 在 Google Sheets 中建立新的試算表
2. 複製試算表的 ID（URL 中的長字串）
3. 將 ID 填入 `.env` 檔案的 `GOOGLE_SPREADSHEET_ID`
4. 將試算表分享給服務帳戶的 email（在 credentials.json 的 client_email 欄位）

### 2.4 建立 Google Drive 資料夾（可選）
1. 在 Google Drive 中建立新資料夾存放圖片
2. 複製資料夾的 ID（URL 中的長字串）
3. 將 ID 填入 `.env` 檔案的 `GOOGLE_DRIVE_FOLDER_ID`
4. 將資料夾分享給服務帳戶的 email（給予編輯權限）

## 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

## 4. 運行應用程式

```bash
python app.py
```

## 5. 使用說明

### 5.1 基本操作
1. **開始儲存**: 在 LINE 中傳送 `/save` 給 Bot
2. **發送訊息**: 在儲存模式下發送文字訊息或圖片
3. **停止儲存**: 傳送 `/end` 給 Bot

### 5.2 功能說明
- **文字訊息**: 直接儲存到 Google Sheets
- **圖片訊息**: 上傳到 Google Drive，連結儲存到 Google Sheets
- **非儲存模式**: 訊息不會被儲存，Bot 會提示先輸入 `/save`

## 6. 部署到 Zeabur

### 6.1 準備部署檔案
確保專案包含以下檔案：
- `zbpack.json` - Zeabur 建置配置
- `runtime.txt` - Python 版本指定
- `requirements.txt` - Python 依賴套件

### 6.2 準備 Google API 憑證（Base64 編碼）
1. 開啟本機的 `credentials.json` 檔案
2. 將整個檔案內容轉換為 Base64 編碼：
   ```bash
   base64 -i credentials.json
   ```
3. 複製輸出的 Base64 字串

### 6.3 部署步驟
1. 在 [Zeabur 儀表板](https://dash.zeabur.com) 建立新專案
2. 連接您的 Git 倉庫（GitHub/GitLab）
3. 選擇要部署的分支
4. 在 Zeabur 中設定環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ID`
   - `GOOGLE_SPREADSHEET_ID`
   - `GOOGLE_DRIVE_FOLDER_ID` (可選)
   - `GOOGLE_CREDENTIALS_BASE64` （步驟 6.2 產生的 Base64 字串）
5. 部署完成後，複製 Zeabur 提供的 URL

### 6.4 設定 LINE Bot Webhook
1. 複製 Zeabur 提供的部署 URL
2. 在 LINE Developers Console 中設定 Webhook URL：
   ```
   https://your-zeabur-app.zeabur.app/callback
   ```
3. 啟用 Webhook 並關閉自動回覆訊息

## 7. 測試

### 7.1 功能測試步驟
1. 在 LINE 中傳送 `/save` 給你的 Bot
2. Bot 應回覆：「開始儲存模式，接下來的訊息和圖片將會儲存到Google Sheets」
3. 傳送文字訊息，檢查是否儲存到 Google Sheets
4. 傳送圖片，檢查是否上傳到 Google Drive 並在 Sheets 顯示連結
5. 傳送 `/end` 停止儲存模式
6. 再傳送訊息，應該不會被儲存

## 8. 故障排除

### 8.1 常見問題
- **API 權限**: 確保 Google Cloud Project 已啟用 Sheets 和 Drive API
- **服務帳戶權限**: 確認服務帳戶 email 有試算表和 Drive 資料夾的存取權限
- **環境變數**: 檢查所有必要的環境變數都已正確設定
- **Base64 編碼**: 確認 `GOOGLE_CREDENTIALS_BASE64` 包含完整且正確的編碼

### 8.2 除錯步驟
- 檢查 Zeabur 部署日誌以獲取錯誤訊息
- 確認 Webhook URL 設定正確
- 測試 Google APIs 連線是否正常
- 驗證服務帳戶憑證檔案格式

## 9. 需要手動添加的項目

### ⚠️ 重要：以下項目需要您手動設定

#### 9.1 Google Cloud Console 設定
1. **啟用 Google Drive API**：
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 搜尋並啟用「Google Drive API」

2. **服務帳戶權限更新**：
   - 確認服務帳戶包含 Drive 存取權限

#### 9.2 環境變數添加
新增到 `.env` 檔案和 Zeabur 環境變數：
```
GOOGLE_DRIVE_FOLDER_ID=你的_Google_Drive_資料夾_ID
```

#### 9.3 Google Drive 資料夾設定
1. **建立 Google Drive 資料夾**存放圖片
2. **重要**：分享資料夾給服務帳戶 email（給予**編輯器**權限）
   - 在 `credentials.json` 中找到 `client_email` 
   - 右鍵點擊資料夾 → 分享 → 輸入 `client_email` → 選擇「編輯器」
3. **複製資料夾 ID**：
   - 開啟資料夾，從 URL 複製 ID (如：`1Qdn5epmh6Zbl3iSsSu2fEH37hhT_yV-B`)
   - 填入環境變數 `GOOGLE_DRIVE_FOLDER_ID`

#### 9.4 故障排除 - Google Drive 問題

##### 問題一：資料夾權限錯誤 ("File not found")
1. **檢查服務帳戶權限**：
   ```
   確認 credentials.json 中的 client_email 已加入：
   - Google Sheets 的分享清單（編輯器權限）
   - Google Drive 資料夾的分享清單（編輯器權限）
   ```

2. **驗證資料夾 ID**：
   - 確認從正確的 Drive URL 複製 ID
   - 資料夾必須是您自己建立或有權限存取的

##### 問題二：服務帳戶儲存配額限制 ("storageQuotaExceeded")
**症狀**：出現 "Service Accounts do not have storage quota" 錯誤

**解決方案**：
1. **建立共享雲端硬碟** (推薦)：
   - 在 Google Drive 中建立「共享雲端硬碟」
   - 將服務帳戶加入為成員
   - 使用共享雲端硬碟的資料夾 ID

2. **暫時解決方案**：
   - 程式會自動使用 Base64 備用方案
   - 圖片資訊仍會儲存到 Google Sheets
   - 圖片以文字描述方式記錄

##### 問題三：設定共享雲端硬碟
1. **建立共享雲端硬碟**：
   - 前往 Google Drive
   - 左側選單 → 共享雲端硬碟 → 新增
   - 輸入名稱 (如：LINE Bot Images)

2. **添加服務帳戶**：
   - 點擊共享雲端硬碟 → 管理成員
   - 添加服務帳戶 email
   - 權限設為「內容管理員」

3. **取得資料夾 ID**：
   - 在共享雲端硬碟中建立資料夾
   - 複製資料夾 ID 到環境變數