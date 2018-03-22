# -*- coding: utf-8 -*-

'''
基金组合收益历史表
@author mrgaolei
'''

from warnings import warn
from MySQLdb import IntegrityError
from datetime import datetime

from libs.db.store import db
from libs.cache import cache, pcache, mc

from core.models.base import EntityModel

_FUND_INCOME_CACHE_PREFIX = 'fund_income:'

FUND_INCOME_CACHE_KEY = _FUND_INCOME_CACHE_PREFIX + '%s'
FUND_INCOME_LEASTMORE_CACHE_KEY = _FUND_INCOME_CACHE_PREFIX + 'leastmore:%s'


class Income(EntityModel):

    def __init__(self, id, group_id, day, net_worth, income, income_stock):
        self.id = str(id)
        self.group_id = group_id
        self.day = day
        self.net_worth = net_worth
        self.income = income
        self.income_stock = income_stock

    @classmethod
    @cache(FUND_INCOME_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, group_id, day, net_worth, income, income_stock '
                        ' from funcombo_income where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, group_id, day, net_worth, income, income_stock):
        from .group import Group
        group = Group.get(group_id)
        if not group:
            warn('group %d not found' % (group_id,))
            return False
        if isinstance(day, datetime):
            day = day.date()
        try:
            id = db.execute('insert into funcombo_income '
                            '(group_id, day, net_worth, income, income_stock) '
                            'values(%s, %s, %s, %s, %s)',
                            (group_id, day, net_worth, income, income_stock))
            if id:
                db.commit()
                mc.delete(FUND_INCOME_LEASTMORE_CACHE_KEY % (group_id,))
                p = cls.get(id)
                return p
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert funcombo_income failed')

    @classmethod
    def get_least(cls, group):
        ids = cls._get_least_more_ids(group.id, 1)
        return cls.get(ids[0]) if ids else None

    @classmethod
    def get_least_more(cls, group, limit=5):
        ids = cls._get_least_more_ids(group.id, limit)
        return cls.gets(ids)

    @classmethod
    @pcache(FUND_INCOME_LEASTMORE_CACHE_KEY % '{group_id}', count=1000)
    def _get_least_more_ids(cls, group_id, limit=5):
        rs = db.execute('select id from funcombo_income where '
                        ' group_id = %s order by day desc limit %s', (group_id, limit))
        ids = [str(id) for (id,) in rs]
        return ids

    @classmethod
    def gets(cls, doc_ids):
        return [cls.get(id) for id in doc_ids]

    @classmethod
    def get_near_day(cls, group_id, days=200):
        ids = cls._get_least_more_ids(group_id, days)
        return cls.gets(ids)

    @classmethod
    def get_by_date(cls, group_id, date):
        sql = ('select id from funcombo_income'
               ' where group_id=%s and day=%s')
        params = (group_id, date)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None
