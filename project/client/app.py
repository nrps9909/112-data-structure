import sys
import os

# 獲取項目根目錄並添加到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 從 assets 目錄導入 config.py 中的內容
from assets.config import service, spreadsheet_id
from dotenv import load_dotenv

# 剩餘代碼保持不變
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

app = Flask(__name__)

# 加載 .env 文件中的環境變量
load_dotenv()

line_bot_api = LineBotApi(channel_access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')

# 剩餘代碼保持不變

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取請求頭中的簽名
    signature = request.headers['X-Line-Signature']

    # 獲取請求體
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證簽名
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    app.logger.info("Received message: " + user_message)

    # 使用ChatGPT進行意圖判斷並生成回答
    try:
        response_message = generate_response(user_message)
    except Exception as e:
        app.logger.error(f"Error in generating response: {str(e)}")
        response_message = "抱歉，處理您的請求時發生錯誤。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_message))

def generate_response(user_message):
    try:
        # 從 Google 表單獲取最新一行的數據
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1").execute()
        values = result.get('values', [])
        if not values:
            raise ValueError("No data found in the spreadsheet.")
        
        headers = values[0]  # 第一行作為標題
        latest_row = values[-1]  # 最後一行作為最新數據
        current_data = {headers[i]: latest_row[i] for i in range(len(headers))}
        
        # 生成數據意義說明
        data_meaning = "以下是用戶今天的活動數據：\n"
        for i, header in enumerate(headers):
            if i == 0:
                data_meaning += f"{header} - {current_data[header]}, 表示記錄的日期；\n"
            elif i == 1:
                data_meaning += f"{header} - {current_data[header]}, 表示記錄的時間；\n"
            elif i == 2:
                data_meaning += f"{header} - {current_data[header]}, 表示小明今天忘記喝水的次數，次數代表，從凌晨00:00開始，每一小時沒喝水的次數，12次就代表有12小時沒有喝水；\n"
            elif i == 3:
                data_meaning += f"{header} - {current_data[header]}, 表示燈的開關狀態，燈開著代表小明起床了，燈關閉代表小明在睡覺；\n"
            elif i == 4:
                data_meaning += f"{header} - {current_data[header]}, 表示小明是否在家；\n"
            elif i >= 5:
                data_meaning += f"{header} - {current_data[header]}, 表示小明今天玩{header}(遊戲)的時長（秒）。\n"
        
        # 使用OpenAI生成回答
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一個監督小明的話不多的管家。你只需要回答用戶想知道的答案，把你的推理過程和計算過程放在心裡，然後根據以下的數據簡短的回答用戶的問題："},
                {"role": "system", "content": data_meaning},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        app.logger.error(f"Error in OpenAI API call: {str(e)}")
        return "抱歉，處理您的請求時發生錯誤。"

if __name__ == "__main__":
    app.run(debug=False)
