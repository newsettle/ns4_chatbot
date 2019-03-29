#-*- coding:utf-8 -*-
from biz_comp_rasa import BizCompRasa
from biz_comp_default import BizCompDefaultMonitor
from context import ContextStore
from common import logger
from biz_comp_chat import BizCompChat

class BizManager:

    def __init__(self,botManager,rasa_server,conf=None):
        self.config = conf
        self.rasa_server = rasa_server
        self.bizComponents = {}
        self.botManager = botManager
        self.contextStore = ContextStore()
        self.initialize()



    def saveContext(self,client,user,group,msg,biz_type,**kwargs):
        key = "{}-{}".format(client,group)
        logger.debug("上下文保存：key=%s",key)

        #保存其他的上下文，用动态参数的原因是因为不同业务的上下文保存的不同
        #比如，审批也中的流程id（flow_id)
        for (k,v) in  kwargs.iteritems():
            # print "{}={}".format(k,v)
            logger.debug("上下文保存：(其他附加\"子\"上下文) k=%r,v=%r", k, v)
            self.contextStore.save_context(key,k,v)

        #保存对话
        logger.debug("保存对话：dialog=%s", msg)
        self.contextStore.save_dialog(key,msg)

        #保存业务类型
        logger.debug("保存业务类型：biz_type=%s", biz_type)
        self.contextStore.save_biz_type(key,biz_type)

        logger.debug("用户对话已经保存到对话引擎的上下文中,key[%s],biz_type[%s]",key,biz_type)

    def initialize(self):
        self.bizComponents['rasa'] = BizCompRasa(self.botManager,self.rasa_server)
        self.bizComponents[BizCompDefaultMonitor.name] = BizCompDefaultMonitor(self.botManager)
        self.bizComponents[BizCompChat.name] = BizCompChat(self.botManager)

    def load_biz_comp(self,flag):
        return self.bizComponents.get(flag,None)

    '''
        系统 -->bot
    '''
    def route(self, client, user, group, msg):
        if msg == "help":
            logger.debug("help命令")
            return self.load_biz_comp("new_monitor"),msg

        if "#" in msg:
            logger.debug("#指令消息")
            return self.load_biz_comp("monitor"),msg

        key = "{}-{}".format(client, group)

        # 先去ContextStore中去寻找之前的上下文
        context = self.contextStore.find_context(key)

        logger.debug("消息路由中，[%s]群组[%s]里的用户[%s]，跟我(bot)说：%s", client, group, user, msg)

        biz_type = BizCompDefaultMonitor.name

        if context is None:
           logger.debug("无法从对话上下文中查找到key[%s]=的上下文", key)
        else:
           biz_type = context.get("biz_type", None)
           if biz_type is None:
               biz_type = BizCompDefaultMonitor.name
               logger.debug("key=[%s]对话上下文存在，但是无法从中查找到biz_type", key)

        logger.debug("当前对话的业务类型,biz_type[%s]", biz_type)
        return self.load_biz_comp(biz_type),context