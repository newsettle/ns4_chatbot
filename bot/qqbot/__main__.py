from qqbot import QQBot
from common.config import Config
from common import logger
from common.common import HtmlContent
from common import common
class MockBizManager:
  def route(self,type,sender,group,msg):
      return None,None

logger.init_4_debug()
conf = Config("bot.conf")
#为了让common.py中的类可以直接访问配置，来个trick
common.set_config(conf)
qqbot = QQBot(None,conf)
qqbot.startup()

#case1:测试文本消息
# qqbot.send("1234567","机器人","新版酷Q测试消息")

#case2:测试HTML消息，会自动格式化成图片发送
qqbot.send("1234567","机器人","新版酷Q测试HTML消息",HtmlContent("<html><head></head><body>自带HTML标签的消息</body></html>","html"))
qqbot.send("1234567","机器人","新版酷Q测试HTML Plain消息",HtmlContent("Plain Text的消息","plain"))

#case3:测试图片消息
# qqbot.send_image("1234567","机器人","./test/bot.png")

#case4:测试接收到回调消息后的处理
# data = \
# {
#       "group_id":"1234567",
#       "font":"1234567",
#       "message":"[CQ:at,qq=25473936] 你好",
#       "message_id":91,
#       "message_type":"discuss",
#       "post_type":"message",
#       "raw_message":"[CQ:at,qq=1234567] 你好",
#       "self_id":"1234567",
#       "sender":{"age":3,"nickname":"jacun","sex":"male","user_id":"1234567"},
#       "time":1546934868,
#       "user_id":"1234567"
# }
# qqbot.on_message(data)