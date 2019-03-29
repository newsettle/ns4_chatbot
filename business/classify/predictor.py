#-*- coding:utf-8 -*-
import time,logging as logger
import pandas as pd
import numpy as np
import sys
sys.path.append("..")
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from common.common import duration
from common.config import Config
from data_process import DataProcess
from sklearn.neighbors import KNeighborsClassifier

class ClassPredictor(object):

	def __init__(self,conf,model_dir = ".cache/model"):
		self.conf = conf
		self.data_processor = DataProcess()
		self.models = {}
		self.model_dir = model_dir

		con = self.data_processor.connect_db(conf.db_host, conf.db_database, conf.db_user, conf.db_pass)
		classes = self.data_processor.get_big_class(con)
		print (classes)
		for index,cls in classes.iterrows():
			system = cls['business_system_code']
			subclass = cls['rule_type_code']
			self.init(system, subclass)

	def init(self,system,subclass):
		conn = self.data_processor.connect_db(
			self.conf.db_host,
			self.conf.db_database,
			self.conf.db_user,
			self.conf.db_pass
		)
		#装载词表,#装载模型
		t = time.time()

		logger.debug("正在初始化[%s-%s]的模型加载",system,subclass)

		dic_name = "dictionary_" + system + "_" + subclass + ".dic"
		dictionary = Dictionary.load(self.model_dir+"/" + dic_name)
		logger.debug("加载了字典:%s", dic_name)
		logger.debug("词袋一共%d个词", len(dictionary.keys()))

		model_name = "tfidf_" + system + "_" + subclass + ".model"
		model = TfidfModel.load(self.model_dir+"/" + model_name)
		logger.debug("加载了TFIDF模型:%s", model_name)

		df_train = pd.read_sql(
			"select * from monitor_cluster_dbscan where business_system_code='{}' and rule_type_code='{}'".format(system,subclass)
			,conn)

		#KNN聚类，然后预测
		knn = self.get_KNN_model(df_train,dictionary,model)
		duration(t,"根据字典和此分类数据，基于tfidf向量，训练出KNN模型")

		if knn is not None:
			key = system+"-"+subclass
			value = {'model':model, 'dictionary':dictionary, 'knn':knn}
			self.models[key] = value

	def get_KNN_model(self,df, dictionary, tfidf_model):
		if df.shape[0] ==0:
			logger.error("此数据集为空，无法进行KNN聚类")
			return None

		X = np.array(df['html_cut'])
		X = self.data_processor.get_tfidf_vector(X, dictionary, tfidf_model)
		y = np.array(df['classes'])
		knn = KNeighborsClassifier()
		knn.fit(X, y)
		return knn

	def predict(self,test_data,system,subclass):

		key = system+"-"+subclass
		logger.debug("预测开始，系统-大类为：%s",key)
		_tfidf_dictionary = self.models.get(key,None)

		if _tfidf_dictionary is None:
			logger.error("无法找到对应的tfidf和字典,KNN")
			return None

		model = _tfidf_dictionary.get("model")
		dictionary = _tfidf_dictionary.get("dictionary")
		knn = _tfidf_dictionary.get("knn")

		if(model is None):
			logger.error("无法找到TFIDF Model")
			return None
		if (dictionary is None):
			logger.error("无法找到dictionary")
			return None
		if (knn is None):
			logger.error("无法找到KNN")
			return None

		t = time.time()
		# 生成清洗完html标签，去掉了数字和英文，停顿词之后的语料，空格分割
		test_data = self.data_processor.process_line(test_data)
		logger.debug("对邮件进行完了处理：%s",test_data)

		x_test = self.data_processor.get_tfidf_vector([test_data],dictionary,model)
		t = duration(t,"加载测试数据")

		#来正式预测
		pred = knn.predict(x_test)
		t = duration(t,"预测结果")
		logger.debug("预测结果：")
		logger.debug(pred)

		return pred[0]

if __name__=="__main__":
	config = Config("../bot.conf")
	predictor = ClassPredictor(config,"../.cache/model")

	#测试数据是：CASH_COMPASS RESPCODE
	test_data =  "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>响应码预警</title><style type=\"text/css\">table, td, th{border-collapse:collapse;border:1px solid blue;}th{height: 40px;background-color: #EFEEEE;}td{height: 30px;text-align: center;}</style></head><body><div><header><h1>响应码报警</h1></header><body><table><tr><th>响应码</th><th>响应信息</th><th>支付类型</th><th>监控指标</th><th>实际发生次数</th><th>次数阀值</th></tr><tr><td>4043</td><td>第三方未返回交易结果</td><td>快捷支付,单笔代扣,单笔代付,二要素鉴权,三要素鉴权,四要素鉴权,签约短信,签约协议,解约协议</td><td>1分钟内出现次数</td><td><font color='red'>6</font></td><td>5</td></tr></table><br><br><b>发生时间区间:</b>2018年08月17日09时17分 - 2018年08月17日09时17分<br><br><b>处理方案:</b>若大批量出现，则联系运营确认通道交易是否正常！<br><br><b>报警内容:</b><br>响应码4043，响应信息第三方未返回交易结果,在2018年08月17日09时17分-2018年08月17日09时17分出现6次，触发了5次的报警阀值<br><br><b>报警明细：</b><br><br><table><tr><th>序号</th><th>商户名称</th><th>商户单号</th><th>批次号</th><th>系统单号</th><th>支付类型</th><th>通道名称</th><th>银行名称</th><th>银行卡号</th><th>交易金额</th><th>交易状态</th><th>响应码</th><th>响应信息</th><th>备注</th></tr><tr><td>1</td><td>新核心-违约客户还款-POS验证</td><td><a href=\"http://xxxxxxxxx/logQuery/result.php?order_id=2018081757297573\">2018081757297573</a></td><td>-</td><td>CEC180817091650948043117583</td><td>单笔代扣</td><td>快付通</td><td>工商银行</td><td>622202****516</td><td>1459.88</td><td>已受理</td><td>4043</td><td>【结算平台消息】第三方返回响应信息为空-快付通单笔收款响应信息为空</td><td></td></tr><tr><td>2</td><td>新核心-违约客户还款-POS验证</td><td><a href=\"http://xxxxxxx/logQuery/result.php?order_id=2018081757297347\">2018081757297347</a></td><td>-</td><td>CEC180817091634772043059615</td><td>单笔代扣</td><td>快付通</td><td>工商银行</td><td>621226****812</td><td>3489.93</td><td>已受理</td><td>4043</td><td>【结算平台消息】第三方返回响应信息为空-快付通单笔收款响应信息为空</td><td></td></tr><tr><td>3</td><td>宜信汇创-签约认证</td><td><a href=\"http://xxxxxxxxxx/logQuery/result.php?order_id=02000030010012573153446863302318\">02000030010012573153446863302318</a></td><td>-</td><td>CEX180817091713260043224849</td><td>签约短信</td><td>快付通协议支付</td><td>工商银行</td><td>621723****962</td><td>0</td><td>交易失败</td><td>4043</td><td>【结算平台消息】第三方返回响应信息为空-快付通协议短信响应信息为空</td><td></td></tr><tr><td>4</td><td>宜人贷</td><td><a href=\"http://xxxxxxxlogQuery/result.php?order_id=as78602\">as78602</a></td><td>-</td><td>CEX180817091708902043209199</td><td>签约短信</td><td>快付通协议支付</td><td>建设银行</td><td>622700****126</td><td>0</td><td>交易失败</td><td>4043</td><td>【结算平台消息】第三方返回响应信息为空-快付通协议短信响应信息为空</td><td></td></tr></table></div></div></body></html>"

	dp = DataProcess()

	db_ip="127.0.0.1"
	db_name="chatbot"
	db_user = "username"
	db_passwd = "password"
	con = dp.connect_db(db_ip, db_name,db_user,db_passwd)
	classes = dp.get_big_class(con)

	system = "NEW_SETTLEMENT"
	subclass="RESPCODE"
	# predictor.init(system,subclass)

	pred = predictor.predict(test_data,system,subclass)


	logger.debug("预测结果是：%r",pred)
	logger.debug("预测结果是：%r",type(pred))