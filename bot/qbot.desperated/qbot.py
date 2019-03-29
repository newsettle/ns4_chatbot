# -*- coding: utf-8 -*-
import common.logger as logger
import sys,time
import threading

from qqbot import _bot as bot
from qqbot.mainloop import Put
from common.common import BaseBot
import logging

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

class QBot(BaseBot):

    def __init__(self,bizManager,conf):
        self.conf = conf
        self.bizManager = bizManager
        self.type = "qq"
        bot.bizManager = bizManager #相当于给bot模块织入了一个bizManager
        bot.qbot = self

    def send_image(self, group, user, img_path):
        logger.debug("QQ发送图片到服务器，未实现！群[%s],图片[%s]", group, img_path)
        pass#do nothing,默认什么也不做，QQ无法发送图片


    #API: def List(self, tinfo, cinfo=None):
    #根据名字查找到组，群优先，讨论组次之
    def find_group_discuss(self,name):
        groups = bot.List('group', name)
        if groups is not None and len(groups)>0:
            return groups[0]

        discusses = bot.List('discuss', name)
        if discusses is not None and len(discusses)>0:
            return discusses[0]

        return None

    #根据组，找到组内符合这个名字的人
    def find_member(self):
        bot.List()

    #回调方法，注意！这个方法是在主线程中被调用的
    def _send(self,group_name, member_name, message):
        logger.debug("准备发往QQ的消息，群[%s],人[%s]:%s", group_name, member_name, message)
        contact = self.find_group_discuss(group_name)
        if contact is None:
            logger.error("找不到QQ群或者讨论组，名字是%s",group_name)
            return

        logger.debug("找到了群组：%r", contact)

        # member = find_member(contact,member_name)
        bot.SendTo(contact, message)
        time.sleep(1)  # 间隔一秒，防止被封
        bot.SendTo(contact, '@' + member_name)

    def send(self,group_name, member_name, message,html=None):

        if html is not None:
            html = html.get_content(self.type)
            message += "\n" + html
        logger.info("qq消息发送：[%s][%s][%s]"%(group_name,member_name,message))
        Put(self._send, group_name, member_name, message)

    def startup(self):
        super(QBot,self).startup()

        logger.info("启动QQ机器人服务器.....")
        cond = threading.Condition()

        cond.acquire()

        t = threading.Thread(target=self._startup, name='qq-bot', args=(cond,))
        t.start()

        logger.debug("启动单独线程来进行QQ登陆")
        cond.wait()
        logger.debug("QQ服务器启动完毕，接下来进行其他组件的加载启动")

    def _startup(self,cond):

        # --bench .cache    临时目录在哪里？
        # --cmdQrcode       使用Console的二维码
        # --pluginPath      插件放在哪个目录

        if not self.conf.debug:
            logger.debug("QQ启动生产模式")
            args = "--bench .cache/qbot/ --mailAccount 12345678@qq.com --mailAuthCode sxlxhrgeqvzoiaba --pluginPath qbot/plugs --plugins message_processor".split(" ")
        else:
            logger.debug("QQ启动调试模式,QQ号:%s",self.conf.debug_qq)
            __arg = "--bench .cache/qbot/ --debug --cmdQrcode -q " + self.conf.debug_qq + " --pluginPath qbot/plugs --plugins message_processor"
            args = __arg.split(" ")
        logger.info("启动bot.Login登录,args:%s",args)
        # bot.rasa_server = rasa_server #bot这个实例身上给生生安上了一个rasa_server的实例

        cond.acquire()
        bot.Login(args)
        cond.notify()
        cond.release()

        logger.debug("进入bot.Run 死循环等待中...")
        logging.getLogger("Utf8Logger").setLevel(logging.WARNING)#去掉QQ的debug日志
        bot.Run()
        '''
        bot会进入一个死循环，就是不停地去消息，然后处理了
        def QQbot..workAt(taskQueue):
            while True:
                try:
                    func, args, kwargs = taskQueue.get(timeout=0.5)
                except Queue.Empty:
                    pass
                else:
                    # func(*args, **kwargs)
                    try:
                        func(*args, **kwargs)

        '''

    #groups 是一个list
    def register(self, group_names):
        logger.debug("注册QQ群组：%r", group_names)
        bot.groups = group_names #生在bot身上注入了一个groups变量，这个是为了让plugin中可以直接访问到



if __name__ == '__main__':
    QBot().startup()

