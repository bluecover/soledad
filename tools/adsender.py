# coding: utf-8

"""
短信群发
"""

import datetime
import requests
from xml.dom.minidom import parseString
from more_itertools import chunked

from solar.utils.storify import storify
from libs.db.store import db
from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.hoard.order import OrderStatus as YixinOrderStatus
from core.models.hoard.zhiwang import ZhiwangOrder

# consts
yimei_cdkey, yimei_pwd = '6SDK-EMY-6666-RDVMN', '206090'
GROUPS = storify(dict(ALL='all_mobile_user',
                      HOARDED='hoarded_user',
                      IDENTIFIED='identified_mobile_user'))
TEXTS = {
    GROUPS.HOARDED: '【好规划】亲爱滴用户，好规划网站升级维护成功。感谢您的耐心等待，送你一张加息券聊表歉意。http://dwz.cn/2pz6hF 退订回TD',
    GROUPS.IDENTIFIED: '【好规划】送你一份感恩礼物，感谢遇到了你。看看你的攒钱助手，有惊喜哦：）http://dwz.cn/2e2Huy 退订回TD'
}


def get_all_user_mobiles():
    sql = 'select alias from account_alias where reg_type=%s'
    rs = db.execute(sql, ACCOUNT_REG_TYPE.MOBILE)
    return [r[0] for r in rs]


def get_all_identified_user_mobiles():
    sql = ('select alias from account_alias where id in '
           '(select id from profile_identity) and reg_type=%s')
    rs = db.execute(sql, ACCOUNT_REG_TYPE.MOBILE)
    return [r[0] for r in rs]


def get_all_hoarded_user_mobiles():
    sql = ('select alias from account_alias,((select user_id from hoard_order '
           'where (status=%s or status=%s)) union (select user_id from hoard_zhiwang_order '
           'where status =%s)) hoarded_users where account_alias.id=hoarded_users.user_id '
           'and account_alias.reg_type=%s order by id')
    params = (YixinOrderStatus.confirmed.value, YixinOrderStatus.exited.value,
              ZhiwangOrder.Status.success.value, ACCOUNT_REG_TYPE.MOBILE)
    rs = db.execute(sql, params)
    return [r[0] for r in rs]


def post_to_yimei(api, data):
    mobiles = data.get('phone', '')
    try:
        r = requests.post(api, data)
        resp_content = r.content.strip()
        print '[Log]:post success: %s\t%s\t%s' % (mobiles, r.status_code, resp_content)
    except Exception as e:
        print '[Log]:post error: %s\t%s' % (mobiles, str(e))
        return

    try:
        xmldoc = parseString(resp_content)
        result = xmldoc.getElementsByTagName('error')[0].childNodes[0].data
        messages = xmldoc.getElementsByTagName('message')[0].childNodes
        if int(result) != 0:
            print '[Log]:responsed error: %s\t(error code:%s)' % (mobiles, result)
        return messages
    except Exception as e:
        print '[Log]:parse msg error:%s\t%s' % (r.content, e)


def query_yimei_balance():
    """Query yimei balance"""
    api = 'http://sdktaows.eucp.b2m.cn:8080/sdkproxy/querybalance.action'
    data = dict(cdkey=yimei_cdkey, password=yimei_pwd)
    messages = post_to_yimei(api, data)
    print 'The balance is %s' % messages[0].data


def send_instant_sms_via_yimei(mobiles, message):
    """Send sms by group via zhangxun client"""
    api = 'http://sdktaows.eucp.b2m.cn:8080/sdkproxy/sendsms.action'
    data = dict(cdkey=yimei_cdkey,
                password=yimei_pwd,
                phone=','.join(mobiles),
                message=message,
                seqid=int(datetime.date.today().strftime('%Y%m%d')),  # 以活动时间作为seqid，实际没什么用
                smspriority=5)
    post_to_yimei(api, data)


def send_reserved_sms_via_yimei(mobiles, message, reserve_time):
    """Send sms by group via zhangxun client"""
    api = 'http://sdktaows.eucp.b2m.cn:8080/sdkproxy/sendtimesms.action'
    data = dict(cdkey=yimei_cdkey,
                password=yimei_pwd,
                phone=','.join(mobiles),
                message=message,
                sendtime=reserve_time.strftime('%Y%m%d%H%M%S'),
                seqid=int(datetime.date.today().strftime('%Y%m%d')),  # 以活动时间作为seqid，实际没什么用
                smspriority=5)
    post_to_yimei(api, data)


def run_sending(groups, reserve_time=None):
    # Start sms sending group by group
    for group_name, group_mobiles in groups:
        sms_text = TEXTS[group_name]
        kind = 'timed(%s)' % reserve_time if reserve_time else 'instant'

        print 'Start sending %s sms to group(%s)(%s total)' % (kind, group_name, len(group_mobiles))
        for seq, mobiles in enumerate(chunked(group_mobiles, 100)):
            phones = [str(m) for m in mobiles if m]
            print '**The %dth group(expect %s, actual %s)' % (seq, len(mobiles), len(phones))
            if not phones:
                continue

            if reserve_time:
                send_reserved_sms_via_yimei(phones, sms_text, reserve_time)
            else:
                send_instant_sms_via_yimei(phones, sms_text)


# Send sms to all target mobile users
if __name__ == '__main__':
    groups = [(GROUPS.HOARDED, get_all_hoarded_user_mobiles())]  # tuple format: (group,mobiles)
    run_sending(groups)
    query_yimei_balance()
