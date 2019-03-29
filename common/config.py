# -*- coding:utf-8 -*-
import ConfigParser

class Config:

	def __init__(self,conf_file="bot.conf"):

		cf = ConfigParser.ConfigParser()
		cf.read(conf_file)

		#基础配置
		self.bot_support = cf.get("common", "bot")
		self.bot_chat_base_interval = cf.getint("common", "bot_chat_base_inteval")
		self.bot_chat_interval = cf.getint("common", "bot_chat_interval")

		#控制登录的时候二维码的登录间隔的参数
		# 每次尝试10次
		self.retry_max_num = cf.getint("common","retry_max_num")
		# 每次等1分钟在再尝试，60秒
		self.retry_interval = cf.getint("common","retry_interval")
		# 尝试了10次后，还不行，就彻底休息10分钟,600秒
		self.retry_sleep = cf.getint("common","retry_sleep")

		self.debug = cf.getboolean("common", "debug")
		self.debug_qq = cf.get("common", "debug_qq")

		#酷Q配置
		self.coolq_url = cf.get("coolq","url")
		self.coolq_qq = cf.get("coolq","qq")
		self.coolq_cache_path = cf.get("coolq","cache_path")

		#基础配置
		self.http_port = cf.getint("http", "port")


		#redis配置
		self.redis_ip = cf.get("redis", "ip")
		self.redis_port = cf.getint("redis", "port")
		self.redis_password = cf.get("redis","password")

		#微信bot配置
		self.wxbot_console_qr = cf.getboolean("wxbot", "console_qr")
		self.wxbot_cache_path = cf.get("wxbot", "cache_path")
		self.wxbot_cache_file = cf.get("wxbot", "cache_file")
		self.wxbot_qr_path = cf.get("wxbot", "qr_path")

		#管理员配置
		self.admin_email = cf.get("admin", "email")
		self.admin_mobile = cf.get("admin", "mobile")

		#邮件配置
		self.email_user = cf.get("email", "user")
		self.email_passwd = cf.get("email", "passwd")
		self.email_server = cf.get("email", "server")
		self.email_port = cf.getint("email", "port")
		self.email_SSL = cf.getboolean("email", "SSL")

		#短信配置
		self.sms_server = cf.get("sms","server")
		self.sms_merchId = cf.get("sms","merchId")
		self.sms_orderId = cf.get("sms","orderId")
		self.sms_smsTypeNo = cf.get("sms","smsTypeNo")

		#数据库配置
		self.db_host = cf.get("db", "host")
		self.db_database = cf.get("db", "database")
		self.db_port = cf.getint("db", "port")
		self.db_user = cf.get("db", "user")
		self.db_pass = cf.get("db", "pass")

		#vocie2txt语音识别配置
		self.voice2txt_engine = cf.get("voice2txt", "engine")
		self.voice2txt_url = cf.get("voice2txt", "url")
		self.voice2txt_app_id = cf.get("voice2txt", "app_id")
		self.voice2txt_secret_key = cf.get("voice2txt", "secret_key")
		self.voice2txt_api_key = cf.get("voice2txt", "api_key")


		#RASA配置
		self.rasa_nlu_model = cf.get("rasa","nlu_model")
		self.rasa_dialog_model = cf.get("rasa","dialog_model")

if __name__ == "__main__":
	config = Config("../bot.conf")

