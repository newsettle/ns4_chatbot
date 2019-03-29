# -*- coding:utf-8 -*-
from threading import Thread
from common.redis_helper import RedisConnect
import json
import time,random
from common import logger,db_helper
from common.common import HtmlContent

class QQSchedule(Thread):
    def __init__(self, name, config, bot, bizManager):
        Thread.__init__(self)
        self.name = name
        self.config = config
        self.bot = bot
        self.bizManager = bizManager

    def run(self):
        key = "CHAT_QQ_MESSAGE_QUEUE"
        logger.info("启动了qq机器人发送消息任务")
        while True:
            try:
                time.sleep(self.config.bot_chat_base_interval + random.random() * self.config.bot_chat_interval)
                (r, rexcute) = RedisConnect().createRedis()
                data = r.lpop(key)
                logger.info("【qq机器人任务】data=%r", data)
                if data != None:
                    data = json.loads(data.encode('utf-8'))
                    biz_type = data.get("biz_type",None)
                    msg_type = data.get("msg_type",None)
                    group = data.get("group",None)
                    msg = data.get("msg", None)
                    user = data.get("user",None)
                    html = data.get("html",None)
                    img_path = data.get("img_path",None)
                    html = HtmlContent(html, "html")
                    if group is not None:
                        if  msg_type == 'text':
                            self.bot.send(group, user, msg, html)
                            if biz_type != 'chat':
                                self.bizManager.saveContext("qq", user, group, msg, biz_type)  # kwargs用于保存额外的上下文
                        else:
                            self.bot.send_image(group, user, img_path)
            except Exception as e:
                logger.error(e)


class WechatSchedule(Thread):
    def __init__(self, name, config,bot, bizManager):
        Thread.__init__(self)
        self.name = name
        self.config = config
        self.bot = bot
        self.bizManager = bizManager

    def run(self):
        key = "CHAT_WECHAT_MESSAGE_QUEUE"
        logger.info("启动了微信机器人发送消息任务")
        while True:
            time.sleep(self.config.bot_chat_base_interval + random.random() * self.config.bot_chat_interval)
            try:
                (r, rexcute) = RedisConnect().createRedis()
                data = r.lpop(key)
                logger.info("【微信机器人任务】data=%r",data)
                if data != None:
                    data = json.loads(data.encode('utf-8'))
                    biz_type = data.get("biz_type",None)
                    msg_type = data.get("msg_type",None)
                    group = data.get("group",None)
                    msg = data.get("msg", None)
                    user = data.get("user",None)
                    html = data.get("html",None)
                    img_path = data.get("img_path",None)
                    html = HtmlContent(html, "html")
                    if group is not None:
                        if  msg_type == 'text':
                            self.bot.send(group , user, msg, html)
                            if biz_type != 'chat':
                                self.bizManager.saveContext("wechat", user, group, msg, biz_type)  # kwargs用于保存额外的上下文
                        else:
                            self.bot.send_image(group, user, img_path)
            except Exception as e:
                logger.error(e)
if __name__ == '__main__':  # 必须要这样启动
    p = QQSchedule('定时发送qq消息')
    p.start()
