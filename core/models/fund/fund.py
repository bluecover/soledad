# -*- coding: utf-8 -*-

'''
基金表
@author mrgaolei
'''

from warnings import warn
from MySQLdb import IntegrityError
from libs.db.store import db
from libs.cache import cache

from core.models.mixin.props import PropsMixin

_FUND_FUND_CACHE_PREFIX = 'fund_fund:'

FUND_FUND_CACHE_PRFIX = _FUND_FUND_CACHE_PREFIX + '%s'


class Fund(PropsMixin):

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def get_db(self):
        return 'funcombo_fund'

    @classmethod
    @cache(FUND_FUND_CACHE_PRFIX % '{code}')
    def get(cls, code):
        rs = db.execute('select code, name '
                        ' from funcombo_fund where code=%s', (code,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, code, name):
        try:
            db.execute('insert into funcombo_fund '
                       '(code, name) '
                       'values(%s, %s)',
                       (code, name))
            db.commit()
            p = cls.get(code)
            return p
        except IntegrityError:
            db.rollback()
            warn('insert funcombo_fund failed')
