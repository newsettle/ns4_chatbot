# -*- coding:utf-8 -*-
import logging.config,sys
import logging,json

logging.basicConfig()

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

def info(msg, *args, **kwargs):

	if type(msg) is dict: msg =  json.dumps(msg, encoding="UTF-8", ensure_ascii=False)
	if type(msg) is tuple:    msg = str(msg).replace('u\'', '\'').decode('unicode-escape')

	logger = logging.getLogger("log")
	logger.info(msg,*args,**kwargs)

def warn(msg, *args, **kwargs):
	logger = logging.getLogger("log")
	logger.warn(msg,*args,**kwargs)


def error(msg, *args, **kwargs):
	logger = logging.getLogger("log")
	print msg
	print args
	print kwargs
	logger.error(msg,*args,**kwargs)

def debug(msg, *args,**kwargs):

	if type(msg) is dict: 	msg =  json.dumps(msg, encoding="UTF-8", ensure_ascii=False)
	if type(msg) is tuple:	msg = str(msg).replace('u\'','\'').decode('unicode-escape')

	logger = logging.getLogger("log")
	logger.debug(msg,*args,**kwargs)

#记录
def history(type,group,user,message):
	if type !="qq" and type!= "wechat":
		raise ValueError("the type must be qq or wechat")

	if group is None or group == "":
		raise ValueError("the group name must not be null")


	#history_file_name = type + "." + group + ".his"
	history_file_name = type + "." + group.encode("gb2312") + ".his"

	history_logger = _get_logger(history_file_name)

	history_logger.info("{}>{}:{}".format(group,user,message))

def _get_logger(logger_name):
	logger = logging.getLogger(logger_name)
	if logger_name in history_logger_names: return logger
	formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	fileHandler = logging.FileHandler("log/"+logger_name, mode='a')
	fileHandler.setFormatter(formatter)

	logger.setLevel(logging.INFO)
	logger.addHandler(fileHandler)

	history_logger_names.append(logger_name)

	return logger