# Google OAuth2 設定指南

本指南將協助您設定個人 Google 帳戶的 OAuth2 認證，以解決服務帳戶儲存空間不足的問題。

## 步驟 1：取得 OAuth2 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 在左側選單中，前往「API 和服務」>「已啟用的 API」
4. 點擊「啟用 API 和服務」，搜尋並啟用：
   - Google Sheets API
   - Google Drive API

5. 前往「憑證」頁面
6. 點擊「建立憑證」>「OAuth 用戶端 ID」
7. 如果尚未設定同意畫面，請先設定：
   - 選擇「外部」使用者類型
   - 填寫必要資訊（應用程式名稱、使用者支援電子郵件等）
   - 在範圍設定中，新增以下範圍：
     - `.../auth/spreadsheets`
     - `.../auth/drive.file`

8. 建立 OAuth 用戶端：
   - 應用程式類型選擇「電腦版應用程式」
   - 輸入名稱（例如：LINE Bot OAuth）

9. 下載憑證 JSON 檔案
10. 將檔案重新命名為 `oauth_credentials.json` 並放在專案根目錄

## 步驟 2：安裝必要套件

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

## 步驟 3：執行初始授權

```bash
python setup_oauth.py
```

執行後會：
1. 開啟瀏覽器要求您登入 Google 帳號
2. 授權應用程式存取您的 Google Sheets 和 Drive
3. 產生 `token.pickle` 檔案儲存認證

## 步驟 4：修改 app.py

將 app.py 中的匯入修改為使用 OAuth 版本：

```python
# 原本的
from google_sheets import GoogleSheetsHandler

# 改為
from google_sheets_oauth import GoogleSheetsOAuthHandler as GoogleSheetsHandler
```

## 步驟 5：部署注意事項

### 本地開發
- `token.pickle` 會自動更新，無需手動處理
- 請勿將 `oauth_credentials.json` 和 `token.pickle` 提交到版本控制

### 雲端部署
1. 將 `token.pickle` 內容轉換為 base64：
   ```bash
   base64 -i token.pickle -o token_base64.txt
   ```

2. 設定環境變數 `GOOGLE_TOKEN_BASE64` 為上述內容

3. 修改 `google_sheets_oauth.py` 以支援從環境變數讀取 token（如需要）

## 環境變數設定

保持原有的環境變數：
- `GOOGLE_SPREADSHEET_ID`: Google Sheets ID
- `GOOGLE_DRIVE_FOLDER_ID`: （選用）Drive 資料夾 ID

## 優點

使用個人 Google 帳號的 OAuth2 認證有以下優點：

1. **免費儲存空間**：使用您個人帳號的 15GB 免費空間
2. **更高的 API 配額**：個人帳號通常有更高的 API 使用限制
3. **更容易管理**：可以直接在您的 Google Drive 中查看上傳的檔案

## 故障排除

### 認證過期
如果出現認證過期錯誤，重新執行 `setup_oauth.py` 即可。

### 權限不足
確保在建立 OAuth 憑證時已加入正確的範圍（Sheets 和 Drive）。

### token.pickle 遺失
重新執行 `setup_oauth.py` 進行認證。