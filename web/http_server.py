#-*- coding:utf-8 -*-
from flask import Flask,jsonify,request,render_template
import sys,threading,os
import common.logger as logger,json
from gevent.pywsgi import WSGIServer
from common.common import BaseService

sys.path.append("..")

class Http_Server(BaseService):
    app = Flask(__name__, static_url_path='')

    def __init__(self,bizManager,config):
        self.config = config
        self.bizManager = bizManager
        #这个设计很ugly，但是也没啥好办法，我实在是需要qqbot的引用啊,liuc,2019.1.8
        self.qqbot = bizManager.botManager.get_bot_by_type("qq")


    def _process_web_request(self,flag,func=None):
        data = None
        s_json = None
        if request.content_type is None:#get请求
            data = request.args
        else:#类型为： application/x-www-form-urlencoded
            s_json = request.get_data()
            if s_json is None or s_json == '':
                logger.warn(u"json数据为空")

            else:
                if flag!="coolq_callback":#QQ的回调接口，任何消息都回调，所以不能记录他们
                    logger.debug("接收到来自网络的数据：%s",s_json)

                try:
                    #2018.10.16 bug，文本中有tab\return 旧会导致json解析失败，替换掉
                    s_json = s_json.replace("\t", "").replace("\n", "")
                    # data = json.loads(s_json.decode('ISO-8859-1'))#.decode('ISO-8859-1')
                    data = json.loads(s_json)

                except ValueError as ve:
                    logger.exception(ve,"无法解析json数据：%s",s_json)
                    return "Error Parse Json: error("+str(ve)+"),json="+s_json,500

        #处理coolq的回调消息，这个是本机上的酷Q-docker接收到消息，回调我们的            
        if flag == "coolq_callback":
            rmsg = self.qqbot.on_message(data) 
            if rmsg:
                return jsonify({"reply":rmsg})#必须是json格式，文档里说文本即可，不行
            else:
                return "",204#大部分消息不需要处理，直接忽略<https://cqhttp.cc/docs/4.7/#/Post?id=%E4%B8%8A%E6%8A%A5%E8%AF%B7%E6%B1%82%E7%9A%84%E5%93%8D%E5%BA%94%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F>

        bizComponent = self.bizManager.load_biz_comp(flag)

        if bizComponent is None:
            logger.error("无法找到业务组件来为此HTTP请求服务,flag=%s",flag)
            return "系统错误：无法找到内部业务组件给您服务", 500
        else:
            logger.debug("加载业务处理器：%r",bizComponent)

        try:
            result = bizComponent.system2bot(data,func)
        except Exception as ve:
            logger.exception(ve,"业务处理组件发生错误data=[%s],func=[%s]",s_json,func)
            return "Error Happen Inside Business Component:"+str(ve),500
        if result=="OK":
            return "OK",200
        else:
            return result, 500

    def bank_notify(self):
        return self._process_web_request("bank_notify",func="bank_notify")
    def chat(self):
        return self._process_web_request("chat")
    def coolq_callback(self):
        return self._process_web_request("coolq_callback")

    def index(self):
        return "ok"

    def startup(self):
        super(Http_Server,self).startup()

        logger.info("启动 WEB 服务.....")
        t = threading.Thread(target=self._startup, name='http-server')
        # t.setDaemon(True)
        t.start()

    def __url_mapping(self):
        logger.debug("HTTP服务已注册监听'/'")
        self.app.add_url_rule('/', view_func=self.index,methods = ['GET', 'POST'] )
        logger.debug("HTTP服务已注册监听'/chat'")
        self.app.add_url_rule('/chat', view_func=self.chat, methods=['GET', 'POST'])
        logger.debug("HTTP服务已注册监听'/coolq_callback'")
        self.app.add_url_rule('/coolq_callback', view_func=self.coolq_callback, methods=['GET', 'POST'])



    def _startup(self):

        self.__url_mapping()

        logger.info("Web服务启动了，端口：%d",self.config.http_port)
        http_server = WSGIServer(('0.0.0.0', self.config.http_port), self.app)
        try:
            http_server.serve_forever()
        except Exception as e:
            logger.exception(e,"Web服务启动发生错误：%s",str(e))