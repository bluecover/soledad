# coding: utf-8

from datetime import datetime
from decimal import Decimal
from enum import Enum
from werkzeug.utils import cached_property

from jupiter.workers.hoard_zhiwang import (
    zhiwang_payment_tracking as mq_payment_tracking,
    zhiwang_asset_fetching as mq_asset_fetching,
)
from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.mixin.props import PropsMixin
from core.models.user.account import Account
from core.models.profile.identity import has_real_identity
from core.models.profile.bankcard import BankCard
from core.models.profile.signals import before_deleting_bankcard
from .profit_hike import ZhiwangOrderProfitHike
from .account import ZhiwangAccount
from .product import ZhiwangProduct
from .wrapped_product import ZhiwangWrappedProduct
from .errors import (
    InvalidStatusTransfer, UnknownProductInheritance,
    UnboundAccountError, SoldOutError, SuspendedError,
    IneligiblePurchase, OffShelfError, ExceedBankAmountLimitError,
    OutOfRangeError)
from ..errors import NotFoundError, InvalidIdentityError
from ..providers import zhiwang
from ..signals import zw_order_succeeded, zw_order_failure
from ..common import ProfitPeriod


class ZhiwangOrder(PropsMixin):
    """The order entity created by users."""

    class Status(Enum):
        #: 本地初始状态
        unpaid = 'U'
        #: 本地支付前状态
        committed = 'C'
        #: 指旺暂时搁置状态
        shelved = 'V'
        #: 指旺正在支付状态
        paying = 'P'
        #: 指旺已成功状态
        success = 'S'
        #: 指旺已失败状态
        failure = 'F'

    # 状态显示文案
    Status.unpaid.label = u'未支付'
    Status.committed.label = u'未支付'
    Status.shelved.label = u'处理中'
    Status.paying.label = u'处理中'
    Status.success.label = u'已支付'
    Status.failure.label = u'已失败'

    # 状态迁移顺序
    Status.unpaid.sequence = 0
    Status.committed.sequence = 1
    Status.shelved.sequence = 2
    Status.paying.sequence = 3
    Status.success.sequence = 4
    Status.failure.sequence = 4

    # 指旺与本地状态映射
    MUTUAL_STATUS_MAP = {
        'order_start': Status.shelved,
        'pay_wait': Status.paying,
        'order_success': Status.success,
        'order_fail': Status.failure,
        'order_cancel': Status.failure,
    }

    # 订单所属合作方
    provider = zhiwang

    # 数据存储
    table_name = 'hoard_zhiwang_order'
    cache_key = 'hoard:zhiwang:order:{id_}:v3'
    cache_has_wrapped_product = 'hoard:zhiwang:order:has_wrapped_product:{user_id}'
    orders_by_user_cache_key = 'hoard:zhiwang:orders:user:{user_id}:v3'
    cache_key_for_total_orders = 'hoard:zhiwang:orders:total:user:{user_id}:v3'
    raw_product_sold_amount_cache_key = (
        'hoard:zhiwang:order:sold_amount:raw_product:{raw_product_id}:v3')
    wrapped_product_sold_amount_cache_key = (
        'hoard:zhiwang:order:sold_amount:raw_product:{raw_product_id}:'
        'wrapped_product:{wrapped_product_id}:v3')

    def __init__(self, id_, user_id, product_id, wrapped_product_id, bankcard_id, amount,
                 pay_amount, expect_interest, start_date, due_date, order_code, pay_code,
                 status, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.product_id = str(product_id)
        self.wrapped_product_id = wrapped_product_id and str(wrapped_product_id)
        self.bankcard_id = str(bankcard_id)
        self.amount = amount
        self.pay_amount = pay_amount
        self.expect_interest = expect_interest
        self.start_date = start_date
        self.due_date = due_date
        self.order_code = str(order_code) if order_code else None
        self.pay_code = str(pay_code) if pay_code else None
        self._status = status
        self.creation_time = creation_time

    def __str__(self):
        return '<ZhiwangOrder %s>' % self.id_

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'zhiwang:order:{.id_}'.format(self)

    def is_owner(self, user):
        return user and user.id == self.user_id

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        self._status = item.value

    @cached_property
    def asset(self):
        from .asset import ZhiwangAsset
        return ZhiwangAsset.get_by_order_code(self.order_code)

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @property
    def profit_hikes(self):
        return ZhiwangOrderProfitHike.get_multi_by_order(self.id_)

    @property
    def coupon(self):
        if self.coupon_record:
            return self.coupon_record.coupon

    @property
    def coupon_record(self):
        from core.models.welfare import CouponUsageRecord
        return CouponUsageRecord.get_by_partner_order(self.provider.id_, self.id_)

    @property
    def woods_burning(self):
        from core.models.welfare import FirewoodBurning
        return FirewoodBurning.get_by_provider_order(self.provider.id_, self.id_)

    @cached_property
    def product(self):
        return ZhiwangProduct.get(self.product_id)

    @cached_property
    def wrapped_product(self):
        if self.wrapped_product_id:
            return ZhiwangWrappedProduct.get(self.wrapped_product_id)

    @property
    def display_status(self):
        return self.status.label

    @property
    def computed_expect_interest(self):
        if self.wrapped_product:
            assert self.wrapped_product.profit_period['min'].unit == 'day'
            return (self.wrapped_product.annual_rate * self.amount *
                    self.wrapped_product.profit_period['min'].value / 100 / 365)
        else:
            return (self.actual_annual_rate * self.amount *
                    self.profit_period.value / 100 / 365)

    @property
    def original_annual_rate(self):
        if self.product.product_type == ZhiwangProduct.Type.fangdaibao:
            return self.product.get_annual_rate_by_date(self.due_date.date())
        else:
            return self.product.annual_rate

    @property
    def actual_annual_rate(self):
        if self.profit_hikes:
            return self.original_annual_rate + sum(h.annual_rate_offset for h in self.profit_hikes)
        return self.original_annual_rate

    @cached_property
    def profit_period(self):
        return ProfitPeriod((self.due_date - self.start_date).days, 'day')

    @cached_property
    def bankcard(self):
        if not self.bankcard_id:
            return
        return BankCard.get(self.bankcard_id)

    @classmethod
    def check_before_adding(
            cls, user_id, bankcard_id, product_id, amount, wrapped_product_id=None):
        product = ZhiwangProduct.get(product_id)
        wrapped_product = ZhiwangWrappedProduct.get(
            wrapped_product_id) if wrapped_product_id else None

        # check the product and wrapped_product
        if wrapped_product_id is not None and not wrapped_product:
            raise NotFoundError(wrapped_product_id, ZhiwangWrappedProduct)
        if wrapped_product and wrapped_product.raw_product.product_id != product_id:
            raise UnknownProductInheritance(product_id, wrapped_product_id)
        if wrapped_product and not wrapped_product.is_qualified(user_id):
            raise IneligiblePurchase(user_id, wrapped_product_id)

        product = wrapped_product if wrapped_product else product
        bankcard = BankCard.get(bankcard_id)
        local_account = Account.get(user_id)
        zhiwang_account = ZhiwangAccount.get_by_local(user_id)

        # checks the related entities
        if not bankcard:
            raise NotFoundError(bankcard_id, BankCard)
        if not local_account:
            raise NotFoundError(local_account, Account)
        if not zhiwang_account:
            raise UnboundAccountError(user_id)

        # checks the identity
        if not has_real_identity(local_account):
            raise InvalidIdentityError

        # 产品是否处于可售状态
        if product.is_either_sold_out:
            raise SoldOutError(product_id, wrapped_product_id)
        # 产品是否处于正常销售状态
        if product.is_taken_down:
            raise SuspendedError(product_id, wrapped_product_id)
        # 产品是否处于在售状态
        if not product.in_stock:
            raise OffShelfError(product_id, wrapped_product_id)

        # checks the product amount limit
        if not isinstance(amount, Decimal):
            raise TypeError('order amount must be decimal')
        amount_range = (product.min_amount, product.max_amount)
        amount_check = [amount.is_nan(),
                        amount < 0,
                        amount < amount_range[0],
                        amount > amount_range[1]]
        if any(amount_check):
            raise OutOfRangeError(amount, amount_range)

        # checks the bank amount limit
        bank_limit = bankcard.bank.zwlib_amount_limit
        bank_limit = max(bank_limit) if cls.is_bankcard_swiped(bankcard) else min(bank_limit)
        if amount > bank_limit:
            raise ExceedBankAmountLimitError(amount, bank_limit)

    @classmethod
    def add(cls, user_id, product_id, bankcard_id, amount, pay_amount, expect_interest, start_date,
            due_date, order_code, pay_code, wrapped_product_id=None, creation_time=None):
        cls.check_before_adding(user_id, bankcard_id, product_id, amount, wrapped_product_id)

        sql = ('insert into {.table_name} (user_id, product_id, bankcard_id, amount, '
               'pay_amount, expect_interest, start_date, due_date, order_code, pay_code, '
               'status, wrapped_product_id, creation_time) values (%s, %s, %s, %s, %s, '
               '%s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (user_id, product_id, bankcard_id, amount, pay_amount, expect_interest,
                  start_date, due_date, order_code, pay_code, cls.Status.unpaid.value,
                  wrapped_product_id, creation_time or datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        order = cls.get(id_)
        order.clear_cache()
        return order

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, product_id, wrapped_product_id, bankcard_id, amount, '
               'pay_amount, expect_interest, start_date, due_date, order_code, '
               'pay_code, status, creation_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_order_code(cls, order_code):
        sql = 'select id from {.table_name} where order_code = %s'.format(cls)
        params = (order_code,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(orders_by_user_cache_key)
    def get_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id = %s '
               'order by creation_time desc').format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_id_list_by_user_id(user_id)
        return [cls.get(id_) for id_ in id_list]

    gets_by_user_id = get_multi_by_user

    @classmethod
    def get_id_list_by_bankcard_id(cls, bankcard_id):
        sql = 'select id from {.table_name} where bankcard_id=%s'.format(cls)
        params = (bankcard_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_for_total_orders)
    def get_total_orders(cls, user_id):
        sql = ('select count(id) from {.table_name} where user_id=%s '
               'and (status=%s or status=%s)').format(cls)
        params = (user_id, cls.Status.paying.value, cls.Status.success.value)
        rs = db.execute(sql, params)
        return rs[0][0]

    @classmethod
    @cache(cache_has_wrapped_product)
    def has_wrapped_product(cls, user_id):
        sql = ('select count(id) from {.table_name} where user_id=%s '
               'and (status=%s or status=%s) '
               'and wrapped_product_id is not null').format(cls)
        params = (user_id, cls.Status.paying.value, cls.Status.success.value)
        rs = db.execute(sql, params)
        return rs[0][0] > 0

    @classmethod
    def get_multi_by_bankcard(cls, bankcard_id):
        id_list = cls.get_id_list_by_bankcard_id(bankcard_id)
        return [cls.get(id_) for id_ in id_list]

    @classmethod
    def is_bankcard_swiped(cls, bankcard):
        assert isinstance(bankcard, BankCard)
        return len([o for o in cls.get_multi_by_bankcard(
            bankcard.id_) if o.status is cls.Status.success]) > 0

    @classmethod
    @cache(raw_product_sold_amount_cache_key)
    def get_raw_product_sold_amount(cls, raw_product_id):
        sql = ('select sum(amount) from {.table_name} where product_id=%s '
               'and (status=%s or status=%s)').format(cls)
        params = (raw_product_id, cls.Status.paying.value, cls.Status.success.value)
        rs = db.execute(sql, params)
        return rs[0][0] or 0

    @classmethod
    @cache(wrapped_product_sold_amount_cache_key)
    def get_wrapped_product_sold_amount(cls, raw_product_id, wrapped_product_id=None):
        """获取子产品销售量，当子产品ID为默认None时获取父产品除去子产品外的销售量"""
        sql = ('select sum(amount) from {.table_name} where (status=%s or status=%s) '
               'and product_id=%s and wrapped_product_id').format(cls)
        sql = '%s %s' % (sql, 'is %s ' if wrapped_product_id is None else '=%s')
        params = (cls.Status.paying.value, cls.Status.success.value,
                  raw_product_id, wrapped_product_id)
        rs = db.execute(sql, params)
        return rs[0][0] or 0

    def update_status(self, new_status):
        """更新订单状态"""
        # 不可反向及原地跳转状态
        if new_status.sequence < self.status.sequence:
            raise InvalidStatusTransfer(self.status, new_status)

        # 更新状态并检查是否生效，未生效者判定为重复行为
        sql = 'update {.table_name} set status=%s where id=%s and status=%s'.format(self)
        params = (new_status.value, self.id_, self.status.value)
        db.execute(sql, params)
        db.commit()

        self.status = new_status
        self.clear_cache()

        rsyslog.send('order %s status changes from %s to %s' % (
            self.id_, self.status.value, new_status.value),
            tag='zhiwang_order_status_change')

        if new_status in [self.Status.shelved, self.Status.paying]:
            # 当支付未完成时将订单放入状态跟踪MQ
            self.track_for_payment()
            return

        if new_status is self.Status.success:
            # 当支付成功时将订单放入获取资产MQ并发送成功广播信号
            rsyslog.send('fetch asset for order %s' % self.id_,
                         tag='zhiwang_fetch_asset')
            mq_asset_fetching.produce(self.id_)
            zw_order_succeeded.send(self)
            return

        if new_status is self.Status.failure:
            # 当支付失败时发送失败广播信号
            zw_order_failure.send(self)
            return

    def track_for_payment(self):
        mq_payment_tracking.produce(self.id_)

    def lock_bonus(self):
        """对订单礼券、抵扣金进行加锁冻结（发生在订单提交支付前）"""
        from core.models.welfare import FirewoodWorkflow, FirewoodBurning

        if self.woods_burning:
            flow = FirewoodWorkflow(self.user_id)
            flow.pick(self.woods_burning, tags=[FirewoodBurning.Kind.deduction.name])

        if self.coupon:
            self.coupon.shell_out(self.product, self.amount)

        for hike in self.profit_hikes:
            hike.occupy()

    def confirm_bonus(self):
        """确认礼券、抵扣金被使用（发生在订单已经被告知成功）"""
        from core.models.welfare import FirewoodWorkflow
        if self.status is not self.Status.success:
            raise ValueError('order %s payment has not succeeded' % self.id_)

        if self.woods_burning:
            FirewoodWorkflow(self.user_id).burn(self.woods_burning)

        if self.coupon:
            self.coupon.confirm_consumption()
            self.coupon_record.commit()

        for hike in self.profit_hikes:
            hike.achieve()

    def unlock_bonus(self):
        """释放礼券、抵扣金（发生在订单已经被告知失败）"""
        from core.models.welfare import FirewoodWorkflow
        if self.status not in [self.Status.unpaid, self.Status.failure]:
            raise ValueError('order %s payment has not terminated' % self.id_)

        if self.woods_burning:
            FirewoodWorkflow(self.user_id).release(self.woods_burning)

        if self.coupon:
            self.coupon.put_back_wallet()

        for hike in self.profit_hikes:
            hike.renew()

    def clear_cache(self):
        mc.delete(self.cache_key.format(id_=self.id_))
        mc.delete(self.orders_by_user_cache_key.format(user_id=self.user_id))
        mc.delete(self.cache_key_for_total_orders.format(user_id=self.user_id))

    @classmethod
    def clear_local_sold_amount_cache(cls, raw_product_id, wrapped_product_id):
        mc.delete(cls.raw_product_sold_amount_cache_key.format(raw_product_id=raw_product_id))
        mc.delete(cls.wrapped_product_sold_amount_cache_key.format(
            raw_product_id=raw_product_id, wrapped_product_id=None))
        mc.delete(cls.wrapped_product_sold_amount_cache_key.format(
            raw_product_id=raw_product_id, wrapped_product_id=wrapped_product_id))


@zw_order_succeeded.connect
def on_order_succeeded(sender):
    order = ZhiwangOrder.get(sender.id_)

    # 清除产品销售额缓存
    ZhiwangOrder.clear_local_sold_amount_cache(order.product_id, order.wrapped_product_id)

    # 确认优惠已被消费使用
    order.confirm_bonus()

    # 记录成功订单日志
    rsyslog.send('\t'.join([
        order.id_, order.product_id, order.user_id, order.creation_time.isoformat(),
        order.order_code, order.bankcard_id, str(round(order.amount, 2))]),
        tag='zhiwang_order_succeeded')


@zw_order_failure.connect
def on_order_failure(sender):
    order = ZhiwangOrder.get(sender.id_)

    # 清除产品销售额缓存
    ZhiwangOrder.clear_local_sold_amount_cache(order.product_id, order.wrapped_product_id)

    # 解除礼券、抵扣金锁
    order.unlock_bonus()


@before_deleting_bankcard.connect
def check_bankcard_is_used_before_deleting(sender, bankcard_id, user_id):
    related_orders = ZhiwangOrder.get_multi_by_bankcard(bankcard_id)
    if len([o for o in related_orders if o.status in (
            ZhiwangOrder.Status.paying, ZhiwangOrder.Status.success)]) > 0:
        # don't remove bankcard which is in use
        return False
