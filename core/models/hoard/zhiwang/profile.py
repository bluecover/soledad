# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from flask import current_app
from werkzeug.utils import cached_property
from requests.exceptions import RequestException

from zwlib.client import RemoteError

from jupiter.ext import sentry, zhiwang
from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.account import Account
from core.models.profile.bankcard import BankCardManager
from .account import ZhiwangAccount
from .asset import ZhiwangAsset
from .order import ZhiwangOrder
from .order import ZhiwangProduct
from ..stats import add_savings_users
from ..errors import NotFoundError


class ZhiwangProfile(object):
    table_name = 'hoard_zhiwang_profile'
    cache_key = 'hoard:zhiwang:profile:{account_id}'

    def __init__(self, account_id, creation_time):
        self.account_id = str(account_id)
        self.creation_time = creation_time

    @cached_property
    def bankcards(self):
        return BankCardManager(self.account_id)

    @cached_property
    def zhiwang_account(self):
        return ZhiwangAccount.get_by_local(self.account_id)

    @cached_property
    def count_saving_fdb(self):
        """指旺房贷宝订单数量"""
        orders = ZhiwangOrder.gets_by_user_id(self.account_id)
        return len([o for o in orders
                    if o.product.product_type == ZhiwangProduct.Type.fangdaibao])

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'zhiwang:profile:%s' % self.account_id

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

    @classmethod
    def get_savings_users(cls):
        sql = ('select distinct user_id from hoard_zhiwang_order where status=%s')
        params = (ZhiwangOrder.Status.success.value,)
        rs = db.execute(sql, params)
        return frozenset([r[0] for r in rs])

    def orders(self):
        """用户所有进入结算的订单"""
        return [order for order in ZhiwangOrder.gets_by_user_id(self.account_id)
                if order.status not in (ZhiwangOrder.Status.unpaid, ZhiwangOrder.Status.committed,
                                        ZhiwangOrder.Status.failure)]

    def assets(self, pull_remote=False):
        """获取用户所有资产"""
        if not self.zhiwang_account:
            return []
        if pull_remote:
            remote_assets = zhiwang.asset_list(self.zhiwang_account.zhiwang_id)
            for remote_asset in remote_assets:
                self.synchronize_asset(remote_asset.asset_code)
        return ZhiwangAsset.gets_by_user_id(self.account_id)

    def synchronize_asset(self, asset_code, raises=False):
        # 资产可能变动的属性：状态，当前资产金额，当前利息，回款银行卡(用户线下变更)
        if not self.zhiwang_account:
            return
        asset = ZhiwangAsset.get_by_asset_no(asset_code)
        if not asset or asset.user_id != self.account_id:
            return

        try:
            detail = zhiwang.asset_details(self.zhiwang_account.zhiwang_id, asset_code)
        except (RemoteError, RequestException):
            if raises:
                raise
            if current_app:
                sentry.captureException()
            return

        status = ZhiwangAsset.MUTUAL_STATUS_MAP.get(detail.status)
        asset.synchronize(status, detail.current_amount,
                          detail.current_interest, detail.user_bank_account)

    def mixins(self, filter_due=False):
        # TODO modify the confused naming `filter_due`
        return list(self.iter_mixins(exclude_due=filter_due))

    def iter_mixins(self, exclude_due=False):
        for order in self.orders():
            asset = ZhiwangAsset.get_by_order_code(order.order_code)
            if exclude_due:
                if order.status is not ZhiwangOrder.Status.success:
                    continue
                if asset and asset.status is ZhiwangAsset.Status.redeemed:
                    continue
            yield (order, asset)

    @cached_property
    def on_account_invest_amount(self):
        """已攒但未到期金额"""
        amount = sum(asset.create_amount for asset in self.assets()
                     if asset.status is not ZhiwangAsset.Status.redeemed)
        return float(amount)

    @cached_property
    def total_invest_amount(self):
        """指旺总资产"""
        amount = sum(asset.create_amount for asset in self.assets())
        return float(amount)

    @cached_property
    def daily_profit(self):
        """由每个资产的预期收益算出的每日收益(即昨日收益)"""
        return sum(asset.daily_profit for asset in self.assets())

    @cached_property
    def total_profit(self):
        """由预期收益计算出的累计日收益(到昨日为止)"""
        today = date.today()
        return sum(asset.fetch_profit_until(today) for asset in self.assets())

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(cls.cache_key.format(account_id=account_id))

    @cached_property
    def yesterday_profit(self):
        today = date.today()
        yesterday = today - timedelta(1)
        profit_until_yesterday = sum(asset.fetch_profit_until(yesterday) for asset in self.assets())
        profit_until_today = sum(asset.fetch_profit_until(today) for asset in self.assets())
        return profit_until_today - profit_until_yesterday
