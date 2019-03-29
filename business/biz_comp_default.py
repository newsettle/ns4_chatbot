# -*- coding:utf-8 -*-
from biz_comp import *
from common import logger
from common.common import HtmlContent

#默认的业务处理类
class BizCompDefaultMonitor(BizComponent):

    name = "default"

    def __init__(self,botManager):
        self.botManager = botManager
        self.biz_type = BizCompDefaultMonitor.name

    def bot2system(self,bot,client,context,user,group,message):
        default_message = "对不起，客官！真心听不懂您在说什么..."


        logger.debug("默认的业务处理组件被处罚(BizDefaultMonitor.bot2system)")
        bot.send(group, user, default_message,None)