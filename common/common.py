#-*- coding:utf-8 -*-
import logger,urllib,urllib2,json,smtplib,time
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import random
import html_clear

def set_config(conf):
    global config
    config = conf

class HtmlContent(object):

    # content：传入的内容，可以是plain(纯文本），也可以是html（html文本）
    # type：来表示content到底是什么类型：plain | Html
    # client：客户端：qq|wechat
    def __init__(self,content,type):
        self.type = type
        self.content = content

    #无论你是什么类型，我都给你转化成纯文本
    def get_plain_content(self):
        if not self.content or self.content == '':
            return ''
        if self.type == "plain":
            logger.debug("得到plain text")
            return self.content
        if self.type == "html":
            logger.debug("得到plain text，但是type=html，所以要去除HTML标签")
            global config
            return html_clear.clean_html(self.content,config)
        return None

    def get_content(self,client):
        if not self.content or self.content == '':
            return ''
        logger.debug("HTML消息处理：type=%s,client=%s",self.type,client)
        if self.type == "plain" :
            logger.debug("plain消息，所以追加HTML标签")
            return "<html><head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>" \
                   "</head><body><pre>" + self.content + "</pre></body></html>"

        #这种情况是，我是plain并且我是QQ，或者我是HTML并且我是微信
        logger.debug("HTML消息，不做任何处理")
        return self.content#传入的是Html，

#定义一个基础服务类
class BaseService(object):
    #定义服务的启动
    def startup(self):
        logger.info("========================================")

# 耗时计算
def duration(t, title):
	now = time.time()
	logger.debug("%s：耗时%f秒", title, (now - t))
	return now

# 使用
def short_url(apiUrl):
    try:
        logger.debug("将长URL[%s]转化成短URL",apiUrl)
        target_url = urllib.quote(str(apiUrl))
        url = "http://suo.im/api.php?format=json&url=" + target_url
        logger.debug("调用短URL生成[%s]", apiUrl)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request,timeout=3)

        result_dict = json.loads(response.read())

        if response.getcode() != 200:
            logger.warn("调用短URL服务失败：%s", result_dict["err"])
            return None

        logger.debug("调用短URL服务返回结果:%s", result_dict["url"])

        return urllib.unquote(result_dict["url"])

    except Exception as e:
        logger.warn("调用短URL服务[%s],发生错误[%s]", apiUrl, str(e))
        return None

def send(apiUrl, data):
    data_json = json.dumps(data)
    headers = {'Content-Type': 'application/json'}  # 设置数据为json格式，很重要
    request = urllib2.Request(url=apiUrl, headers=headers, data=data_json)
    response = urllib2.urlopen(request,timeout=3)
    print response.read()

    content = json.dumps(response.read())  # _,encoding="UTF-8", ensure_ascii=False)
    result = {'code': response.getcode(), 'content': content}
    print("调用[%s]返回结果:%r" % (apiUrl, result))
    return result

def send_sms(content,mobile_num = None):
    # logger.debug("调用内部系统[%s],data[%r]",apiUrl,data)

    try:

        data = {"merchId": config.sms_merchId,
                "orderId": config.sms_orderId,
                "smsTypeNo": config.sms_smsTypeNo,
                "mobile": config.admin_mobile,
                "stp_content": str(content)}
        data_urlencode = urllib.urlencode(data)
        request = urllib2.Request(url=config.sms_server, data=data_urlencode)
        response = urllib2.urlopen(request,timeout=3)
        result = {'code': response.getcode(), 'content':json.loads(response.read())}
        if result['content']['retCode'] == '0000':
            logger.info("短信发送成功")
        else:
            logger.info("短信发送失败：状态[%s],原因[%s]",result['content']['retCode'],result['content']['retInfo'])
        # 返回'content' 的内容
        # {
        #     "retCode": "0000",
        #     "retInfo": "提交成功",
        #     "data": {}
        # }
        return result['content']
    except Exception as e:
        #这里不能用logger.error或者logger.exception，否则，容易形成死循环
        logger.info("短信发送失败：content=%s",content)
        logger.info("短信失败原因：%s", str(e))
        return None


def send_email(email,subject,content,attach_file_path=None):

    if not email: email = config.admin_email

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = config.email_user
    msg['To'] = email

    to_users = email.split(',')

    # 构造文字内容
    text_plain = MIMEText(content, 'plain', 'utf-8')
    msg.attach(text_plain)

    # jpg类型附件
    if attach_file_path is not None:
        part = MIMEApplication(open(attach_file_path, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=attach_file_path)
        msg.attach(part)

    try:

        if config.email_SSL:
            s = smtplib.SMTP_SSL(config.email_server, config.email_port)  # 邮件服务器及端口号
        else:
            s = smtplib.SMTP(config.email_server, config.email_port)  # 邮件服务器及端口号
        s.login(config.email_user, config.email_passwd)
        s.sendmail(config.email_user,to_users, msg.as_string())
        logger.debug("邮件发送完毕：title=%s,content=%s", subject, content)
        s.quit()
        return True
    except Exception as e:
        #这里不能用logger.error或者logger.exception，否则，容易形成死循环
        logger.info("邮件发送失败：title=%s,content=%s",subject,content)
        logger.info("邮件失败原因：%s", str(e))
        logger.info("邮件配置信息：server=%s,user=%s,pass=%s,to=%s",
                    config.email_server,
                    config.email_user,
                    config.email_passwd,
                    config.admin_email)
        return False



if __name__ == "__main__":
    print "common"
    logger.init_4_debug()
    url = u"http://xxxxxxxx/index.html#/monitorFlow/flowDetail?workOrderId=00EC2F262FCA49CFB8529C5BC315BD42&alarmId=86A034B317734471990381EB6C744D66&workOrderTitle=【订单超时】结算平台订单超时预警邮件&workOrderNumber=20180604123715003583&workOrderStateCode=UNTREATED&importantLevelCode=IMPORTANT&businessSystemCode=NEW_SETTLEMENT&disposeResultCode&ruleTypeCode=TRADE_OVERTIME&pstateCode=UNTREATED&bussysCode=NEW_SETTLEMENT&levelCode=IMPORTANT"
    print short_url(url)
    #send_sms("这是一个托尔斯泰代码")
