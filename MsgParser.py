class MsgParser:
    msg = None

    @staticmethod
    def setMsg(msg):
        MsgParser.msg = msg

    @staticmethod
    def getReplyToken():
        return MsgParser.msg['replyToken']

    @staticmethod
    def getMsgType():
        return MsgParser.msg['message']['type']

    @staticmethod
    def getMsgText():
        return MsgParser.msg['message']['text']
    
    @staticmethod
    def getSrcType():
        return MsgParser.msg['source']['type']
    
    @staticmethod
    def getUserId():
        return MsgParser.msg['source']['userId']