#-*- coding:utf-8 -*-
import sys,pymysql,time,datetime,json,jieba,re,progressbar,codecs
import logging as logger,gensim
from bs4 import BeautifulSoup
from scipy.sparse import csc_matrix
import numpy as np
import pandas as pd
from jieba import analyse
from gensim import corpora, models, similarities
from sklearn.manifold import TSNE
from time import time
from sqlalchemy import create_engine
from scipy.spatial.distance import pdist,squareform
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
from sklearn import manifold, datasets
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import NullFormatter
from sklearn.neighbors import KNeighborsClassifier
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
#
def connect_db():
	conn = create_engine('mysql+mysqldb://username:password@localhost:3306/chatbot?charset=utf8')
	return conn

def get_KNN_model(df,dictionary,tfidf_model):
	X = np.array(df['html_cut'])
	X = get_tfidf_vector(X,dictionary,tfidf_model)
	y = np.array(df['classes'])
	knn = KNeighborsClassifier()
	knn.fit(X,y)
	return knn

# 耗时计算
def duration(t, title):
	now = time()
	logger.debug("%s：耗时%f秒", title, (now - t))
	return now

def _init():
	logger.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logger.DEBUG)
	logger.getLogger("gensim").setLevel(logger.WARNING)
	logger.getLogger("jieba").setLevel(logger.WARNING)

import sys
sys.path.append("..")
from dbscan_analysis import *

def main():

	_init()

	#装载词表,#装载模型
	t = time()
	dictionary = Dictionary.load("../out/dictionary.dic")
	logger.debug("词袋一共%d个词",len(dictionary.keys()))
	model = TfidfModel.load("../out/tfidf.model")
	t = duration(t,"加载词表和TFIDF模型")

	#加载训练数据集
	t = time()
	#df_train = pd.read_csv(open("../out/cluster_dbscan_9900.csv",'rU'), encoding='utf-8', engine='c')
	df_train = pd.read_sql("select * from cluster_dbscan limit  9900", connect_db())
	t = duration(t,"加载历史数据用于训练KNN")

	knn = get_KNN_model(df_train,dictionary,model)
	t = duration(t,"训练出KNN模型")

	df_test = pd.read_sql("select * from clean_cut_data  limit 9900,100", connect_db())
	doc_list = df_test['html_cut'].tolist()
	x_test = get_tfidf_vector(doc_list,dictionary,model)
	logger.debug("x_test's shape:%r",x_test.shape)
	t = duration(t,"加载测试数据")

	pred = knn.predict(x_test)
	t = duration(t,"预测结果")
	logger.debug("预测结果：")
	logger.debug(pred)

	df_test['classes'] = pred

	for index, row in df_test.iterrows():
		_class = row['classes']
		test_title = row['work_order_title']
		label_title = df_train[df_train['classes']==_class].iloc[0,:]['work_order_title']
		logger.debug("类别(%d),测试标题(%s),样本标题(%s)",_class,test_title,label_title)





