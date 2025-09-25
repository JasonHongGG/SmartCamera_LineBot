from linebot.v3.messaging.models import TextMessage, StickerMessage
from MsgParser import MsgParser
from ActionHandler.TextHandler import TextHandler

class ActionManager:
    def __init__(self):
        self.text_handler = TextHandler()

    def trigger(self, msg):
        type = MsgParser.getMsgType()
        

        if type=="text":
            reply =  self.text_handler.handle(msg) 
        elif type=="sticker":
            reply = "你傳的是貼圖呦～"
        else:
            reply = "你傳的不是文字呦～"

        
        return [TextMessage(text = reply)]