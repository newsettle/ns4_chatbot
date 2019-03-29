#-*- coding:utf-8 -*-
import time
from bs4 import BeautifulSoup
from scipy.sparse import csc_matrix
import pandas as pd
import jieba,re,sys
from gensim import corpora, models
import gensim
import logging as logger
from time import time
from sqlalchemy import create_engine
import sys,numpy as np
from common.common import duration
import progressbar

class DataProcess(object):

	def __init__(self):
		reload(sys)
		if sys.getdefaultencoding() != 'utf-8':
			sys.setdefaultencoding('utf-8')
		logger.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logger.DEBUG)

		self.stopwords = self.load_stopword()

	def process_line(self,html):
		content_with_alphabet_num = self.clean_html(html)
		pure_content = self.filter_only_Chinese(content_with_alphabet_num)
		cut_text = self.cut_words(pure_content, self.stopwords)
		return cut_text

	def clean_process(self,df):
		t = time()

		pb = progressbar.ProgressBar(len(df))
		pb.start()

		MAX_LENGTH = 10000
		for index, row in df.iterrows():

			cut_text = self.process_line(row['email_html'])

			try:
				pb.update(index)
			except ValueError:
				pass

			if len(cut_text) > MAX_LENGTH: cut_text = cut_text[0:MAX_LENGTH]
			df.loc[index,'html_cut'] = cut_text

			#每列遍历，都看看长度是否大于某个值，截断

			for k, v in row.iteritems():
				if v is None : continue
				if len(v)>MAX_LENGTH:
					logger.warn("列[%r]的值长度[%d]大于[%d],截断",k,len(v),MAX_LENGTH)
					# row[k] = v[0:MAX_LENGTH]
					df.loc[index, k] = v[0:MAX_LENGTH]

			# 进度条
			try:
				pb.update(index)
			except ValueError:
				pass
		pb.finish()
		duration(t, "清洗数据：去除HTML tag，去除无用字符")

		return df


	def caculate_tfidf(self,df):
		logger.debug("一共%d行文本数据",len(df))

		all_rows = []
		#每行，再把空格链接的大字符串变成数组
		for one in df['html_cut']:
			#print(one)
			#print ("------------------")
			cut_content_list = one.split(" ")
			all_rows.append(cut_content_list)

		#得到词典	，去重的
		dictionary = corpora.Dictionary(all_rows)
		logger.debug("词袋一共%d个词",len(dictionary.keys()))

		#把他所有的句子变成one-hot的词袋向量,corpus里面是一个向量数组
		#corpus = [dictionary.doc2bow(one_row) for one_row in all_rows]
		corpus = []
		for index, one_row in df.iterrows():
			html_cut = one_row['html_cut'].split(" ")
			bow = dictionary.doc2bow(html_cut)#频次数组
			one_row['doc2bow'] = bow #每一行增加一个字段bow，存在这个语料的向量
			one_row['hash'] = hash(str(bow)) #每一行增加一个字段hash,hash这个语料

			corpus.append(bow)

		logger.debug("语料行数：%d",len(corpus))

		#从one-hot向量 ---> 生成tf-idf模型
		tfidf_model = models.TfidfModel(corpus,dictionary)
		logger.debug("由语料生成TFIDF模型")
		print (tfidf_model)

		#对每行语料进行tf-idf向量化
		corpus_tfidf = tfidf_model[corpus]
		scipy_csc_matrix =gensim.matutils.corpus2csc(corpus_tfidf,num_terms=len(dictionary.keys()))
		data = csc_matrix(scipy_csc_matrix).T.toarray()
		logger.debug("得到每行语料的tfidf向量，是一个矩阵,Shape:%r",data.shape)

		return data,dictionary,tfidf_model

	#把一行文档，转成一个tfidf的向量，维度是词表，值是tfidf值
	#入参是一个字符串list["我 唉 北京","天安门 上 太阳","升 起 国旗",...]
	#出参是还你一个tfidf数组
	def get_tfidf_vector(self,doc_list,dictionary,tfidf_model):

		corpus = [ doc.split(" ") for doc in doc_list] #	["xx xxx xx"=>['xx','xxx','xx'],...
		# logger.debug("得到的语料为：%r",corpus)
		doc_bows = []
		docs_tfidf = []
		for c in corpus:
			try:
				doc_bow = dictionary.doc2bow(c) # ['xx','xxx','xx']=>[12,24,12],词表中的id
				# logger.debug(doc_bow)
				doc_bows.append(doc_bow)

				doc_tfidf = tfidf_model[doc_bow]  # 从模型中得到对应的tfidf
				docs_tfidf.append(doc_tfidf)
			except TypeError as e:
				logger.error("处理语料成为one hot失败:%r", c)

		logger.debug("正在转化%d个分词行成为OneHot tfidf向量",len(doc_bows))

		#从doc_tfidf变成一个稀硫矩阵，doc_tfidf是gensim的一个类，而得到的也是一个压缩矩阵
		_csc_matrix = gensim.matutils.corpus2csc(docs_tfidf,num_terms=len(dictionary.keys()))
		data = csc_matrix(_csc_matrix).T.toarray()#还原成标准矩阵，需要转置一下
		logger.debug("得到的tfidf向量维度为：%r",data.shape)
		return data


	def filter_only_Chinese(self,content):
		r = '[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
		return re.sub(r, '', content)

	#这个是业务的一个大类，
	#我是是按照： 系统->大类->分类来分的
	#这个类，亚可正在整理，会定义出来，目前先按照rule_type_code来聚类
	def get_big_class(self,con):

		df = pd.DataFrame(np.array(
				[['NEW_SETTLEMENT', 'RESPCODE'],
				 ['NEW_SETTLEMENT', 'BATCH_EXCEPTION_TRADE'],
				 ['NEW_SETTLEMENT', 'TRANSFER_PROCESSING_TIMEOUT'],
				 ['NEW_SETTLEMENT', 'NETWORK_EXCEPTION'],
				 ['NEW_SETTLEMENT', 'STATISTICALTRADERATE'],
				 ['NEW_SETTLEMENT', 'TRADE_OVERTIME'],
				 ['NEW_SETTLEMENT', 'MID_STATE'],
				 ['CASH_COMPASS', 'TRADE_USETIME'],
				 ['CASH_COMPASS', 'RESPCODE'],
				 ['CASH_COMPASS', 'TRADE_OVERTIME'],
				 ['CASH_COMPASS', 'TIMER_START'],
				 ['CASH_COMPASS', 'TIMER_OVERTIME'],
				 ['CASH_COMPASS', 'BANK_TRADE_USETIME'],
				 ['CASH_COMPASS', 'ERR_CODE'],
				 ['CASH_COMPASS', 'DATA_OVER_STOCK'],
				 ['CASH_COMPASS', 'NETWORK_EXCEPTION']]),
				# index=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
				columns=['business_system_code','rule_type_code'])
		# df = pd.DataFrame(np.random.randint(low=0, high=10, size=(5, 5)),
		# columns = ['a', 'b', 'c', 'd', 'e'])
		return df

		# sql = "SELECT distinct alarm.business_system_code,alarm.rule_type_code \
		# 	  FROM work_order, alarm \
		# 	  WHERE work_order.alarm_id = alarm.alarm_id ";
		# df = pd.read_sql(sql,con=con)
		# return df#['business_system_code','rule_type_code']

	def test_html_parse(self):
		stop_words = self.load_stopword()
		with open("1.html","r") as f:
			html  = f.read()
			pure_content = self.process_line(html,stop_words)
			print(pure_content)


	def connect_db(self,db_ip,db_name,user,passwd):
		conn = create_engine("mysql+mysqldb://{}:{}@{}:3306/{}?charset=utf8".format(user,passwd,db_ip,db_name)
							 , pool_recycle=3600)

		return conn

	def load_data(self,conn):
		#NEW_SETTLEMENT

		#故障码类型的，准确出警的
		sql = " \
		SELECT 	\
			work_order_id,alarm.alarm_id,\
			work_order_title,email_title, \
			alarm.business_system_code,important_level_code,\
			dispose_result_code,dispose_result_name, \
			work_order_type_code,alarm.rule_type_code, \
			alarm_content,email_html,alarm_level,alarm_title \
		FROM work_order, alarm \
		WHERE work_order.alarm_id = alarm.alarm_id  \
		LIMIT 10000 "

		df = pd.read_sql(sql,con=conn)
		return df

	def clean_html(self,html):
		bs = BeautifulSoup(html,"lxml")
		return bs.getText().strip()

	def load_stopword(self):
		f_stop = open('corpus/stopwords.txt')
		sw = [line.strip() for line in f_stop]
		f_stop.close()
		return sw

	def cut_words(self,line,stop_words):
		seg_list = jieba.cut(line,cut_all=False)
		return " ".join([word for word in seg_list if word not in stop_words])

if __name__ == '__main__':
	dp = DataProcess()
# 	con = dp.connect_db(db_ip,db_name,user,passwd)
	print(dp.get_big_class(None))
	print("完事了！")