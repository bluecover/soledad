# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from werkzeug.utils import cached_property

from jupiter.ext import xinmi
from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.account import Account
from core.models.profile.bankcard import BankCardManager
from .account import XMAccount
from .asset import XMAsset
from .order import XMOrder
from ..stats import add_savings_users
from ..errors import NotFoundError


class XMProfile(object):
    table_name = 'hoard_xm_profile'
    cache_key = 'hoard:xm:profile:{account_id}'

    def __init__(self, account_id, creation_time):
        self.account_id = str(account_id)
        self.creation_time = creation_time

    @cached_property
    def bankcards(self):
        return BankCardManager(self.account_id)

    @cached_property
    def xm_account(self):
        return XMAccount.get_by_local(self.account_id)

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'xm:profile:%s' % self.account_id

    @classmethod
    def add(cls, account_id):
        if not Account.get(account_id):
            raise NotFoundError(account_id, Account)

        existent = cls.get(account_id)
        if existent:
            # 临时做法，弥补之前未添加创建时间的错误
            if existent.creation_time is None:
                supply_sql = ('update {.table_name} set creation_time=%s'
                              'where account_id=%s').format(cls)
                supply_params = (datetime.now(), account_id)
                db.execute(supply_sql, supply_params)
                db.commit()
                cls.clear_cache(account_id)
            return existent

        sql = ('insert into {.table_name} (account_id, creation_time) '
               'values (%s, %s) '
               'on duplicate key update account_id = account_id').format(cls)
        params = (account_id, datetime.now())
        db.execute(sql, params)
        db.commit()

        from core.models.hoard.profile import HoardProfile
        # if user hasn't hoard profile
        # TODO: Users must diff with zhiwangs
        if not HoardProfile.get(account_id):
            add_savings_users()

        cls.clear_cache(account_id)
        return cls.get(account_id)

    @classmethod
    @cache(cache_key)
    def get(cls, account_id):
        sql = ('select account_id, creation_time '
               'from {.table_name} where account_id = %s').format(cls)
        params = (account_id,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    def orders(self):
        """用户所有进入结算的订单"""
        return [order for order in XMOrder.gets_by_user_id(self.account_id)
                if order.status not in (XMOrder.Status.unpaid, XMOrder.Status.committed,
                                        XMOrder.Status.failure)]

    def mixins(self, filter_due=False):
        # TODO modify the confused naming `filter_due`
        return list(self.iter_mixins(exclude_due=filter_due))

    def iter_mixins(self, exclude_due=False):
        for order in self.orders():
            asset = XMAsset.get_by_order_code(order.order_code)
            if exclude_due:
                if order.status is not XMOrder.Status.success:
                    continue
                if asset and asset.status is XMAsset.Status.redeemed:
                    continue
            yield (order, asset)

    def assets(self, pull_remote=False):
        """获取用户所有资产"""
        if not self.account_id:
            return []
        if pull_remote:
            orders = XMOrder.gets_by_user_id(self.account_id)
            for order in orders:
                remote_asset = xinmi.get_invest(order.order_code)
                self.synchronize_asset(order, remote_asset)
        return XMAsset.gets_by_user_id(self.account_id)

    def synchronize_asset(self, order, remote_asset):
        # 资产可能变动的属性：状态，当前资产金额，当前利息，回款银行卡(用户线下变更)
        if not self.xm_account:
            return
        asset = XMAsset.get_by_order_code(order.order_code)
        if not asset:
            XMAsset.add(asset_no=remote_asset.invest_id or remote_asset.order_id,
                        order_code=xinmi.get_order_id(remote_asset.order_id),
                        bank_account=order.bankcard.card_number, bankcard_id=order.bankcard_id,
                        product_id=remote_asset.product_id,
                        user_id=remote_asset.user_id,
                        status=XMAsset.MUTUAL_STATUS_MAP.get(remote_asset.order_status),
                        annual_rate=remote_asset.return_rate,
                        actual_annual_rate=remote_asset.return_rate,
                        create_amount=remote_asset.buy_amount,
                        current_amount=remote_asset.buy_amount,
                        base_interest=remote_asset.buy_amount,
                        expect_interest=order.expect_interest,
                        current_interest=remote_asset.return_amount,
                        interest_start_date=remote_asset.effect_date,
                        interest_end_date=remote_asset.product_expire_date,
                        expect_payback_date=remote_asset.finish_time,
                        buy_time=remote_asset.buy_time)
        else:
            status = XMAsset.MUTUAL_STATUS_MAP.get(remote_asset.order_status)
            if status in [XMAsset.Status.redeemed, XMAsset.Status.withdrawing,
                          XMAsset.Status.earning, XMAsset.Status.cancel]:
                asset.status = status
                order.status = XMOrder.MUTUAL_STATUS_MAP.get(remote_asset.order_status)

    @cached_property
    def on_account_invest_amount(self):
        """已攒但未到期金额"""
        amount = sum(asset.create_amount for asset in self.assets()
                     if asset.status is XMAsset.Status.earning)
        return float(amount)

    @cached_property
    def total_invest_amount(self):
        """新米总资产"""
        amount = sum(asset.create_amount for asset in self.assets())
        return float(amount)

    def get_valid_asset(self, assets, valid_status):
        """根据传入的状态筛选asset"""
        if assets is None:
            return
        for asset in assets:
            if asset.status in valid_status:
                yield asset

    @cached_property
    def daily_profit(self):
        """由每个资产的预期收益算出的每日收益(即昨日收益)"""
        valid_status = [XMAsset.Status.earning]
        return sum(asset.daily_profit for asset in
                   self.get_valid_asset(self.assets(), valid_status))

    @cached_property
    def total_profit(self):
        """由预期收益计算出的累计日收益(到昨日为止)"""
        today = date.today()
        valid_status = [XMAsset.Status.earning, XMAsset.Status.redeemed]
        return sum(asset.fetch_profit_until(today) for asset in
                   self.get_valid_asset(self.assets(), valid_status))

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(cls.cache_key.format(account_id=account_id))

    @cached_property
    def yesterday_profit(self):
        valid_status = [XMAsset.Status.earning, XMAsset.Status.redeemed]
        today = date.today()
        yesterday = today - timedelta(1)
        profit_until_yesterday = sum(asset.fetch_profit_until(yesterday) for asset in
                                     self.get_valid_asset(self.assets(), valid_status))
        profit_until_today = sum(asset.fetch_profit_until(today) for asset in
                                 self.get_valid_asset(self.assets(), valid_status))
        return profit_until_today - profit_until_yesterday
