import os
import base64
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsHandler:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')
        self.DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')  # 可選，用於指定儲存資料夾
        self.RANGE_NAME = 'A:E'  # 預設範圍: A到E欄
        self.service = self._authenticate()
        self.drive_service = self._authenticate_drive()
    
    def _get_credentials(self):
        """取得 Google API 憑證"""
        # 優先從環境變數讀取憑證
        google_credentials = os.getenv('GOOGLE_CREDENTIALS')
        google_credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
        
        if google_credentials_base64:
            try:
                # 從 Base64 編碼的環境變數讀取憑證
                decoded_credentials = base64.b64decode(google_credentials_base64).decode('utf-8')
                credentials_info = json.loads(decoded_credentials)
                return Credentials.from_service_account_info(
                    credentials_info, scopes=self.SCOPES)
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
                return Credentials.from_service_account_info(
                    credentials_info, scopes=self.SCOPES)
            except json.JSONDecodeError as e:
                logger.error(f"Google API 憑證 JSON 格式錯誤: {e}")
                logger.error(f"憑證內容長度: {len(google_credentials)}")
                logger.error(f"憑證開頭: {google_credentials[:100]}...")
                # 繼續嘗試其他方法
        
        # 如果環境變數不存在，嘗試從檔案讀取（本地開發用）
        if os.path.exists('credentials.json'):
            return Credentials.from_service_account_file(
                'credentials.json', scopes=self.SCOPES)
        
        # 如果所有方法都失敗
        raise FileNotFoundError(
            "找不到 Google API 憑證。請設定 GOOGLE_CREDENTIALS_BASE64 或 GOOGLE_CREDENTIALS 環境變數，或提供 credentials.json 檔案"
        )

    def _authenticate(self):
        """Google Sheets API 認證 - 使用服務帳戶"""
        try:
            creds = self._get_credentials()
            logger.info("Google Sheets API 認證成功")
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            logger.error(f"Google Sheets 認證失敗: {e}")
            raise

    def _authenticate_drive(self):
        """Google Drive API 認證 - 使用服務帳戶"""
        try:
            creds = self._get_credentials()
            logger.info("Google Drive API 認證成功")
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Google Drive 認證失敗: {e}")
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
    
    def upload_image_to_drive(self, image_data, filename):
        """上傳圖片到 Google Drive 並返回可分享的連結"""
        try:
            # 建立檔案 metadata
            file_metadata = {
                'name': filename,
                'parents': [self.DRIVE_FOLDER_ID] if self.DRIVE_FOLDER_ID else []
            }
            
            # 建立媒體上傳物件
            media = MediaIoBaseUpload(
                io.BytesIO(image_data),
                mimetype='image/jpeg',
                resumable=True
            )
            
            # 上傳檔案
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            
            # 設定檔案權限為公開可讀取
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            # 建立可分享的連結
            download_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            logger.info(f"Image uploaded to Google Drive: {download_url}")
            return download_url
            
        except HttpError as error:
            logger.error(f"Google Drive API error: {error}")
            return None
        except Exception as error:
            logger.error(f"Error uploading image to Drive: {error}")
            return None

    def save_image(self, user_id, image_data, message_id, timestamp):
        """儲存圖片到Google Drive並將連結存到Google Sheets"""
        try:
            # 生成檔案名稱
            filename = f"linebot_image_{message_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # 上傳圖片到 Google Drive
            image_url = self.upload_image_to_drive(image_data, filename)
            
            if image_url:
                # 儲存圖片資訊和連結到Google Sheets
                image_info = f"圖片大小: {len(image_data)} bytes"
                
                values = [
                    [timestamp, user_id, 'image', image_info, image_url]
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
                
                logger.info(f"Image saved to Google Sheets with Drive link: {result.get('updates', {}).get('updatedCells', 0)} cells updated")
                return image_url
            else:
                # 如果 Drive 上傳失敗，仍然儲存基本資訊
                image_info = f"圖片上傳失敗 - ID: {message_id}, 大小: {len(image_data)} bytes"
                
                values = [
                    [timestamp, user_id, 'image', image_info, "上傳失敗"]
                ]
                
                body = {
                    'values': values
                }
                
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.SPREADSHEET_ID,
                    range=self.RANGE_NAME,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                return None
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return None
        except Exception as error:
            logger.error(f"Error saving image: {error}")
            return None
    
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