#-*- coding:utf-8 -*-
import sys
sys.path.append("..")

from wxpy import *
import threading
from common import logger
from bot.bot import BaseBot
from common.common import send_email,send_sms
from common.retry import Retry
import imgkit,time
import tempfile,random,string
import random, time

class Wexin_Bot(BaseBot):

    bot = None

    def __init__(self,bizManager,config):
        self.config = config
        self.bizManager = bizManager
        self.type = "wechat"
        self.retry = Retry()


    def startup(self):
        super(Wexin_Bot,self).startup()
        logger.info("启动微信机器人.....")
        t = threading.Thread(target=self._startup, name='wx-bot')#传入参数rasa_server给线程

        t.start()
        # join所完成的工作就是线程同步，即主线程任务结束之后，进入阻塞状态，一直等待其他的子线程执行结束之后，主线程在终止
        # 这里会阻塞，等到t这个结束后，才能继续
        #这里加入这个，是为了等待_startup函数结束后，再继续往下走，这样，外面，也就是Main.py中的register函数才能严格按顺序执行
        t.join()
        logger.info("微信机器人启动完毕！")

    #status：登陆成功->'200'，已扫描二维码->'201'，二维码失效->'408'，未获取到信息->'0'
    def qr(self,uuid, status, qrcode): #这个回调参数是在itchat.component.login.py line 50找到的
        # status：登陆成功->'200'，已扫描二维码->'201'，二维码失效->'408'，未获取到信息->'0'
        if status == u'201' or status == u'200':
            logger.info("QR返回200，已经登录状态")
            return

        if not self.retry.is_need_retry(self.config): return

        qr_path = self.config.wxbot_qr_path
        logger.debug("QR二维码产生出来了:uuid[%r],status[%r],QR[%r]",uuid,status,qrcode)

        if len(qrcode)==0:
            logger.error("异常！QR二维码生成的图片为空，无法完成登录任务，只能稍后再试，status[%r]",status)
            return
        else:
            with open(qr_path, 'wb') as f:
                f.write(qrcode)
            logger.debug("生成新的QR二维码文件：%s",qr_path)

        if not send_email(self.config.admin_email, "微信登录请求", "请尽快扫描此微信二维码，用来登录助手机器人", qr_path ):
            logger.error("发送微信二维码到管理员邮箱失败")
            return

        send_sms("微信重新登陆，尽快去邮箱扫描二维码")

        logger.info("已将二维码发送到管理员邮箱，请尽快扫码登录")

    def login(self):
        logger.info("已经成功登录到微信服务器")

    def __process_login(self):
        cache_file = self.config.wxbot_cache_path + "/" + self.config.wxbot_cache_file
        logger.debug("启动微信登录：cache_file=%s,console_qr=%r,qr_path=%s",
                     cache_file,
                     self.config.wxbot_console_qr,
                     self.config.wxbot_qr_path)
        if self.config.wxbot_console_qr:
            self.bot = Bot(
                cache_path=cache_file,
                console_qr=self.config.wxbot_console_qr,
                login_callback=self.login,
                logout_callback=self.logout)
        else:
            self.bot = Bot(
                cache_path=cache_file,
                console_qr=self.config.wxbot_console_qr,
                qr_path=self.config.wxbot_qr_path,
                qr_callback=self.qr,
                login_callback=self.login,
                logout_callback=self.logout)


    def logout(self):

        logger.error("!!!警告：微信机器人已经登出，正在尝试重新登陆!!!")

        # #删除QR图片，之前报错，诡异的一个filenotfound异常，所以，暂时先不删除QR了
        # if os.path.exists(self.config.wxbot_qr_path):
        #     logger.info("QR文件缓存存在，登出的时候删除掉它")
        #     os.remove(self.config.wxbot_qr_path)

        self.__process_login()

    def _startup(self):
        logger.info("正在启动微信登录过程...")
        self.__process_login()

        #保存rasa的引用
        logger.info("微信机器人登录结束...")

        #在启动后，直接调用register来注册一个on_message函数，到指定的微信群上
        #为何要在这里做呢？因为如果这个时候不做，后面这句 bot.join就会阻塞这个过程
        #如果在外面调用，必须等待这个_startup运行完毕，
        #但是，这里面必须要写个
        #self.register(group_names)
        #这个线程，会挂在这里，防止退出


    #能bot.search到的群，应该都是之前注册的那些群
    def send(self, group_name, user_name, message,html=None): #html type is "Content"

        groups = self.bot.search(group_name)
        if groups is None or len(groups)==0:
            logger.warn("无法找到微信群[%s]",group_name)
            logger.warn("因此，    发送消息到微信群失败：%s",message)
            return

        for group in groups:

            self.__send_html(group,html)

            # http://wxpy.readthedocs.io/zh/latest/faq.html,
            # 此api项目不支持@，这里@，只是一个字符串消息而已
            try:
                self.random_wait()
                if user_name:
                    group.send(message + "\n\n@" + user_name)
                else:
                    group.send(message)
            except ResponseError as e:
                logger.exception(e, "发送消息给微信服务失败，原因：%s", str(e))
                return

            logger.debug("成功发给[%s]消息:%s",group_name,message)

    def __send_html(self,group,html):
            #还要把大的html消息转成图片发送过去
            if html is None: return
            content = html.get_content("wechat")
            img_path = ''
            if content:
                img_path = self.html2img(content)
            self.random_wait()
            if not img_path or img_path is None:
                if content:
                    logger.debug("发送HTML文本给用户：%s", html)
                    group.send(html.get_plain_content())
                return

            try:
                logger.debug("发送本地HTML生成图片[%s]给用户", img_path)
                group.send_image(img_path)
            except ResponseError as e:
                logger.warn("发送图片到微信服务器失败，改为发送文本消息，图片发送失败原因：%s",str(e))
                logger.debug("发送HTML文本给用户：%s", html)
                group.send(html.get_plain_content())

    def send_image(self,group_name,user,img_path):
        logger.debug("发送图片到微信服务器，群[%s],图片[%s]",group_name,img_path)
        if group_name is None:
            logger.error("发送图片到微信服务器，群名字为空")
            return

        groups = self.bot.search(group_name)
        if groups is None or len(groups) == 0:
            logger.warn(u"无法找到微信群[%s],发送图片到此群失败", group_name)
            return
        for group in groups:
            try:
                logger.debug(u"发送图片[%s]给用群[%s]", img_path,group)
                self.random_wait()
                group.send_image(img_path)
            except ResponseError as e:
                logger.warn(u"发送图片到微信服务器失败,原因：%s", str(e))

 

    #注册我对那些微信群感兴趣
    def register(self,group_names):
        logger.debug("注册微信群组：%r",group_names)
        if not isinstance(group_names,str) and not isinstance(group_names,list):
            raise TypeError("groups must be string or list")

        groups = []

        if isinstance(group_names,list):
            for one_group in group_names:
                groups = groups + self.bot.search(one_group)

        if isinstance(group_names, str):
            groups = groups + self.bot.search(group_names)

        logger.debug("注册消息接受函数：%r", groups)

        #消息处理函数，记住，这个函数的返回，就是要发给群组的消息
        @self.bot.register(groups)
        def on_message(msg):
            message = msg.text

            logger.debug("接收到微信消息：type=%s,message=%s",msg.type,msg.text)

            if msg.type =="TEXT":
                logger.debug("从微信端接收的raw消息：%s",message)

                # 把聊天内容保存到文章中
                logger.history(self.type, msg.chat.name, msg.member.name, message)

            #如果不是群聊，不理他    
            if not isinstance(msg.chat, Group):
                logger.warn("目前，只支持群聊天")
                return "目前只支持群聊天"

            # 如果是群聊，但没有被 @，则不回复
            # msg.chat:
            #   消息所在的聊天会话，即:
            #   对于自己发送的消息，为消息的接收者
            #   对于别人发送的消息，为消息的发送者

            str_msg = ""
            if msg.type.upper() =="TEXT" and msg.is_at:
                pass
            else:
                logger.debug("不是@给自己的消息，忽略：%s", message)
                return


            #如果录音的话，就不管@没@了，直接接受语音转成文字，作为消息
            if msg.type == "Recording":
                logger.debug("消息格式为声音，使用科大讯飞或百度转化")
                str_msg = "FAILED"#voice2txt.v2t(msg.get_file())
                logger.debug("科大讯飞转化结果为：%s",str_msg)
                if str_msg is None:
                    logger.error("语音转化失败")
                    return
                else:
                    msg.reply("您说：["+str_msg+"]")
            elif msg.type.upper() =="TEXT":
                str_msg = self.remove_at(message)

            logger.debug("接收到发给我(bot)的消息：%s", str_msg)

            user = msg.member.name
            group = msg.chat.name

            # 得到我们的业务处理组件 | route(self, client, user, group, msg):
            biz_comp, context = self.bizManager.route(self.type, user, group, str_msg)
            # 调用业务组件的接口方法来处理消息
            logger.debug("调用业务组件bot2system：type=%s,user=%s,group=%s,msg=%s",self.type,user, group, str_msg)
            returnMsg = biz_comp.bot2system(self,self.type, context, user, group, str_msg)

            self.random_wait()  # 间隔一下，防止被封

            return returnMsg

    def remove_at(self,msg):
        ret=msg.split()
        print(ret)
        ret=ret[1:]
        print(ret)
        wocao=""
        for i in ret:
            wocao+=i+' '
        return wocao.strip()

if __name__ == '__main__':
    # s="<!DOCTYPE html><html><head><meta charset=utf-8><title></title><style type=text/css>table, td, th{border-collapse:collapse;border:1px solid blue;}th{height: 40px;background-color: #EFEEEE;}td{height: 30px;text-align: center;}</style></head><body><div><header><h1></h1></header><div><h4>预留备注：订单超时</h4><h3>报警内容：</h3><p><font color='red'>在过去【1】分钟，出现超时订单或者超时【0】秒未完成订单，达到了【41】笔，超过了报警阈值【0】笔,统计时间段：【201807051613】-【201807051614】,请关注！</font></p><h5>以下为各个超时订单具体信息：</h5><table><tr><th>订单号</th><th>商户名称</th><th>支付方式</th><th>通道名称</th><th>银行名称</th><th>交易金额</th><th>响应码</th><th>响应信息</th></tr><tr><td>jk031805161359005367395271</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161357490174487665</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161356607068482871</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161354393638518371</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161353082092927267</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161351687408208787</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161350707995863471</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161349542628158209</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161347560531062201</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161346525383097442</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161345120636064819</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161343558692639478</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161342531705342473</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161341733973466103</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161340922327412020</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161338202320802351</td><td>0000105</td><td>03</td><td>HYL</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161337549347008789</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161335037559598506</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161334494747111307</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161333455032571020</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161331521976765053</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161330397579079210</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161329848237851570</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161327046185990115</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161326015150533500</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161324409978140977</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161323214142313364</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161322576255054558</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161321930944170033</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161319813982175182</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161318496102684803</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161316481329655662</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161315538593430807</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161308275752985140</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161308464960248669</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161305985776726386</td><td>0000105</td><td>03</td><td>HYL</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161305277033352521</td><td>0000105</td><td>03</td><td>HYL</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161302616052939638</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161302532274233578</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161259817844826298</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161259718313109371</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr></table></div>预警等级：严重!,</br></br><div><p>【以下内容可忽略】 为定位报警系统问题预留，读取规则信息：</br>通知邮件发送时间[2018-07-05 16:14:00 020],</br></p></div></div></body></html>"
    # bot = Wexin_Bot(None)
    # print bot.__html2img(s)

    s = "<!DOCTYPE html><html><head><title></title><style type=text/css>table, td, th{border-collapse:collapse;border:1px solid blue;}th{height: 40px;background-color: #EFEEEE;}td{height: 30px;text-align: center;}</style></head><body><div><header><h1></h1></header><div><h4>预留备注：订单超时</h4><h3>报警内容：</h3><p></p></div></div></body></html>"
    bot = Wexin_Bot(None)
    print s
    print "---------------"
    print bot.__insert_meta(s)

