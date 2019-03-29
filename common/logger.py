# -*- coding:utf-8 -*-

import logging.config,sys,json,traceback
import common,logging

reload(sys)
sys.setdefaultencoding('utf-8')
history_logger_names = []

def init_4_debug():
	#配置日志级别
	logging.basicConfig(level=logging.DEBUG,
					   format='%(asctime)s %(filename)s[%(lineno)d] %(levelname)s %(message)s',
					   datefmt='%H:%M:%S')

def init(logger_file="log.conf"):

	#配置日志级别
	logging.config.fileConfig(logger_file)
	logging.getLogger("gensim").setLevel(logging.WARNING)
	logging.getLogger("jieba").setLevel(logging.WARNING)
	logging.getLogger("Utf8Logger").setLevel(logging.WARNING)

def convert_str(msg):

	if type(msg) is list: return ",".join(str(v) for v in msg).decode('unicode-escape')
	if type(msg) is dict: return json.dumps(msg, encoding="UTF-8", ensure_ascii=False)
	if type(msg) is tuple:return str(msg).replace('u\'', '\'').decode('unicode-escape')

	# print "============%s" % msg
	return str(msg)

def info(msg, *args, **kwargs):

	_logger = logging.getLogger("log")
	try:
		msg = convert_str(msg)
		_logger.info(msg,*args,**kwargs)
	except Exception as e:
		print(str(e))
		traceback.print_exc()
		print (msg)
		print (args)
		print (kwargs)

def warn(msg, *args, **kwargs):
	_logger = logging.getLogger("log")
	try:
		msg = convert_str(msg)
		_logger.warn(msg,*args,**kwargs)
	except Exception as e:
		print (str(e))
		traceback.print_exc()
		print (msg)
		print (args)
		print (kwargs)

def exception(e,msg, *args, **kwargs):
	error(msg+",Exception:"+str(e), *args, **kwargs)
	logger = logging.getLogger("log")
	traceback.print_exc()
	logger.error("====================================异常堆栈为====================================", exc_info=True)
	info("==================================================================================")

def error(msg, *args, **kwargs):
	logger = logging.getLogger("log")

	try:
		msg = convert_str(msg)
		logger.error(msg,*args,**kwargs)
		common.send_email(None,"聊天机器人故障错误",msg % args)
		common.send_sms(msg % args)
	except Exception as e:
		print (str(e))
		traceback.print_exc()
		print (msg)
		print (args)
		print (kwargs)

def debug(msg, *args,**kwargs):

	_logger = logging.getLogger("log")
	try:
		msg = convert_str(msg)
		# print msg
		# print args
		# print kwargs

		_logger.debug(msg ,*args,**kwargs)
	except Exception as e:
		print (str(e))
		traceback.print_exc()
		print (msg)
		print (args)
		print (kwargs)

#记录
def history(type,group,user,message):
	if type !="qq" and type!= "wechat":
		raise ValueError("the type must be qq or wechat")

	if group is None or group == "":
		raise ValueError("the group name must not be null")

	history_file_name = type+"."+group+".his"#.encode("gb2312"),windows下调试用

	history_logger = _get_logger(history_file_name)

	history_logger.info("{}>{}:{}".format(group,user,message))

def _get_logger(logger_name):
	logger = logging.getLogger(logger_name)
	if logger_name in history_logger_names: return logger

	formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	fileHandler = logging.FileHandler("log/"+logger_name, mode='a')
	# fileHandler = logging.FileHandler("log/aa.txt", mode='a')
	fileHandler.setFormatter(formatter)

	logger.setLevel(logging.INFO)
	logger.addHandler(fileHandler)

	history_logger_names.append(logger_name)

	return logger

if __name__=="__main__":
	convert_str(['我','我'])
	convert_str(['我', '我'])
	init_4_debug()
	error("测试参数传递%s,%s,%r","参数1","参数2",{})