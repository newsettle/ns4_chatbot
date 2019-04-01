# 聊天机器人项目
官方文档请点击
（https://github.com/newsettle/ns4_chatbot/blob/master/docs/ns4_chatbot%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3.pdf ）

这个项目是针对业务的一个聊天机器人的聊天框架，实际上是一个集成项目，集成了qqbot、wxchat、rasa以及web服务。

## 实现的功能
1. 接受内部系统，如监控系统的系统调用，从而把消息推送给QQ或者微信用户
    内部系统调用才服务的时候，需要提供以下信息
    - 发给哪个群组
    - 发给这个群组中的那个用户
    - 发送的消息
    
2. 可以接受QQ、微信用户的对话，理解其意图，并且回应用户

## 目录结构
```
Main.py 系统的主入口
|-bin/     	启动、停止脚本
|-bot/      bot机器人相关代码
|   |-wxpy  微信机器人
|   |-qqbot qq机器人
|   |-rasa  对话机器人
|-data/     数据库初始脚本和其他预制数据
|-business/ 业务处理器，对应各类业务的处理类
|-common/   一些共通处理，基础类
|-database/ 单独的一个数据库中间件服务器，用于部署于app区做数据库代理
|-log/      用于存放日志文件
|-test/     测试相关的脚本
|-web/      Web服务器的程序
```

## 设计、问题、解决方案
- 关于配置

- 整合rasa
    - 和rasa集成
        过去和wechat微信集成，使用它的WexinChannel，但是这种方式不太灵活，
        后来参考他的rasa_core.server代码，发现只要调用star_handle_message方法即可    

- 关于qqbot和wechat的统一
    这两种聊天机器人是两种风格，wechat是靠@register这种python wapper机制来绑定消息响应函数的，而qqbot是靠插件形式完成的，
    而消息发送，是统一成send函数，wechat是靠直白地bot.send，而qqbot是靠发送一个_send函数到队列实现的（参考qbot设计）

- QQ、微信无法发给非好友用户
    QQ和微信，无法直接发消息给群组中的非好友用户，
    只能通过@的方式提醒，
    
- 启动顺序
    需要先启动rasa，然后把它传给qbot、wechatbot，然后把wechatbot和qqbot再传给httpserver

- rasa/core 目录内都是之前的各种rasa测试代码以及训练代码，保留，以后可能会用得到    

- 记录聊天记录

