# LINE Bot 設定指南

## 1. 環境變數設定

建立 `.env` 檔案並填入您的 LINE Bot 資訊：

```
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
LINE_CHANNEL_ID=你的_Channel_ID
GOOGLE_SPREADSHEET_ID=你的_Google_Spreadsheet_ID
```

## 2. Google Sheets API 設定

### 2.1 建立 Google Cloud Project
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API

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

## 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

## 4. 運行應用程式

```bash
python app.py
```

## 5. 部署到 Zeabur

### 5.1 準備部署檔案
確保專案包含以下檔案：
- `zbpack.json` - Zeabur 建置配置
- `runtime.txt` - Python 版本指定
- `requirements.txt` - Python 依賴套件

### 5.2 準備 Google API 憑證（Base64 編碼）
1. 開啟本機的 `credentials.json` 檔案
2. 將整個檔案內容轉換為 Base64 編碼：
   ```bash
   base64 -i credentials.json
   ```
3. 複製輸出的 Base64 字串

### 5.3 部署步驟
1. 在 [Zeabur 儀表板](https://dash.zeabur.com) 建立新專案
2. 連接您的 Git 倉庫（GitHub/GitLab）
3. 選擇要部署的分支
4. 在 Zeabur 中設定環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ID`
   - `GOOGLE_SPREADSHEET_ID`
   - `GOOGLE_CREDENTIALS_BASE64` （步驟 5.2 產生的 Base64 字串）
5. 部署完成後，複製 Zeabur 提供的 URL

### 5.4 設定 LINE Bot Webhook
1. 複製 Zeabur 提供的部署 URL
2. 在 LINE Developers Console 中設定 Webhook URL：
   ```
   https://your-zeabur-app.zeabur.app/callback
   ```
3. 啟用 Webhook 並關閉自動回覆訊息

## 6. 測試

在 LINE 中傳送訊息給你的 Bot，檢查是否正確儲存到 Google Sheets。

## 故障排除

- 確保所有環境變數都已正確設定
- 檢查 Google Sheets API 憑證的 Base64 編碼是否正確
- 確認 Zeabur 部署狀態正常且 Webhook URL 正確
- 查看 Zeabur 部署日誌以獲取錯誤訊息
- 確保 `GOOGLE_CREDENTIALS_BASE64` 環境變數包含完整的 Base64 字串