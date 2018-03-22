# coding: utf-8

import datetime
from decimal import Decimal
from more_itertools import first


from enum import Enum
from functools import partial
from werkzeug.utils import cached_property
from xmlib.consts import OrderStatus
from envcfg.json.solar import DEBUG

from jupiter.workers.hoard_xm import xm_send_exit_sms as mq_sms_sender
from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin
from core.models.profile.bankcard import BankCard
from core.models.user.account import Account
from .product import XMProduct
from .order import XMOrder
from .errors import (
    AssetCreatedError, UnknownOrderError, UnmatchedOrderInfoError, InvalidRedeemBankCardError)
from ..providers import xmpay
from ..signals import xm_asset_redeemed

unicode_type = partial(str.decode, encoding='utf-8')


class XMAsset(PropsMixin):
    class Status(Enum):
        unpaid = 'U'
        earning = 'E'
        withdrawing = 'W'
        redeemed = 'R'
        cancel = 'C'

    MUTUAL_STATUS_MAP = {
        OrderStatus.waiting: Status.unpaid,
        OrderStatus.paying: Status.unpaid,
        OrderStatus.payed: Status.earning,
        OrderStatus.applying: Status.earning,
        OrderStatus.applyed: Status.earning,
        OrderStatus.redeeming: Status.withdrawing,
        OrderStatus.finished: Status.redeemed,
        OrderStatus.auto_cancel: Status.cancel,
        OrderStatus.user_cancel: Status.cancel
    }

    provider = xmpay
    table_name = 'hoard_xm_asset'
    cache_key = 'hoard:xm:asset:{id_}:v1'
    user_cache_key = 'hoard:xm:assets:user:{user_id}:v1'
    order_code_cache_key = 'hoard:xm:asset:order:{order_code}:v1'
    cache_key_payback_date_sorted_id_list_by_user_id = (
        'hoard:xm:asset:payback_date_sorted_id_list:{user_id}')

    def __init__(self, id_, asset_no, order_code, bankcard_id, bank_account, product_id, user_id,
                 status, annual_rate, actual_annual_rate, create_amount, current_amount,
                 base_interest, expect_interest, current_interest, interest_start_date,
                 interest_end_date, expect_payback_date, buy_time, creation_time, update_time):
        self.id_ = str(id_)
        self.asset_no = asset_no
        self.order_code = order_code
        self.bankcard_id = bankcard_id
        self.bank_account = bank_account
        self.product_id = str(product_id)
        self.user_id = str(user_id)
        self._status = status
        self.annual_rate = annual_rate
        self.actual_annual_rate = actual_annual_rate
        self.create_amount = create_amount
        self.current_amount = current_amount
        self.base_interest = base_interest
        self.expect_interest = expect_interest
        self.current_interest = current_interest
        self.interest_start_date = interest_start_date
        self.interest_end_date = interest_end_date
        self.expect_payback_date = expect_payback_date
        self.buy_time = buy_time
        self.creation_time = creation_time
        self.update_time = update_time

    def __str__(self):
        return '<XMAsset %s>' % self.id_

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'xm:asset:{.id_}'.format(self)

    def is_owner(self, user):
        return user and user.id == self.user_id

    @cached_property
    def product(self):
        return XMProduct.get(self.product_id)

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def order(self):
        return XMOrder.get_by_order_code(self.order_code)

    @property
    def bankcard(self):
        if not self.bankcard_id:
            return
        return BankCard.get(self.bankcard_id)

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        sql = 'update {.table_name} set status=%s where id=%s;'.format(self)
        params = (item.value, self.id_,)
        db.execute(sql, params)
        db.commit()
        self.clear_cache()
        self._status = item.value

    @property
    def display_status(self):
        return {
            'U': u'处理中',
            'E': u'攒钱中',
            'W': u'转出中',
            'R': u'已转出',
            'C': u'已取消',
        }.get(self.status.value, '未知')

    @property
    def frozen_days(self):
        return (self.interest_end_date - self.interest_start_date).days

    @property
    def daily_profit(self):
        """资产平均到每日的收益."""
        # 当资产到期时，每日收益变为0
        if self.status is not self.Status.earning:
            return Decimal(0)

        # 当超出攒钱封闭期时，每日收益变为0
        if (self.interest_start_date.date() <=
                datetime.date.today() <
                self.interest_end_date.date()):
            return self.expect_interest / self.frozen_days
        return Decimal(0)

    def fetch_profit_until(self, date):
        """该资产到某日为止的累计收益."""
        # 已转出则返回已结算的收益
        if self.status is self.Status.redeemed:
            return self.current_interest

        # 未转出则使用预期每日收益按日累加
        if date >= self.interest_end_date.date():
            return self.expect_interest
        elif date < self.interest_start_date.date():
            return Decimal(0)
        else:
            return (date - self.interest_start_date.date()).days * self.daily_profit

    @classmethod
    def check_before_adding(cls, asset_no, order_code, create_amount, product_id):
        pair = (asset_no, order_code)
        order = XMOrder.get_by_order_code(order_code)
        if not order:
            raise UnknownOrderError('unknown order %s|%s' % pair)
        check_conditions = [('product_id', order.product_id != str(product_id))]

        if not DEBUG:
            check_conditions.append(('order_amount', int(order.amount) != int(create_amount)))
        unmatched = [field_name for field_name, field_unmatched in check_conditions
                     if field_unmatched]

        if unmatched:
            raise UnmatchedOrderInfoError('unmatched info %s|%s:(%s)' %
                                          (asset_no, order_code, unmatched))

        if cls.get_by_asset_no(asset_no) or cls.get_by_order_code(order_code):
            raise AssetCreatedError('asset created %s|%s' % pair)

    @classmethod
    def add(cls, asset_no, order_code, bankcard_id, bank_account, product_id, user_id, status,
            annual_rate, actual_annual_rate, create_amount, current_amount, base_interest,
            expect_interest, current_interest, interest_start_date,
            interest_end_date, expect_payback_date, buy_time, creation_time=None):
        try:
            cls.check_before_adding(asset_no, order_code, create_amount, product_id)
        except AssetCreatedError:
            return None

        sql = ('insert into {.table_name}(asset_no, order_code, bankcard_id, bank_account, '
               'product_id, user_id, status, annual_rate, actual_annual_rate, create_amount, '
               'current_amount, base_interest, expect_interest, current_interest, '
               'interest_start_date, interest_end_date, expect_payback_date, buy_time, '
               'creation_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
               '%s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (asset_no, order_code, bankcard_id, bank_account, product_id, user_id,
                  status.value, annual_rate, actual_annual_rate, create_amount, current_amount,
                  base_interest, expect_interest, current_interest, interest_start_date,
                  interest_end_date, expect_payback_date, buy_time,
                  creation_time or datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        instance = cls.get(id_)
        instance.clear_cache()
        return instance

    def update_bankcard(self, new_card):
        """更新资产回款卡（当且仅当用户挂失银行卡情况被新米确认并修改后调用）"""
        assert isinstance(new_card, BankCard)

        if new_card.user_id != self.user_id or new_card.status is not BankCard.Status.active:
            raise InvalidRedeemBankCardError()

        sql = ('update {.table_name} set bankcard_id=%s where id=%s').format(self)
        params = (new_card.id_, self.id_)
        self._commit_and_refresh(sql, params)

    def synchronize(self, new_status, current_amount, current_interest, bank_account):
        """根据新米接口更新资产属性"""
        assert isinstance(new_status, self.Status)

        original_status = self.status
        if all([new_status is original_status,
                current_amount == self.current_amount,
                current_interest == self.current_interest,
                bank_account == self.bank_account]):
            return

        sql = ('update {.table_name} set status=%s, current_amount=%s, '
               'current_interest=%s, bank_account=%s where id=%s').format(self)
        params = (new_status.value, current_amount, current_interest, bank_account, self.id_)
        self._commit_and_refresh(sql, params)

        if new_status is not original_status and new_status is self.Status.redeemed:
            # 发出赎回信号
            xm_asset_redeemed.send(self)

            # 发送赎回短信提醒
            mq_sms_sender.produce(self.id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, asset_no, order_code, bankcard_id, bank_account, product_id, '
               'user_id, status, annual_rate, actual_annual_rate, create_amount, '
               'current_amount, base_interest, expect_interest, current_interest, '
               'interest_start_date, interest_end_date, expect_payback_date, buy_time, '
               'creation_time, update_time from {.table_name} where id = %s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_asset_no(cls, asset_no):
        sql = ('select id from {.table_name} where '
               'asset_no=%s').format(cls)
        params = (asset_no,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(order_code_cache_key)
    def get_by_order_code(cls, order_code):
        sql = ('select id from {.table_name} where '
               'order_code=%s').format(cls)
        params = (order_code,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(user_cache_key)
    def get_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id = %s '
               'order by creation_time desc').format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def gets_by_user_id(cls, user_id):
        ids = cls.get_id_list_by_user_id(user_id)
        return [cls.get(id_) for id_ in ids]

    @classmethod
    @cache(cache_key_payback_date_sorted_id_list_by_user_id)
    def _get_payback_date_sorted_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id=%s and status=%s'
               ' order by expect_payback_date, buy_time').format(cls)
        params = (user_id, cls.Status.redeemed.value)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_first_redeemed_asset_by_user_id(cls, user_id):
        ids = cls._get_payback_date_sorted_id_list_by_user_id(user_id)
        assets = (cls.get(id_) for id_ in ids)
        return first((o for o in assets), None)

    def _commit_and_refresh(self, sql, params):
        db.execute(sql, params)
        db.commit()
        self.clear_cache()

        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

    def clear_cache(self):
        mc.delete(self.cache_key.format(id_=self.id_))
        mc.delete(self.user_cache_key.format(user_id=self.user_id))
        mc.delete(self.order_code_cache_key.format(order_code=self.order_code))
