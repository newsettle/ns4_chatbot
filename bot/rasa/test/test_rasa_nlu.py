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

def print_beatuiful(obj):
	if isinstance(obj,dict):
		for k,v  in obj.items():
			print "\t",
			print str(k).decode("unicode-escape"), 
			print " = " , 
			print str(v).decode("unicode-escape")

# where `model_directory points to the folder the model is persisted in
interpreter = Interpreter.load("../model/default/latest/")

sentence = u"我 的 手机号 是 xxxxxxx"
result = interpreter.parse(sentence)

print sentence
print "预测结果为："

import json
print type(result)
print json.dumps(result, indent=4, sort_keys=True).decode("unicode-escape")
# print print_beatuiful(result)


