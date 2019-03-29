# -*- coding:utf-8 -*-
from biz_comp import BizComponent
from common import neo4j_helper
import common.logger as logger
from common import web_client

#这是一个不太高明的设计，上面的设计意图已经表达清楚了
#就是case2："2. 发现这个人没有任何和某个系统沟通的上下文，那么怎么办呢？"
#所以在，bizManager.route()里面，如果找不到其他的业务组件，就只好调用这个rasa来做回应了
class BizCompRasa(BizComponent):

	def __init__(self,botManager,rasa_server):
		BizComponent.__init__(self,botManager)
		self.rasa_server = rasa_server
		self.biz_type = "classify"

	def bot2system(self,bot,client,context,user,group,message):

		key = "{}-{}-{}".format(client, group, user)

		#TODO: 这里未来需要重构，因为rasa只要返回意图就可以了，然后我们判断这个意图是不是一个业务系统调用
		#TODO：如果不是调用，再去给知识图谱引擎来做知识回答，未来扩展性的考虑

		# 回复消息内容和类型
		# 若消息来自群聊，则此属性为消息的实际发送人(具体的群成员)
		answers = self.rasa_server.talk(message, key)  # 这个人要传给rasa，rasa才可以控制多人对话
		if answers is None or len(answers)==0 :
			logger.debug("rasa不理睬我")
			return "Sorry，不太明白您的意思"
		else:
			logger.debug("rasa给我返回了消息,发送给微信：%r", answers)
			return "\n".join(answers)

	def system2bot(self,data,func):
		raise NotImplementedError()
