#-*- coding:utf-8 -*-
import sys,pymysql,time,datetime,json
import logger,config
import dbinit
import time
import json

from flask import Flask,request
try:
    con=dbinit.con
except BaseException:
    logger.error("连不上数据库")



if sys.getdefaultencoding() != 'utf-8':
	sys.setdefaultencoding('utf-8')
	reload(sys)

app = Flask(__name__)


#匹配部门的名字/别名  和  值班表中的名字
def match_department(department, dept_name_of_duty):

	if department is None: return False
	if dept_name_of_duty is None: return False

	if department['name'] == dept_name_of_duty: return True
	if department['other_name'] is None: return False

	other_names = department['other_name'].split("|")
	for on in other_names:
		if on==dept_name_of_duty: return True
	return False

#输入的是一个部门的别名，这个别名是从报警过来的，like"定时器超时监控(账务组)"中的账务组
#我们从这个名字，要返回一个qq和wechat的group，还要返回这个组中的值班的人
def find_group_by_name(department):
    try:
        #1.从这个名字，去部门中，去确定部门，这样也得到了qq和微信的群号
        cursor = con.cursor()

        #查当日值班的人
        sql = "SELECT duration,duty_person,`group` FROM cb_duty where duty_date = CURDATE()"
        logger.debug (sql)
        cursor.execute(sql)
        dutys = cursor.fetchall()
    except pymysql.Error as e:
        logger.error('Got error  {!r} in ececute {}, errno is {}'.format(e, sql,e.args[0]))
        return None

    group_duty_person = None
    am_person = None
    pm_person = None
    department_name = None
    wechat_group = None
    qq_group = None
    group_duty_person = None
    for d in dutys:
        # logger.debug("遍历每个当天值班的人")
		# logger.debug (d)
        if d[0]=='AM': am_person = d[1]#duration
        if d[0]=='PM': pm_person = d[1]
        #如果值班人的部门，可以咋样部门表中的部门名字或者别名中找到, TODO:一个部门可能有2个人，这里是个一个bug，回头修复
        if match_department(department,d[2]):
            group_duty_person = d[1]
            wechat_group = department['wechat_group']
            qq_group = department['qq_group']
            department_name = department['name']
            break

    #3.再有人名去查找其对应的人全名，不过貌似这步骤不用，只要知道他对应的群组就可以，@的时候，@他的名字就成
	#原因是qq和wechat无法@一个真名

	#如果现在已经4点以后了，就是下午值班的人了
	syear, smonth, sday, _, _ = time.strftime("%Y,%m,%d,%H,%M").split(',')
    AM_16_00 = datetime.datetime(int(syear), int(smonth), int(sday), 16)
    now = datetime.datetime.now()
    if now > AM_16_00:
        monitor_room_duty_person = pm_person
    else:
        monitor_room_duty_person = am_person

    data={
		'monitor_room':{
			'person':monitor_room_duty_person,
			'qq_group':'testbot',
			'wechat_group':'testbot'
		},
		'group_duty':{
			'person':group_duty_person,
			'department':department_name,
			'wechat_group': wechat_group,
			'qq_group': qq_group
		}
	}

    return data


@app.route("/find_group_by_name",methods=['GET', 'POST'])
def get_group():
    data = json.loads(request.get_data())
    dept_name = data.get("dept_name", "no dept_name")
    if dept_name == "no dept_name":
        logger.error("无效的部门名字%s",dept_name)
    duties=find_group_by_name(dept_name)
    if duties == None:
        logger.error("找不到相关值班部门信息")
        # return '找不到相关值班部门{%s}的信息'.format(dept_name)
    else:
        logger.debug("找到相关部门的信息")
        return json.dumps(duties)



if __name__ == "__main__":
	# app.run(host='0.0.0.0',port='8000')
    logger.init()
    app.run(host=config.db_app_host, port=config.db_app_port)
