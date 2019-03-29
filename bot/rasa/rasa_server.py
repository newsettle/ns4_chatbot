# -*- coding: utf-8 -*-
from rasa_core.agent import Agent
import os
from wxpy import *
from common.common import BaseService
from common import config,logger

parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append('../MITIE/mitielib')

class Rasa_Server(BaseService):

    def startup(self):
        super(Rasa_Server,self).startup()
        #训练的NLU模型，所以，不需要再提供nlu_config.yml了，在这里
        logger.info("Rasa开始启动了...")

        ######### 各种配置 #########
        ## 意图理解模型 路径
        nlu_model_path = config.rasa_nlu_model#'rasa/model/default/latest'
        ## 对话模型 路径
        model_directory = config.rasa_dialog_model#"rasa/model/dialogue"

        # 启动agent
        self.agent = Agent.load(model_directory, nlu_model_path)

        logger.info("Rasa已经加载了所有的模型...")

    '''
        和谁去说话，
        sender：
        message:消息
    '''
    def talk(self,message,sender):
        logger.debug("Rasa收到来自[%s]的消息：%s",sender,message)
        answers = self.agent.handle_message(message,sender_id= sender)#保存sender_id很重要，用于rasa响应多个人的对话
        text_answers = []
        for answer in answers:
            # {"recipient_id": recipient_id, "text": message}
            logger.debug("RASA产生回答：")
            logger.debug("用户[%s]\t", answer['recipient_id'])
            logger.debug("回答:\t%s", answer['text'])
            text_answers.append(answer['text'])
        return text_answers
