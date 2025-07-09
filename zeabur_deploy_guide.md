# Zeabur 部署指南

## 前置準備

1. **建立 Git 倉庫**
   - 在 GitHub 或 GitLab 上建立新的倉庫
   - 將專案代碼推送到倉庫

2. **準備必要檔案**
   確保專案包含以下檔案：
   - `app.py` - 主應用程式
   - `google_sheets.py` - Google Sheets 整合
   - `requirements.txt` - Python 依賴套件
   - `zbpack.json` - Zeabur 建置配置
   - `runtime.txt` - Python 版本指定
   - `credentials.json` - Google API 憑證（需要手動上傳）
   - `.env` - 環境變數（不會被提交到 Git）

## 部署步驟

### 1. 建立 Zeabur 專案

1. 前往 [Zeabur 儀表板](https://dash.zeabur.com)
2. 點擊「建立新專案」
3. 選擇「從 Git 倉庫部署」
4. 選擇您的 Git 提供商（GitHub/GitLab）
5. 選擇要部署的倉庫和分支

### 2. 設定環境變數

在 Zeabur 專案設定中添加以下環境變數：

```
LINE_CHANNEL_ACCESS_TOKEN=您的_Channel_Access_Token
LINE_CHANNEL_SECRET=您的_Channel_Secret
LINE_CHANNEL_ID=您的_Channel_ID
GOOGLE_SPREADSHEET_ID=您的_Google_Spreadsheet_ID
```

### 3. 上傳 Google API 憑證

由於 `credentials.json` 包含敏感資訊，不應提交到 Git 倉庫：

1. 在 Zeabur 專案中，找到檔案管理功能
2. 手動上傳 `credentials.json` 到專案根目錄
3. 確保檔案路徑正確為 `/credentials.json`

### 4. 部署設定

Zeabur 會自動讀取 `zbpack.json` 設定：

```json
{
  "build_command": "pip install -r requirements.txt",
  "start_command": "python app.py"
}
```

### 5. 完成部署

1. 點擊「部署」按鈕
2. 等待建置完成
3. 部署成功後，複製 Zeabur 提供的 URL

## 設定 LINE Bot Webhook

### 1. 取得 Webhook URL

部署完成後，您的 Webhook URL 格式為：
```
https://your-app-name.zeabur.app/callback
```

### 2. 設定 LINE Developers Console

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 選擇您的 Messaging API Channel
3. 在「Messaging API」分頁中找到「Webhook settings」
4. 填入 Webhook URL：`https://your-app-name.zeabur.app/callback`
5. 點擊「Update」
6. 啟用「Use webhook」
7. 關閉「Auto-reply messages」

### 3. 驗證設定

點擊「Verify」按鈕測試 Webhook 連接是否正常。

## 測試部署

1. 在 LINE 中傳送訊息給您的 Bot
2. 檢查 Google Sheets 是否正確記錄了訊息
3. 檢查 Zeabur 的部署日誌是否有錯誤

## 故障排除

### 常見問題

1. **部署失敗**
   - 檢查 `requirements.txt` 是否正確
   - 確認 `zbpack.json` 設定正確
   - 查看 Zeabur 建置日誌

2. **環境變數問題**
   - 確認所有必要的環境變數都已設定
   - 檢查變數名稱是否正確

3. **Google API 認證失敗**
   - 確認 `credentials.json` 已正確上傳
   - 檢查服務帳戶權限是否正確
   - 確認 Google Sheets 已分享給服務帳戶

4. **LINE Bot 無回應**
   - 檢查 Webhook URL 是否正確
   - 確認 LINE Bot 設定中的 Webhook 已啟用
   - 查看 Zeabur 應用程式日誌

### 查看日誌

在 Zeabur 儀表板中：
1. 進入您的專案
2. 點擊「日誌」分頁
3. 查看即時日誌輸出

## 更新部署

當您需要更新代碼時：
1. 推送新代碼到 Git 倉庫
2. Zeabur 會自動重新部署
3. 等待部署完成

## 成本考量

- Zeabur 提供免費額度，超過後會收費
- 建議監控使用量避免意外費用
- 可以設定使用量警告通知