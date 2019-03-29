# -*- coding:utf-8 -*-
import jieba
import logging as logger
from bs4 import BeautifulSoup
import pandas as pd
from jieba import analyse
from gensim import corpora
from time import time
from sklearn.cluster import DBSCAN
from common.common import duration
from data_process import DataProcess
import time,sqlalchemy

class DBSCAN_Analysis():


	def __init__(self):
		self.data_processor = DataProcess()
		self.model_dir = ".cache/model"

	#删除数字
	#https://www.cnblogs.com/wushuaishuai/p/7687074.html
	def clean_line(self,line):
		line = line.replace('【', ' ')
		line = line.replace(' ：', ' ')
		line = line.replace('】', ' ')
		line = line.replace('--', ' ')
		line = line.replace('-', ' ')
		line = line.replace(':', ' ')
		line = line.replace('：', ' ')
		line = line.replace('。', ' ')
		line = line.replace('，', ' ')
		line = line.replace(',', ' ')
		line = line.replace('！', ' ')
		line = line.replace('~', ' ')
		return line

	def get_dictionary(df):
		logger.debug("一共%d行文本数据", len(df))

		all_rows = []
		for one in df['html_cut']:
			#不知为何从csv加载的有的html切词是nan，然后识别成float类型了，加上这个做错误处理
			if not isinstance(one, str):
				logger.error("当前行的html_cut数据类型不是Str：%r", one)
				continue
			cut_content_list = one.split(" ")
			all_rows.append(cut_content_list)
		# 得到词典
		dictionary = corpora.Dictionary(all_rows)
		#为了防止未来词表乱掉，先保存一个词表，固定下来。后续的分类验证的时候，会用这个固定词表
		# dictionary.save("out/dictionary.dic")
		logger.debug("词袋一共%d个词", len(dictionary.keys()))

		return dictionary

	def test_html_parse(self):
		with open("data/1.html", "r") as f:
			html = f.read()
			pure_content = self.data_processor.clean_html(html)
			logger.debug("测试去除HTML标签内容")
			logger.debug(pure_content)

	def clean_html(html):
		bs = BeautifulSoup(html, "lxml")
		return bs.getText().strip()


	def load_stopword():
		f_stop = open('stopword.txt')
		sw = [line.strip() for line in f_stop]
		f_stop.close()
		return sw


	def cut_words(line, stop_words):
		now = time()
		seg_list = jieba.cut(line, cut_all=False)  # cut_all:False，这种不会冗余切词
		return " ".join([word for word in seg_list if word not in stop_words])


	def init(self):
		# logger.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logger.DEBUG,filename='log.txt')
		logger.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logger.DEBUG)
		logger.getLogger("gensim").setLevel(logger.WARNING)
		logger.getLogger("jieba").setLevel(logger.WARNING)

		jieba.initialize()
		jieba.load_userdict("data/addwords.txt")
		jieba.analyse.set_stop_words('data/stopwords.txt')


	def DBSCAN_analysis(self,tfidf_data):
		dbscan = DBSCAN()#5是默认的
		labels = dbscan.fit_predict(tfidf_data)
		logger.debug("DBSCAN聚出来类：%d", len(set(labels)))
		# logger.debug(labels)
		cores = dbscan.core_sample_indices_
		# logger.debug("dbscan components:%r",dbscan.components_)
		return labels, dbscan,cores

	# 先将words变成tfidf，那么tfidf词表就不能变化，这个点要注意
	# - 要验证词表没有变化，这样才能保证tfidf向量不会变化
	# - 还要注意传入的分词组中不存在的词会不会报错
	# 然后，启动KNN的it，将之前保存的分类传入KNN，形成KNN模型
	# 使用KNN模型来预测这个新传入的分词组，属于的类别，并打印词类别中的3个样例，随机
	#核心方法！！！！
	def process(self,con,df):
		big_class = self.data_processor.get_big_class(con)

		# logger.debug(df.columns)
		for _,each_big_class in big_class.iterrows():
			system = each_big_class['business_system_code']
			big_class = each_big_class['rule_type_code']

			t = time.time()

			# logger.debug("system:%s,big_class:%s",system,big_class)
			sub_df = df[(df.business_system_code == system) & (df.rule_type_code == big_class)]

			corpus_vector,dictionary,model = self.data_processor.caculate_tfidf(sub_df)

			dic_name = "dictionary_"+system+"_"+big_class+".dic"
			dictionary.save(self.model_dir+"/"+dic_name)
			logger.debug("保存词表：%s",dic_name)

			model_name = "tfidf_" + system + "_" + big_class + ".model"
			model.save(self.model_dir+"/"+model_name)
			logger.debug("保存TFIDF模型：%s",model_name)

			t = duration(t,"完成转化语料为tfidf向量！")

			if corpus_vector.shape[0] == 0:
				logger.error("这里一类(%s-%s)没有语料，忽略",system,big_class)
				continue

			classes, dbscan , _= self.DBSCAN_analysis(corpus_vector)
			logger.debug("%s-%s完成DBSCAN聚类",system,big_class)
			t = duration(t, "DBSCAN聚类")

			sub_df['classes'] = classes
			# logger.debug("DBSCAN聚类 lables：%r",dbscan.labels_)
			# logger.debug("DBSCAN聚类 core_sample_indices_：%r",dbscan.core_sample_indices_)
			# logger.debug("DBSCAN聚类 get_params:%r",dbscan.get_params())
			sub_df.to_sql("monitor_cluster_dbscan", con, if_exists='append',chunksize=100)
			# sub_df.sort_values(['classes'])

			#保存这一个大类的聚出来的类的信息==>monitor_classes
			self.generate_class_title( sub_df, system, big_class, con)


	def generate_class_title(self,df,system,big_class,conn):
		tf = lambda  x : ' '.join(x['email_title'])#把所有的切词的内容都拼接出来
		groups = df.groupby(['classes']).apply(tf)#返回一个序列Series


		df_classes = pd.DataFrame(columns=['class_id','description','business_system_code','rule_type_code','alarm_count'])
		for index,value in groups.items():
			#清洗数据
			value = self.clean_line(value)
			#取得这个分类的中的所有的词拼在一起的词的词频里最靠前的top10

			tags = jieba.analyse.extract_tags(value, topK=20, withWeight=False, allowPOS=())

			new_tags = []
			i=0
			for x in tags:
				i +=1
				if i>10: break
				if not x.isdigit():
					new_tags.append(x)
				elif len(x) == 4 or len(x) == 6:
					new_tags.append(x)

			top_10 = ",".join(new_tags)
			# logger.debug("分组：%s",top_10)
			df_classes = df_classes.append({
				'class_id':index,
				'description':top_10,
				'business_system_code':system,
				'rule_type_code':big_class},
				ignore_index=True)
			logger.debug("类别%d的主题是：%s",index,top_10)

		# print(df_classes.head(4))

		df_classes.to_sql("monitor_classes",conn,
				dtype = {
				 'class_id': sqlalchemy.types.INTEGER(),
				 'description': sqlalchemy.types.NVARCHAR(length=2000),
				 'business_system_code': sqlalchemy.types.NVARCHAR(length=255),
				 'rule_type_code':  sqlalchemy.types.NVARCHAR(length=255),
				 },
				if_exists = 'append',
				chunksize=100)

