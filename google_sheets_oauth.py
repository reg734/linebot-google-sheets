import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
import json
import logging
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class GoogleSheetsOAuthHandler:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')
        self.DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        self.RANGE_NAME = 'A:E'
        
        # OAuth2 認證檔案路徑
        self.TOKEN_FILE = 'token.pickle'
        self.CREDENTIALS_FILE = 'oauth_credentials.json'
        
        self.creds = self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def _authenticate(self):
        """使用 OAuth2 進行認證"""
        creds = None
        
        # 優先從環境變數讀取 token
        token_base64 = os.getenv('GOOGLE_TOKEN_BASE64')
        if token_base64:
            try:
                import base64
                token_data = base64.b64decode(token_base64)
                creds = pickle.loads(token_data)
                logger.info("從環境變數載入 OAuth2 token")
            except Exception as e:
                logger.error(f"從環境變數載入 token 失敗: {e}")
                creds = None
        
        # Token 檔案儲存使用者的存取和更新 tokens
        elif os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
                logger.info("從 token.pickle 載入現有認證")
        
        # 如果沒有有效的認證，則讓使用者登入
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("更新過期的認證 token")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"找不到 OAuth 認證檔案: {self.CREDENTIALS_FILE}\n"
                        "請先從 Google Cloud Console 下載 OAuth2 憑證檔案"
                    )
                
                logger.info("開始新的 OAuth2 認證流程")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, self.SCOPES)
                
                # 使用本地伺服器進行認證
                creds = flow.run_local_server(port=0)
                logger.info("OAuth2 認證成功")
            
            # 儲存認證以供下次使用
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
                logger.info("認證 token 已儲存")
        
        return creds
    
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
        """儲存圖片到Google Drive並將連結存到Google Sheets"""
        try:
            # 生成檔案名稱
            filename = f"linebot_image_{message_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # 建立檔案 metadata
            file_metadata = {
                'name': filename
            }
            
            # 如果有指定資料夾，加入 parents
            if self.DRIVE_FOLDER_ID:
                file_metadata['parents'] = [self.DRIVE_FOLDER_ID]
            
            logger.info(f"準備上傳圖片: {filename}")
            
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
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"檔案上傳成功，ID: {file_id}")
            
            # 取得分享連結
            # 使用 webViewLink 可以直接在瀏覽器中查看
            view_link = file.get('webViewLink')
            
            # 儲存到 Google Sheets
            image_info = f"圖片大小: {len(image_data)} bytes"
            values = [
                [timestamp, user_id, 'image', image_info, view_link]
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
            
            logger.info(f"Image saved to Google Sheets: {result.get('updates', {}).get('updatedCells', 0)} cells updated")
            return view_link
            
        except HttpError as error:
            if error.resp.status == 403:
                logger.error("權限不足：請確認 OAuth 範圍包含 Drive 存取權限")
            else:
                logger.error(f"Google Drive API error: {error}")
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
    
    def test_connection(self):
        """測試 Google API 連接"""
        try:
            # 測試 Sheets API
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.SPREADSHEET_ID
            ).execute()
            logger.info(f"成功連接到 Google Sheets: {spreadsheet.get('properties', {}).get('title')}")
            
            # 測試 Drive API
            if self.DRIVE_FOLDER_ID:
                folder = self.drive_service.files().get(
                    fileId=self.DRIVE_FOLDER_ID
                ).execute()
                logger.info(f"成功連接到 Drive 資料夾: {folder.get('name')}")
            else:
                logger.info("未設定 Drive 資料夾，將使用根目錄")
            
            return True
            
        except Exception as error:
            logger.error(f"連接測試失敗: {error}")
            return False