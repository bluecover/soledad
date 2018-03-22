#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
检查站上礼券到期情况并推送通知用户
"""


from datetime import date, timedelta
from collections import namedtuple

from libs.db.store import db
from core.models.notification import Notification
from core.models.notification.kind import coupon_expiring_notification


CouponExpirationSummary = namedtuple('CouponExpirationSummary', 'user_id expiring_coupon_count')


def get_user_coupon_expiration(expiration_date):
    sql = ('select user_id, count(*) from coupon where '
           'date(expire_time)=%s group by user_id')
    params = (expiration_date, )
    rs = db.execute(sql, params)

    for r in rs:
        yield CouponExpirationSummary(r[0], r[1])


def main():
    """获取在两天后过期的礼券用户情况（用户X有Y张礼券在1天后过期）"""
    expiration_date = date.today() + timedelta(days=1)

    for summary in get_user_coupon_expiration(expiration_date):
        # 添加消息通知
        Notification.create(
            summary.user_id, coupon_expiring_notification,
            dict(expiring_coupon_count=summary.expiring_coupon_count)
        )


if __name__ == '__main__':
    main()
