# -*- coding: utf-8 -*-
import time
import tempfile,random,string
from common.common import BaseService
import HTMLParser
import imgkit
from common import logger
class BaseBot(BaseService):

    type = None
    '''
        给指定的群组和用户发消息
        由于目前，很少给用户发消息，所以，没必要定一个send(user,message)接口
        group:   QQ群名称、QQ讨论群名称、微信群名称
        user：   QQ中的昵称，微信群中的昵称
        message：消息
    '''
    def send(self,group,user,message,html):
        raise NotImplementedError

    def send_image(self,group,user,img_path):
        raise NotImplementedError

    def register(self,groups):
        raise NotImplementedError

    #为防止发送过于频繁，等待一个1-3秒的随机数
    def random_wait(self):
        time.sleep(random.random()*3)

   # 报警的邮件要转成图片发给微信机器人，遇到字体问题， out.jpg图片是乱码，反反复复实践解决：
    # 2.必须要修改网页，加入 < meta charset = "UTF-8”>到HTML里面
    def __insert_meta(self, html):

        html_parser = HTMLParser.HTMLParser()
        html = html_parser.unescape(html)  # 先把 &quot转成"
        html_pos = html.find("<head>")
        if html_pos == -1:
            logger.warn("无法在邮件的HTML文本中查找到<head>标记，插入meta-charset失败")
            return html
        meta = "<meta charset=\"UTF-8\">"
        html_pos = html_pos + 6
        html = html[:html_pos] + meta + html[html_pos:]
        return html

    # 将html转成图片，存放到系统临时目录
    def html2img(self, html,dir=None):

        html = self.__insert_meta(html)
        if dir is None :
            dir = tempfile.gettempdir()

        random_file_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        temp_file = dir + "/" + random_file_name + ".jpg"
        try:
            imgkit.from_string(html, temp_file, {"xvfb": "", "encoding": "UTF-8"})#, {"xvfb": "", "encoding": "UTF-8"})  #  {"xvfb": "", "encoding": "UTF-8"}这个选项是在Ubuntu上测试的时候发现的
        except Exception as e:
            logger.exception(e, "将HTML转化成图片失败：%s,\n%s", str(e), html)
            return None
        return temp_file        