# -*- coding: utf-8 -*-

"""
基金组合Mass工具
"""

from crons.mass.calculator.masscal import compute_net_worth
from envcfg.json.solar import MASS_API_URL, MASS_API_TOKEN
from libs.db.store import db
from libs.cache import mc
from libs.partner.mass.client import MassClient
from core.models.fund.group import Group
from core.models.fund.income import (
    Income, FUND_INCOME_CACHE_KEY, FUND_INCOME_LEASTMORE_CACHE_KEY)
from core.models.fund.incomeuser import FUND_INCOMEUSER_CACHE_KEY


def clear_income_cache(group):
    mc.delete(FUND_INCOME_LEASTMORE_CACHE_KEY % (group.id,))

    ids = Income._get_least_more_ids(group.id, 1000)
    for id in ids:
        mc.delete(FUND_INCOME_CACHE_KEY % (id,))


def clear_income_user_cache_by_date(day):
    sql = 'select id from funcombo_income_user where day=%s'
    params = (day,)
    rs = db.execute(sql, params)
    if rs:
        for user_id in rs[0]:
            mc.delete(FUND_INCOMEUSER_CACHE_KEY % (user_id,))


def clear_income_by_date(day):
    sql = 'delete from funcombo_income where day=%s'
    params = (day,)
    db.execute(sql, params)
    db.commit()


def clear_income_user_by_date(day):
    sql = 'delete from funcombo_income_user where day=%s'
    params = (day,)
    db.execute(sql, params)
    db.commit()


def update_net_worth(group, client):
    sql = ('select id, day from funcombo_income'
           ' where group_id=%s and net_worth<0.000001')
    params = (group.id)
    rs = db.execute(sql, params)
    for x in rs:
        net_worth = compute_net_worth(group, x[1], client)
        sql = 'update funcombo_income set net_worth=%s where id=%s'
        params = (net_worth, x[0])
        db.execute(sql, params)
        db.commit()

if __name__ == '__main__':
    client = MassClient(MASS_API_URL, MASS_API_TOKEN)
    groups = Group.paginate()
    for group in groups:
        update_net_worth(group, client)
        clear_income_cache(group)
