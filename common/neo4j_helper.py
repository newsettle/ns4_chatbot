#-*- coding:utf-8 -*-

import sys
import logger,config

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

def init():
    global graph

def find_qq_wechat_group_by_email(email):

    cypher_sql = """\
        match(e:employee)-[:所属部门]-(d:department) \
        where e.email = "{}"
        with e,d \
            optional match(d:department)-[:在群里]-(qq:qq_group) \
            optional match(d:department)-[:在群里]-(wechat:wechat_group) \
        return  \
            e.name as name, \
            e.email as email, \
            d.name as department,  \
            qq.name as qq_group,  \
            wechat.name as wechat_group""".format(email)
    logger.debug(cypher_sql)
    result = graph.run(cypher_sql).data()
    # logger.debug()
    # logger.info("jieguo#############################################################################")
    #logger.debug(result)
    if result is None or len(result)==0:
        logger.warn("无法查找到邮件为[%s]用户的信息",email)
        return None
    return result[0]

#按照一个模糊的名字，超找到单位，然后返回单位的所有信息
#模糊查找，可能会有bug，暂时先不考虑
def find_department_by_name(name):
    #用optional做类左连接
    cypher_sql = \
        "match(d:department)  \
        with d  \
            optional match(d:department)-[:在群里]-(wechat:wechat_group) \
            optional match(d:department)-[:在群里]-(qq:qq_group) \
        return  d.name as name, \
                d.other_name as other_name, \
                qq.name as qq_group, \
                wechat.name as wechat_group"

    #这里查出所有的部门，没有加过滤条件，只是做了链接，把群的信息也查出来而已
    logger.debug(cypher_sql)
    result = graph.run(cypher_sql).data()

    for r in result:
        #logger.debug(r)
        #logger.debug("部门别名为：%s,别名为%s",r['name'],r['other_name'])
        found = False
        if( r['name']==name): found = True
        if (r['other_name']==name): found = True

        if (r['name'] in name): found = True
        if (name in r['name']): found = True

        # 看看部门名字是不是在里面，如 账户|账户部门|资产账户组 ----- 账户
        if r['other_name'] is not None and name in r['other_name']: found = True

        if found: return r
    return None

def find_all_employee():
    cypher_sql = "match(e:employee) return e.name as name"
    return graph.run(cypher_sql).data()


def find_email_by_name(name):
    cypher_sql = "match(e:employee) return e.name as name, e.email as email"
    result = graph.run(cypher_sql).data()
    # logger.debug(result)
    for r in result:
        if name in r['name']: return r['email']
    return None

#按照邮件地址
def find_approvers_info_by_email(approvers):

    result = []
    for approver in approvers:
        result.append(find_qq_wechat_group_by_email(approver))
    return result


#按照邮件地址
def find_all_groups():
    return {'qq_group': ['testbot'], 'wechat_group': ['testbot']}
    cypher_sql = "match(e:qq_group) return e.name as name"
    qq_groups = graph.run(cypher_sql).data()
    qq_list = [x['name'] for x in qq_groups]

    cypher_sql = "match(e:wechat_group) return e.name as name"
    wechat_groups = graph.run(cypher_sql).data()
    wechat_list = [x['name'] for x in wechat_groups]

    return {'qq_group':qq_list,'wechat_group':wechat_list}

if __name__ == "__main__":
    logger.init_4_debug()
    init()
    logger.debug(find_approvers_info_by_email(['xingfeiyin']))
