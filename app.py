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
    
    # 儲存到Google Sheets
    try:
        sheets_handler.save_message(user_id, text, 'text', timestamp)
        logger.info(f"Text message saved: {text}")
        
        # 回覆訊息
        reply_text = f"已收到您的訊息並儲存至Google Sheets: {text}"
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
    
    try:
        # 取得圖片內容
        message_content = line_bot_api.get_message_content(message_id)
        image_data = message_content.content
        
        # 儲存圖片到Google Sheets
        image_url = sheets_handler.save_image(user_id, image_data, message_id, timestamp)
        
        logger.info(f"Image message saved: {message_id}")
        
        # 回覆訊息
        reply_text = f"已收到您的圖片並儲存至Google Sheets"
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