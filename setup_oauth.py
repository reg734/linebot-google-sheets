#!/usr/bin/env python3
"""
OAuth2 設定腳本
用於初始化 Google API OAuth2 認證
"""

import os
import sys
import logging
from google_sheets_oauth import GoogleSheetsOAuthHandler

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("=== Google OAuth2 設定程式 ===\n")
    
    # 檢查必要的環境變數
    if not os.getenv('GOOGLE_SPREADSHEET_ID'):
        print("錯誤：請先設定 GOOGLE_SPREADSHEET_ID 環境變數")
        print("範例：export GOOGLE_SPREADSHEET_ID='your-spreadsheet-id'")
        sys.exit(1)
    
    # 檢查 OAuth 憑證檔案
    if not os.path.exists('oauth_credentials.json'):
        print("錯誤：找不到 oauth_credentials.json 檔案")
        print("\n請按照以下步驟取得 OAuth2 憑證：")
        print("1. 前往 Google Cloud Console: https://console.cloud.google.com/")
        print("2. 建立新專案或選擇現有專案")
        print("3. 啟用 Google Sheets API 和 Google Drive API")
        print("4. 建立 OAuth 2.0 憑證 (類型選擇 Desktop)")
        print("5. 下載憑證 JSON 檔案並重新命名為 oauth_credentials.json")
        print("6. 將檔案放在此目錄中")
        sys.exit(1)
    
    print("開始 OAuth2 認證流程...")
    print("稍後會開啟瀏覽器要求您授權")
    print("請使用您的個人 Google 帳號登入\n")
    
    try:
        # 建立處理器實例，這會觸發認證流程
        handler = GoogleSheetsOAuthHandler()
        
        print("\n認證成功！")
        print("正在測試連接...")
        
        # 測試連接
        if handler.test_connection():
            print("\n✅ 所有測試通過！")
            print("OAuth2 設定完成，token 已儲存在 token.pickle")
            print("\n現在您可以修改 app.py 來使用 OAuth 認證版本")
        else:
            print("\n❌ 連接測試失敗，請檢查設定")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n錯誤：{e}")
        logger.exception("認證過程發生錯誤")
        sys.exit(1)

if __name__ == "__main__":
    main()