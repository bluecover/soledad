# -*- coding:utf-8 -*-
from libs.logger.rsyslog import rsyslog
from core.models.fund.fundata import Fundata


def compute_net_worth(group, day, client):
    """ 计算某个基金组合某一天的净值 """
    funds = group.get_funds_m2m()  # 只能按当前组合方式计算净值，不能回溯历史
    net_worth = 0.0
    for fund in funds:
        fund_day_data = get_save_fundata(fund.fund_code, day, client)
        if not fund_day_data:
            rsyslog.send(
                '%s day %s fundata not found' % (fund.fund_code, day),
                tag='fund')
            return

        net_worth += fund.rate * float(fund_day_data.net_worth)
    return net_worth


def get_save_fundata(fund_code, day, client):
    """ 得到某只基金某天的净值，若不存在从mass取并入库 """
    fundata = Fundata.get_by_fund_day(fund_code, day)
    if fundata:
        return fundata

    response = client.get_fundata(fund_code, day)
    if response.total_count:
        obj = response.objects[0]
        return Fundata.add(fund_code, obj.day, obj.NRR)


def get_save_stockindexvalue(stockindex, day, client):
    """ 从mass得到股票指数 """
    response = client.get_siv(day, stockindex)
    if response.total_count:
        obj = response.objects[0]
        return obj.close_price


def compute_income(since_value, cur_value):
    """ 计算收益率 """
    return (cur_value / since_value - 1) if (since_value > 0.000001) else 0.0
