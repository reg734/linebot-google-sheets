# LINE Bot with Google Sheets Integration

這是一個 LINE Bot 應用程式，可以接收文字訊息和圖片，並將它們儲存到 Google Sheets 中。

## 功能特色

- 接收並回覆 LINE 使用者的文字訊息
- 接收並處理 LINE 使用者傳送的圖片
- 將所有訊息記錄到 Google Sheets
- 安全的憑證管理

## 檔案結構

```
.
├── app.py                 # 主要的 Flask 應用程式
├── google_sheets.py       # Google Sheets API 整合
├── requirements.txt       # Python 依賴套件
├── .env.example          # 環境變數範例
├── .gitignore            # Git 忽略檔案
├── setup_guide.md        # 詳細設定指南
├── test_sheets.py        # Google Sheets 連線測試
├── start_local_test.py   # 本地測試啟動器
└── README.md             # 本檔案
```

## 快速開始

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp .env.example .env
```

編輯 `.env` 檔案，填入您的資訊：

```
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
LINE_CHANNEL_ID=你的_Channel_ID
GOOGLE_SPREADSHEET_ID=你的_Google_Spreadsheet_ID
```

### 3. 設定 Google Sheets API

1. 從 Google Cloud Console 下載服務帳戶 JSON 憑證
2. 重新命名為 `credentials.json` 並放在專案根目錄

### 4. 測試 Google Sheets 連線

```bash
python test_sheets.py
```

### 5. 部署到 Zeabur

1. 在 Zeabur 儀表板建立新專案
2. 連接您的 Git 倉庫
3. 設定環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ID`
   - `GOOGLE_SPREADSHEET_ID`
4. 上傳 `credentials.json` 檔案到專案根目錄
5. 部署完成後，複製 Zeabur 提供的 URL

### 6. 設定 LINE Bot Webhook

1. 複製 Zeabur 提供的部署 URL
2. 在 LINE Developers Console 設定 Webhook URL：
   `https://your-zeabur-app.zeabur.app/callback`
3. 啟用 Webhook

## 使用方式

1. 在 LINE 中傳送文字訊息給您的 Bot
2. 傳送圖片給您的 Bot
3. 檢查 Google Sheets 是否正確記錄了訊息

## 故障排除

- 確保所有環境變數正確設定
- 檢查 Google Sheets API 憑證
- 確認 Zeabur 部署狀態正常
- 查看 Zeabur 部署日誌獲取錯誤訊息

## 安全性

- 所有敏感資訊存放在 `.env` 檔案中
- `.env` 和 `credentials.json` 已加入 `.gitignore`
- 不會將機密資訊提交到版本控制系統

## 詳細設定指南

請參考 `setup_guide.md` 獲取完整的設定說明。