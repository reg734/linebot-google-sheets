import os
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsHandler:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')
        self.RANGE_NAME = 'A:E'  # 預設範圍: A到E欄
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Google Sheets API 認證 - 使用服務帳戶"""
        try:
            # 優先從環境變數讀取憑證
            google_credentials = os.getenv('GOOGLE_CREDENTIALS')
            google_credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
            
            if google_credentials_base64:
                try:
                    # 從 Base64 編碼的環境變數讀取憑證
                    decoded_credentials = base64.b64decode(google_credentials_base64).decode('utf-8')
                    credentials_info = json.loads(decoded_credentials)
                    creds = Credentials.from_service_account_info(
                        credentials_info, scopes=self.SCOPES)
                    logger.info("使用 Base64 編碼的 Google API 憑證")
                    return build('sheets', 'v4', credentials=creds)
                except Exception as e:
                    logger.error(f"Base64 憑證解碼失敗: {e}")
                    # 繼續嘗試其他方法
            
            if google_credentials:
                try:
                    # 處理可能的 JSON 轉義問題
                    if google_credentials.startswith('"') and google_credentials.endswith('"'):
                        # 如果被額外引號包圍，移除它們
                        google_credentials = google_credentials[1:-1]
                    
                    # 處理轉義的引號和換行符
                    google_credentials = google_credentials.replace('\\"', '"').replace('\\n', '\n')
                    
                    # 從環境變數讀取 JSON 憑證
                    credentials_info = json.loads(google_credentials)
                    creds = Credentials.from_service_account_info(
                        credentials_info, scopes=self.SCOPES)
                    logger.info("使用環境變數中的 Google API 憑證")
                    return build('sheets', 'v4', credentials=creds)
                except json.JSONDecodeError as e:
                    logger.error(f"Google API 憑證 JSON 格式錯誤: {e}")
                    logger.error(f"憑證內容長度: {len(google_credentials)}")
                    logger.error(f"憑證開頭: {google_credentials[:100]}...")
                    # 繼續嘗試其他方法
            
            # 如果環境變數不存在，嘗試從檔案讀取（本地開發用）
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file(
                    'credentials.json', scopes=self.SCOPES)
                logger.info("使用本地 credentials.json 檔案")
                return build('sheets', 'v4', credentials=creds)
            
            # 如果所有方法都失敗
            raise FileNotFoundError(
                "找不到 Google API 憑證。請設定 GOOGLE_CREDENTIALS_BASE64 或 GOOGLE_CREDENTIALS 環境變數，或提供 credentials.json 檔案"
            )
                
        except json.JSONDecodeError as e:
            logger.error(f"Google API 憑證 JSON 格式錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"Google Sheets 認證失敗: {e}")
            raise
    
    def save_message(self, user_id, message, message_type, timestamp):
        """儲存訊息到Google Sheets"""
        try:
            values = [
                [timestamp, user_id, message_type, message, '']
            ]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=self.RANGE_NAME,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Message saved to Google Sheets: {result.get('updates', {}).get('updatedCells', 0)} cells updated")
            return True
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return False
        except Exception as error:
            logger.error(f"Error saving message: {error}")
            return False
    
    def save_image(self, user_id, image_data, message_id, timestamp):
        """儲存圖片資訊到Google Sheets"""
        try:
            # 將圖片轉換為base64編碼
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 為了避免Google Sheets單一儲存格的限制，我們只儲存圖片的基本資訊
            # 實際應用中可以將圖片上傳到雲端儲存服務並儲存URL
            image_info = f"Image ID: {message_id}, Size: {len(image_data)} bytes"
            
            values = [
                [timestamp, user_id, 'image', image_info, f"[IMAGE_DATA_BASE64_TRUNCATED]"]
            ]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=self.RANGE_NAME,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Image info saved to Google Sheets: {result.get('updates', {}).get('updatedCells', 0)} cells updated")
            return True
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return False
        except Exception as error:
            logger.error(f"Error saving image: {error}")
            return False
    
    def create_headers(self):
        """建立Google Sheets的表頭"""
        try:
            headers = [['時間戳記', '使用者ID', '訊息類型', '內容', '額外資訊']]
            
            body = {
                'values': headers
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.SPREADSHEET_ID,
                range='A1:E1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info("Headers created in Google Sheets")
            return True
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return False
        except Exception as error:
            logger.error(f"Error creating headers: {error}")
            return False