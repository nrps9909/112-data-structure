import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 全局变量设置
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SERVICE_ACCOUNT_FILE = os.path.join(project_root, 'assets', 'googleAPI.json')
print(f"Using service account file: {SERVICE_ACCOUNT_FILE}")

# 初始化 Google Sheets API 凭证和服务
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
spreadsheet_id = os.getenv('SPREADSHEET_ID')  # 从环境变量中读取 Google 表单 ID
