# -*- coding: UTF-8 -*-
from rasa_core.agent import Agent
from rasa_core.domain import TemplateDomain
import logging,os
from rasa_core.tracker_store import InMemoryTrackerStore
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#from rasa_core.channels.console import ConsoleInputChannel
sys.path.append('../MITIE/mitielib')

#训练的NLU模型，所以，不需要再提供nlu_config.yml了，在这里
nlu_model_path = 'model/default/latest'
logger = logging.getLogger(__name__)
domain_conf_path = "./domain.yml"
agent_model_path = "model/agent/"

def train(max_training_samples=3,serve_forever=True):
    story = 'stories.md'

    from rasa_core.interpreter import RasaNLUInterpreter
    interpreter = RasaNLUInterpreter(nlu_model_path)

    #domain配置文件
    
    default_domain = TemplateDomain.load("./domain.yml")


    if  os.path.exists(agent_model_path):
        agent = Agent.load(agent_model_path, 
            interpreter=interpreter,
            tracker_store=InMemoryTrackerStore(default_domain))
    else:
        agent = Agent(domain_conf_path,
                  policies=[MemoizationPolicy(), KerasPolicy()],
                  interpreter=interpreter,
                  tracker_store=InMemoryTrackerStore(default_domain))
    #for debug: print(interpreter.parse(u"你好"))

    logger.info("开始训练...")

    training_data = agent.load_data(story)

    agent.train(training_data,
                epochs=50)
    return agent

if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    agent = train()
    agent.persist(agent_model_path)