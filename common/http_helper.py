# -*- coding:utf-8 -*-
from common import logger
import requests
import urllib2,json
def do_request_json(url,param):
    try:
        headers = {'Content-Type': 'application/json'}
        request = urllib2.Request(url=url, headers=headers, data=json.dumps(param))
        response = urllib2.urlopen(request,timeout=3)
        r = response.read().decode('utf-8')
        return json.loads(r)
    except Exception as e:
        logger.warn("http调用失败:%s",str(e))
        return None


#post请求 param = {"data": ""}
def do_get_http_request(url, param):
    requests.adapters.DEFAULT_RETRIES = 0
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    r = s.get(url, data=param ,timeout = 3)
    return r

# post请求  param = {"data":""}
def do_post_http_request(url,param):
    requests.adapters.DEFAULT_RETRIES = 0
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    r = s.post(url, data=param ,timeout=3)
    return r

if __name__=="__main__":
    a = do_get_http_request("http://localhost:8080/timer_monitor_report/notify",{'message': "Opportunitiesandchallengestogether"})
