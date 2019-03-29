#-*- coding:utf-8 -*-
from qqbot.qqbot import QQBot
from wxbot.wxbot import Wexin_Bot
from mail_bot import Email_Bot
# import neo4j_helper
from common import logger,db_helper
import time,random
import json
from common.redis_helper import RedisConnect
from task.bot_schedule import *



class BotManager:
    def __init__(self,conf):
        self.bots = []
        self.bot_dict = {}#增加一个字典，存放机器人实例
        self.config = conf

    def get_bot_by_type(self,type):
        return self.bot_dict.get(type,None)

    def startup(self,bizManager,conf):
        self.config = conf
        self.bizManager = bizManager

        bot_supports = self.config.bot_support.split(",")
        # 找到所有的qq和微信群
        qq_groups, wechat_groups = self.query_groups_info()

        if "qq" in bot_supports:
            # 启动QQBot
            qq_bot = QQBot(bizManager,self.config)
            qq_bot.startup()
            qq_bot.register(qq_groups)
            self.bots.append(qq_bot)
            self.bot_dict["qq"]= qq_bot
            logger.info("启动了QQ机器人")

        if "wechat" in bot_supports:
            # 启动微信Bot
            wxbot = Wexin_Bot(bizManager,self.config)
            wxbot.startup()

            wxbot.register(wechat_groups)
            self.bots.append(wxbot)
            self.bot_dict["wechat"]=wxbot
            logger.info("启动了微信机器人")

        if "email" in bot_supports:
            # 启动EmailBot
            email_bot = Email_Bot(bizManager,self.config)
            self.bots.append(email_bot)
            self.bot_dict["email"] = email_bot

            logger.info("启动了邮件机器人")

    def startTask(self):
        for bot in self.bots:
            if bot.type == "qq":
                QQSchedule("qq发送消息任务",self.config,bot,self.bizManager).start()
            elif bot.type == "wechat":
                WechatSchedule("微信发送消息任务",self.config,bot,self.bizManager).start()



    #给bot们发送消息 groups={'qq_group':'xxx','wechat_group':'yyy'}
    def send_image(self,groups, user,img_path):
        if not isinstance(groups, dict):
            logger.warn("send_image参数groups不合法,需要字典类型：%r",groups)
            return
        logger.debug("发送图片send_image,groups=%r",groups)    
        qq_group = groups.get('qq_group',None)
        wechat_group = groups.get('wechat_group',None)
        email = groups.get('email',None) #这个设计有些诡异，为了统一，暂时先这样吧

        params = {}
        params["user"] = user
        params["msg_type"] = "image"
        params["img_path"] = img_path
        if qq_group:
            params["group"] = qq_group
            self.send_qq_queue(params)
        if wechat_group:
            params["group"] = wechat_group
            self.send_wechat_queue(params)

        for bot in self.bots:  # bots是qqbot和wxbot的实例
            # if bot.type == "qq" and qq_group:
            #     bot.send_image(qq_group,user,img_path)
            # if bot.type == "wechat" and wechat_group:
            #     bot.send_image(wechat_group,user,img_path)
            if bot.type == "email" and email:
                bot.send_image(email,user,img_path)

    #给bot们发送消息
    def send(self,groups,user,msg,html,biz_type,bot_type_list=None,**kwargs):

        #需要把这个对话，放入到上下文中，这个是发给bot的，需要记录下来，
        #另外一侧，也就是bot发过来的，也需要记录下来
        qq_group = groups.get('qq_group',None)
        wechat_group = groups.get('wechat_group',None)
        email = groups.get('email',None) #这个设计有些诡异，为了统一，暂时先这样吧
        params = {}
        params["user"] = user
        params["msg"] = msg

        params["msg_type"] = "text"
        params["biz_type"] = biz_type
        if qq_group :
            params["html"] = html.get_content("qq")
            params["group"] = qq_group
            self.send_qq_queue(params)
        if wechat_group:
            params["html"] = html.get_content("wechat")
            params["group"] = wechat_group
            self.send_wechat_queue(params)

        #这里随机等待1-3秒，防止频率过快导致被封号!
        # time.sleep(self.config.bot_chat_base_interval + random.random() * self.config.bot_chat_interval)

        for bot in self.bots:#bots是qqbot和wxbot的实例
            # 如果bot_type_list非空，就检查一下，qq是否在这个里，如果不在，就忽略，直接跳走
            if bot_type_list and not bot.type in bot_type_list:
                logger.debug("不在bot list，此类型[%s]机器人不发送",bot.type)
                continue

            # if bot.type == "qq":
            #
            #     if qq_group == None:
            #         logger.warn("找不到[%s]所在的qq群[%s]",user,qq_group)
            #     else:
            #         logger.debug("发送给qq消息[%s][%s]:%s",user,qq_group,msg)
            #         bot.send(qq_group,user,msg,html)
            #
            #         self.bizManager.saveContext("qq",   user, qq_group,msg,biz_type,**kwargs)#kwargs用于保存额外的上下文
            #         logger.debug("保存QQ对话上下文[%s][%s]", user, qq_group)
            #
            # if bot.type == "wechat":
            #
            #     if wechat_group == None:
            #         logger.warn("找不到[%s]所在的微信群[%s]", user, wechat_group)
            #     else:
            #         logger.debug("发送给微信消息[%s][%s]:%s", user,wechat_group,msg)
            #         bot.send(wechat_group,user,msg,html)
            #
            #         self.bizManager.saveContext("wechat", user, wechat_group,msg,biz_type,**kwargs)#kwargs用于保存额外的上下文
            #         logger.debug("保存微信对话上下文[%s][%s]", user, wechat_group)

            if bot.type == "email":

                if email == None:
                    logger.warn("邮件地址为空")
                else:
                    self.debug = logger.debug("发送给邮件[%s]消息:%s", email, msg)
                    bot.send(email,user,msg,html)

    def send_qq_queue(self,data):
        key = "CHAT_QQ_MESSAGE_QUEUE"
        data = json.dumps(data, encoding='utf-8', ensure_ascii=False)
        (r, rexcute) = RedisConnect().createRedis()
        logger.info("CHAT_QQ_MESSAGE_QUEUE存放数据：data=%r", data)
        r.lpush(key, data)

    def send_wechat_queue(self,data):
        key = "CHAT_WECHAT_MESSAGE_QUEUE"
        data = json.dumps(data, encoding='utf-8', ensure_ascii=False)
        (r, rexcute) = RedisConnect().createRedis()
        r.lpush(key, data)

    def query_groups_info(self):
        qq_group = db_helper.find_group_by_qqtype()
        wechat_group = db_helper.find_group_by_wechattype()
        logger.debug("查询出的qq群组：[%r]",qq_group)
        logger.debug("查询出的wechat群组：[%r]", wechat_group)

        return qq_group,wechat_group
