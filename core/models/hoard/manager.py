# coding: utf-8

from datetime import datetime

from werkzeug.utils import cached_property

from core.models.hoard import HoardOrder, HoardProfile
from core.models.hoard.stats import get_savings_amount, get_savings_users
from core.models.hoard.zhiwang import ZhiwangOrder, ZhiwangProfile
from core.models.hoard.xinmi import XMProfile, XMOrder


__all__ = ['SavingsManager']


def combined_property(name):
    def wrapped(self):
        return sum([
            (getattr(self.yx_profile, name) if self.yx_profile else 0),
            (getattr(self.zw_profile, name) if self.zw_profile else 0),
            (getattr(self.xm_profile, name) if self.xm_profile else 0),
            (getattr(self.hoarder_profile, name) if self.hoarder_profile else 0)
        ])
    wrapped.__name__ = wrapped.func_name = name
    return cached_property(wrapped)


class SavingsManager(object):
    """用户的攒钱助手梗概"""

    on_account_invest_amount = combined_property('on_account_invest_amount')
    total_invest_amount = combined_property('total_invest_amount')
    total_profit = combined_property('total_profit')

    def __init__(self, user_id):
        self.user_id = user_id
        self.yx_profile = HoardProfile.get(user_id)
        self.zw_profile = ZhiwangProfile.get(user_id)
        self.xm_profile = XMProfile.get(user_id)
        from core.models.hoarder.profile import HoarderProfile
        self.hoarder_profile = HoarderProfile(user_id)

    @classmethod
    def get_savings_users(cls):
        return HoardProfile.get_savings_users().union(ZhiwangProfile.get_savings_users())

    @property
    def plan_amount(self):
        if not self.yx_profile:
            return 0
        return int(self.yx_profile.plan_amount or 0)

    @cached_property
    def fin_ratio(self):
        if not self.plan_amount:
            return 0
        return self.on_account_invest_amount / self.plan_amount

    @cached_property
    def total_saving_amount(self):
        # FIXME: naming typo: saving -> savings
        return get_savings_amount()

    @cached_property
    def total_saving_users(self):
        return get_savings_users()

    def refresh_profile(self):
        if self.yx_profile:
            self.yx_profile.orders()

    @cached_property
    def total_orders(self):
        from core.models.hoarder.order import HoarderOrder
        yx_orders = HoardOrder.get_total_orders(self.user_id)
        zw_orders = ZhiwangOrder.get_total_orders(self.user_id)
        xm_orders = XMOrder.get_total_orders(self.user_id)
        sxb_orders = HoarderOrder.get_order_amount_by_user(self.user_id)
        return yx_orders + zw_orders + xm_orders + sxb_orders

    @property
    def daily_profit(self):
        amount = 0
        amount += self.yx_profile.daily_profit if self.yx_profile else 0
        amount += self.zw_profile.daily_profit if self.zw_profile else 0
        amount += self.xm_profile.daily_profit if self.xm_profile else 0
        amount += self.hoarder_profile.yesterday_profit if self.hoarder_profile else 0
        return amount

    @property
    def yesterday_profit(self):
        amount = 0
        amount += self.yx_profile.yesterday_profit if self.yx_profile else 0
        amount += self.zw_profile.yesterday_profit if self.zw_profile else 0
        amount += self.xm_profile.yesterday_profit if self.xm_profile else 0
        amount += self.hoarder_profile.yesterday_profit if self.hoarder_profile else 0
        return amount

    @property
    def is_new_savings_user(self):
        return self.total_orders == 0

    def has_bought_newcomer_product(self):
        """判断是否购买了新手产品
           暂时适用于2016年5月1日之后购买第一笔订单的用户"""
        from core.models.hoarder.order import HoarderOrder
        if ZhiwangOrder.has_wrapped_product(self.user_id):
            return True
        start_time = datetime(2016, 05, 01, 0, 0, 0)

        xm_orders = XMOrder.get_multi_by_user(self.user_id)
        xm_orders = [o for o in xm_orders if o.status in [XMOrder.Status.committed,
                                                          XMOrder.Status.shelved,
                                                          XMOrder.Status.paying,
                                                          XMOrder.Status.success]
                     ]
        xm_order = xm_orders[-1] if len(xm_orders) > 0 else None
        condition_xm_orders = bool(xm_order and xm_order.creation_time < start_time)
        orders = HoarderOrder.get_multi_by_user(self.user_id)
        orders = [o for o in orders if o.status in [HoarderOrder.Status.committed,
                                                    HoarderOrder.Status.shelved,
                                                    HoarderOrder.Status.paying,
                                                    HoarderOrder.Status.success]
                  ]
        order = orders[-1] if len(orders) > 0 else None
        condition_orders = bool(order and order.creation_time < start_time)

        if any([HoardOrder.get_total_orders(self.user_id) > 0,
                ZhiwangOrder.get_total_orders(self.user_id) > 0,
                condition_xm_orders, condition_orders]):
            return True
        return False
