# coding: utf-8

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.account import Account
from core.models.utils import round_half_up
from core.models.base import EntityModel
from core.models.hoard.providers import ProductProvider


class FirewoodBurning(EntityModel):
    """抵扣金账户消费记录

    当用户购买攒钱产品或基金产品等时，可使用抵扣金抵扣一部分订单金额，
    消费记录在最终订单支付提交时将被创建，在支付失败后被删除。
    """

    class Kind(Enum):
        withdraw = 'WD'  # 返现金额被提现使用
        deduction = 'DC'  # 返现金额在购物时被抵扣使用

    Kind.withdraw.label = u'系统提现'
    Kind.deduction.label = u'下单抵扣'

    class Status(Enum):
        ready = 'R'
        placed = 'P'
        burned = 'B'
        canceled = 'C'

    table_name = 'firewood_burning'
    cache_key = 'firewood:burning:{id_}:v5'
    cache_key_by_user_id = 'firewood:burning:user:{user_id}:v5'
    cache_key_by_provider_order = 'firewood:burning:provider:{provider_id}:order:{order_id}:v5'

    def __init__(self, id_, user_id, amount, kind, status, provider_id, order_id,
                 remote_transaction_id, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        # 消费金额
        self.amount = amount
        # 消费类型
        self._kind = kind
        # 抵扣金使用状态
        self._status = status
        # 消费产品合作方ID
        self.provider_id = provider_id
        # 消费订单ID
        self.order_id = order_id
        # 抵扣金服务端交易ID
        self._remote_transaction_id = remote_transaction_id
        self.creation_time = creation_time

    def __str__(self):
        return '<FireWoodBurning %s>' % self.id_

    @cached_property
    def kind(self):
        return self.Kind(self._kind)

    @property
    def display_remark(self):
        return self.kind.label

    @property
    def display_amount(self):
        return u'-%s元' % round_half_up(self.amount, 2)

    @property
    def simplified_display_amount(self):
        return u'-%s' % round_half_up(self.amount, 2)

    @property
    def signed_amount(self):
        return -self.amount

    @property
    def remote_transaction_id(self):
        if self._remote_transaction_id:
            return UUID(self._remote_transaction_id)

    @property
    def status(self):
        return self.Status(self._status)

    @cached_property
    def provider(self):
        return ProductProvider.get(self.provider_id)

    @classmethod
    def add(cls, user, amount, kind, provider, order_id):
        """创建抵扣金预消费记录"""
        assert isinstance(user, Account)
        assert isinstance(amount, Decimal)
        assert isinstance(kind, cls.Kind)
        assert isinstance(provider, ProductProvider)

        # TODO: validation of provider and related order entity should be done later

        sql = ('insert into {.table_name} (user_id, amount, kind, status, provider_id, '
               'order_id, creation_time) values (%s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (user.id_, amount, kind.value, cls.Status.ready.value, provider.id_,
                  order_id, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache_key_by_user_id(user.id_)
        cls.clear_cache_key_by_provider_order(provider.id_, order_id)
        return cls.get(id_)

    def lay_up(self, remote_transaction_id):
        """已随订单提交支付并进入冻结状态"""
        if self.status not in (self.Status.ready, self.Status.canceled):
            raise ValueError('current status is not ready')

        if isinstance(remote_transaction_id, UUID):
            raise ValueError('Please "lay_up(remote_transaction_id.hex)" instead.')

        sql = ('update {.table_name} set remote_transaction_id=%s, status=%s '
               'where id=%s').format(self)
        params = (remote_transaction_id, self.Status.placed.value, self.id_)
        self._commit_and_clear(sql, params)

    def burn_out(self):
        """已随订单支付成功而确认抵扣生效"""
        if self.status is not self.Status.placed:
            raise ValueError('current status is not placed')

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.burned.value, self.id_)
        self._commit_and_clear(sql, params)

    def take_back(self):
        """由于订单支付失败而导致抵扣金重新释放"""
        if self.status not in (self.Status.placed, self.Status.canceled):
            raise ValueError('current status is not placed')

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.canceled.value, self.id_)
        self._commit_and_clear(sql, params)

    def _commit_and_clear(self, sql, params):
        # commit
        db.execute(sql, params)
        db.commit()
        # clear cache
        self.clear_cache(self.id_)
        self.clear_cache_key_by_user_id(self.user_id)
        self.clear_cache_key_by_provider_order(self.provider_id, self.order_id)
        # update local vars
        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, amount, kind, status, provider_id, order_id, '
               'remote_transaction_id, creation_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_user_id)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s and status=%s'.format(cls)
        params = (user_id, cls.Status.burned.value)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_ids_by_user(user_id)
        return cls.get_multi(id_list)

    @classmethod
    @cache(cache_key_by_provider_order)
    def get_by_provider_order(cls, provider_id, order_id):
        sql = 'select id from {.table_name} where provider_id=%s and order_id=%s'.format(cls)
        params = (provider_id, order_id)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_key_by_user_id(cls, user_id):
        mc.delete(cls.cache_key_by_user_id.format(user_id=user_id))

    @classmethod
    def clear_cache_key_by_provider_order(cls, provider_id, order_id):
        mc.delete(cls.cache_key_by_provider_order.format(
            provider_id=provider_id, order_id=order_id))
