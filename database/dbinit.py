#-*- coding:utf-8 -*-
import pymysql
import logger

global con
try:
	con = pymysql.connect(host=config.db_host,
					   user=config.db_user,
					   passwd=config.db_pass,
					   db=config.db_database,
					   charset="utf8")
except pymysql.Error as e:
	logger.error('connect mysql {} Got error {!r}, errno is {}'.format(config.db_database,e, e.args[0]))
