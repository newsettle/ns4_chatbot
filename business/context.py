#-*- coding:utf-8 -*-


#存放对话上下文
#key是：类型（如qq|微信）+ 群组名 + 用户名
#value是一个dict,
#这个value（类型是dict）可以放任何上下文，
#但是有个特殊的key，叫"dialogs"，用于存放对话，最多保存10句
# {
#     "key1":{
#         "biz_type":"db_approval" //有db_approval,rasa,monitor3个，目前，未来可能会有更多
#         "context_key1":"context_value",
#         "dialogs":['11111','22222','333333'...]
#     }
# }
#key1，就是类型（如qq|微信）+ 群组名 + 用户名
class ContextStore:
    def __init__(self):
        self.store = {}
        self.maxsize = 10

    def save_biz_type(self,key,biz_type):
        self.save_context(key,"biz_type",biz_type)

    #key是某个人对话的上下文标识，
    #context_key，就是这个人对话中，想要存入的上下文的key
    #context，存入的内容
    #比如，审批中，需要存入flow_id，
    #那么调用就是 save_context("qq-testbot-chuangliu18","flow_id","OA_AUTH_00394965")
    def save_context(self,key,context_key,context):
        value = self.store.get(key,None)
        #如果这个上下文不存在，就创建之
        if value is None:
            value = {context_key:context}
            self.store[key] = value
        #存在，就放入新的
        else:
             value[context_key] = context

    #value其实就是对话内容
    def save_dialog(self,key,dialog):
        value = self.store.get(key,None)

        #如果这个上下文不存在，就创建之
        if value is None:
            _dialogs = Stack(self.maxsize)
            _dialogs.push(dialog)
            value = {'dialogs': _dialogs}
            self.store[key] = value
        #存在，就放入新的
        else:
            _dialogs = value.get('dialogs',None)
            if _dialogs is None:
                _dialogs = Stack(self.maxsize)
                _dialogs.push(dialog)
                value['dialogs'] = _dialogs
                self.store[key] = value
            else:
                _dialogs.push(dialog)

    def find_context(self,key):
        return self.store.get(key,None)


    #得到某一个context内部的key-value
    def find_sub_context(self,key,context_key):
        value = self.store.get(key)
        if value is None: return None
        return value.get(context_key,None)


    def find_dialog(self,key):
        value = self.store.get(key)
        if value is None: return None
        return value.get('dialogs',None)

class BusinessContext:
    def __init__(self):
        pass

class Stack(object):
    # 初始化栈为空列表
    def __init__(self,maxsize):
        self.items = []
        self.size = maxsize

    # 判断栈是否为空，返回布尔值
    def is_empty(self):
        return self.items == []

    # 返回栈顶元素
    def peek(self):
        return self.items[len(self.items) - 1]

    # 返回栈的大小
    def size(self):
        return len(self.items)

    # 把新的元素堆进栈里面（程序员喜欢把这个过程叫做压栈，入栈，进栈……）
    def push(self, item):
        if len(self.items)>= self.size:
            self.items.pop(0)
        self.items.append(item)

    # 把栈顶元素丢出去（程序员喜欢把这个过程叫做出栈……）
    def pop(self):
        return self.items.pop()

    def __str__(self):
        return str(self.items)

if __name__ == "__main__":
    # stack = Stack(3)
    # stack.push(1)
    # stack.push(2)
    # stack.push(3)
    # stack.push(4)
    # stack.push(5)
    # print stack
    # stack.pop()
    # print stack
    # stack.push(6)
    # print stack

    #测试的时候，把maxsize改成3
    store = ContextStore()
    store.save_dialog("key1", "x1")
    store.save_dialog("key1", "x2")
    store.save_dialog("key1", "x3")
    store.save_dialog("key1", "x4")
    store.save_dialog("key1", "x5")
    store.save_context("key1", "context_key1" , "context1")
    store.save_dialog("key2", "y1")
    store.save_dialog("key2", "y2")
    store.save_context("key2", "context_key2" , "context2")
    print store.find_dialog("key1")
    print store.find_context("key1","dialogs")
    print store.find_context("key1", "context_key1")
    print
    print store.find_dialog("key2")
    print store.find_context("key2","dialogs")
    print store.find_context("key2", "context_key2")
    print
    print store.find_dialog("key3")
