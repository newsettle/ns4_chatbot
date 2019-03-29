# -*- coding: UTF-8 -*-
from rasa_core.agent import Agent
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from rasa_core.channels.console import ConsoleInputChannel
sys.path.append('../MITIE/mitielib')
from rasa_core.domain import TemplateDomain
import logging,os
import numpy as np
from rasa_core.policies import Policy
from rasa_core.actions.action import ACTION_LISTEN_NAME
from rasa_core import utils
from rasa_core.interpreter import NaturalLanguageInterpreter
from rasa_nlu.model import Metadata, Interpreter
from rasa_core.tracker_store import InMemoryTrackerStore
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_nlu import config
from rasa_core.interpreter import RasaNLUInterpreter

#训练的NLU模型，所以，不需要再提供nlu_config.yml了，在这里
nlu_model_path = "../model/latest/"
logger = logging.getLogger(__name__)
domain_conf_path = "../domain.yml"
agent_model_path = "../model/agent/"

def train(max_training_samples=3,serve_forever=True):
    training_data = 'stories.md'

    from rasa_core.interpreter import RasaNLUInterpreter
    interpreter = RasaNLUInterpreter("../model/latest/")

    default_domain = TemplateDomain.load("domain.yml")

    if os.path.exists(agent_model_path):
        logger.info("加载已有的模型")
        # agent = Agent.load(
        #     agent_model_path)

        # interpreter=interpreter,
        # tracker_store=InMemoryTrackerStore(default_domain)

        ######### 各种配置 #########
        ## 意图理解模型 路径
        nlu_model_path = '../model/latest'
        ## 对话模型 路径
        model_directory = "../model/agent"

        # 启动agent
        agent = Agent.load(model_directory, nlu_model_path)

    else:
        logger.info("从头创建模型")
        agent = Agent(domain_conf_path,
            interpreter=interpreter,
            policies=[MemoizationPolicy(), KerasPolicy()],
            tracker_store=InMemoryTrackerStore(default_domain))
    #for debug: print(interpreter.parse(u"你好"))

    logger.info("开始在线训练...")

    agent.train_online(training_data,
                       input_channel=ConsoleInputChannel(),
                       epochs=1)#,                       max_training_samples=max_training_samples

    return agent

if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    agent = train()
    agent.persist(agent_model_path)