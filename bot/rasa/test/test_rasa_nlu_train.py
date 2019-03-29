# -*- coding: UTF-8 -*-
import sys,io,os
from mitie import *
from collections import defaultdict

reload(sys)
sys.setdefaultencoding('utf-8')


#此代码参考：https://nlu.rasa.com/python.html

#这个代码是为了测试，直接通过python api去获取rasa nlu的意图和实体识别接口

sys.path.append('../MITIE/mitielib')

from rasa_nlu.model import Metadata, Interpreter


# where `model_directory points to the folder the model is persisted in
interpreter = Interpreter.load("../model/default/latest/")

from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config

training_data = load_data('../train_nlu.md')
trainer = Trainer(config.load(""))
trainer.train(training_data)
model_directory = trainer.persist('./projects/default/')  # Returns the directory the model is stored in


