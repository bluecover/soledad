# coding: utf-8

from __future__ import absolute_import

import datetime
import decimal

from enum import Enum
from werkzeug.utils import cached_property

from jupiter.workers.hoard_placebo import placebo_order_exiting
from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.profile.identity import has_real_identity
from core.models.profile.bankcard import BankCard
from .product import PlaceboProduct
from ..errors import InvalidIdentityError
from ..zhiwang.errors import (  # TODO move to top-level
    InvalidProductError, OffShelfError, OutOfRangeError)
from ..providers import placebo


__all__ = ['PlaceboOrder', 'placebo_order_exiting']


class PlaceboOrder(EntityModel):
    """攒钱助手体验金订单."""

    table_name = 'hoard_placebo_order'
    cache_key = 'hoard:placebo:order:{id_}'
    cache_by_user_key = 'hoard:placebo:order:user:{user_id}:ids'
    yxpay_biz_id_prefix = 'gh:s:p:'

    provider = placebo

    class Status(Enum):
        #: 攒钱中
        running = '1'
        #: 已取消 (失败)
        failure = '2'
        #: 转出中
        exiting = '3'
        #: 已转出
        exited = '4'

    Status.running.display_text = u'攒钱中'
    Status.failure.display_text = u'已取消'
    Status.exiting.display_text = u'转出中'
    Status.exited.display_text = u'已转出'

    def __init__(self, id_, user_id, product_id, bankcard_id, amount,
                 annual_rate_hike, status, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.product_id = str(product_id)
        self.bankcard_id = str(bankcard_id)
        self.amount = amount
        self.annual_rate_hike = annual_rate_hike
        self._status = str(status)
        self.creation_time = creation_time

    @property
    def status(self):
        return self.Status(self._status)

    @cached_property
    def biz_id(self):
        return '%s%s' % (self.yxpay_biz_id_prefix, self.id_)

    @cached_property
    def product(self):
        return PlaceboProduct.get(self.product_id)

    @cached_property
    def bankcard(self):
        return BankCard.get(self.bankcard_id)

    @cached_property
    def profit_period(self):
        return self.product.profit_period['min']

    @cached_property
    def profit_annual_rate(self):
        return self.product.profit_annual_rate['min'] + self.annual_rate_hike

    @cached_property
    def start_date(self):
        return self.creation_time.date()

    @cached_property
    def due_date(self):
        assert self.profit_period.unit == 'day'
        return self.creation_time + datetime.timedelta(days=self.profit_period.value)

    def calculate_profit_amount(self):
        assert self.profit_period.unit == 'day'
        daily_rate = self.profit_annual_rate / 100 / 365 * self.profit_period.value
        return daily_rate * self.amount

    @cached_property
    def owner(self):
        return Account.get(self.user_id)

    def transfer_status(self, status):
        sql = (
            'update {0} set status = %s where id = %s'
            ' and status = %s').format(self.table_name)
        params = (status.value, self.id_, self.status.value)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self._status = status.value
        return self.status

    def assign_annual_rate_hike(self, hike):
        if self.status is not self.Status.running:
            raise NotRunningError()
        if hike <= 0 or hike.is_nan():
            raise ValueError('hike must be positive')
        sql = (
            'update {0} set annual_rate_hike = %s where id = %s '
            'and status = %s').format(self.table_name)
        params = (hike, self.id_, self.status.value)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self.annual_rate_hike = hike
        vars(self).pop('profit_annual_rate', None)
        return self.annual_rate_hike

    def mark_as_exited(self, response):
        assert self.status is self.Status.exiting
        remote_status = YixinPaymentStatus(int(response.state))
        if remote_status is not YixinPaymentStatus.SUCCESS:
            raise YixinPaymentError(self, remote_status)
        rsyslog.send(
            'transaction_id=%s\tcomplete_time=%s' % (
                response.tx_id, response.complete_time),
            tag='savings_placebo_exited')
        self.transfer_status(self.Status.exited)

    @classmethod
    def add(cls, user_id, product_id, bankcard_id, amount):
        user, product, bankcard, amount = cls.check_before_adding(
            user_id, product_id, bankcard_id, amount)

        sql = (
            'insert into {0} (user_id, product_id, bankcard_id, amount,'
            ' annual_rate_hike, status, creation_time) '
            'values (%s, %s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (
            user.id_, product.id_, bankcard.id_, amount, decimal.Decimal(0),
            cls.Status.running.value, datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_user(user.id_)
        return cls.get(id_)

    @classmethod
    def check_before_adding(cls, user_id, product_id, bankcard_id, amount):
        product = PlaceboProduct.get(product_id)
        bankcard = BankCard.get(bankcard_id)
        user = Account.get(user_id)

        # 检查关联对象
        for attr_name, attr in [
                ('product_id', product), ('bankcard_id', bankcard),
                ('user_id', user)]:
            if not attr:
                raise ValueError('invalid %s' % attr_name)

        # 检查身份认证
        if not has_real_identity(user):
            raise InvalidIdentityError()

        # 检查产品是否可售
        if not product.strategy.target(user_id):
            raise InvalidProductError(product_id)  # 策略拒绝
        if not product.in_stock:
            raise OffShelfError(product_id)        # 下架

        # 检查金额范围
        if amount is None and product.min_amount == product.max_amount:
            amount = product.min_amount
        if (amount.is_nan() or amount < product.min_amount or
                amount > product.max_amount):
            raise OutOfRangeError(
                amount, (product.min_amount, product.max_amount))

        return user, product, bankcard, amount

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, user_id, product_id, bankcard_id, amount,'
            ' annual_rate_hike, status, creation_time '
            'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_biz_id(cls, biz_id):
        if biz_id.startswith(cls.yxpay_biz_id_prefix):
            return cls.get(biz_id[len(cls.yxpay_biz_id_prefix):])

    @classmethod
    @cache(cache_by_user_key)
    def get_ids_by_user(cls, user_id):
        sql = (
            'select id from {0} where user_id = %s '
            'order by id desc').format(cls.table_name)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def iter_multi_for_exiting(cls):
        """获取准备转出的订单."""
        products = {
            id_: PlaceboProduct.get(id_)
            for id_ in PlaceboProduct.get_all_ids()}

        sql = (
            'select id, product_id, creation_time from {0} where status = %s '
            'order by id desc').format(cls.table_name)
        params = (cls.Status.running.value,)
        rs = db.execute(sql, params)

        for order_id, product_id, creation_time in rs:
            product = products[str(product_id)]
            exiting_date = product.make_exiting_date(creation_time.date())
            if exiting_date <= datetime.date.today():
                yield cls.get(order_id), product

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_by_user_key.format(**locals()))


class NotRunningError(Exception):
    """订单状态不再是攒钱中了."""


class YixinPaymentError(Exception):
    """回款失败"""


class YixinPaymentStatus(Enum):
    NOT_FOUND = -2             # fail
    FAILED_SUBMIT = -1         # fail
    UNSENT_TO_BANK = 1         # middle
    SUCCESS = 2                # success
    FAILURE = 3                # fail
    UNRESPONSED_FROM_BANK = 4  # middle
    REFUNDED = 33              # fail
