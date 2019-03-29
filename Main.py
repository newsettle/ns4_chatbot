# -*- coding: utf-8 -*-
from web.http_server import Http_Server
from bot.bot_manager import BotManager
from business.biz_manager import BizManager
from common import db_helper
from common import common
import common.logger as logger
from common.config import Config
from common.redis_helper import RedisConnect

def welcome():
	return \
"  _______          _________ _______         ______   _______ _________\n \
(  ___  )|\     /|\__   __/(  ___  )       (  ___ \ (  ___  )\__   __/\n \
| (   ) || )   ( |   ) (   | (   ) |       | (   ) )| (   ) |   ) (   \n \
| (___) || |   | |   | |   | |   | | _____ | (__/ / | |   | |   | |   \n \
|  ___  || |   | |   | |   | |   | |(_____)|  __ (  | |   | |   | |   \n \
| (   ) || |   | |   | |   | |   | |       | (  \ \ | |   | |   | |   \n \
| )   ( || (___) |   | |   | (___) |       | )___) )| (___) |   | |   \n \
|/     \|(_______)   )_(   (_______)       |/ \___/ (_______)   )_(   \n \
\
@copyright 2018 - fuqianla.com"

if __name__ == "__main__":

	print welcome()

	#配置
	conf = Config()
	logger.init()

	#为了让common.py中的类可以直接访问配置，来个trick
	common.set_config(conf)

	RedisConnect(conf.redis_ip,conf.redis_port,conf.redis_password).init()

	#初始化数据库 TODO，创建了一个全局变量con/graph，得改
	if not db_helper.init(conf): exit(0)

	#启动机器人管理器
	botManager = BotManager(conf)

	#创建业务管理器，
	bizManager = BizManager(botManager,None,conf)

	#启动各个机器人（微信、QQ）
	botManager.startup(bizManager,conf)

	# #启动Flask Web 服务
	logger.info("启动Web服务器.....")
	http_server = Http_Server(bizManager,conf)
	http_server.startup()
	logger.info("启动机器人发送消息任务")
	botManager.startTask()

	logger.info("所有的服务启动完毕！")

