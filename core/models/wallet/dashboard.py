from __future__ import print_function, absolute_import, unicode_literals

import datetime
import operator
import decimal

from werkzeug.utils import cached_property

from .annual_rate import WalletAnnualRate
from .transaction import WalletTransaction
from .account import WalletAccount
from .profit import WalletProfit
from .providers import zhongshan


class PublicDashboard(object):
    """The public dashboard for all users (including anonymous users)."""

    provider = zhongshan

    def __init__(self, date):
        self.date = date

    @classmethod
    def today(cls):
        return cls(datetime.date.today())

    @cached_property
    def weekly_annual_rates(self):
        return WalletAnnualRate.get_multi_by_date_range(
            date_from=self.date - datetime.timedelta(days=7),
            date_to=self.date, fund_code=self.provider.fund_code)

    @cached_property
    def latest_annual_rate(self):
        if not self.weekly_annual_rates:
            return self._empty_annual_rate
        return max(self.weekly_annual_rates, key=operator.attrgetter('date'))

    @cached_property
    def _empty_annual_rate(self):
        return WalletAnnualRate(0, self.date, 0, 0, self.provider.fund_code)


class UserDashboard(object):
    """The dashboard for current user."""

    cache_key_for_balance = 'wallet:d:{self.wallet_account.id_}:balance'

    def __init__(self, date, account):
        assert isinstance(account, WalletAccount)
        self.date = date
        self.account = account

    @classmethod
    def today(cls, *args, **kwargs):
        return cls(datetime.date.today(), *args, **kwargs)

    @cached_property
    def balance(self):
        balance = WalletTransaction.get_balance_by_account(self.account.id_)
        return balance + self.total_profit_amount

    @cached_property
    def weekly_profits(self):
        date_range = (self.date - datetime.timedelta(days=7), self.date)
        return WalletProfit.get_multi_by_date(self.account, date_range)

    @cached_property
    def monthly_profits(self):
        date_range = (self.date - datetime.timedelta(days=30), self.date)
        return WalletProfit.get_multi_by_date(self.account, date_range)

    @cached_property
    def latest_profit(self):
        for p in self.weekly_profits:
            if p.date == datetime.date.today() - datetime.timedelta(days=1):
                return p

    @cached_property
    def latest_profit_amount(self):
        if not self.latest_profit:
            return decimal.Decimal(0)
        return self.latest_profit.amount

    @cached_property
    def weekly_profit_amount(self):
        if not self.weekly_profits:
            return decimal.Decimal(0)
        return sum(p.amount for p in self.weekly_profits)

    @cached_property
    def monthly_profit_amount(self):
        if not self.monthly_profits:
            return decimal.Decimal(0)
        return sum(p.amount for p in self.monthly_profits)

    @cached_property
    def total_profit_amount(self):
        return WalletProfit.get_total_by_account(self.account.id_)

    @cached_property
    def total_transations(self):
        ids = WalletTransaction.get_ids_by_account(self.account.id_)
        return len(WalletTransaction.get_multi(ids))
