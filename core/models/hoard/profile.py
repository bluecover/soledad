# coding: utf-8

from datetime import datetime, date
from warnings import warn

from werkzeug.utils import cached_property
from dateutil.relativedelta import relativedelta

from jupiter.ext import yixin
from jupiter.workers.hoard_yrd import hoard_yrd_order_syncronizer
from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.user.account import Account
from core.models.profile.bankcard import BankCardManager
from core.models.profile.identity import Identity
from core.models.utils.switch import CacheKeySwitch
from .order import HoardOrder, OrderStatus
from .errors import NotFoundError
from .account import YixinAccount
from .stats import add_savings_users
from .signals import yrd_order_paid, yrd_order_confirmed, yrd_order_failure


ORDER_STATUS_MAP = {
    u'支付中': u'确认中',
    u'购买成功': u'确认中',
    u'理财中': u'攒钱中',
    u'退出中': u'转出中',
    u'产品类型转换处理中': u'错误',
    u'已锁定(异常理财单)': u'错误',
    u'已结束': u'已转出',
}


class HoardProfile(PropsMixin):
    """The user profile of hoard product."""

    table_name = 'hoard_profile'
    cache_key = 'hoard:user:profile:{account_id}:v1'
    cache_account_ids_key = 'hoard:user:profile:account_ids'

    #: 是否开启订单拉取, 宜人贷(习惯性)宕机时应关闭
    pulling_switch = CacheKeySwitch('hoard:yrd:profile:pulling')

    #: the target amount in plan
    plan_amount = PropsItem('plan_amount', default=0)

    #: the stashed order
    stashed_order = PropsItem('stashed_order', default={}, secret=True)

    #: account info fetchable switch
    account_info_fetchable = PropsItem('account_info_fetchable', default=False)

    #: all account order info
    person_account_info = PropsItem('person_account_info', default='',
                                    secret=True)

    def __init__(self, account_id, creation_time):
        self.account_id = str(account_id)
        self.creation_time = creation_time

    @cached_property
    def bankcards(self):
        return BankCardManager(self.account_id)

    @cached_property
    def _identity(self):
        return Identity.get(self.account_id)

    @property
    def person_name(self):
        warn('Please use Identity directly instead.', DeprecationWarning)
        return self._identity.person_name if self._identity else ''

    @property
    def person_ricn(self):
        warn('Please use Identity directly instead.', DeprecationWarning)
        return self._identity.person_ricn if self._identity else ''

    @person_name.setter
    def person_name(self, value):
        raise DeprecationWarning('Please use Identity.save instead.')

    @person_ricn.setter
    def person_ricn(self, value):
        raise DeprecationWarning('Please use Identity.save instead.')

    @property
    def bank_cards(self):
        warn('Please use profile.bankcards instead.', DeprecationWarning)
        return self.bankcards

    def get_uuid(self):
        return 'user:profile:{account_id}'.format(account_id=self.account_id)

    def get_db(self):
        return 'hoard'

    @classmethod
    def add(cls, account_id):
        """Creates a new profile for specific account and return it.

        If a profile exists, it will be return directly.

        :param account_id: the primary key of local account.
        :returns: the created (or existent) profile.
        """
        if not Account.get(account_id):
            raise NotFoundError(account_id, Account)

        existent = cls.get(account_id)
        if existent:
            return existent

        sql = ('insert into {.table_name} (account_id) values (%s) '
               'on duplicate key update account_id = %s').format(cls)
        params = (account_id, account_id)
        db.execute(sql, params)
        db.commit()

        from core.models.hoard.zhiwang.profile import ZhiwangProfile
        from core.models.hoard.xinmi.profile import XMProfile
        # if user hasn't zhiwang and xm profile
        if not ZhiwangProfile.get(account_id) and not XMProfile.get(account_id):
            add_savings_users()

        cls.clear_cache(account_id)
        cls.clear_cache_for_account_ids()
        return cls.get(account_id)

    @classmethod
    @cache(cache_key)
    def get(cls, account_id):
        """Gets a existent profile.

        :param account_id: the primary key of local account.
        :returns: the existent profile.
        """
        sql = ('select account_id, creation_time from {.table_name} '
               'where account_id = %s').format(cls)
        params = (account_id,)
        rs = db.execute(sql, params)
        if not rs:
            return
        return cls(*rs[0])

    @classmethod
    @cache(cache_account_ids_key)
    def get_account_ids(cls):
        sql = 'select account_id from {.table_name}'.format(cls)
        rs = db.execute(sql,)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_savings_users(cls):
        sql = 'select distinct user_id from hoard_order where status=%s or status=%s'
        params = (OrderStatus.confirmed.value, OrderStatus.exited.value)
        rs = db.execute(sql, params)
        return frozenset([r[0] for r in rs])

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(cls.cache_key.format(account_id=account_id))

    @classmethod
    def clear_cache_for_account_ids(cls):
        mc.delete(cls.cache_account_ids_key)

    @property
    def bank_name(self):
        if not self.bank_extra_info:
            return ''
        return self.bank_extra_info['bank_name']

    def is_identity_valid(self):
        warn('Please use Identity.get instead.', DeprecationWarning)
        return bool(self._identity)

    def active_amount_in_period(self, period):
        """累计给定的订单中同一封闭期的在账金额总数."""
        orders = self._cached_orders
        # TODO (tonyseek) extract the copied status text
        amount = sum(
            order.order_amount for order, _, status in orders
            if (status in [u'确认中', u'攒钱中', u'转出中'] and
                int(order.service.frozen_time) == int(period)))
        return amount

    @cached_property
    def on_account_invest_amount(self):
        """已攒但未到期金额"""
        orders = self._cached_orders
        amount = sum(
            order.order_amount for order, _, status in orders
            if status in [u'确认中', u'攒钱中', u'转出中'])
        return float(amount)

    @cached_property
    def total_invest_amount(self):
        """累计已攒金额"""
        orders = self._cached_orders
        amount = sum(
            order.order_amount for order, _, status in orders)
        return float(amount)

    @cached_property
    def daily_profit(self):
        """由每个订单的预期收益算出的每日收益(即昨日收益)"""
        orders = self._cached_orders
        return sum(order.fetch_daily_profit(orders) for order, _, _ in orders)

    @cached_property
    def yesterday_profit(self):
        return self.daily_profit

    @cached_property
    def total_profit(self):
        """由预期收益计算出的累计日收益(到昨日为止)"""
        orders = self._cached_orders
        today = date.today()
        return sum(
            order.fetch_profit_until(today, orders) for order, _, _ in orders)

    @cached_property
    def fin_ratio(self):
        if not self.plan_amount:
            return 0
        return self.on_account_invest_amount / int(self.plan_amount)

    @cached_property
    def _cached_orders(self):
        return self.orders()

    @classmethod
    def synchronize_in_worker(cls, account_id):
        hoard_yrd_order_syncronizer.produce(account_id)

    def orders(self, filter_due=False):
        account_info = self.person_account_info
        if not account_info:
            return []

        os_info = {}
        for info in account_info:
            os_info[info['finOrderNo']] = info

        os = HoardOrder.gets_by_user_id(self.account_id)

        orders = []

        for order in os:
            o_info = os_info.get(order.fin_order_id)
            if not o_info:
                continue
            order_status = ORDER_STATUS_MAP.get(
                o_info['finOrderStatus'], u'未知状态')
            if filter_due and order_status == u'已转出':
                continue
            if not o_info['frozenDate']:
                idate = datetime.strptime(o_info['investDate'], '%Y-%m-%d') \
                    + relativedelta(months=int(o_info['frozenTime'])) \
                    + relativedelta(days=3)
                o_info['frozenDatetime'] = idate
            else:
                o_info['frozenDatetime'] = datetime.strptime(
                    o_info['frozenDate'], '%Y-%m-%d')
            orders.append((order, o_info, order_status))

        if filter_due:
            # reverse the orders
            orders = sorted(orders, key=lambda x: x[1]['frozenDatetime'])

        return orders

MC_FETCH_ACCOUNT_STATUS_BY_USER = 'hoard:fetch:account:info:by:{user_id}:v1'


def fetch_account_info(profile):
    """fetch all of the account order info"""
    yixin_account = YixinAccount.get_by_local(profile.account_id)
    if not yixin_account:
        return

    fetch_status = mc.get(MC_FETCH_ACCOUNT_STATUS_BY_USER.format(
        user_id=profile.account_id))
    if fetch_status:
        return profile.person_account_info

    response = yixin.client.query.account_info(
        token=yixin_account.p2p_token, timeout=15)

    profile.person_account_info = response.data.p2pservice_list
    sync_orders_by_account_info(profile)

    # set fetch status with expire time
    mc.set(MC_FETCH_ACCOUNT_STATUS_BY_USER.format(
        user_id=profile.account_id), True)
    return profile.person_account_info


def sync_orders_by_account_info(profile):
    account_info = profile.person_account_info
    for info in account_info:
        order = HoardOrder.get_by_fin_order_id(info['finOrderNo'])
        if not order:
            continue
        if not order.order_id and order.stashed_order_id:
            order.mark_as_paid(order.stashed_order_id)


def clear_account_info_cache(user_id):
    mc.delete(MC_FETCH_ACCOUNT_STATUS_BY_USER.format(user_id=user_id))


@yrd_order_paid.connect
@yrd_order_confirmed.connect
@yrd_order_failure.connect
def on_order_status_changed(sender):
    clear_account_info_cache(sender.user_id)
