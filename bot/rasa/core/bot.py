# -*- coding: utf-8 -*-
from rasa_core.agent import Agent
from wexin_channel import WeixinInputChannel
import logging as logger
import os
from wxpy import *

logger.basicConfig(
    level=logger.DEBUG,
    format="[%(levelname)s] %(message)s"
)

parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append('../MITIE/mitielib')

def main():
    bot = Bot(cache_path=None,console_qr=True)

    #训练的NLU模型，所以，不需要再提供nlu_config.yml了，在这里
    logger.info("Rasa process starting")
    nlu_model_path = '../model/default/latest'
    model_directory = "../model/dialogue"
    agent = Agent.load(model_directory, nlu_model_path)
    logger.info("Finished loading agent, starting input channel & server.")

    weixin_input_channel = WeixinInputChannel(bot)
    agent.handle_channel(weixin_input_channel)

    # 进入Python命令行，让程序保持运行
    embed(shell='python')

if __name__ == '__main__':
    main()
