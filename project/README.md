# Line Bot with OpenAI and Google Sheets Integration

該項目是一個集成了 OpenAI 的 GPT-4 和 Google Sheets 的 Line Bot。該機器人可以通過從 Google 表單中獲取最新數據，使用 OpenAI 進行處理，並發送有意義的回復來響應用戶消息。

## 功能

- **Line Bot 集成**：通過 Line 消息平台與用戶通信。
- **OpenAI GPT-4**：利用 OpenAI 的 GPT-4 模型，根據用戶查詢和 Google 表單數據生成回復。
- **Google Sheets 集成**：從指定的 Google 表單中獲取最新數據，以提供上下文響應。

## 先決條件

- Python 3.6+
- 啟用 Sheets API 的 Google Cloud 項目
- LINE Messaging API 憑證
- OpenAI API 密鑰

## 安裝


1. **克隆倉庫**：

   `git clone https://github.com/nrps9909/112-data-structure.git`
   `cd nrps9909`

2. **創建並激活虛擬環境**：

   `python -m venv venv`
   `source venv/bin/activate`  # Windows 用戶使用 `venv\Scripts\activate`

3. **安裝依賴項**：

   `pip install -r requirements.txt`

4. **設置環境變量**：

   在項目根目錄下創建一個 `.env` 文件，並添加以下內容：
   ```sh
   LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
   LINE_CHANNEL_SECRET=your_channel_secret
   OPENAI_API_KEY=your_openai_api_key
   SPREADSHEET_ID='your_Google_forum_ID'
   MONITOR_USER_ID='Line_User_ID(不是加好友的那個ID)'
   ```
5. **配置 Google Sheets API**：

   確保你在 `assets` 目錄中有一個包含你的服務帳號憑證的 `googleAPI.json` 文件（不提交到版本控制系統）。

6. **運行應用程序**：

   `cd client
   python app.py`

   `cd server 
   python server.py`

   打開CMD:
   `ngrok http 5000`

   去(https://developers.line.biz/console/channel/2005448178/messaging-api)輸入Forwarding的網址 尾端加上/callback


---

### 依賴庫及其許可

**Flask**: BSD-3-Clause License

**line-bot-sdk**: MIT License

**openai**: MIT License

**google-api-python-client**: Apache License 2.0

**google-auth**: Apache License 2.0

**google-auth-oauthlib**: Apache License 2.0

**google-auth-httplib2**: Apache License 2.0
**bleak**: MIT License

**psutil**: BSD-3-Clause License

**opencv-python**: MIT License

**ultralytics**: GNU General Public License v3.0

**supervision**: BSD-3-Clause License

**numpy**: BSD-3-Clause License

**python-dotenv**: BSD-3-Clause License

**torch**: BSD-3-Clause License

**torchaudio**: BSD-3-Clause License

**torchvision**: BSD-3-Clause License

