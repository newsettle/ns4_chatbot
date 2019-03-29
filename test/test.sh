#!/usr/bin/env bash
BOT_SERVER=127.0.0.1
BOT_PORT=8080

if [ "$1" = "" ];then
    echo "命令格式不对：test.sh  chat"
    exit
fi

if [ "$1" = "chat" ]; then
    echo "测试微信qq接口..."
    curl -XPOST http://$BOT_SERVER:$BOT_PORT/chat -d \
    '{
            "qqGroupId":   "12345678",
            "wxGroupName":   "testbot",
            "msgId":"10000001",
            "type": "testbot",
            "user":   "亚可",
            "msg": "现金罗盘报警测试"
            "html": "<!DOCTYPE html><html><head><title></title><style type=text/css>table, td, th{border-collapse:collapse;border:1px solid blue;}th{height: 40px;background-color: #EFEEEE;}td{height: 30px;text-align: center;}</style></head><body>test</body></html>"
            "remark": "现金罗盘"
    }'
fi

