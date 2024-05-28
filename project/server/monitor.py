import asyncio
import time
import psutil
import globals

async def monitor_computer_usage():
    while not globals.stop_event.is_set():
        current_time = int(time.time())  # 取整
        for app in globals.app_names:
            app_running = any(proc for proc in psutil.process_iter(attrs=['name']) if proc.info['name'] == app)
            if app_running:
                if globals.app_start_times[app] is None:
                    globals.app_start_times[app] = current_time
                else:
                    elapsed_time = current_time - globals.app_start_times[app]
                    globals.app_timers[app] += elapsed_time
                    globals.app_start_times[app] = current_time  # 重置開始時間
            else:
                globals.app_start_times[app] = None

        await asyncio.sleep(1)
    print("Computer usage monitoring stopped.")

if __name__ == "__main__":
    globals.stop_event = asyncio.Event()
    asyncio.run(monitor_computer_usage())
