# coding: utf-8

from collections import OrderedDict
from operator import attrgetter
from datetime import datetime, timedelta
from werkzeug.utils import cached_property

from .coupon import Coupon


class CouponManager(object):
    """用户礼券管理

    :param user_id: 礼券使用者的用户 ID
    """

    def __init__(self, user_id):
        self.user_id = user_id

    @cached_property
    def deduplicated_available_coupons(self):
        return OrderedDict((c.kind.id_, c) for c in self.available_coupons).values()

    @cached_property
    def available_coupons(self):
        statuses = (Coupon.Status.in_wallet,)
        coupons = self.get_coupons_by_statuses(statuses)
        return sorted([c for c in coupons if not c.outdated], key=attrgetter('sort_key'))

    @cached_property
    def history_coupons(self):
        """近一个月内过期或用掉的礼券"""
        unconsumeds = self.get_coupons_by_statuses((Coupon.Status.in_wallet, ))
        unconsumeds = [c for c in unconsumeds if c.outdated and c.expire_time +
                       timedelta(days=30) > datetime.now()]

        consumeds = [c for c in self.consumed_coupons if c.consumed_time +
                     timedelta(days=30) > datetime.now()]
        return sorted(consumeds + unconsumeds, key=attrgetter('sort_key'))

    @cached_property
    def consumed_coupons(self):
        statuses = (Coupon.Status.consumed,)
        coupons = self.get_coupons_by_statuses(statuses)
        return sorted(coupons, key=attrgetter('consumed_time'))

    def get_coupons_by_statuses(self, statuses):
        coupons = Coupon.get_multi_by_user(self.user_id)
        return [c for c in coupons if c.status in statuses]
