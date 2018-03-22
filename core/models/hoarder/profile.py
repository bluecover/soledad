# coding: utf-8
from datetime import date

from werkzeug.utils import cached_property

from .asset import Asset


class HoarderProfile(object):

    def __init__(self, user_id):
        self.user_id = str(user_id)

    def assets(self):
        return Asset.gets_by_user_id(self.user_id)

    @cached_property
    def on_account_invest_amount(self):
        amount = sum(asset.total_amount for asset in self.assets()
                     if asset.status is Asset.Status.earning)
        return float(amount)

    @cached_property
    def total_invest_amount(self):
        amount = sum(asset.total_amount for asset in self.assets())
        return float(amount)

    @cached_property
    def daily_profit(self):
        return sum(asset.daily_profit for asset in self.assets())

    @cached_property
    def total_profit(self):
        today = date.today()
        return sum(asset.fetch_profit_until(today) for asset in self.assets())

    @cached_property
    def yesterday_profit(self):
        amount = sum(asset.yesterday_profit for asset in self.assets()
                     if asset.status is Asset.Status.earning)
        return amount
