import sys
import os

# 获取项目根目录并添加到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import asyncio
from threading import Thread
from monitor import monitor_computer_usage
from object_detection import object_detection
from light import light_control
from log_to_google_sheet import log_to_google_sheet
from bluetooth import run_bleak_in_mta
import globals

async def main():
    try:
        await asyncio.gather(
            monitor_computer_usage(),
            object_detection(),
            light_control(),
            log_to_google_sheet(),
            stop_monitoring()
        )
    except asyncio.CancelledError:
        print("Main task cancelled, cleaning up...")

async def stop_monitoring():
    await asyncio.get_event_loop().run_in_executor(None, input, "Press Enter to stop...\n")
    globals.stop_event.set()

if __name__ == "__main__":
    globals.stop_event = asyncio.Event()

    bleak_thread = Thread(target=run_bleak_in_mta)
    bleak_thread.start()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, stopping all tasks...")
        globals.stop_event.set()
        bleak_thread.join()
        print("All tasks stopped.")
