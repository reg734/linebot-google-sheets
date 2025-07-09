#!/usr/bin/env python3
"""
本地測試啟動腳本
"""

import subprocess
import sys
import time
import os
from dotenv import load_dotenv

def check_environment():
    """檢查環境變數設定"""
    load_dotenv()
    
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET',
        'GOOGLE_SPREADSHEET_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少環境變數：{', '.join(missing_vars)}")
        print("請檢查 .env 檔案並確保所有必要的變數都已設定")
        return False
    
    print("✅ 環境變數檢查通過")
    return True

def check_credentials():
    """檢查 Google API 憑證"""
    if not os.path.exists('credentials.json'):
        print("❌ 找不到 credentials.json 檔案")
        print("請從 Google Cloud Console 下載服務帳戶的 JSON 憑證檔案")
        return False
    
    print("✅ Google API 憑證檔案存在")
    return True

def check_deployment_files():
    """檢查 Zeabur 部署所需檔案"""
    required_files = [
        'zbpack.json',
        'runtime.txt',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少部署檔案：{', '.join(missing_files)}")
        return False
    
    print("✅ Zeabur 部署檔案檢查通過")
    return True

def main():
    """主要執行流程"""
    print("🤖 LINE Bot 本地測試與部署檢查器")
    print("=" * 50)
    
    # 檢查環境變數
    if not check_environment():
        print("\n請先設定環境變數：")
        print("1. 複製 .env.example 為 .env")
        print("2. 填入您的 LINE Bot 資訊")
        return
    
    # 檢查憑證
    if not check_credentials():
        print("\n請先設定 Google API 憑證：")
        print("1. 從 Google Cloud Console 下載服務帳戶 JSON 憑證")
        print("2. 重新命名為 credentials.json")
        return
    
    # 檢查部署檔案
    if not check_deployment_files():
        print("\n缺少 Zeabur 部署所需檔案，請檢查專案設定")
        return
    
    print("\n" + "=" * 50)
    print("🚀 所有檢查通過！")
    print("🌐 您可以：")
    print("1. 本地測試：python app.py")
    print("2. 部署到 Zeabur：推送代碼到 Git 倉庫並在 Zeabur 中部署")
    print("3. 設定 LINE Bot Webhook URL 為您的 Zeabur 應用程式 URL")
    print("=" * 50)
    
    # 詢問是否啟動本地測試
    choice = input("\n是否啟動本地測試？(y/N): ").strip().lower()
    if choice in ['y', 'yes']:
        print("\n🚀 啟動本地測試...")
        print("請按 Ctrl+C 停止服務")
        try:
            subprocess.run([sys.executable, 'app.py'])
        except KeyboardInterrupt:
            print("\n✅ 服務已停止")

if __name__ == "__main__":
    main()