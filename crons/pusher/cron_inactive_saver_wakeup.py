#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
检查站上注册后三天以上未投资攒钱助手的用户并推送通知
"""


from datetime import date, timedelta

from more_itertools import chunked

from jupiter.workers.pusher import (
    notifications_multicast_push as mq_multicast_push)
from libs.db.store import db
from core.models.hoard.order import OrderStatus
from core.models.hoard.zhiwang import ZhiwangOrder
from core.models.notification.kind import lazy_saver_notification


def get_lazy_savers(last_registration_date):
    sql = ('select id from (select id from account where date(create_time) <= %s) '
           'as act where id not in (select distinct(user_id) from hoard_order '
           'where status=%s union select distinct(user_id) from '
           'hoard_zhiwang_order where status=%s)')
    params = (last_registration_date, OrderStatus.confirmed.value,
              ZhiwangOrder.Status.success.value)
    rs = db.execute(sql, params)

    for r in rs:
        yield str(r[0])


def main():
    """获取注册后三天以上未投资攒钱助手的用户并推送通知"""
    last_registration_date = date.today() - timedelta(days=3)

    for sequence, user_ids in enumerate(chunked(get_lazy_savers(last_registration_date), 1000)):
        multicast_info = ':'.join([lazy_saver_notification.id_, ','.join(user_ids)])
        # 0.5秒间隔缓慢推送
        mq_multicast_push.produce(multicast_info, delay=sequence * 0.5)

if __name__ == '__main__':
    main()
