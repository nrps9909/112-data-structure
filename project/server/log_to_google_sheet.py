import sys
import os

# 获取项目根目录并添加到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from assets.config import service, spreadsheet_id
import asyncio
from datetime import datetime
import globals

async def log_to_google_sheet():
    while not globals.stop_event.is_set():
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        app_usage_times = [globals.app_timers[app] for app in globals.app_names]
        values = {
            'values': [[current_date, current_time, globals.counter_drink, globals.light, globals.status] + app_usage_times]
        }
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Sheet1',
            valueInputOption='RAW',
            body=values
        ).execute()

        await asyncio.sleep(10)  # 每10秒輸出一次
    print("Google Sheet logging stopped.")
