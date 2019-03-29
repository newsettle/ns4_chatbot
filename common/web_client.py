# -*- coding=utf-8 -*-
import urllib2
import json
import logger
import traceback

def send(apiUrl,data,method=None):
    logger.debug("调用内部系统[%s],data[%r]",apiUrl,data)
    try:
        data_json = json.dumps(data)
        headers = {'Content-Type': 'application/json'} # 设置数据为json格式，很重要
        request = urllib2.Request(url=apiUrl, headers=headers, data=data_json)
        if method is not None:
            request.get_method = method

        response = urllib2.urlopen(request)
        result = {'code':response.getcode(),'content':response.read()}
        logger.debug("调用[%s]返回结果:%r",apiUrl,result)
        return result
    except Exception as e:
        #traceback.print_stack()
        logger.exception(e,"调用内部系统[%s],data[%r],发生错误[%r]", apiUrl, data,e)
        return None

if __name__ == "__main__":
    logger.init_4_debug()
