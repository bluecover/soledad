#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
根据历史净值计算历史收益记录
"""

from datetime import datetime, timedelta

from crons.mass.calculator.masscal import compute_income, compute_stock_income
from envcfg.json.solar import MASS_API_URL, MASS_API_TOKEN
from libs.partner.mass.client import MassClient
from core.models.fund.group import Group
from core.models.fund.income import Income


def main():
    """计算历史收益"""
    client = MassClient(MASS_API_URL, MASS_API_TOKEN)
    groups = Group.paginate()
    for group in groups:
        compute_history_income(group, client)


def compute_history_income(group, client):
    loop_date = group.create_time
    # 循环从基金成立日到今天的每一天
    while loop_date <= datetime.today():
        # 计算每天的收益率
        income_rate_avg = compute_income(group, loop_date, group.create_time, client)
        income_stock_000001 = compute_stock_income(loop_date, group.create_time, '000001', client)
        print loop_date, income_rate_avg, income_stock_000001
        if income_rate_avg and income_stock_000001:
            Income.add(group.id, loop_date, income_rate_avg, income_stock_000001)

        loop_date = loop_date + timedelta(days=1)


if __name__ == '__main__':
    main()
