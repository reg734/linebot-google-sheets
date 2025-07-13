from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
import os
import logging
from datetime import datetime
from google_sheets import GoogleSheetsHandler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LINE Bot 設定
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Google Sheets 處理器
sheets_handler = GoogleSheetsHandler()

# 用戶狀態管理 - 追蹤誰在儲存模式中
user_save_states = {}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """處理文字訊息"""
    user_id = event.source.user_id
    text = event.message.text
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 檢查是否為控制指令
    if text == '/save':
        user_save_states[user_id] = True
        reply_text = "開始儲存模式，接下來的訊息和圖片將會儲存到Google Sheets"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        logger.info(f"User {user_id} started save mode")
        return
    
    elif text == '/end':
        user_save_states[user_id] = False
        reply_text = "停止儲存模式，接下來的訊息和圖片將不會儲存"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        logger.info(f"User {user_id} ended save mode")
        return
    
    # 檢查用戶是否在儲存模式中
    if not user_save_states.get(user_id, False):
        reply_text = "目前非儲存模式，請先輸入 /save 開始儲存"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return
    
    # 儲存到Google Sheets (只在儲存模式中)
    try:
        sheets_handler.save_message(user_id, text, 'text', timestamp)
        logger.info(f"Text message saved: {text}")
        
        # 回覆訊息
        reply_text = f"已儲存訊息: {text}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    except Exception as e:
        logger.error(f"Error saving text message: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="訊息儲存失敗，請稍後再試")
        )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """處理圖片訊息"""
    user_id = event.source.user_id
    message_id = event.message.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 檢查用戶是否在儲存模式中
    if not user_save_states.get(user_id, False):
        reply_text = "目前非儲存模式，請先輸入 /save 開始儲存"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return
    
    try:
        # 取得圖片內容
        message_content = line_bot_api.get_message_content(message_id)
        image_data = message_content.content
        
        # 儲存圖片到Google Drive和Google Sheets
        image_url = sheets_handler.save_image(user_id, image_data, message_id, timestamp)
        
        logger.info(f"Image message saved: {message_id}")
        
        # 回覆訊息
        if image_url:
            reply_text = f"已儲存圖片至Google Drive: {image_url}"
        else:
            reply_text = "圖片已儲存但上傳Google Drive時發生問題"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        
    except Exception as e:
        logger.error(f"Error saving image message: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="圖片儲存失敗，請稍後再試")
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)