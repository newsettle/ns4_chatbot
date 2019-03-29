# -*- coding:utf-8 -*-
import time
import logger
class Retry:

	def __init__(self):
		self.retry_next_time = time.time()
		self.retry_counter = 0

	# 为了防止太频繁，设计这么一个机制：试10分钟，每分钟1次，如果不行，就休息10分钟，再试。这一样，1个小时30次，如果，否则，我们的邮箱就该爆炸了
	def is_need_retry(self,config):
		if time.time() < self.retry_next_time:
			logger.debug("QR二维码过期了，重新生成，但是未到下次处理时间，忽略掉")
			return False

		self.retry_counter += 1
		self.retry_next_time = time.time() + config.retry_interval

		if self.retry_counter > config.retry_max_num:
			logger.error("QR二维码过期了，重新生成，但是已经尝试了10次，10分钟后再次尝试")
			self.retry_counter = 0
			self.retry_next_time = time.time() + config.retry_sleep
			return False

		return True
