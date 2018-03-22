# -*- coding: utf-8 -*-

"""
基金组合订阅刷新
"""

from core.models.fund.fundata import Fundata
from core.models.fund.subscription import Subscription


def update_fund_subscription_start_date():
    likes = Subscription.all()
    for like in likes:
        if not like.start_date:
            like.start_date = Fundata.get_last_transaction_day(
                like.create_time.date())

if __name__ == '__main__':
    update_fund_subscription_start_date()
