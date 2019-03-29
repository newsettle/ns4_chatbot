#这个工程用于外网的chatbot访问内网的数据库， chatbot->db_app->db

-dbinit
    初始化一个数据库链接

-config.conf
    数据库的配置

-config.py
    读取配置文件

-logger.py
    日志记录文件

-database.py
    在database.py起一个flask app，路由函数get_group用来接收来自chatbot的请求，并在get_group中调用find_group_by_name函数执行数据库的查询，并把查询结果返回给chatbot



