# globals.py
stop_event = None
use_count = 0
counter_drink = 0
light = ""
at_home = False
status = "未知"
last_update_time = 0

# 初始化每個應用程序的計時器變量
app_names = ['LeagueClient.exe', 'Discord.exe']
app_timers = {app: 0 for app in app_names}  # 以秒為單位記錄每個應用程序的使用時間
app_start_times = {app: None for app in app_names}  # 記錄每個應用程序的開始時間
