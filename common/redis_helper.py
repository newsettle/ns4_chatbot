# -*- coding:utf-8 -*-
import redis
from common import logger

class RedisConnect(object):
    _instance = None
    pool = None

    def __init__(self,url=None,port=None,password=None):
        self.url = url
        self.port = port
        self.password = password

    def init(self):
        logger.info("Redis连接池创建：ip=%s,port=%d,password=%s",self.url, self.port,self.password)
        self.pool = redis.ConnectionPool(host=self.url, port=self.port,password=self.password)

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(RedisConnect, cls).__new__(cls, *args, **kw)
            logger.debug("创建RedisConnect单例")
        return cls._instance

    def createRedis(self):
        r = redis.Redis(connection_pool=self.pool)
        rexcute = r.pipeline(transaction=True)
        logger.debug("获得redis execute")
        return r, rexcute

if __name__=="__main__":
    rc1 = RedisConnect("127.0.0.1",6337)
    rc2 = RedisConnect("127.0.0.1",6337)
    print("----")
    print(rc1)
    print(rc2)
    print("----")
    print(rc1.pool)
    print(rc2.pool)
    rc3 = RedisConnect("127.0.0.1", 6337)
    rc3.connect_redis()
    print("----")
    print(rc1.pool)
    print(rc2.pool)
    print(rc3.pool)
