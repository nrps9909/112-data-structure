import asyncio
from datetime import datetime
import globals

async def light_control():
    while not globals.stop_event.is_set():
        globals.light = "on" if 8 <= datetime.now().hour < 22 else "off"
        await asyncio.sleep(3600)  # 每小時更新一次
    print("Light control stopped.")
