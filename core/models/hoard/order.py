# coding: utf-8

import decimal
import datetime

import arrow
from enum import Enum
from werkzeug.utils import cached_property

from jupiter.workers.hoard_yrd import (
    hoard_yrd_payment_tracking as mq_payment_tracking,
    hoard_yrd_withdrawing as mq_withdrawing,
    hoard_yrd_confirming as mq_confirming,
    hoard_yrd_exiting_checker as mq_exiting_checker,
)
from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.utils import round_half_up
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.user.account import Account
from core.models.profile.identity import has_real_identity
from core.models.profile.bankcard import BankCard, BankCardChanged
from core.models.profile.signals import before_deleting_bankcard, bankcard_updated
from .account import YixinAccount
from .providers import yirendai
from .service import YixinService
from .signals import yrd_order_paid, yrd_order_confirmed, yrd_order_failure, yrd_order_exited
from .errors import (
    NotFoundError, UnboundAccountError, DuplicatePaymentError,
    OutOfRangeError, SellOutError, TakeDownError, InvalidIdentityError)


__all__ = ['HoardOrder']


ORDER_STATUS_COLOR_MAP = {
    u'确认中': '#9B9B9B',
    u'攒钱中': '#6192B3',
    u'转出中': '#F5A623',
    u'错误': '#D42C41',
    u'已转出': '#6C9F31',
    u'未知状态': '#9B9B9B',
}


class RemoteStatus(Enum):
    success = u'0'
    failure = u'1'
    unknown = u'2'


class OrderStatus(Enum):
    unpaid = 'U'
    paid = 'P'
    confirmed = 'C'
    failure = 'F'
    exited = 'E'


class HoardOrder(PropsMixin):
    """The order entity created by users."""

    provider = yirendai

    table_name = 'hoard_order'
    cache_key = 'hoard:order:{id_}:v1'
    fin_order_cache_key = 'hoard:fin:order:{fin_order_id}'
    orders_by_user_cache_key = 'hoard:orders:{user_id}:2'
    cache_key_for_total_orders = 'hoard:orders:total:{user_id}:2'

    stashed_order_id = PropsItem('stashed_order_id')

    def get_uuid(self):
        return 'order:{.id_}'.format(self)

    def get_db(self):
        return 'hoard'

    def __init__(self, id_, service_id, user_id, creation_time, fin_order_id,
                 order_amount, order_id, bankcard_id, status):
        self.id_ = str(id_)
        self.service_id = str(service_id)
        self.user_id = str(user_id)
        self.creation_time = creation_time
        self.fin_order_id = str(fin_order_id) if fin_order_id else None
        self.order_amount = order_amount
        self.order_id = str(order_id) if order_id else None
        self.bankcard_id = str(bankcard_id) if bankcard_id else None
        self.status = OrderStatus(status)

    def __str__(self):
        return '<HoardOrder %s>' % self.id_

    def is_owner(self, user):
        """Checks the specific user is order owner or not."""
        return user and user.id == self.user_id

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def profit_period(self):
        return self.service.profit_period['min']  # XXX: For API

    @cached_property
    def annual_rate(self):
        return self.service.profit_annual_rate['min']

    def bind_bankcard(self, bankcard):
        """Binds a bank card."""
        if not bankcard or bankcard.user_id != self.user_id:
            raise ValueError('invalid bankcard %r' % bankcard)
        sql = ('update {.table_name} set bankcard_id = %s '
               'where id = %s').format(self)
        params = (bankcard.id_, self.id_)
        self._commit_and_refresh(sql, params)

    def restore_bankcard(self, force=False):
        if not self.bankcard_id:
            raise ValueError('missing bankcard_id')
        try:
            return BankCard.restore(self.bankcard_id, self.user_id)
        except BankCardChanged as e:
            if force:
                new_bankcard_id = e.args[0]
                self.migrate_bankcard(self.bankcard_id, new_bankcard_id)
                self.bankcard_id = new_bankcard_id
                try:
                    del self.bankcard
                except AttributeError:
                    pass
                return self.bankcard
            else:
                raise

    @classmethod
    def migrate_bankcard(cls, old_bankcard_id, new_bankcard_id):
        order_ids = cls.get_id_list_by_bankcard_id(old_bankcard_id)
        sql = ('update {.table_name} set bankcard_id = %s '
               'where id = %s').format(cls)
        for order_id in order_ids:
            db.execute(sql, (new_bankcard_id, order_id))
        db.commit()
        for order_id in order_ids:
            order = cls.get(order_id)
            order.clear_cache()
        rsyslog.send(
            '%s to %s\t%r' % (old_bankcard_id, new_bankcard_id, order_ids),
            tag='hoard_migrate_bankcard')

    def track_for_payment(self):
        if self.status is OrderStatus.unpaid:
            mq_payment_tracking.produce(self.id_)

    def mark_as_paid(self, order_id):
        """Marks this order as paid.

        :param order_id: the ``orderNo`` from Yixin API.
        """
        if self.is_success:
            raise DuplicatePaymentError('order has been paid', self.id_)

        sql = ('update {.table_name} set order_id = %s, status = %s'
               'where id = %s').format(self)
        params = (order_id, OrderStatus.paid.value, self.id_)
        self._commit_and_refresh(sql, params)

        # trigger event
        yrd_order_paid.send(self)

        # request to confirm
        mq_confirming.produce(self.id_)

    def mark_as_confirmed(self):
        if self.status is OrderStatus.unpaid:
            raise ValueError('order has not been paid', self.id_)
        if self.status is OrderStatus.confirmed:
            return

        sql = ('update {.table_name} set status = %s'
               'where id = %s').format(self)
        params = (OrderStatus.confirmed.value, self.id_)
        self._commit_and_refresh(sql, params)

        # trigger event
        yrd_order_confirmed.send(self)

        # request to register withdrawing
        mq_withdrawing.produce(self.id_)

    def mark_as_exited(self):
        if self.status is OrderStatus.exited:
            return

        sql = ('update hoard_order set status = %s '
               'where id = %s').format(self)
        params = (OrderStatus.exited.value, self.id_)
        self._commit_and_refresh(sql, params)

        # remove event push code for batch updating
        # trigger event
        # yrd_order_exited.send(self)

        # request exit notification sms when order exit is caught in time
        # expect_exit_date = (
        #    self.creation_time.date() + relativedelta(days=self.profit_period.value))
        # if (datetime.date.today() - expect_exit_date).days < 6:
        #    mq_sms_sender.produce(self.id_)

    def track_for_exited(self):
        if self.status is OrderStatus.exited:
            return

        # request to check status
        mq_exiting_checker.produce(self.id_)

    def mark_as_failure(self):
        if self.status is OrderStatus.confirmed or OrderStatus.exited:
            raise DuplicatePaymentError('order has been confirmed', self.id_)

        sql = ('update {.table_name} set status = %s'
               'where id = %s').format(self)
        params = (OrderStatus.failure.value, self.id_)
        self._commit_and_refresh(sql, params)

        # trigger event
        yrd_order_failure.send(self)

    @classmethod
    def get_orders_by_period(cls, date_from, date_to, closure):
        sql = ('select id from hoard_order where status=%s '
               'and date(creation_time) between %s and %s').format(cls)
        params = (OrderStatus.confirmed.value, date_from, date_to)
        rs = db.execute(sql, params)
        orders = (cls.get(r[0]) for r in rs)
        return [order for order in orders if int(order.service.frozen_time) == closure]

    def _commit_and_refresh(self, sql, params):
        # 执行SQL并提交
        db.execute(sql, params)
        db.commit()

        # 清除数据库缓存
        self.clear_cache()

        # 刷新实例内属性值
        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

        # 清除实例内缓存
        self.__dict__.pop('bankcard', None)

    @property
    def is_success(self):
        """``True`` if this order has been paid."""
        return self.status in [OrderStatus.confirmed, OrderStatus.paid, OrderStatus.exited]

    @property
    def is_failure(self):
        return self.status == OrderStatus.failure

    @cached_property
    def service(self):
        return YixinService.get(self.service_id)

    @cached_property
    def due_date(self):
        order_info, _ = self._fetch_order_info()
        return order_info['frozenDatetime']

    @classmethod
    def check_before_adding(cls, service_id, user_id, order_amount):
        yixin_service = YixinService.get(service_id)
        yixin_account = YixinAccount.get_by_local(user_id)
        user = Account.get(user_id)

        # checks the related entities
        if not yixin_service:
            raise NotFoundError(service_id, YixinService)
        if not user:
            raise NotFoundError(user_id, Account)
        if not yixin_account:
            raise UnboundAccountError(user_id)

        # checks the identity
        if not has_real_identity(user):
            raise InvalidIdentityError

        # checks available
        if yixin_service.sell_out:
            raise SellOutError(yixin_service.uuid)
        if yixin_service.take_down:
            raise TakeDownError(yixin_service.uuid)

        # checks the amount type
        if not isinstance(order_amount, decimal.Decimal):
            raise TypeError('order_amount must be decimal')

        # checks the amount range
        amount_range = (yixin_service.invest_min_amount,
                        yixin_service.invest_max_amount)
        if (order_amount.is_nan() or order_amount < 0 or
                order_amount < yixin_service.invest_min_amount or
                order_amount > yixin_service.invest_max_amount):
            raise OutOfRangeError(order_amount, amount_range)

    @classmethod
    def add(cls, service_id, user_id, order_amount, fin_order_id,
            creation_time=None):
        """Creates a unpaid order.

        :param service_id: the UUID of chosen P2P service.
        :param user_id: the user id of order creator.
        :param order_amount: the payment amount for this order.
        :param fin_order_id: the UUID of remote order.
        :returns: the created order.
        """
        cls.check_before_adding(service_id, user_id, order_amount)

        creation_time = creation_time or datetime.datetime.now()
        sql = ('insert into {.table_name} (service_id, user_id, order_amount,'
               ' fin_order_id, creation_time, status) '
               'values (%s, %s, %s, %s, %s, %s)').format(cls)
        params = (service_id, user_id, order_amount, fin_order_id,
                  creation_time, OrderStatus.unpaid.value)

        id_ = db.execute(sql, params)
        db.commit()

        order = cls.get(id_)
        order.clear_cache()
        return order

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, service_id, user_id, creation_time, fin_order_id,'
               ' order_amount, order_id, bankcard_id, status '
               'from {.table_name} where id = %s').format(cls)
        params = (id_,)

        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_by_order_no(cls, order_id):
        sql = ('select id from {.table_name} where order_id = %s').format(cls)
        params = (order_id,)

        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    @cache(fin_order_cache_key)
    def get_id_by_fin_order_id(cls, fin_order_id):
        sql = ('select id from {.table_name} '
               'where fin_order_id = %s').format(cls)
        params = (fin_order_id,)

        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_fin_order_id(cls, fin_order_id):
        id = cls.get_id_by_fin_order_id(fin_order_id)
        if id:
            return cls.get(id)

    @classmethod
    @cache(orders_by_user_cache_key)
    def get_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id = %s '
               'order by creation_time desc').format(cls)
        params = (user_id,)

        rs = db.execute(sql, params)
        if rs:
            return [r[0] for r in rs]

    @classmethod
    def gets_by_user_id(cls, user_id):
        """get all paid orders by user"""
        id_list = cls.get_id_list_by_user_id(user_id)
        orders = [cls.get(id_) for id_ in id_list or []]
        return [o for o in orders if o.is_success]

    @classmethod
    def gets_by_user_in_period(cls, user_id, start, end):
        """get user successed orders in period"""
        id_list = cls.get_id_list_by_user_id(user_id)
        if id_list:
            orders = [cls.get(id_) for id_ in id_list]
            successful_orders = [order for order in orders if order.status
                                 is OrderStatus.confirmed or OrderStatus.exited]
            return [o for o in successful_orders if start <= o.creation_time < end]

    @classmethod
    def gets_by_date(cls, date):
        sql = ('select id from {.table_name} '
               'where DATE(creation_time) = %s ').format(cls)
        params = (date,)

        rs = db.execute(sql, params)
        if rs:
            return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_id_list_by_bankcard_id(cls, bankcard_id):
        sql = 'select id from {.table_name} where bankcard_id = %s'.format(cls)
        params = (bankcard_id,)

        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_bankcard(cls, bankcard_id):
        id_list = cls.get_id_list_by_bankcard_id(bankcard_id)
        orders = [cls.get(id_) for id_ in id_list or []]
        return [o for o in orders if o.is_success]

    def clear_cache(self):
        mc.delete(self.cache_key.format(id_=self.id_))
        mc.delete(self.cache_key_for_total_orders.format(user_id=self.user_id))
        mc.delete(self.orders_by_user_cache_key.format(user_id=self.user_id))
        mc.delete(self.fin_order_cache_key.format(
            fin_order_id=self.fin_order_id))

    @classmethod
    @cache(cache_key_for_total_orders)
    def get_total_orders(cls, user_id):
        sql = ('select count(id) from {.table_name} where user_id=%s '
               'and (status=%s or status=%s or status=%s)').format(cls)
        params = (user_id, OrderStatus.paid.value, OrderStatus.confirmed.value,
                  OrderStatus.exited.value)
        rs = db.execute(sql, params)
        return rs[0][0]

    @cached_property
    def bankcard(self):
        if not self.bankcard_id:
            return
        return BankCard.get(self.bankcard_id)

    @classmethod
    def gets_by_month(cls, date):
        # start, end should be 'yyyy-mm'
        year, month = date.split('-')

        sql = ('select id from {.table_name} where year(creation_time) = %s '
               'and month(creation_time) = %s').format(cls)
        params = (year, month)

        rs = db.execute(sql, params)
        if rs:
            return [cls.get(r[0]) for r in rs]

    def register_for_withdrawing(self, client, token):
        return client.query.set_finance_exit_bank_info(
            token, self.fin_order_id, self.bankcard.bank.yxlib_id,
            self.bankcard.city_id, self.bankcard.province_id,
            self.bankcard.card_number, self.bankcard.local_bank_name)

    @cached_property
    def expected_profit(self):
        """预期的到期总收益."""
        order_info, order_status = self._fetch_order_info()
        if order_status == u'已转出':
            return decimal.Decimal(order_info['incomeAmount'])
        monthly_ratio = self.service.expected_income / 100 / 12
        result = monthly_ratio * self.order_amount * self.service.frozen_time
        return round_half_up(result, 2)

    def fetch_status(self, orders=None):
        """该订单在宜人贷的状态."""
        order_info, order_status = self._fetch_order_info(orders)
        if order_info and order_status:
            return order_status
        return getattr(self, '_order_status', None)  # for testing

    def fetch_daily_profit(self, orders=None):
        """该订单平均到每日的收益."""
        amount = decimal.Decimal(self.order_amount)
        order_info, order_status = self._fetch_order_info(orders)
        if not order_info or not order_status:
            return decimal.Decimal(0)
        if order_status not in [u'攒钱中', u'转出中']:
            return decimal.Decimal(0)
        return (
            amount * decimal.Decimal(order_info['expectedIncome']) / 100 / 365)

    def fetch_profit_until(self, date, orders=None):
        """该订单到某日为止的累计收益."""
        order_info, order_status = self._fetch_order_info(orders)

        # 已转出则返回已结算的收益
        if order_status == u'已转出':
            return decimal.Decimal(order_info['incomeAmount'])

        # 未转出则使用预期每日收益按日累加
        invest_date = arrow.get(order_info['investDate']).date()
        days = (date - invest_date).days
        if days <= 0:
            return decimal.Decimal(0)
        return days * self.fetch_daily_profit(orders)

    def _fetch_orders(self):
        from .profile import HoardProfile
        profile = HoardProfile.add(self.user_id)
        return profile.orders()

    def _fetch_order_info(self, orders=None):
        orders = orders or self._fetch_orders()
        for order, order_info, order_status in orders:
            if order.id_ == self.id_:
                return order_info, order_status
        return None, None


@yrd_order_confirmed.connect
def on_order_confirmed(sender):
    msg = '\t'.join([
        sender.id_, sender.service_id, sender.user_id,
        sender.creation_time.isoformat(), sender.fin_order_id or '0',
        sender.order_id,
        sender.bankcard_id or '0', str(round(sender.order_amount, 2))])
    rsyslog.send(msg, tag='savings_paid')


@yrd_order_exited.connect
def on_order_exited(sender):
    msg = '\t'.join([
        sender.id_, sender.service_id, sender.user_id,
        sender.creation_time.isoformat(), str(round(sender.order_amount, 2))])
    rsyslog.send(msg, tag='savings_exited')


@before_deleting_bankcard.connect
def check_bankcard_is_used_before_deleting(sender, bankcard_id, user_id):
    if HoardOrder.get_multi_by_bankcard(bankcard_id):
        # don't remove bankcards which is used in paid orders
        return False


@bankcard_updated.connect
def check_bankcard_update(sender, changed_fields):
    if 'local_bank_name' not in changed_fields:
        return
    orders = HoardOrder.get_multi_by_bankcard(sender.id_)
    for order in orders:
        mq_withdrawing.produce(order.id_)
