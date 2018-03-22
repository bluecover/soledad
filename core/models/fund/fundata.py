# -*- coding: utf-8 -*-

'''
基金数据（日期、净值等）表
@author mrgaolei
'''

from warnings import warn
from MySQLdb import IntegrityError
from libs.db.store import db
from libs.cache import cache

from core.models.mixin.props import PropsMixin


_FUND_FUNDATA_CACHE_PRFIX = 'fund_data:'

FUND_FUNDATA_CACHE_PRFIX = _FUND_FUNDATA_CACHE_PRFIX + '%s'
FUND_FUNDDATA_SOMEDAY_DATA_CACHE_PREFIX = (
    _FUND_FUNDATA_CACHE_PRFIX + 'data:%s:%s')


class Fundata(PropsMixin):

    def __init__(self, id, fund_code, day, net_worth):
        self.id = str(id)
        self.fund_code = fund_code
        self.day = day
        self.net_worth = net_worth

    def get_db(self):
        return 'funcombo_data'

    @classmethod
    @cache(FUND_FUNDATA_CACHE_PRFIX % '{id}')
    def get(cls, id):
        rs = db.execute('select id, fund_code, day, net_worth '
                        ' from funcombo_data where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, fund_code, day, net_worth):
        from fund import Fund
        fund = Fund.get(fund_code)
        if not fund:
            warn('fund %d not found' % (fund_code,))
            return False

        try:
            id = db.execute('insert into funcombo_data '
                            '(fund_code, day, net_worth) '
                            'values(%s, %s, %s)',
                            (fund_code, day, net_worth))
            db.commit()
            p = cls.get(id)
            return p
        except IntegrityError:
            db.rollback()
            warn('insert funcombo_data failed')

    @classmethod
    @cache(FUND_FUNDDATA_SOMEDAY_DATA_CACHE_PREFIX % ('{fund_code}', '{day}'))
    def get_by_fund_day(cls, fund_code, day):
        '''
        得到某只基金某一天的数据
        '''
        rs = db.execute('select id, fund_code, day, net_worth '
                        ' from funcombo_data where fund_code=%s and day=%s', (fund_code, day))
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_fundatas(cls, fund, days=7):
        '''
        得到某个基金最近n天的净值
        '''
        rs = db.execute('select id '
                        ' from funcombo_data where fund_code=%s '
                        ' order by day desc limit %s', (fund.code, days))
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_near_data(cls, fund_code, from_day, days=200):
        '''
        取得某只基金从from_day开始最近days天的净值信息
        '''
        rs = db.execute('select id, fund_code, day, net_worth '
                        ' from funcombo_data where fund_code=%s '
                        ' and day >= %s order by day desc limit %s', (from_day, fund_code, days))
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_last_transaction_day(cls, create_time):
        '''
        获取距离某个时间最近的一个交易日
        '''

        sql = 'select max(day) from funcombo_data where day < %s'
        params = (create_time,)
        rs = db.execute(sql, params)
        return rs[0][0] if rs else None
