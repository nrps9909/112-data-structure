import psutil

def list_running_apps():
    app_list = []
    for proc in psutil.process_iter(attrs=['name']):
        app_name = proc.info['name']
        if app_name not in app_list:
            app_list.append(app_name)
    return app_list

if __name__ == "__main__":
    running_apps = list_running_apps()
    print("Running applications:")
    for app in running_apps:
        print(app)
