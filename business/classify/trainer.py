#-*- coding:utf-8 -*-
from data_process import DataProcess
from dbscan_analysis import DBSCAN_Analysis
import pandas as pd
import time,logging as logger
import jieba
import sys
sys.path.append("..")
from common.common import duration

class ClassTrainer():

	def __init__(self,model_dir=".cache/model"):

		self.data_processor = DataProcess()
		self.dbscan = DBSCAN_Analysis()
		self.model_dir = model_dir

	def train(self,db_ip,db_name,user,passwd):

		t = time.time()

		#数据加载
		conn = self.data_processor.connect_db(db_ip,db_name,user,passwd)
		df = self.data_processor.load_data(conn)
		t = duration(t,"从数据库中加载数据")

		#数据清洗,主要是把邮件内容做清洗，去除html标签和停用词，然后分词
		df = self.data_processor.clean_process(df)

		#调用dbscan，对每个系统的每个大类进行分别聚类，然后将结果保存到db_monitor_classes中
		self.dbscan.process(conn,df)

	def get_classes(conn):
		df = pd.read_sql("cluster_dbscan", conn)

if __name__=="__main__":
	# - 训练结束后，会得到以下内容：
	# - 每个邮件报警的类别
	# - 每个大类下的类别表
	# - 每个大类下的tfidf模型和词表
	logger.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logger.DEBUG)
	logger.getLogger("gensim").setLevel(logger.WARNING)
	logger.getLogger("jieba").setLevel(logger.WARNING)

	jieba.initialize()
	jieba.load_userdict("../corpus/addwords.txt")
	jieba.analyse.set_stop_words('../corpus/stopwords.txt')

	db_ip="127.0.0.1"
	db_name="chatbot"
	db_user = "username"
	db_passwd = "password"

	trainer = ClassTrainer("../.cache/model")
	trainer.train(db_ip, db_name,db_user,db_passwd)
