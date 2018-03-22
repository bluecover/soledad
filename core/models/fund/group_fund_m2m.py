# -*- coding: utf-8 -*-

'''
基金组合 基金 多对多映射表
@author mrgaolei
'''

from warnings import warn
from MySQLdb import IntegrityError
from werkzeug.utils import cached_property
from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin

from .fund import Fund

_FUND_GFM2M_CACHE_PREFIX = 'fund_GFM2M:'

FUND_GFM2M_CACHE_PRFIX = _FUND_GFM2M_CACHE_PREFIX + '%s'
FUND_GFM2M_GROUP_CACHE_PRFIX = _FUND_GFM2M_CACHE_PREFIX + 'group:%s'


class GroupFundRelationship(PropsMixin):

    def __init__(self, id, group_id, fund_code, rate, reason):
        self.id = id
        self.group_id = group_id
        self.fund_code = fund_code
        self.rate = rate
        self.reason = reason

    @classmethod
    @cache(FUND_GFM2M_CACHE_PRFIX % '{id}')
    def get(cls, id):
        rs = db.execute('select id, group_id, fund_code, rate, reason '
                        ' from funcombo_group_fund '
                        'where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    def update(self, rate, reason):
        try:
            db.execute('update funcombo_group_fund set '
                       'rate = %s,'
                       'reason = %s,'
                       'where id = %s', (rate,
                                         reason,
                                         self.id))
            db.commit()
            mc.delete(FUND_GFM2M_CACHE_PRFIX % (self.id,))
            return self.get(self.id)
        except IntegrityError:
            db.rollback()
            warn('update funcombo_group_fund_m2m failed')

    @classmethod
    @cache(FUND_GFM2M_GROUP_CACHE_PRFIX % '{group_id}')
    def get_fund_by_group(cls, group_id):
        rs = db.execute('select id, group_id, fund_code, rate, reason '
                        ' from funcombo_group_fund where group_id = %s',
                        (group_id,))
        return [cls(*r) for r in rs]

    @cached_property
    def group(self):
        from .group import Group
        return Group.get(self.group_id)

    @cached_property
    def fund(self):
        return Fund.get(self.fund_code)

    @classmethod
    def add_fund(cls, group, fund, reason, rate=0.2):
        try:
            id = db.execute('insert into funcombo_group_fund '
                            '(group_id, fund_code, rate, reason)'
                            'values(%s, %s, %s, %s)',
                            (group.id, fund.code, rate, reason))
            if id:
                db.commit()
                mc.delete(FUND_GFM2M_GROUP_CACHE_PRFIX % (group.id,))
                p = cls.get(id)
                return p
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('add fund to group failed')

    @classmethod
    def remove_fund(cls, group, fund):
        try:
            db.execute('delete from funcombo_group_fund '
                       ' where group_id = %s and fund_code = %S',
                       (group.id, fund.code))
            db.commit()
            mc.delete(FUND_GFM2M_GROUP_CACHE_PRFIX % (group.id,))
            return True
        except IntegrityError:
            db.rollback()
            warn('remove fund from group failed')
            return False

    def clear_cache(self):
        mc.delete(FUND_GFM2M_CACHE_PRFIX % (self.id,))
