#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
从 mass 同步基金数据
"""

import sys
import getopt
from datetime import datetime, date, timedelta

from core.models.fund.group import Group
from core.models.fund.income import Income
from core.models.fund.incomeuser import IncomeUser
from core.models.fund.subscription import Subscription
from core.models.fund.fundata import Fundata
from libs.partner.mass.client import MassClient

from crons.mass.calculator.masscal import compute_net_worth,\
    compute_income, get_save_stockindexvalue

try:
    from envcfg.json.solar import MASS_API_URL, MASS_API_TOKEN
except ImportError:
    MASS_API_URL = None
    MASS_API_TOKEN = None


def main(cur_day):
    """sync data from mass."""

    if not MASS_API_URL or not MASS_API_TOKEN:
        return

    stockindex = '000001'
    client = MassClient(MASS_API_URL, MASS_API_TOKEN)
    group_net_worth = {}

    # 获取当天股票指数
    cur_stock_value = get_save_stockindexvalue(stockindex, cur_day, client)
    if not cur_stock_value:
        return

    groups = Group.paginate()
    for group in groups:
        since_day = group.create_time.date()

        # 计算当天的基金组合净值
        cur_net_worth = compute_net_worth(group, cur_day, client)
        if cur_net_worth is not None:
            # 在内存中缓存当天基金组合净值，用于后续用户关注收益率计算
            group_net_worth[group.id] = cur_net_worth
        else:
            continue

        income_rate = 0.0
        income_stock = 0.0
        if since_day < cur_day:
            # 计算基金组合收益率
            his_income = Income.get_by_date(group.id, since_day)
            if his_income is not None:
                income_rate = compute_income(
                    his_income.net_worth, cur_net_worth)

            # 计算股票指数收益率
            his_stock_value = get_save_stockindexvalue(
                stockindex, since_day, client)
            if his_stock_value is not None:
                income_stock = compute_income(his_stock_value, cur_stock_value)

        # 保存当天基金组合结果
        Income.add(group.id, cur_day, cur_net_worth, income_rate, income_stock)

    likes = Subscription.all()
    for like in likes:
        group = Group.get(like.group_id)
        if not like.start_date:
            # 起始日期为空，说明还没计算过该用户的收益率，需要获取到关注时刻之前最近的一个交易日作为起始日期
            like.start_date = Fundata.get_last_transaction_day(
                like.create_time.date())

        # 计算用户关注的基金组合收益率
        user_income_rate = 0.0
        his_user_income = Income.get_by_date(group.id, like.start_date)
        if his_user_income is not None:
            user_income_rate = compute_income(
                his_user_income.net_worth, group_net_worth[group.id])

        # 保存当天用户关注基金组合结果
        IncomeUser.add(
            like.group_id, like.user_id, cur_day, user_income_rate)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 't:')
    except getopt.GetoptError, err:
        sys.exit(0)

    cur_day = date.today() + timedelta(days=-1)
    for op, value in opts:
        if op == '-t':
            cur_day = datetime.strptime(value, '%Y-%m-%d').date()

    main(cur_day)
