# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import os, platform, uuid, subprocess, time
import threading
from qqbot.utf8logger import WARN, INFO, DEBUG, ERROR
from qqbot.common import StartDaemonThread, LockedValue, HasCommand, SYSTEMSTR2STR
from qqbot.qrcodeserver import QrcodeServer
from mailagent import MailAgent

Image = None

class QrcodeManager(object):
    def __init__(self, conf):
        qrcodeId = uuid.uuid4().hex
        self.qrcodePath = conf.QrcodePath(qrcodeId)

        if conf.mailAccount:
            self.mailAgent = MailAgent(
                conf.mailAccount, conf.mailAuthCode, name='QQBot管理员'
            )
            

            html = ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                        '若二维码已过期，请将本邮件设为已读邮件，之后 QQBot 会在'
                        '1~2分钟内将最新的二维码发送到本邮箱。</p>'
                        '<p>{{png}}</p>')
            
            html += '<p>conf.user=%r, conf.qq=%r</p>' % (conf.user, conf.qq)

            self.qrcodeMail = {
                'to_addr': conf.mailAccount,
                'html': html,
                'subject': ('%s[%s]' % ('QQBot二维码', qrcodeId)),
                'to_name': '我'
            }
            
            self.qrcode = LockedValue(None)

        else:
            self.mailAgent = None
        
        # self.cmdQrcode = conf.cmdQrcode

    
    def Show(self, qrcode):
        with open(self.qrcodePath, 'wb') as f:
            f.write(qrcode)

        from qqbot import _bot
        if hasattr(_bot, 'onQrcode'):
            _bot.onQrcode(self.qrcodePath, qrcode)

        
        if self.mailAgent:
            if self.qrcode.getVal() is None:
                self.qrcode.setVal(qrcode)
                # first show, start a thread to send emails
                StartDaemonThread(self.sendEmail)
            else:
                self.qrcode.setVal(qrcode)
    
    def sendEmail(self):
        lastSubject = ''
        while True:
            if lastSubject != self.qrcodeMail['subject']:
                qrcode = self.qrcode.getVal()            
                if qrcode is None:
                    break
                qrcode = '' if self.qrcodeServer else qrcode
                try:
                    with self.mailAgent.SMTP() as smtp:
                        smtp.send(png_content=qrcode, **self.qrcodeMail)
                except Exception as e:
                    WARN('无法将二维码发送至邮箱%s %s', self.mailAgent.account, e, exc_info=True)
                else:
                    INFO('已将二维码发送至邮箱%s', self.mailAgent.account)
                    if self.qrcodeServer:
                        break
                    else:
                        lastSubject = self.qrcodeMail['subject']
            else:
                time.sleep(65)
                qrcode = self.qrcode.getVal()            
                if qrcode is None:
                    break
                try:
                    DEBUG('开始查询邮箱 %s 中的最近的邮件', self.mailAgent.account)
                    with self.mailAgent.IMAP() as imap:
                        lastSubject = imap.getSubject(-1)
                except Exception as e:
                    WARN('查询邮箱 %s 中的邮件失败 %s', self.mailAgent.account, e)
                else:
                    DEBUG('最近的邮件： %s', lastSubject)
    
    def Destroy(self):
        if self.mailAgent:
            self.qrcode.setVal(None)

        try:
            os.remove(self.qrcodePath)
        except OSError:
            pass

class LockedValue(object):
    def __init__(self, initialVal=None):
        self.val = initialVal
        self.lock = threading.Lock()

    def setVal(self, val):
        with self.lock:
            self.val = val

    def getVal(self):
        with self.lock:
            val = self.val
        return val


if __name__ == '__main__':
    from qconf import QConf

    # 需要先在 ~/.qqbot-tmp/v2.x.conf 文件中设置好邮箱帐号和授权码
    conf = QConf()
    conf.Display()

    qrm = QrcodeManager(conf)
    with open('tmp.png', 'rb') as f:
        qrcode = f.read()
    qrm.Show(qrcode)
    time.sleep(5)
    qrm.Show(qrcode)
    qrm.Destroy()
