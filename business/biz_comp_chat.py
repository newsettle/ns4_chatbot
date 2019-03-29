# -*- coding:utf-8 -*-
from biz_comp import *
from common import logger
import tempfile,random,string
import base64
from common.common import HtmlContent

# 默认的业务处理类
class BizCompChat(BizComponent):
	name = "chat"

	def __init__(self, botManager):
		self.botManager = botManager
		self.biz_type = BizCompChat.name

	def bot2system(self,bot,client,context,user,group,msg):
		bot.send(group,user,"收到您的消息，测试成功",None)


	def base64_2_file(self,file_name,base64_data):
		base64.decode()
		decoded = base64.b64decode(base64_data)
		output_file = open(file_name, 'w')
		output_file.write(decoded)
		output_file.close()

	def system2bot(self, data, func=None):
		logger.debug("聊天组件接收到参数：%r", data)
		qqGroupId = data.get('qqGroupId', None)
		wxGroupName = data.get('wxGroupName', None)
		type = data['type']
		user = data.get("user", None)
		msg = data.get("msg", None)
		html = data.get('html', None)
		image_base64 = data.get('imgData', None)
		msgId = data.get("msgId",None)
		remark = data.get("remark",None)

		logger.debug("聊天组件收到消息：qqGroupId=%r,wxGroupName=%r, msgId=%r,remark=%r,type=%r,user=%r,msg=%r,html=%r", qqGroupId, wxGroupName,msgId,remark,
					 type, user, msg, html)
		groups = {'wechat_group': None, 'qq_group': None, 'email': None}
		if (type == "wechat"):
			groups['wechat_group'] = wxGroupName
		if (type == "qq"):
			groups['qq_group'] = qqGroupId
		if (type == "wxqq"):
			groups['wechat_group'] = wxGroupName
			groups['qq_group'] = qqGroupId

		if image_base64 is None or image_base64.strip() == "":
			logger.debug("消息中没有图片")
		else:
				dir = tempfile.gettempdir()
				image_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
				image_name +=".jpg"
				logger.debug("图片名没有，自动生成一个：%s",image_name)
				temp_file = dir + "/" + image_name
				self.base64_2_file(temp_file,image_base64)
				logger.debug("产生临时文件:%s",temp_file)

				self.botManager.send_image(groups, user, temp_file)
		if not html:
			html = ""
		html = HtmlContent(html, "html")
		self.botManager.send(groups, user, msg, html , self.biz_type)
		return "OK"
