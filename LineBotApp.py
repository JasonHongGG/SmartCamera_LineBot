from flask import Flask, request
import os
import traceback
import json
from datetime import datetime
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.configuration import Configuration
from linebot.v3.messaging.api_client import ApiClient
from linebot.v3.messaging.models import ReplyMessageRequest, PushMessageRequest, ImageMessage, TextMessage

from MsgParser import MsgParser
from ActionManager import ActionManager

from dotenv import load_dotenv


class LineBotApp:
    def __init__(self):
        self.check_env_variables()
        self.app = Flask(__name__)
        self.line_bot_api = MessagingApi(
                ApiClient(
                    Configuration(access_token=os.environ.get('LINE_ACCESS_TOKEN'))
                )
            )
        self.handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
        self.msg = None
        self.action_manager = ActionManager()
        self.setup_routes()

    def check_env_variables(self):
        required_vars = ['LINE_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET', 'LINE_GROUP_ID']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def parse_request(self):
        body = request.get_data(as_text=True)
        signature = request.headers['X-Line-Signature']
        LineBotApp.msg = json.loads(body)['events'][0]
        LineBotApp.handler.handle(body, signature) # 若有 handle 方法可加上

    def setup_routes(self):
        @self.app.route("/", methods=['POST'])
        def linebot():
            try:
                self.parse_request()
                MsgParser.setMsg(self.msg)
                print(json.dumps(self.msg, indent=2, ensure_ascii=False))
                replyMsg = self.action_manager.trigger(self.msg)
                self.line_bot_api.reply_message(ReplyMessageRequest(
                    reply_token=MsgParser.getReplyToken(),
                    messages=replyMsg
                ))
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                pass
            return 'OK'

        @self.app.route("/triggerAlarm", methods=['POST'])
        def trigger_alarm():
            print(f"Alarm Triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            data = request.json
            image_url = data.get('image_url')
            msg = data.get('msg')
            print(f"Image URL: {image_url}, Message: {msg}")

            msgList = []

            if image_url:
                msgList.append(ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                ))

            if msg:
                msgList.append(TextMessage(text=msg))

            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=os.environ.get('LINE_GROUP_ID'),
                    messages=msgList
                )
            )
            return 'OK'

    def run(self):
        self.app.run(host='0.0.0.0', port=5001, debug=True)

if __name__ == "__main__":
    load_dotenv()
    LineBotApp().run()