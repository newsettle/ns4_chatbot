# -*- coding: utf-8 -*-
from rasa_core.agent import Agent
from wexin_channel import WeixinInputChannel
import logging as logger
import os
import cmd
from wxpy import *

logger.basicConfig(
    level=logger.INFO,
    format="[%(levelname)s] %(message)s"
)

parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append('../MITIE/mitielib')

class RasaCmd(cmd.Cmd):
    intro = 'RASA聊天机器人测试：\n'
    prompt = '>'

    def __init__(self, agent):
        self.agent  = agent
        cmd.Cmd.__init__(self)

    def default(self,line):
        line = line.decode("utf-8")

        answers = self.agent.handle_message(line)

        for answer in answers:
            # {"recipient_id": recipient_id, "text": message}
            print "用户[" , answer['recipient_id'] , "]\t" ,
            print answer['text']


    def do_exit(self,arg):
        self.do_bye(arg)

    def do_bye(self, arg):
        print '拜拜啦'
        exit(0)


def main():

    #训练的NLU模型，所以，不需要再提供nlu_config.yml了，在这里
    logger.info("Rasa process starting")
    nlu_model_path = '../model/default/latest'
    model_directory = "../model/dialogue"
    agent = Agent.load(model_directory, nlu_model_path)
    logger.info("Finished loading agent, starting input channel & server.")

    cmd = RasaCmd(agent)
    cmd.cmdloop()

if __name__ == '__main__':
    main()
