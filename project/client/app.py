import sys
import os
import asyncio
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import logging

# 獲取項目根目錄並添加到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 從 assets 目錄導入 config.py 中的內容
from assets.config import service, spreadsheet_id
from client.notifications import notify_skipping_class, notify_gaming_addiction, notify_drink_water
from client.light_control import turn_11_on, turn_11_off, turn_12_on, turn_12_off

app = Flask(__name__)

# 加載 .env 文件中的環境變量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')

# 配置日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取請求頭中的簽名
    signature = request.headers['X-Line-Signature']

    # 獲取請求體
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)

    # 驗證簽名
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id  # 獲取用戶 ID
    logger.info(f"Received message from user {user_id}: {user_message}")

    # 使用ChatGPT進行意圖判斷並生成回答
    try:
        reply_message, action = generate_response(user_message)
        logger.info(f"Generated response: {reply_message}, action: {action}")

        # 檢查 reply_message 是否為空
        if not reply_message.strip():
            reply_message = "抱歉,我現在無法回答您的問題。"

    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}")
        reply_message = "抱歉,處理您的請求時發生錯誤。"
        action = None

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))

    # 根據GPT的意圖判斷執行相應的動作
    if action == "turn_on_light":
        turn_11_on()

    elif action == "turn_off_light":
        turn_11_off()
        
    elif action == "notify_drink_water":
        asyncio.run(notify_drink_water())

def generate_response(user_message):
    try:
        # 從 Google 表單獲取最新一行的數據
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1").execute()
        values = result.get('values', [])
        if not values:
            raise ValueError("在試算表中沒有找到數據。")
        
        headers = values[0]  # 第一行作為標題
        latest_row = values[-1]  # 最後一行作為最新數據
        current_data = {headers[i]: latest_row[i] for i in range(len(headers))}
        
        logger.info(f"當前數據: {current_data}")
        
        # 生成數據意義說明
        data_meaning = "以下是使用者今天的活動數據：\n"
        for i, header in enumerate(headers):
            if i == 0:
                data_meaning += f"{header} - {current_data[header]},表示記錄的日期；\n"
            elif i == 1:
                data_meaning += f"{header} - {current_data[header]},表示記錄的時間；\n"
            elif i == 2:
                data_meaning += f"{header} - {current_data[header]},表示小明今天忘記喝水的次數,次數代表,從凌晨00:00開始,每一小時沒喝水的次數,12次就代表有12小時沒有喝水；\n"
            elif i == 3:
                data_meaning += f"{header} - {current_data[header]},表示燈的開關狀態，燈開著代表小明起床了，燈關閉代表小明在睡覺；\n"
            elif i == 4:
                data_meaning += f"{header} - {current_data[header]},表示小明是否在家，如果在家就代表小明沒去上學，如果出門就代表小明去上家；\n"
            elif i >= 5:
                data_meaning += f"{header} - {current_data[header]},表示小明今天玩{header}的時長(秒)，並且所有APP都是遊戲。\n"
        
        logger.info(f"數據意義: {data_meaning}")
        
        # 生成小明的當前狀態
        ming_status = f"小明目前的狀態：\n" \
                      f"是否在家：{current_data['是否在家']}\n" \
                      f"房間燈光：{'開著' if current_data['房間內燈光狀態'] == '1' else '關閉'}\n" \
                      f"忘記喝水次數：{current_data['過長時間沒喝水']}\n" \
                      f"遊戲時長：\n"
        for header in headers[5:]:
            ming_status += f"- {header}: {current_data[header]}秒\n"
        
        logger.info(f"小明的狀態: {ming_status}")
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一個監督小明的管家。請根據提供的數據,判斷使用者的意圖,並生成相應的簡短回覆使用者的需求。如果使用者想要開燈或關燈,請在回覆中包含相應的操作指令。如果使用者詢問小明的狀態,請輸出完整的狀態資訊。如果你有需要推理或是思考的部分，請放在心裡，不需要輸出給使用者。如果使用者有任何要提醒小明喝水的訊息，請輸出action: notify_drink_water"},
                    {"role": "system", "content": data_meaning},
                    {"role": "system", "content": ming_status},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7,
            )
        except openai.error.APIError as e:
            raise Exception(f"OpenAI API 返回了一個 API 錯誤: {str(e)}")
        except openai.error.APIConnectionError as e:
            raise Exception(f"無法連接到 OpenAI API: {str(e)}")
        except openai.error.RateLimitError as e:
            raise Exception(f"OpenAI API 請求超過了速率限制: {str(e)}")
        except Exception as e:
            raise Exception(f"在 OpenAI API 請求期間發生了一個錯誤: {str(e)}")

        reply_message = response.choices[0].message['content'].strip()

        # 檢查 GPT 生成的回答,確定是否需要開關燈或提醒喝水
        action = None
        if "action: turn_on_light" in reply_message:
            action = "turn_on_light"
            reply_message = "已經為您打開了燈。"
        elif "action: turn_off_light" in reply_message:
            action = "turn_off_light"
            reply_message = "已經為您關閉了燈。"
        elif "action: notify_drink_water" in reply_message or "提醒小明喝水" in user_message or "叫小明喝水" in user_message:
            action = "notify_drink_water"
            reply_message = "已經提醒小明喝水了。"

        return reply_message, action

    except Exception as e:
        logger.error(f"在 generate_response 中發生錯誤: {str(e)}")
        return "抱歉,處理您的請求時發生錯誤。", None

async def notify_drink_water():
    turn_12_on()
    await asyncio.sleep(5)
    turn_12_off()

async def check_ming_status():
    while True:
        try:
            # 获取最新数据
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1").execute()
            values = result.get('values', [])
            if not values:
                logger.info("No data found in the spreadsheet.")
                continue
            
            headers = values[0]
            latest_row = values[-1]
            current_data = {headers[i]: latest_row[i] for i in range(len(headers))}
            
            logger.info(f"Current data: {current_data}")
            
            # 检测小明是否在不对的时间待在家里
            current_hour = int(current_data["時間"].split(":")[0])
            if current_hour in range(8, 17) and current_data["是否在家"] == "在家":
                logger.info("Detected that Ming is at home during class time.")
                notify_skipping_class()

            # 检测小明是否电玩成瘾
            total_gaming_time = sum(int(current_data[header]) for header in headers[5:] if current_data[header].isdigit())
            if total_gaming_time > 15:  # 超過1小時
                logger.info(f"Detected that Ming has been gaming for {total_gaming_time} seconds.")
                notify_gaming_addiction()
                
            drink_water_time = int(current_data["過長時間沒喝水"][0])
            if drink_water_time > 20:  # 超過1小時
                logger.info(f"Detected that Ming has not been drinking for {drink_water_time} times.")
                notify_drink_water()

        except Exception as e:
            logger.error(f"Error in check_ming_status: {str(e)}")

        await asyncio.sleep(10)  # 每分鐘檢查一次,便於測試

async def main():
    loop = asyncio.get_event_loop()
    check_ming_status_task = loop.create_task(check_ming_status())
    flask_task = loop.run_in_executor(None, app.run)
    await asyncio.gather(check_ming_status_task, flask_task)

if __name__ == "__main__":
    asyncio.run(main())
