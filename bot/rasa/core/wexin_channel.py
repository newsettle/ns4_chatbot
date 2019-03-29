# -*- coding: UTF-8 -*-
from rasa_core.channels.channel import UserMessage
from rasa_core.channels.channel import InputChannel, OutputChannel
import random, time
from wxpy import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#当需要发送消息
class WeixinOutputChannel(OutputChannel):

    def __init__(self, weixin_group = None):
        self.weixin_group = weixin_group

    #message就是rasa产生的utterance对话，用于发送到微信去
    def send_text_message(self, recipient_id, message):
        print "准备push到微信机器人的消息：%s" % message
        time.sleep(3*random.random())#休息3秒以内，防止频发发往微信，防止被封号
        self.weixin_group.send(message)

#用于接收到消息，用于从微信接受消息，并转发到机器人
class WeixinInputChannel(InputChannel):
    def __init__(self, bot = None):
        self.bot = bot

    def _record_messages(self, on_message):
        group_name = u'聊天机器人'
        groups = self.bot.groups().search(group_name)
        if groups is None and len(groups) == 0:
            print("找不到聊天群：%s" % group_name)
            exit()

        the_group = groups[0]
        print("找到目标群：%s" % the_group)

        @self.bot.register(the_group, run_async=False)
        def print_message(msg):
            print(msg.text)
            #这里和微信衔接上了，将微信的消息转发给RASA系统
            on_message(UserMessage(msg.text, WeixinOutputChannel(the_group)))

    def start_async_listening(self, message_queue):
        self._record_messages(message_queue.enqueue)

    def start_sync_listening(self, message_handler):
        self._record_messages(message_handler)
