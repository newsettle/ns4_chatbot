# -*- coding: utf-8 -*-
import common.logger as logger
import sys,time
import threading
from common import http_helper
from bot.bot import BaseBot
import logging
from shutil import copyfile

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

ERROR_CODE={}
ERROR_CODE["1"]="同时 status 为 async，表示操作已进入异步执行，具体结果未知"
ERROR_CODE["100"]="参数缺失或参数无效，通常是因为没有传入必要参数"
ERROR_CODE["102"]="酷 Q 函数返回的数据无效，一般是因为传入参数有效但没有权限，比如试图获取没有加入的群组的成员列表"
ERROR_CODE["103"]="操作失败，一般是因为用户权限不足，或文件系统异常、不符合预期["
ERROR_CODE["104"]="由于酷 Q 提供的凭证（Cookie 和 CSRF Token）失效导致请求"
ERROR_CODE["201"]="工作线程池未正确初始化（无法执行异步任务）"

class QQBot(BaseBot):

    def __init__(self,bizManager,conf):
        self.conf = conf
        self.type = "qq"
        self.bizManager = bizManager #相当于给bot模块织入了一个bizManager
        self.qq = conf.coolq_qq

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

    class Message():

        def parse(self,data,qq):
            self.is_at = False

            sender = data.get('sender',None)
            if sender is None:
                logger.warn("此QQ消息没有sender:%r",data)
                return False
            group_id = data.get('group_id',None)    
            if group_id is None:
                logger.warn("此QQ消息没有group:%r",data)
                return False
            _msg = data.get('message',None)
            if _msg is None:
                logger.warn("此QQ消息没有message:%r",data)
                return False

            # sender":{"age":3,"nickname":"jacun","sex":"male","user_id":2796228812},
            self.sender = "{}({})".format(sender['nickname'] , sender['user_id'])
            self.group = group_id
            #   "message":"[CQ:at,qq=25473936] \xe6\xb5\x8b\xe8\xaf\x95”,
            self.msg = _msg

            if "CQ:at" not in self.msg: return True #只是发到群的消息，但是没有@我

            #@消息
            logger.debug("这是一条@消息：%s",self.msg)
            s = self.msg.find("qq=")
            e = self.msg.find("]")
            if s==-1 or e==-1: 
                logger.warn("无法@的QQ号码：%s",self.msg)
                return False

            self.qq = self.msg[s+3:e]
            if self.qq != qq: 
                logger.debug("@的QQ号码：%s和我的QQ号不同:%s", self.qq, qq)
                return False

            self.is_at = True
            logger.debug("是@给我[机器人]的消息，我来处理")
            self.msg = self.msg[e:]
            logger.debug("消息:%s",self.msg)

            return True

    #消息格式：    
    # b’{
    #     "discuss_id":1520910408,
    #     "font":35232408,
    #     "message":"[CQ:at,qq=25473936] \xe6\xb5\x8b\xe8\xaf\x95”,
    #     "message_id":91,
    #     "message_type":"discuss”,
    #     "post_type":"message”,
    #     "raw_message":"[CQ:at,qq=25473936] \xe6\xb5\x8b\xe8\xaf\x95”,
    #     "self_id":25473936,”
    #     sender":{"age":3,"nickname":"jacun","sex":"male","user_id":2796228812},
    #     "time":1546934868,
    #     "user_id":2796228812
    # }’
    def on_message(self,data):
        msg = self.Message()

        if not msg.parse(data,self.qq):
            logger.warn("解析消息失败：%r",data)
            return None
        else:
            # 记录这个群的消息到日志文件
            logger.history("qq", str(msg.group), msg.sender, msg.msg)

        #不在我注册的群组里，不予处理
        if not str(msg.group) in self.group_list: return None

        logger.debug('收到消息[message]：%s', msg.msg)
        logger.debug('发消息者[sender]：%s', msg.sender)
        logger.debug('发送群[group]：%s', msg.group)

        #被群内其他成员 @ 的通知
        if not msg.is_at:
            logger.debug("不是@我的消息")
            return None

        logger.debug("检查bot上注册的群/讨论组：group[%s],sender[%s]",msg.group,msg.sender)

        # 得到我们的业务处理组件 | route(self, client, user, group, msg):
        biz_comp, context = self.bizManager.route("qq", msg.sender, msg.group, msg.msg)
        if biz_comp is None:
            logger.error("无法找到对应的业务处理器！[QQ],user[%s],group[%s]",msg.sender,msg.group)
            return "不理解您的回复，请再对我说点啥"

        logger.debug("成功加载业务处理器[%r]",biz_comp)

        # 调用业务组件的接口方法来处理消息
        return biz_comp.bot2system(self,"qq",context,msg.sender, msg.group, msg.msg)
        
    #通过酷Q的http api发送消息
    #targe_id分别是qq_id， group_id，   
    #私聊消息需要对方先说话
    def __send_msg(self,action,target_type,target_id,msg):

        super(QQBot,self).random_wait()#随机等待3秒

        url = self.conf.coolq_url+action
        qq = self.conf.coolq_qq
        data = {target_type:target_id,"message":msg,"auto_escape":False}

        logger.debug("消息发往酷Q：url=%s,user_id=%s,message=%r",url,qq,data)
        result = http_helper.do_request_json(url,data)
        logger.debug("HTTP返回结果：%r",result)
        if result is None: return False
        '''
        {
            "status": "ok",
            "retcode": 0,
            "data": {
                "id": 123456,
                "nickname": "滑稽"
            }
        }
        '''
        status = result['status']
        retcode = result['retcode']
        error_msg = ERROR_CODE.get(str(retcode),"未知错误码")
        if retcode!=0:
            logger.warn("调用酷Q HTTP接口失败：status=[%s],retcode=[%d],error=[%s]",
                status,retcode,error_msg)
            return False

        return True


    #私聊消息需要对方先说话
    def send_private_msg(self,action,target_id,msg):
        self.__send_msg("send_private_msg","user_id",target_id,msg)

    def send_group_msg(self,group_id,msg):
        return self.__send_msg("send_group_msg","group_id",group_id,msg)

    #讨论组不是单纯的讨论组id，需要转换,讨论组 ID（正常情况下看不到，需要从讨论组消息上报的数据中获得）
    def send_discuss_msg(self,discuss_id,msg):
        self.__send_msg("send_discuss_msg","discuss_id",discuss_id,msg)


    #注意，这个时候，组为对应的群的号，不在是名称了    
    def send(self,group_id, user, message,html=None):
        msg = message
        if user:
            msg = message + "\n@" + user
        r = self.send_group_msg(group_id,msg)

        if not r:
            logger.warn("CoolQ调用API失败")

        self.__send_html(group_id,user,html)

    def send_image(self,group_id,user,img_path):
        logger.debug("发送图片到QQ服务器，群[%s],图片[%s]",group_id,img_path)
        if group_id is None:
            logger.error("错误发送图片到QQ服务器，群名字为空")
            return False
        #./coolq/data/image/CJKunlGo.jpg ==> CJKunlGo.jpg   
        #只需要文件名，因为文件已经放到酷Q约定的目录里了，是在bot.conf coolq[cache_path]定义的
        img_name = img_path[img_path.rfind("/")+1:]    

        src = img_path
        dst = self.conf.coolq_cache_path+"/"+img_name

        if src!=dst:
            logger.debug("复制QQ图片到酷Q目录，src:%s => det:%s",src,dst) 
            copyfile(src,dst)   
        else:
            logger.debug("QQ图片源目标相同，忽略:%s",src) 

        try:
            
            self.random_wait()
            #[CQ:image,file=file:///C:\Users\richard\Pictures\1.png]
            if user:
                msg = "[CQ:image,file={}] \n@{}".format(img_name,user)
            else :
                msg = "[CQ:image,file={}]".format(img_name)
            logger.debug(u"发送图片[%s]给QQ群[%s]", msg,group_id)
            return self.send_group_msg(group_id,msg)
        except Exception as e:
            logger.warn(u"发送图片到QQ失败,原因：%s", str(e))
            return False        

    def __send_html(self,group_id,user,html):
        #还要把大的html消息转成图片发送过去
        if html is None: return

        #这里传入coolq的图片路径，是为了直接生成，不用再拷贝了
        content = html.get_content("qq")
        img_path = ''
        if content:
            img_path = super(QQBot,self).html2img(content,self.conf.coolq_cache_path)

        super(QQBot,self).random_wait()

        if img_path is None:
            logger.debug("图片生成失败，发送纯文本给QQ用户：%s",html)
            if content:
                r = self.send_group_msg(group_id,html.get_plain_content())
                logger.debug("CoolQ API调用结果：%r",r)
            return False

        try:
            logger.debug("发送本地HTML生成图片[%s]给QQ用户", img_path)
            r = self.send_image(group_id,user,img_path)
            logger.debug("CoolQ API调用：%r",r)
        except Exception as e:
            logger.warn("发送图片到QQ服务器失败，改为发送文本消息，图片发送失败原因：%s",str(e))
            logger.debug("发送HTML文本给QQ用户：%s", html)
            r = self.send_group_msg(group_id,html.get_plain_content())
            logger.debug("CoolQ API调用结果：%r",r)

        return r

    def startup(self):
        logger.info("启动QQ机器人服务器.....")

    #groups 是一个list
    def register(self, group_names):
        logger.debug("注册QQ群组：%r", group_names)
        self.group_list = group_names
