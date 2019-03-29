# -*- coding: utf-8 -*-
from qqbot.utf8logger import DEBUG
from common import logger

def __remove_at(msg):
	msg=msg.strip()
	end=msg.find(' ')
	return msg[end:].strip()

# 当收到 QQ 消息时被调用
# bot     : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
# contact : QContact 对象，消息的发送者
# member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
# content : str 对象，消息内容
def onQQMessage(bot, contact, member, content):
	# 记录这个群的消息到日志文件
	logger.history("qq", contact.name, member.name, content)

	#当本 QQ 发消息时， QQBot 也会收到一条同样的消息， bot 对象提供一个 isMe 方法来判断是否是自己发的消息
	if bot.isMe(contact, member):
		DEBUG('是我自己发的消息')
		return #自己发的没必要记录日志，但是需要保存到聊天历史当中

	DEBUG('收到消息[message]：%s', content)
	DEBUG('发消息者[contact]：%s', contact)
	DEBUG('发送成员[member ]：%s', member)

	#被群内其他成员 @ 的通知
	if '@ME' in content:
		logger.debug("是发给机器人的消息，也就是别人@机器人了")
		#bot.SendTo(contact, member.name + '，艾特我干嘛呢？')
	else:
		#logger.debug("@ME不在消息中，此消息不是@机器人的，忽略掉")
		return

	#消息都是 "@xxx yyyyyy"，要把@xxx去掉，否则，无法做意图识别
	content = __remove_at(content)
	logger.debug('去除@后的消息：[message]：%s', content)
	for group in bot.groups:

		logger.debug("检查bot上注册的群/讨论组：group[%s],contact.name[%s]",group,contact.name)

		if contact.name == group:
			logger.debug('是这个群组[%s]的消息，我立即消息路由',group)

			# 得到我们的业务处理组件 | route(self, client, user, group, msg):
			biz_comp, context = bot.bizManager.route("qq", member.name, group, content)
			if biz_comp is None:
				logger.error("无法找到对应的业务处理器！[QQ],user[%s],group[%s]",member.name,group)
				return "不理解您的回复，请再对我说点啥"

			logger.debug("成功加载业务处理器[%r]",biz_comp)

			# 调用业务组件的接口方法来处理消息
			returnMsg = biz_comp.bot2system(bot.qbot,"qq",context,member.name, group, content)


if __name__ == "__main__":

	logger.init()
	logger.debug( __remove_at("@刘创 你好呀！"))

	print __remove_at("@刘创你好呀！")
	print __remove_at("@刘创  你好呀！")
	print __remove_at("  @刘创 你好呀！  ")
	print __remove_at("你好呀！ @刘创 ")
	print __remove_at("你好呀@刘创  ")
	print __remove_at("你好呀刘创")