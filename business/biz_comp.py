#-*- coding:utf-8 -*-

class BizComponent:

    def __init__(self,botManager):
        self.botManager = botManager

    # 出来来自公司内部系统的消息，发往机器人
    # func：子功能，某个子系统可能包含多个子功能，strå类型
    # data：相应的数据，dict类型的
    def system2bot(self,data,func):
        raise NotImplemented()

    # 如果冷不丁地聊天机器人收到一个周恒发的同意，我需要知道针对那件事，这个需要一个路由
    # 我应该有多个业务处理器，先判断这句话对应的意图是啥，我应该检索出，我和周恒的对话，
    # 我和周恒的对话，应该是在一个全局的列表中存着，
    # 结构是： 啥机器人(qq | wechat) - -跟谁(这个靠名字) - -对话列表(存10句就够了)
    # 然后，收到一句话，我就去计算出我和周恒在这个机器人的对话，判断，业务类型
    def bot2system(self,bot,client,context,user,group,msg):
        raise NotImplemented()

