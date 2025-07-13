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
    
    def _verify_drive_folder(self):
        """驗證 Google Drive 資料夾是否可存取"""
        if not self.DRIVE_FOLDER_ID:
            logger.info("未設定 GOOGLE_DRIVE_FOLDER_ID，將上傳到根目錄")
            return None
            
        try:
            # 嘗試取得資料夾資訊以驗證存取權限
            folder = self.drive_service.files().get(fileId=self.DRIVE_FOLDER_ID).execute()
            logger.info(f"Drive 資料夾驗證成功: {folder.get('name')}")
            return self.DRIVE_FOLDER_ID
        except HttpError as error:
            logger.error(f"Drive 資料夾存取失敗 ({self.DRIVE_FOLDER_ID}): {error}")
            logger.info("將改用根目錄上傳")
            return None
        except Exception as error:
            logger.error(f"Drive 資料夾驗證錯誤: {error}")
            return None

    def _save_image_as_base64(self, image_data, filename):
        """備用方案：將圖片轉換為 Base64 並儲存到 Google Sheets"""
        try:
            logger.info(f"使用 Base64 備用方案儲存圖片: {filename}")
            
            # 將圖片轉換為 base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 建立一個簡單的 HTML 頁面來顯示圖片
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><title>{filename}</title></head>
            <body>
                <h2>LINE Bot 圖片</h2>
                <p>檔案名稱: {filename}</p>
                <img src="data:image/jpeg;base64,{image_base64}" style="max-width:100%;height:auto;" />
            </body>
            </html>
            """
            
            # 這裡可以考慮使用其他免費圖床服務
            # 暫時返回一個說明連結
            info_url = f"data:text/html;base64,{base64.b64encode(html_content.encode()).decode()}"
            
            logger.info("已使用 Base64 方案處理圖片")
            return f"[Base64圖片] 大小: {len(image_data)} bytes"
            
        except Exception as e:
            logger.error(f"Base64 備用方案失敗: {e}")
            return None

    def save_image(self, user_id, image_data, message_id, timestamp):
        """儲存圖片到Google Drive並將連結存到Google Sheets"""
        try:
            # 生成檔案名稱
            filename = f"linebot_image_{message_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # 先嘗試上傳到 Google Drive
            drive_result = self._try_drive_upload(image_data, filename)
            
            if drive_result and drive_result.startswith('https://'):
                # Drive 上傳成功
                image_info = f"圖片大小: {len(image_data)} bytes"
                image_url = drive_result
                
                values = [
                    [timestamp, user_id, 'image', image_info, image_url]
                ]
                
                logger.info(f"圖片成功上傳到 Google Drive: {image_url}")
                
            else:
                # Drive 上傳失敗，使用 Base64 備用方案
                logger.info("Drive 上傳失敗，使用 Base64 備用方案")
                base64_info = self._save_image_as_base64(image_data, filename)
                
                image_info = f"Base64 圖片 - 大小: {len(image_data)} bytes"
                image_url = "Base64 儲存 (無法上傳到 Drive)"
                
                values = [
                    [timestamp, user_id, 'image', image_info, image_url]
                ]
            
            # 儲存到 Google Sheets
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
            return image_url
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return None
        except Exception as error:
            logger.error(f"Error saving image: {error}")
            return None

    def _try_drive_upload(self, image_data, filename):
        """嘗試上傳到 Google Drive，成功返回 URL，失敗返回 None"""
        try:
            # 驗證並取得有效的資料夾 ID
            valid_folder_id = self._verify_drive_folder()
            
            # 建立檔案 metadata
            file_metadata = {
                'name': filename,
                'parents': [valid_folder_id] if valid_folder_id else []
            }
            
            logger.info(f"準備上傳圖片: {filename} 到 {'指定資料夾' if valid_folder_id else '根目錄'}")
            
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
                fields='id,name,parents'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"檔案上傳成功，ID: {file_id}")
            
            # 設定檔案權限為公開可讀取
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            logger.info("檔案權限設定完成")
            
            # 建立可分享的連結
            download_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            logger.info(f"Image uploaded to Google Drive: {download_url}")
            return download_url
            
        except HttpError as error:
            if 'storageQuotaExceeded' in str(error):
                logger.error("服務帳戶沒有儲存配額，無法上傳到 Drive")
            else:
                logger.error(f"Google Drive API error: {error}")
            return None
        except Exception as error:
            logger.error(f"Error uploading image to Drive: {error}")
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