#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup,NavigableString
from common import logger
import HTMLParser

# 报警的邮件要转成图片发给微信机器人，遇到字体问题， out.jpg图片是乱码，反反复复实践解决：
# 2.必须要修改网页，加入 < meta charset = "UTF-8”>到HTML里面
def __insert_meta(html):
	html_parser = HTMLParser.HTMLParser()
	html = html_parser.unescape(html)  # 先把 &quot转成"
	html_pos = html.find("<head>")
	if html_pos == -1:
		logger.error("无法在邮件的HTML文本中查找到<head>标记，插入meta-charset失败")
		return html
	meta = "<meta charset=\"UTF-8\">"
	html_pos = html_pos + 6
	html = html[:html_pos] + meta + html[html_pos:]
	return html


#去除html中的标签和表格，用于qq中显示
#qq比较操蛋的是，无法发送图片信息
def clean_html(html,config):
	__insert_meta(html)

	bs = BeautifulSoup(html)
	body = bs.body

	full_content = __clear(body,config)

	#限定一下发到QQ中的文本长度，太长了
	max = config.monitor_max_text_length
	if len(full_content)> max:
		return full_content[0:max]
	else:
		return full_content

line_elements = ['br','p','h1','h2','h3','h4','h5']

def __clear(parent_node,config):
	# return bs.prettify()
	content = ""
	# print parent_node
	if isinstance(parent_node, NavigableString):
		return parent_node.string

	if parent_node.name in line_elements:
		content += "\n"

	children = parent_node.contents

	for child in children:
		if child.name == "table":
			content += parse_table(child,config)
		else:
			content += __clear(child,config)

	return content


def parse_table(tab,config):
	content = "\n"
	line = 0

	for tr in tab.findAll('tr'):

		if line > config.monitor_max_table_line:break

		content += "|"
		for td in tr.findAll('th'):
			content += td.getText().strip() + "|"
		for td in tr.findAll('td'):
			content += td.getText().strip() + "|"
		content = content + "\n"

		line += 1
	content = content + "...\n"
	return content


if __name__ == '__main__':
	s="<!DOCTYPE html><html><head><meta charset=utf-8><title></title><style type=text/css>table, td, th{border-collapse:collapse;border:1px solid blue;}th{height: 40px;background-color: #EFEEEE;}td{height: 30px;text-align: center;}</style></head><body><div><header><h1></h1></header><div><h4>预留备注：订单超时</h4><h3>报警内容：</h3><p><font color='red'>在过去【1】分钟，出现超时订单或者超时【0】秒未完成订单，达到了【41】笔，超过了报警阈值【0】笔,统计时间段：【201807051613】-【201807051614】,请关注！</font></p><h5>以下为各个超时订单具体信息：</h5><table><tr><th>订单号</th><th>商户名称</th><th>支付方式</th><th>通道名称</th><th>银行名称</th><th>交易金额</th><th>响应码</th><th>响应信息</th></tr><tr><td>jk031805161359005367395271</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161357490174487665</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161356607068482871</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161354393638518371</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161353082092927267</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161351687408208787</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161350707995863471</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161349542628158209</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161347560531062201</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161346525383097442</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161345120636064819</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161343558692639478</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161342531705342473</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161341733973466103</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161340922327412020</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161338202320802351</td><td>0000105</td><td>03</td><td>HYL</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161337549347008789</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161335037559598506</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161334494747111307</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161333455032571020</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161331521976765053</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161330397579079210</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161329848237851570</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161327046185990115</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161326015150533500</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161324409978140977</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161323214142313364</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161322576255054558</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161321930944170033</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161319813982175182</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161318496102684803</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161316481329655662</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161315538593430807</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161308275752985140</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161308464960248669</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161305985776726386</td><td>0000105</td><td>03</td><td>HYL</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161305277033352521</td><td>0000105</td><td>03</td><td>HYL</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161302616052939638</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161302532274233578</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161259817844826298</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr><tr><td>jk031805161259718313109371</td><td>0000105</td><td>03</td><td>-</td><td>0102</td><td>0.11</td><td>-</td><td>-</td></tr></table></div>预警等级：严重!,</br></br><div><p>【以下内容可忽略】 为定位报警系统问题预留，读取规则信息：</br>通知邮件发送时间[2018-07-05 16:14:00 020],</br></p></div></div></body></html>"

	print clean_html(s)