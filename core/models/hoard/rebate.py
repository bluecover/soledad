# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from operator import attrgetter
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from solar.utils.storify import storify

from core.models.hoard.profile import HoardProfile
from core.models.hoard.order import HoardOrder, OrderStatus
from core.models.hoard.errors import CreateUserRebateError
from core.models.profile.bankcard import BankCard
from core.models.utils import round_half_up


SETTLED = 1
UNSETTLED = 0
DELETED = 1

REBATE_TYPE = storify(dict(
    RESERVE=1,
    TW=2,
    POOR=3,
    SOHU=4,
    MLR_CLOSURE_3=5,
    MLR_CLOSURE_6=6,
    MLR_CLOSURE_12=7,
    MLR_CLOSURE_9=8,
    MLR_ILLUMINATOR_3_15=9,
    MLR_ILLUMINATOR_9_15=10,
    MLR_ILLUMINATOR_12_15=11,
    PROMOTION=20,
    INVITE_REGISTER=30,  # 邀请发送方
    INVITE_INVEST_SENDER=31,  # 邀请投资——发送方
    INVITE_INVEST_ACCEPT=32,  # 邀请投资——接受方
))

REBATE_TYPE_NAME_MAP = {
    REBATE_TYPE.RESERVE: u'预约福利',
    REBATE_TYPE.TW: u'双十二福利',
    REBATE_TYPE.POOR: u'比穷福利',
    REBATE_TYPE.SOHU: u'搜狐福利',
    REBATE_TYPE.MLR_CLOSURE_3: u'三月期礼券福利',
    REBATE_TYPE.MLR_CLOSURE_6: u'六月期礼券福利',
    REBATE_TYPE.MLR_CLOSURE_9: u'九月期礼券福利',
    REBATE_TYPE.MLR_CLOSURE_12: u'十二月期礼券福利',
    REBATE_TYPE.MLR_ILLUMINATOR_3_15: u'三月期普照礼券福利',
    REBATE_TYPE.MLR_ILLUMINATOR_9_15: u'九月期普照礼券福利',
    REBATE_TYPE.MLR_ILLUMINATOR_12_15: u'十二月期普照礼券福利',
    REBATE_TYPE.PROMOTION: u'破亿福利',
    REBATE_TYPE.INVITE_REGISTER: u'邀请注册福利',
    REBATE_TYPE.INVITE_INVEST_SENDER: u'邀请新人福利',
    REBATE_TYPE.INVITE_INVEST_ACCEPT: u'邀请投资福利',
}


class HoardRebate(object):

    table_name = 'hoard_rebate'
    cache_key = 'hoard:rebate:{id_}:v3'
    user_rebates_cache_key = 'hoard:rebate:user:{user_id}:v3'

    def __init__(self, id, user_id, withdraw_id, order_pk, order_amount,
                 rebate_amount, creation_time, settled_time, type,
                 is_settled, is_deleted, reason):
        self.id = str(id)
        self.user_id = str(user_id)
        self.withdraw_id = withdraw_id
        self.order_pk = str(order_pk) if order_pk else 0
        self.order_amount = order_amount
        self.rebate_amount = rebate_amount
        self.creation_time = creation_time
        self.settled_time = settled_time
        self.type = type
        self.is_settled = is_settled
        self._delete = is_deleted
        self.reason = reason

    def __repr__(self):
        return '<HoardRebate id=%s, order_id=%s, status=%s, delete=%s>' % (
               self.id, self.order_pk, self.is_settled, self._delete)

    @property
    def id_(self):
        return self.id

    @cached_property
    def profile(self):
        return HoardProfile.get(self.user_id)

    @cached_property
    def order(self):
        return HoardOrder.get(self.order_pk)

    @property
    def order_id(self):
        return self.order.id_  # for backward compatibility

    @property
    def bank_card(self):
        return BankCard.get(self.order.bankcard_id) if self.order else ''

    @property
    def is_deleted(self):
        return self._delete == DELETED

    @classmethod
    def add(cls, user_id, order, order_amount, rebate_amount, type_=0):
        """Create an unsettled rebate."""

        if not order.is_success or order.status is OrderStatus.paid:
            raise ValueError('order %r has not been confirmed' % order.id_)

        # the "order_id" and "type" field is deprecated and duplicated
        if cls.get_by_order_id(order.order_id, type_):
            raise ValueError('Dup rebates for order %s' % order.id)

        return cls._add(user_id, rebate_amount, type_, order.order_id, order.id_, order_amount)

    @classmethod
    def add_by_activity(cls, user_id, rebate_amount, activity_id=0, type_=0):
        """Create unsettled rebate by activity"""
        return cls._add(user_id, rebate_amount, type_=type_, activity_id=activity_id)

    @classmethod
    def _add(cls, user_id, rebate_amount, type_=0, order_id=0, order_pk=0, order_amount=0,
             activity_id=0):
        """Create an unsettled rebate."""
        sql = ('insert into {.table_name} (user_id, order_id, order_pk,'
               ' order_amount, rebate_amount, type, creation_time, activity_id) '
               'value (%s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (user_id, order_id, order_pk, order_amount,
                  rebate_amount, type_, datetime.now(), activity_id)

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(user_id, id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, withdraw_id, order_pk, order_amount, '
               'rebate_amount,creation_time, settled_time, type, is_settled, '
               'is_deleted, reason from {.table_name} where id=%s').format(cls)
        params = (id_,)

        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])
        return

    @classmethod
    def gets_by_withdraw_id(cls, withdraw_id):
        sql = ('select id from {.table_name} '
               'where withdraw_id = %s').format(cls)
        params = (withdraw_id,)
        rs = db.execute(sql, params)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_by_order_pk(cls, order_pk, kind=None):
        sql = 'select id from {.table_name} where order_pk=%s'.format(cls)
        params = (order_pk,)
        rs = db.execute(sql, params)
        if rs:
            rebates = [cls.get(r[0]) for r in rs]
            if kind:
                kind_rebates = [r for r in rebates if r.type == kind]
                if len(kind_rebates) == 0:
                    return
                elif len(kind_rebates) > 1:
                    raise ValueError('Dup rebates for order %s' % order_pk)
                else:
                    return kind_rebates[0]
            else:
                return rebates

    @classmethod
    def get_by_order_id(cls, order_id, kind=None):
        sql = 'select id from {.table_name} where order_id=%s'.format(cls)
        params = (order_id,)
        rs = db.execute(sql, params)
        if rs:
            rebates = [cls.get(r[0]) for r in rs]
            if kind:
                kind_rebates = [r for r in rebates if r.type == kind]
                if len(kind_rebates) == 0:
                    return
                elif len(kind_rebates) > 1:
                    raise ValueError('Dup rebates for order %s' % order_id)
                else:
                    return kind_rebates[0]
            else:
                return rebates

    @classmethod
    def get_all(cls):
        sql = 'select id from {.table_name}'.format(cls)
        rs = db.execute(sql)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_by_settled_status(cls, is_settled=SETTLED):
        sql = 'select id from {.table_name} where is_settled = %s'.format(cls)
        params = (is_settled,)
        rs = db.execute(sql, params)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_by_date(cls, date, is_settled=None):
        # 1 for settled orders
        # 0 for unsettled orders
        # None for all orders
        sql = ('select id, is_settled from {.table_name} '
               'where DATE(creation_time) = %s').format(cls)
        params = (date,)
        rs = db.execute(sql, params)
        if is_settled is None:
            return [cls.get(r[0]) for r in rs]
        else:
            return [cls.get(r[0]) for r in rs if is_settled == r[-1]]

    @classmethod
    def get_by_user(cls, user_id, is_settled=None):
        rebates = cls._get_by_user(user_id)
        if is_settled is not None:
            rebates = [r for r in rebates if r.is_settled == is_settled]
        return rebates

    @classmethod
    @cache(user_rebates_cache_key)
    def _get_by_user(cls, user_id):
        sql = ('select id from {.table_name} where user_id = %s').format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_totals_by_user(cls, user_id):
        sql = ('select sum(rebate_amount) from {.table_name} '
               'where user_id = %s').format(cls)
        params = (user_id,)
        r = db.execute(sql, params)
        if r:
            return r[0][0] or 0
        return 0

    @classmethod
    def get_totals_by_user_and_type(cls, user_id, type):
        sql = ('select sum(rebate_amount) from {.table_name} '
               'where user_id = %s and type = %s').format(cls)
        params = (user_id, type)
        r = db.execute(sql, params)
        if r:
            return r[0][0] or 0
        return 0

    @classmethod
    def get_totals_of_rebate_amount(cls, user_id, type=None, is_settled=None):
        rebates = cls.get_by_user(user_id)
        if type is not None:
            rebates = [r for r in rebates if r.type in type]
        if is_settled is not None:
            rebates = [r for r in rebates if not r.is_withdrawing]
            rebates = [r for r in rebates if r.is_settled == is_settled]
        amount = float(round_half_up(sum(r.rebate_amount for r in rebates), 2))
        return amount

    @classmethod
    def get_cashables_by_user(cls, user_id):
        rebates = cls.get_by_user(user_id, UNSETTLED)
        rebates = [r for r in rebates if not r.is_withdrawing]
        amount = float(round_half_up(sum(r.rebate_amount for r in rebates), 2))
        return rebates, amount

    @classmethod
    def get_display(cls, rebates):
        _rebates = dict()
        for rebate in sorted(rebates, key=attrgetter('type')):
            name = REBATE_TYPE_NAME_MAP.get(rebate.type)
            name = u'礼券福利' if u'礼券福利' in name else name
            _rebates[name] = '%s 元' % round_half_up(rebate.rebate_amount, 2)
        return _rebates

    def commit(self, status=SETTLED):
        """
        Update is_settled value to para status_status.
        """

        sql = ('update {.table_name} set is_settled=%s, settled_time=%s '
               'where id = %s').format(self)
        params = (status, datetime.now(), self.id)
        db.execute(sql, params)
        db.commit()
        rsyslog.send('commit\t' + self.id, tag='hoard_rebate')
        # update is_settled value
        self.is_settled = status
        self.clear_cache(self.user_id, self.id)

    @classmethod
    def commit_by_ids(cls, ids, status=SETTLED):
        """
        Update all ids value.
        """

        ids_groups = [ids[x:x + 50] for x in xrange(0, len(ids), 50)]

        for ids_group in ids_groups:
            for id_ in ids_group:
                sql = ('update {.table_name} set is_settled=%s, '
                       'settled_time=%s where id=%s').format(cls)
                params = (status, datetime.now(), id_)
                db.execute(sql, params)
            db.commit()
            rsyslog.send('commits_by_id\t' + ','.join(str(i) for i in ids),
                         tag='hoard_rebate')

        for id_ in ids:
            rebate = cls.get(id_)
            cls.clear_cache(rebate.user_id, id_)

        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, user_id, rebate_id):
        mc.delete(cls.user_rebates_cache_key.format(user_id=user_id))
        mc.delete(cls.cache_key.format(id_=rebate_id))

    def delete(self, reason=None):
        reason = reason or 'deleted by system'
        reason = '%s - %s' % (datetime.now(), reason)
        sql = ('update {.table_name} set is_deleted = %s, '
               'reason = %s where id=%s').format(self)
        params = (DELETED, reason, self.id)
        db.execute(sql, params)
        db.commit()
        rsyslog.send('rebate delete\t%s\t%s' % (self.id, reason),
                     tag='hoard_rebate')
        self.clear_cache(self.user_id, self.id)


class RebateManager(object):

    REBATE_RULE = []

    @classmethod
    def has_rebate(cls, user_id):
        for r_type, r_cls in cls.REBATE_RULE:
            ur = r_cls.get_by_user(user_id)
            if not ur.has_reserved():
                continue
            if not ur.amount:
                continue

            # 获得已返现的总和
            total_rebate_amount = HoardRebate.get_totals_by_user_and_type(
                user_id, r_type)

            # 如果已经返现大于max_rebate，则不进入返现表
            if total_rebate_amount >= Decimal(ur.amount):
                continue
            return r_type, r_cls

    @classmethod
    def create_rebate(cls, order):
        raise CreateUserRebateError()

    @classmethod
    def _max_ratio_rebate_rule(cls, order, rebate_type, max_rebate,
                               rebate_ratio):
        # 获得已返现的总和
        total_rebate_amount = HoardRebate.get_totals_by_user_and_type(
            order.user_id, rebate_type)

        # 获得返现的价格
        target_rebate_amount = int(
            order.order_amount * Decimal(rebate_ratio))

        rebate_amount = target_rebate_amount

        # 如果返现小于max_rebate
        if total_rebate_amount < Decimal(max_rebate):
            if total_rebate_amount + rebate_amount > Decimal(max_rebate):
                rebate_amount = Decimal(max_rebate) - total_rebate_amount
        return rebate_amount
