#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
生日礼券发放
"""

from datetime import date

from libs.db.store import db
from core.models.user.account import Account
from core.models.sms import ShortMessage
from core.models.sms.kind import birthday_package_remind_sms
from core.models.welfare.package.package import distribute_welfare_gift
from core.models.welfare.package.kind import happy_birthday_package


def get_users_by_birthday(date_str):
    sql = 'select id from profile_identity where substring(person_ricn, 11, 4)=%s'
    rs = db.execute(sql, date_str)
    for r in rs:
        yield Account.get(r[0])


def main():
    # 获取所有出生在当前日期的用户
    for user in get_users_by_birthday(date.today().strftime('%m%d')):
        distribute_welfare_gift(user, happy_birthday_package)

        # 向用户手机发送提醒短信
        if user.has_mobile():
            sms = ShortMessage.create(user.mobile, birthday_package_remind_sms)
            sms.send_async()


if __name__ == '__main__':
    main()
