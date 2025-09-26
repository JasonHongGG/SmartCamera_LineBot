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
load_dotenv()

class LineBotApp:
    app = Flask(__name__)
    line_bot_api = MessagingApi(
        ApiClient(
            Configuration(access_token=os.environ.get('LINE_ACCESS_TOKEN'))
        )
    )
    handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
    msg = None
    action_manager = ActionManager()

    @staticmethod
    def parse_request():
        body = request.get_data(as_text=True)
        signature = request.headers['X-Line-Signature']
        LineBotApp.msg = json.loads(body)['events'][0]
        LineBotApp.handler.handle(body, signature) # 若有 handle 方法可加上

    @staticmethod
    @app.route("/", methods=['POST'])
    def linebot():
        try:
            LineBotApp.parse_request()
            MsgParser.setMsg(LineBotApp.msg)
            print(json.dumps(LineBotApp.msg, indent=2, ensure_ascii=False))
            replyMsg = LineBotApp.action_manager.trigger(LineBotApp.msg)
            LineBotApp.line_bot_api.reply_message(ReplyMessageRequest(
                reply_token=MsgParser.getReplyToken(), 
                messages=replyMsg
            ))
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            pass
        return 'OK'

    @staticmethod
    @app.route("/triggerAlarm", methods=['POST'])
    def trigger_alarm():
        print(f"Alarm Triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        data = request.json
        image_url = data.get('image_url')
        msg = data.get('msg')
        print(f"Image URL: {image_url}, Message: {msg}")

        msgList = [ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                )]
        if msg:
            msgList.append(TextMessage(text=msg))

        LineBotApp.line_bot_api.push_message(
            PushMessageRequest(
                to=os.environ.get('LINE_GROUP_ID'),
                messages=msgList
            )
        )
        return 'OK'

    @classmethod
    def run(cls):
        cls.app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    LineBotApp.run()