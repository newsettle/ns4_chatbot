#-*- coding:utf-8 -*-
import sys
sys.path.append("..")

from common import logger
from common.common import send_email
from bot import BaseBot

class Email_Bot(BaseBot):

    bot = None

    def __init__(self,bizManager,config):
        self.config = config
        self.bizManager = bizManager
        self.type = "email"

    #能bot.search到的群，应该都是之前注册的那些群
    def send(self, email, user_name, message,html=None): #html type is "Content"
		msg_split_pos = message.find("\n") #第一行为标题
		title = message[0:msg_split_pos]
		content = message[msg_split_pos + 1:]

		send_email(email,title,content)
		logger.debug("成功发给邮件[%s]消息:%s",email,content)

    def send_image(self,group_name,user,img_path):
		pass

    def register(self,group_names):
		pass

if __name__ == '__main__':
	pass
