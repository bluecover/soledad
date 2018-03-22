# coding:utf-8

from collections import namedtuple
from decimal import Decimal
from enum import Enum

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel

ProfitHikeItem = namedtuple('ProfitHikeItem', ['kind', 'annual_rate', 'deduction_amount'])
ProfitHikeItem.__new__.__defaults__ = (None, Decimal('0'), Decimal('0'))


class XMOrderProfitHike(EntityModel):

    table_name = 'hoard_xm_profit_hike'
    cache_key = 'xinmi:order:profit_hike:{id_}:v1'
    cache_key_by_order = 'xinmi:order:profit_hike:order_id:{order_id}:v1'
    cache_key_by_user = 'xinmi:order:profit_hike:user_id:{user_id}:v1'

    class Status(Enum):
        promised = 'P'
        occupied = 'O'
        achieved = 'A'

    Status.promised.sequence = 0
    Status.occupied.sequence = 1
    Status.achieved.sequence = 2

    class Kind(Enum):
        replenish = 'RP'
        newcomer = 'NC'
        coupon_rate = 'CR'
        coupon_deduction = 'CD'
        firewood_deduction = 'RD'

    Kind.replenish.label = u'特权加息福利'
    Kind.newcomer.label = u'新手加息福利'
    Kind.coupon_rate.label = u'礼券加息福利'
    Kind.coupon_deduction.label = u'礼券抵扣福利'
    Kind.firewood_deduction.label = u'红包抵扣福利'

    def __init__(self, id_, user_id, order_id, kind, status, annual_rate_offset, deduct_amount):
        self.id_ = id_
        self.user_id = str(user_id)
        self.order_id = str(order_id)
        self._kind = kind
        self._status = status
        self.annual_rate_offset = annual_rate_offset
        self.deduct_amount = deduct_amount

    @property
    def kind(self):
        return self.Kind(self._kind)

    @property
    def display_text(self):
        if self.kind is self.Kind.newcomer:
            return self.order.wrapped_product.display_privilege

        rate = self.annual_rate_offset
        deduction = self.deduct_amount
        return u' | '.join([s for s in [u'年化收益率 +%.2f%%' % rate if rate else 0.0,
                                        u'抵扣 -%.2f元' % deduction if deduction else 0.0] if s])

    @property
    def status(self):
        return self.Status(self._status)

    @cached_property
    def order(self):
        from .order import XMOrder
        return XMOrder.get(self.order_id)

    @classmethod
    def add(cls, user_id, order_id, kind, annual_rate_offset, deduct_amount):
        assert isinstance(kind, cls.Kind)
        assert isinstance(annual_rate_offset, Decimal)
        assert isinstance(deduct_amount, Decimal)

        sql = ('insert into {0} (user_id, order_id, kind, status, annual_rate_offset, '
               'deduct_amount) values (%s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (user_id, order_id, kind.value, cls.Status.promised.value,
                  annual_rate_offset, deduct_amount)
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache_by_user(user_id=user_id)
        cls.clear_cache_by_order(order_id=order_id)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, order_id, kind, status, annual_rate_offset, '
               'deduct_amount from {0.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_order)
    def get_ids_by_order(cls, order_id):
        sql = 'select id from {0.table_name} where order_id=%s'.format(cls)
        params = (order_id, )
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_order(cls, order_id):
        id_list = cls.get_ids_by_order(order_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_ids_by_user(user_id)
        return cls.get_multi(id_list)

    @classmethod
    @cache(cache_key_by_user)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {0.table_name} where user_id=%s'.format(cls)
        params = (user_id, )
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    def occupy(self):
        """冻结用户优惠"""
        if self.status not in (self.Status.promised, self.Status.occupied):
            raise ValueError('current status is not promised')

        if self.kind is self.Kind.newcomer:
            if any(
                p for p in self.get_multi_by_user(self.user_id)
                if (p.status.sequence > self.Status.promised.sequence and
                    p.kind is self.Kind.newcomer)
            ):
                raise ProfitHikeLockedError()

        self._update_status(self.Status.occupied)

    def achieve(self):
        """确认用户已使用优惠"""
        from .order import XMOrder
        self.clear_cached_properties()

        if self.status is not self.Status.occupied:
            raise ValueError('current status is not occupied')
        if self.order.status is not XMOrder.Status.success:
            raise ValueError('order status is mismatched to make it achived')
        self._update_status(self.Status.achieved)

    def renew(self):
        """只有当支付失败时才将优惠资格返还"""
        from .order import XMOrder
        self.clear_cached_properties()

        if self.status is not self.Status.occupied:
            raise ValueError('current status is not occupied')
        if self.order.status not in (XMOrder.Status.unpaid, XMOrder.Status.failure):
            raise ValueError('order status is mismatched to make it renewed')
        self._update_status(self.Status.promised)

    def _update_status(self, new_status):
        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (new_status.value, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self.clear_cache_by_user(self.user_id)
        self.clear_cache_by_order(self.order_id)

    def clear_cached_properties(self):
        self.__dict__.pop('order', None)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_order(cls, order_id):
        mc.delete(cls.cache_key_by_order.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_key_by_user.format(**locals()))


class ProfitHikeLockedError(Exception):

    def __unicode__(self):
        return u'抱歉，请处理尚未完成支付的订单'


class ProfitHikeMixin(object):
    """为订单提供临时加息数据."""

    def has_profit_hike(self):
        """是否有优惠活动"""
        return False

    def get_profit_hike(self, days=None):
        """获取当前产品的加息率."""
        return Decimal(0)
