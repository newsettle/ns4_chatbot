#-*- coding:utf-8 -*-
import sys,pymysql,time,datetime
import logger,config,neo4j_helper
import web_client
import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB


import json
from config import Config
if sys.getdefaultencoding() != 'utf-8':
	sys.setdefaultencoding('utf-8')
	reload(sys)

__connection_pool = None

def init(config):
	try:
		global __connection_pool
		__connection_pool = PooledDB(
				creator=MySQLdb,
				mincached=1,
				maxcached=20,
				host=config.db_host,
				port=config.db_port,
				user=config.db_user,
				passwd=config.db_pass,
				db=config.db_database,
				use_unicode=False,
				charset="utf8",
				cursorclass=DictCursor)

		return True
	except Exception as e:
		logger.exception(e,"Mysql数据库初始化失败:host=%s,user=%s,pass=%s,db=%s",config.db_host,config.db_user,config.db_pass,config.db_database)
		return False

def find_group_by_qqtype():
	#查询qq所属组
	sql = "select DISTINCT(qq_group) as qq_group from biz_system_tree"
	logger.debug("sql:%s", sql)
	conn = __connection_pool.connection()
	cursor = conn.cursor()
	cursor.execute(sql)
	dutys = cursor.fetchall()
	qq_groups  = []
	for d in dutys:
		qq_groups.append(d['qq_group'].decode('UTF-8'))

	cursor.close()
	conn.close()
	return qq_groups

def find_group_by_wechattype():
	#查询wechat所属组
	sql = "select DISTINCT(wechat_group) as wechat_group from biz_system_tree"
	logger.debug("sql:%s", sql)
	# conn = pymysql.connect(host="127.0.0.1",user="username",passwd="password",
	# 					  				   db="chatbot",
	# 					  				   charset="utf8")
	conn = __connection_pool.connection()
	cursor = conn.cursor()
	cursor.execute(sql)
	dutys = cursor.fetchall()

	wechat_groups  = []
	for d in dutys:
		wechat_groups.append(d['wechat_group'].decode('UTF-8'))

	cursor.close()
	conn.close()
	return wechat_groups

if __name__ == "__main__":
	logger.init_4_debug()