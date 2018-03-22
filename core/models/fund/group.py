# -*- coding: utf-8 -*-

'''
组合推荐
'''


from datetime import datetime

from warnings import warn
from MySQLdb import IntegrityError
from libs.db.store import db
from libs.cache import cache, pcache, mc
from decimal import Decimal
from libs.logger.rsyslog import rsyslog
from core.models.mixin.props import PropsMixin

from .income import Income
from .fundata import Fundata
from .group_fund_m2m import GroupFundRelationship

_FUND_GROUP_CACHE_PREFIX = 'fund_group:'

FUND_GROUP_CACHE_KEY = _FUND_GROUP_CACHE_PREFIX + '%s'
FUND_GROUP_IDS_CACHE_KEY = _FUND_GROUP_CACHE_PREFIX + ':ids'


class Group(PropsMixin):

    def __init__(self, id, subject, subtitle, subtitle2, description,
                 create_time, update_time, reason, highlight, reason_update, related):
        self.id = str(id)
        self.subject = subject
        self.subtitle = subtitle
        self.subtitle2 = subtitle2
        self.description = description
        self.create_time = create_time
        self.update_time = update_time
        self.reason = reason
        self.highlight = highlight
        self.reason_update = reason_update
        self.related = related

    def get_db(self):
        return 'funcombo_group'

    @classmethod
    def add(cls, subject, subtitle, subtitle2, description, create_time,
            update_time, reason, highlight, reason_update, related):
        params = (
            subject,
            subtitle,
            subtitle2,
            description,
            create_time,
            update_time,
            reason,
            highlight,
            reason_update,
            related)
        try:
            id = db.execute('insert into funcombo_group '
                            '(subject, subtitle, subtitle2, description, '
                            ' create_time, update_time, reason, highlight, reason_update, related) '
                            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', params)
            if id:
                db.commit()
                mc.delete(FUND_GROUP_IDS_CACHE_KEY)
                p = cls.get(id)
                return p
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert funcombo_group failed')

    @classmethod
    @cache(FUND_GROUP_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, subject, subtitle, subtitle2, description, '
                        ' create_time, update_time, reason, highlight, reason_update, related '
                        ' from funcombo_group '
                        'where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    def update(self, subject, subtitle, subtitle2, description,
               reason, highlight, reason_update, related):

        params = (
            subject,
            subtitle,
            subtitle2,
            description,
            reason,
            highlight,
            reason_update,
            related,
            datetime.now(),
            self.id)
        try:
            db.execute('update funcombo_group set '
                       'subject = %s,'
                       'subtitle = %s,'
                       'subtitle2 = %s,'
                       'description = %s,'
                       'reason = %s,'
                       'highlight = %s,'
                       'reason_update = %s,'
                       'related = %s,'
                       'update_time = %s '
                       'where id = %s', params)
            db.commit()
            mc.delete(FUND_GROUP_CACHE_KEY % (self.id,))
            return self.get(self.id)
        except IntegrityError:
            db.rollback()
            warn('update funcombo_group failed')

    @classmethod
    @pcache(FUND_GROUP_IDS_CACHE_KEY)
    def _get_all_ids(cls, start=0, limit=20):
        sql = 'select id from funcombo_group order by id desc limit %s,%s'
        rs = db.execute(sql, (start, limit))
        ids = [str(id) for (id,) in rs]
        return ids

    @classmethod
    def paginate(cls, start=0, limit=20):
        ids = cls._get_all_ids(start=start, limit=limit)
        return [cls.get(id) for id in ids]

    def get_funds_m2m(self):
        return GroupFundRelationship.get_fund_by_group(self.id)

    def add_fund(self, fund, reason, rate=0.2):
        return GroupFundRelationship.add_fund(self, fund, reason, rate)

    def is_liked(self, user_id):
        from .subscription import Subscription
        return Subscription.is_like(self.id, user_id)

    @property
    def total_income(self):
        '''
        组合成立以来总收益（self.create_time）
        '''
        return Income.get_least(self).income

    @property
    def yesterday_income(self):
        '''
        昨日收益
        '''
        incomes = Income.get_least_more(self, 2)
        income_cur = incomes[0].income
        income_far = incomes[-1].income
        return (income_cur - income_far) / (1 + income_far)

    @property
    def last_week_income(self):
        '''
        近一周收益（行业内规定一周6天）
        '''
        incomes = Income.get_least_more(self, 6)
        income_cur = incomes[0].income
        income_far = incomes[-1].income
        return (income_cur - income_far) / (1 + income_far)
        # return self.get_income(datetime.today()+timedelta(weeks=-1),
        #                        datetime.today()+timedelta(days=-1))

    @property
    def last_month_income(self):
        '''
        近一月收益（行业规定一个月21天）
        '''
        incomes = Income.get_least_more(self, 21)
        income_cur = incomes[0].income
        income_far = incomes[-1].income
        return (income_cur - income_far) / (1 + income_far)
        # return self.get_income(datetime.today()+timedelta(days=-30),
        #                        datetime.today()+timedelta(days=-1))

    @property
    def last_3month_income(self):
        '''
        近三月收益（行业规定一个月61天）
        '''
        incomes = Income.get_least_more(self, 61)
        income_cur = incomes[0].income
        income_far = incomes[-1].income
        return (income_cur - income_far) / (1 + income_far)
        # return self.get_income(datetime.today()+timedelta(days=-90),
        #                        datetime.today()+timedelta(days=-1))

    def get_income(self, from_day, to_day):
        '''
        以from_day对比to_day日收益情况
        '''
        funds = self.get_funds_m2m()
        income = 0
        for fund in funds:
            # 基金成立日净值
            create_time_data = Fundata.get_by_fund_day(fund.fund.code, datetime.date(from_day))
            if not create_time_data:
                rsyslog.send(
                    'not found create_time fundata %s %s' % (fund.fund.code, from_day),
                    tag='fund')
                return 0
            # 当日净值
            today_data = Fundata.get_by_fund_day(fund.fund.code, datetime.date(to_day))
            if not today_data:
                rsyslog.send(
                    'not found today fundata %s %s' % (fund.fund.code, to_day),
                    tag='fund')
                return 0
            income += (today_data.net_worth / create_time_data.net_worth - 1) * Decimal(fund.rate)
        return income
