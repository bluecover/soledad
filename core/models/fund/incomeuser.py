# -*- coding: utf-8 -*-

'''
基金组合收益用户历史表
@author mrgaolei
'''

from warnings import warn
from libs.cache import cache, mc
from MySQLdb import IntegrityError
from libs.db.store import db

from core.models.mixin.props import PropsMixin

_FUND_INCOMEUSER_CACHE_PREFIX = 'fund_incomeuser:'
FUND_INCOMEUSER_CACHE_KEY = _FUND_INCOMEUSER_CACHE_PREFIX + '%s'


class IncomeUser(PropsMixin):

    def __init__(self, id, group_id, user_id, day, income):
        self.id = str(id)
        self.group_id = group_id
        self.user_id = user_id
        self.day = day
        self.income = income

    def get_db(self):
        return 'funcombo_income_user'

    @classmethod
    @cache(FUND_INCOMEUSER_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, group_id, user_id, day, income '
                        ' from funcombo_income_user where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, group_id, user_id, day, income):
        from .group import Group
        group = Group.get(group_id)
        if not group:
            warn('group %d not found' % (group_id,))
            return False
        try:
            id = db.execute('insert into funcombo_income_user '
                            '(group_id, user_id, day, income) '
                            'values(%s, %s, %s, %s)',
                            (group_id, user_id, day, income))
            db.commit()
            mc.delete(FUND_INCOMEUSER_CACHE_KEY % (id,))
            p = cls.get(id)
            return p
        except IntegrityError:
            db.rollback()
            warn('insert funcombo_income_user failed')

    @classmethod
    def get_near_day(cls, group_id, user_id, days=200):
        rs = db.execute('select id, group_id, user_id, day, income '
                        ' from funcombo_income_user where group_id = %s '
                        ' and user_id = %s'
                        ' order by day desc limit %s', (group_id, user_id, days))
        return [cls.get(r[0]) for r in rs]
