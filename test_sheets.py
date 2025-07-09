#!/usr/bin/env python3
"""
測試 Google Sheets 連線的腳本
"""

import os
from dotenv import load_dotenv
from google_sheets import GoogleSheetsHandler

def test_google_sheets_connection():
    """測試Google Sheets連線"""
    load_dotenv()
    
    print("測試 Google Sheets 連線...")
    
    # 檢查環境變數
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    if not spreadsheet_id:
        print("❌ 錯誤：未設定 GOOGLE_SPREADSHEET_ID 環境變數")
        return False
    
    try:
        # 建立 Google Sheets 處理器
        sheets_handler = GoogleSheetsHandler()
        
        # 測試建立表頭
        print("建立表頭...")
        if sheets_handler.create_headers():
            print("✅ 表頭建立成功")
        else:
            print("❌ 表頭建立失敗")
            return False
        
        # 測試儲存訊息
        print("測試儲存訊息...")
        if sheets_handler.save_message("test_user", "測試訊息", "text", "2024-01-01 12:00:00"):
            print("✅ 訊息儲存成功")
        else:
            print("❌ 訊息儲存失敗")
            return False
        
        print("✅ Google Sheets 連線測試成功！")
        return True
        
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

if __name__ == "__main__":
    success = test_google_sheets_connection()
    if success:
        print("\n🎉 所有測試通過！您可以開始使用 LINE Bot 了。")
    else:
        print("\n❌ 測試失敗，請檢查設定。")