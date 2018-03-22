#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
获取每天转出订单，并发提示短信
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from core.models.hoard.order import HoardOrder
from core.models.hoard.service import YixinService


def main():
    # 所有可能的封闭期月数
    available_closures = {int(s.frozen_time) for s in YixinService.get_all()}
    # 获取所有可能在今天到期的订单
    for closure in available_closures:
        # 对每种封闭期产品进行状态检查
        end = date.today() - relativedelta(months=closure)
        start = end - timedelta(days=7)
        orders = HoardOrder.get_orders_by_period(start, end, closure)
        for order in orders:
            order.track_for_exited()


if __name__ == '__main__':
    main()
