import asyncio
from datetime import datetime
from bleak import BleakScanner
import globals

async def monitor_bluetooth_device():
    target_device_address = "E4:3C:F7:5C:15:33"  # 小明手機的藍牙MAC地址
    status_home = "在家"
    status_out = "出門"

    while not globals.stop_event.is_set():
        devices = await BleakScanner.discover()
        device_found = any(device.address == target_device_address for device in devices)
        
        if device_found:
            if not globals.at_home:
                globals.at_home = True
                globals.status = status_home
        else:
            if globals.at_home:
                globals.at_home = False
                globals.status = status_out

        await asyncio.sleep(10)  # 每10秒檢查一次

    print("Bluetooth device monitoring stopped.")

def run_bleak_in_mta():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_bluetooth_device())

if __name__ == "__main__":
    from bleak.backends.winrt.util import init_apartment
    init_apartment()
    globals.stop_event = asyncio.Event()
    run_bleak_in_mta()
