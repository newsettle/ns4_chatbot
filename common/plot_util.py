# -*- coding:utf8 -*-
import numpy as np
import matplotlib as mpl
mpl.use('Agg') #https://blog.csdn.net/ydyang1126/article/details/77247654
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import random ,string
from common import logger
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签


def generate_dummy_data():
	__category = ["所有", "未处理", "已处理", "关注"]
	category = np.tile(__category, 24)
	hour = np.ndarray([0, ])
	for i in range(1, 25):
		# hour.concatenate( np.repeat(i,len(__category))  )
		hour = np.concatenate((hour, np.repeat(i, len(__category))))
	value = np.random.randint(30, size=24 * len(__category))

	data = np.stack((category, hour, value)).T
	return data


def generate_dummy_data2():
	result = {}
	__category = ["所有", "未处理", "已处理", "关注"]

	for c in __category:
		result[c] = np.random.randint(300, size=24)

	# print (result)
	return result

def generate_dummy_data3():
	result = {}
	__category = ["所有", "未处理", "已处理"]#, "关注"]

	for c in __category:
		result[c] = np.random.randint(30, size=24)

	
	result['关注'] = np.random.randint(10, size=14)


	# print (result)
	return result


# data_dict =
# {
# 	'所有':[1,2,3,4,45,5,5,56],
# 	'未处理':[121，2，2，2，2，2],
# 	'分类数':[1,2,2,3,3,34,4,4,]
# }
# title = "xxxxxx"
# x_label = "xxx"
# y1_label = "xxx"
# y2_label = "xxx"
# isLastY2 = True
# img_path = draw_it(title,data_dict,x_label,y_label)

def draw_it(title, x_label, y_label, data,x_start=0,x_end=24,image_path=".cache/image"):
	# print(data)
	f, ax = plt.subplots()

	logger.debug("数据：%r", data)
	for c in data:
		logger.debug("开始画 数据分类：%r",c)
		_data = data[c]
		_data = np.array(_data)#有可能传入的是个数组，所以要转换成ndarray
		sns.lineplot(marker='o', data=_data, err_style="bars", label=c)

	ax.xaxis.set_major_locator(MultipleLocator(1))
	ax.xaxis.set_minor_locator(MultipleLocator(1))
	# ax.yaxis.set_major_locator(MultipleLocator(5))
	# ax.yaxis.set_minor_locator(MultipleLocator(1))	
	ax.tick_params(axis='x', colors='b')
	plt.xlim((x_start,x_end))
	plt.ylim(bottom=1)
	#plt.xlim((0,24))

	plt.xticks(fontsize=10)
	plt.legend(loc='upper right')
	plt.title(title, fontsize='large', fontweight='bold')  # 设置字体大小与格式
	plt.xlabel(x_label, fontsize=10)
	plt.ylabel(y_label, fontsize=10)

	# plt.show()
	random_file_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
	temp_file = image_path + "/" + random_file_name + ".jpg"
	logger.debug("将图片保存到文件：%s", temp_file)
	f.savefig(temp_file, dpi=100, bbox_inches='tight')
	return temp_file


if __name__ == '__main__':
	data = generate_dummy_data3()
	file = draw_it(title=u"报警趋势图", data=data, x_label=u"小时", y_label=u"次数",image_path="../.cache/image")
	print(file)