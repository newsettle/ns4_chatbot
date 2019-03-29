# -*- coding:utf-8 -*-
import ConfigParser


cf = ConfigParser.ConfigParser()
cf.read("database/config.conf")

#数据库配置
db_host = cf.get("db", "host")
db_database = cf.get("db", "database")
db_port = cf.getint("db", "port")
db_user = cf.get("db", "user")
db_pass = cf.get("db", "pass")

#db_app配置
db_app_host = cf.get("db_app","host")
db_app_port = cf.get("db_app","port")