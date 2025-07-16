# Zeabur OAuth2 部署指南

本指南說明如何將使用 OAuth2 認證的 LINE Bot 部署到 Zeabur。

## 前置作業

1. 確保已完成本地 OAuth2 設定（執行過 `setup_oauth.py`）
2. 確保 `token.pickle` 檔案存在
3. 確保 `app.py` 已改為使用 `GoogleSheetsOAuthHandler`

## 步驟 1：準備 Token Base64 編碼

將 `token.pickle` 轉換為 base64：

```bash
base64 -i token.pickle -o token_base64.txt
```

或在 Windows 使用 PowerShell：
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("token.pickle")) > token_base64.txt
```

## 步驟 2：更新 GitHub Repository

確保以下檔案已提交到 GitHub：
- `app.py` (使用 OAuth 版本)
- `google_sheets_oauth.py`
- `requirements.txt`
- `zbpack.json`
- `runtime.txt`

**注意**：不要提交以下檔案（應在 .gitignore 中）：
- `oauth_credentials.json`
- `token.pickle`
- `.env`
- `token_base64.txt`

## 步驟 3：在 Zeabur 設定環境變數

在 Zeabur 儀表板中設定以下環境變數：

### 必要環境變數
- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Bot 存取權杖
- `LINE_CHANNEL_SECRET` - LINE Bot 密鑰
- `LINE_CHANNEL_ID` - LINE Bot 頻道 ID
- `GOOGLE_SPREADSHEET_ID` - Google Sheets ID
- `GOOGLE_TOKEN_BASE64` - token_base64.txt 的內容（整個內容複製貼上）

### 選用環境變數
- `GOOGLE_DRIVE_FOLDER_ID` - Google Drive 資料夾 ID（如果需要指定上傳位置）

## 步驟 4：部署

1. 在 Zeabur 連接您的 GitHub repository
2. 選擇要部署的分支
3. Zeabur 會自動偵測並開始部署
4. 等待部署完成

## 步驟 5：設定 LINE Webhook URL

部署完成後：
1. 從 Zeabur 取得應用程式 URL
2. 在 LINE Developers Console 設定 Webhook URL：
   ```
   https://your-app.zeabur.app/callback
   ```
3. 啟用 Webhook

## 注意事項

### Token 更新
如果 OAuth token 過期或需要更新：
1. 在本地重新執行 `setup_oauth.py`
2. 重新產生 base64 編碼
3. 在 Zeabur 更新 `GOOGLE_TOKEN_BASE64` 環境變數

### 權限問題
如果遇到權限錯誤：
1. 確認 Google Drive 資料夾 ID 是您個人帳號可存取的
2. 或者清空 `GOOGLE_DRIVE_FOLDER_ID`，讓圖片上傳到根目錄

### 偵錯
查看 Zeabur 的日誌以了解任何錯誤：
- OAuth 認證錯誤通常顯示為 401 或 403
- 檢查環境變數是否正確設定
- 確認 token base64 編碼是否完整複製

## 環境變數總結

```bash
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=你的LINE存取權杖
LINE_CHANNEL_SECRET=你的LINE密鑰
LINE_CHANNEL_ID=你的LINE頻道ID

# Google API 設定
GOOGLE_SPREADSHEET_ID=你的試算表ID
GOOGLE_TOKEN_BASE64=base64編碼的token內容
GOOGLE_DRIVE_FOLDER_ID=你的Drive資料夾ID（選用）
```