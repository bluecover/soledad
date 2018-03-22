# coding: utf-8

import datetime
from decimal import Decimal

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.profile.bankcard import BankCard
from .product import Product
from .account import Account
from .order import HoarderOrder
from .errors import InvalidRedeemBankCardError


class Asset(PropsMixin):
    """资产"""

    table_name = 'hoarder_asset'

    class Status(Enum):
        """本地资产状态"""
        unpaid = 'U'
        earning = 'E'
        withdrawing = 'W'
        redeemed = 'R'
        cancel = 'C'

    cache_key = 'hoarder:asset:{asset_id}:v1'
    user_cache_key = 'hoarder:assets:user:{user_id}:{product_id}:v1'
    product_cache_key = 'hoarder:assets:all_ids:{product_id}:v1'
    order_code_cache_key = 'hoarder:asset:order:{order_code}:{product_id}:v1'
    user_id_cache_key = 'hoarder:assets:user_id:{user_id}:v1'

    # 实时年化收益率(日日盈类产品每日更新)
    actual_annual_rate = PropsItem('actual_annual_rate', 0.00, Decimal)
    # 累计收益
    hold_profit = PropsItem('hold_profit', 0.00, Decimal)
    # 持有资产
    hold_amount = PropsItem('hold_amount', 0.00, Decimal)
    # 未到账资产
    uncollected_amount = PropsItem('uncollected_amount', 0.00, Decimal)
    # 昨日收益
    yesterday_profit = PropsItem('yesterday_profit', 0, Decimal)
    # 剩余免费赎回次数
    residual_redemption_times = PropsItem('residual_redemption_times', 0, int)

    def __init__(self, id_, asset_no, order_code, bankcard_id, bank_account, product_id, user_id,
                 status, remote_status, annual_rate, create_amount, current_amount,
                 fixed_service_fee, service_fee_rate, base_interest, expect_interest,
                 current_interest, interest_start_date, interest_end_date, expect_payback_date,
                 buy_time, creation_time, update_time):
        self.id_ = id_
        self.asset_no = asset_no
        self.order_code = order_code
        self.bankcard_id = bankcard_id
        self.bank_account = bank_account
        self.product_id = product_id
        self.user_id = user_id
        self._status = status
        self.remote_status = remote_status
        self.annual_rate = annual_rate
        self.create_amount = create_amount
        self.current_amount = current_amount
        self.fixed_service_fee = fixed_service_fee
        self.service_fee_rate = service_fee_rate
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
        return '<Asset %s>' % self.id_

    def get_db(self):
        return 'hoarder'

    def get_uuid(self):
        return 'hoarder:asset:{.id_}'.format(self)

    def is_owner(self, user):
        return user and user.id_ == self.user_id

    @cached_property
    def product(self):
        return Product.get(self.product_id)

    @cached_property
    def user(self):
        return Account.get(self.user_id)

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
        }.get(self.status.value, u'未知')

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

    def update_service_fee(self, fixed_service_fee, service_fee_rate):
        need_update = False
        if self.fixed_service_fee != fixed_service_fee:
            self.fixed_service_fee = fixed_service_fee
            need_update = True
        if self.service_fee_rate != service_fee_rate:
            self.service_fee_rate = service_fee_rate
            need_update = True
        if not need_update:
            return
        sql = ('update {.table_name} set fixed_service_fee=%s, service_fee_rate=%s '
               'where id=%s').format(self)
        params = (self.fixed_service_fee, self.service_fee_rate, self.id_,)
        db.execute(sql, params)
        db.commit()
        self.clear_cache()

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
    def add(cls, asset_no, order_code, bankcard_id, bank_account, product_id, user_id, status,
            remote_status, fixed_service_fee, service_fee_rate,
            annual_rate, create_amount, current_amount, base_interest,
            expect_interest, current_interest, interest_start_date,
            interest_end_date, expect_payback_date, buy_time, creation_time=None):

        sql = ('insert into {.table_name}(asset_no, order_code, bankcard_id, bank_account, '
               'product_id, user_id, status, remote_status, fixed_service_fee, service_fee_rate, '
               'annual_rate, create_amount, '
               'current_amount, base_interest, expect_interest, current_interest, '
               'interest_start_date, interest_end_date, expect_payback_date, buy_time, '
               'creation_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
               '%s, %s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (asset_no, order_code, bankcard_id, bank_account, product_id, user_id,
                  status.value, remote_status, fixed_service_fee, service_fee_rate, annual_rate,
                  create_amount, current_amount,
                  base_interest, expect_interest, current_interest, interest_start_date,
                  interest_end_date, expect_payback_date, buy_time,
                  creation_time or datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        instance = cls.get(id_)
        instance.clear_cache()
        return instance

    def update_bankcard(self, new_card):
        """更新资产回款卡（当且仅当用户挂失银行卡情况被确认并修改后调用）"""
        assert isinstance(new_card, BankCard)

        if new_card.user_id != self.user_id or new_card.status is not BankCard.Status.active:
            raise InvalidRedeemBankCardError()

        sql = 'update {.table_name} set bankcard_id=%s where id=%s'.format(self)
        params = (new_card.id_, self.id_)
        self._commit_and_refresh(sql, params)

    @classmethod
    @cache(cache_key)
    def get(cls, asset_id):
        sql = ('select id, asset_no, order_code, bankcard_id, bank_account, product_id, '
               'user_id, status, remote_status, annual_rate, create_amount, current_amount, '
               'fixed_service_fee, service_fee_rate, base_interest, expect_interest, '
               'current_interest, interest_start_date, interest_end_date, '
               'expect_payback_date, buy_time, creation_time, update_time from {.table_name} '
               'where id = %s').format(cls)
        params = (asset_id,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_asset_no_with_product_id(cls, asset_no, product_id):
        sql = ('select id from {.table_name} where '
               'asset_no=%s, product_id=%s').format(cls)
        params = (asset_no, product_id,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(order_code_cache_key)
    def get_by_order_code_with_product_id(cls, order_code, product_id):
        sql = ('select id from {.table_name} where '
               'order_code=%s, product_id=%s').format(cls)
        params = (order_code, product_id,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(user_cache_key)
    def get_id_list_by_user_id_with_product_id(cls, user_id, product_id):
        sql = ('select id from {.table_name} where user_id = %s and product_id=%s '
               'order by creation_time desc').format(cls)
        params = (user_id, product_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def gets_by_user_id_with_product_id(cls, user_id, product_id):
        ids = cls.get_id_list_by_user_id_with_product_id(user_id, product_id)
        return [cls.get(id_) for id_ in ids]

    def _commit_and_refresh(self, sql, params):
        db.execute(sql, params)
        db.commit()
        self.clear_cache()

        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

    def clear_cache(self):
        mc.delete(self.cache_key.format(asset_id=self.id_))
        mc.delete(self.user_id_cache_key.format(user_id=self.user_id))
        mc.delete(self.user_cache_key.format(user_id=self.user_id, product_id=self.product_id))
        mc.delete(self.order_code_cache_key.format(order_code=self.order_code,
                                                   product_id=self.product_id))
        mc.delete(self.product_cache_key.format(product_id=self.product_id))

    @classmethod
    @cache(user_id_cache_key)
    def get_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id = %s '
               'order by creation_time desc').format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(product_cache_key)
    def get_ids_by_product_id(cls, product_id):
        sql = ('select id from {.table_name} where product_id = %s '
               'order by creation_time desc').format(cls)

        params = (product_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def gets_by_user_id(cls, user_id):
        ids = cls.get_id_list_by_user_id(user_id)
        return [cls.get(id_) for id_ in ids]

    @property
    def total_amount(self):
        return self.hold_amount + self.uncollected_amount

    @property
    def redeemed_amount_today(self):
        return HoarderOrder.get_redeemed_amount_by_user_today(self.user_id)

    @property
    def remaining_amount_today(self):
        if not self.product.can_redeem:
            return 0
        return min(self.hold_amount,
                   self.product.day_redeem_amount - self.redeemed_amount_today,
                   self.product.max_redeem_amount - self.redeemed_amount_today)
