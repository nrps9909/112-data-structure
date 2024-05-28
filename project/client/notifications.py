import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv


load_dotenv()

line_bot_api = LineBotApi(channel_access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
monitor_user_id = os.getenv('MONITOR_USER_ID')

def notify_skipping_class():
        message = "小明在不對的時間還待在家裡,可能翹課了！"
        line_bot_api.push_message(monitor_user_id, TextSendMessage(text=message))

def notify_gaming_addiction():
        message = "小明電腦玩超過時間,可能電玩成癮了！"
        line_bot_api.push_message(monitor_user_id, TextSendMessage(text=message))
