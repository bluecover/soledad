# coding: utf-8

from __future__ import absolute_import

import datetime
import decimal

from enum import Enum
from more_itertools import first

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.user.signals import user_register_completed
from core.models.notification import Notification
from core.models.notification.kind import (
    spring_gift_reserved_notification, spring_gift_obtained_notification)
from core.models.hoard.signals import zw_order_succeeded
from core.models.hoard.zhiwang import ZhiwangOrder
from core.models.hoard.zhiwang.errors import InvalidProductError
from core.models.hoard.placebo import PlaceboProduct, PlaceboOrder, strategies
from core.models.welfare.package.kind import spring_2016_package
from core.models.welfare.package.package import distribute_welfare_gift


class SpringGift(EntityModel):
    """2016 春节体验金."""

    table_name = 'promotion_spring_2016'
    cache_key = 'promotion:spring_2016:{id_}'
    cache_by_mobile_phone_key = 'promotion:spring_2016:m:{mobile_phone}:id_'
    cache_by_user_id_key = 'promotion:spring_2016:u:{user_id}:id_'

    placebo_order_amount = decimal.Decimal('8888')
    placebo_hike_amount = decimal.Decimal('2.2')

    class Status(Enum):
        #: 已获取活动资格
        reserved = 'R'

        #: 已获取一笔体验金
        obtained = 'O'

        #: 已分享加息
        upgraded = 'U'

    def __init__(self, id_, mobile_phone, status, order_id, user_id,
                 reserved_time, obtained_time, upgraded_time):
        self.id_ = str(id_)
        self.mobile_phone = mobile_phone
        self._status = status
        self.order_id = str(order_id)
        self.user_id = str(user_id)
        self.reserved_time = reserved_time
        self.obtained_time = obtained_time
        self.upgraded_time = upgraded_time

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        self._status = item.value

    @classmethod
    def add(cls, mobile_phone, status=Status.reserved):
        id_ = cls.get_id_by_mobile_phone(mobile_phone)
        if id_ is not None:
            return cls.get(id_)

        sql = (
            'insert into {0} (mobile_phone, status, order_id, user_id,'
            ' reserved_time, obtained_time, upgraded_time) '
            'values (%s, %s, %s, %s, %s, %s, %s)').format(cls.table_name)
        now = datetime.datetime.now()
        params = (mobile_phone, status.value, None, None, now, None, None)
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_mobile_phone(mobile_phone)

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, mobile_phone, status, order_id, user_id,'
            ' reserved_time, obtained_time, upgraded_time '
            'from {0} where id=%s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_by_mobile_phone_key)
    def get_id_by_mobile_phone(cls, mobile_phone):
        sql = 'select id from {0} where mobile_phone = %s'.format(cls.table_name)
        params = (mobile_phone,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    @cache(cache_by_user_id_key)
    def get_id_by_user_id(cls, user_id):
        sql = 'select id from {0} where user_id = %s'.format(cls.table_name)
        params = (user_id,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_user(cls, user):
        id_ = cls.get_id_by_user_id(user.id_)
        if id_:
            return cls.get(id_)
        if user.mobile:
            id_ = cls.get_id_by_mobile_phone(user.mobile)
            if id_:
                return cls.get(id_)

    def mark_as_obtained(self, user_id, order_id):
        if self.status is not self.Status.reserved:
            return False

        sql = (
            'update {0} set status = %s, user_id = %s, order_id = %s,'
            ' obtained_time = %s '
            'where id = %s and status = %s').format(self.table_name)
        params = (
            self.Status.obtained.value, user_id, order_id,
            datetime.datetime.now(), self.id_, self.Status.reserved.value)
        cursor = db.get_cursor()
        affected_rows = cursor.execute(sql, params)
        db.commit()

        self.status = self.Status.obtained
        self.clear_cache(self.id_)
        self.clear_cache_by_mobile_phone(self.mobile_phone)
        self.clear_cache_by_user(user_id)

        return affected_rows > 0

    def mark_as_upgraded(self):
        if self.status is not self.Status.obtained:
            return False

        sql = (
            'update {0} set status = %s, upgraded_time = %s '
            'where id = %s and status = %s').format(self.table_name)
        params = (
            self.Status.upgraded.value, datetime.datetime.now(),
            self.id_, self.Status.obtained.value)
        cursor = db.get_cursor()
        affected_rows = cursor.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)

        return affected_rows > 0

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_mobile_phone(cls, mobile_phone):
        mc.delete(cls.cache_by_mobile_phone_key.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_by_user_id_key.format(**locals()))


def get_placebo_product():
    """根据策略获取本次活动的体验金产品."""
    product_ids = PlaceboProduct.get_ids_by_strategy(
        strategies.strategy_2016_spring.id_)
    if len(product_ids) != 1:
        raise RuntimeError('placebo products are dirty')
    product_id = first(product_ids)
    return PlaceboProduct.get(product_id)


def get_placebo_order(user_id):
    """获取本次活动体验金订单."""
    order_ids = PlaceboOrder.get_ids_by_user(user_id)
    orders = (PlaceboOrder.get(order_id) for order_id in order_ids)
    product = get_placebo_product()
    return first((o for o in orders if o.product == product), None)


def reserve_spring_gift(mobile_phone):
    """预约体验金."""
    # 给老用户派发礼包
    is_new = SpringGift.get_id_by_mobile_phone(mobile_phone) is None
    user = Account.get_by_alias(mobile_phone)

    # 给新老用户预约体验金
    gift = SpringGift.add(mobile_phone)

    # 为老用户发放礼包并创建通知
    if gift and is_new and user:
        distribute_welfare_gift(user, spring_2016_package)
        notify_spring_gift(user, gift)

    return gift


def notify_spring_gift(user, gift):
    """创建体验金通知."""
    if gift.status is SpringGift.Status.reserved:
        Notification.create(user, spring_gift_reserved_notification, dict(
            spring_gift_id=gift.id_))
    elif gift.status is SpringGift.Status.obtained:
        Notification.create(user, spring_gift_obtained_notification, dict(
            spring_gift_id=gift.id_))


def obtain_spring_gift(user, order):
    """领取体验金."""
    gift = SpringGift.get_by_user(user)
    if not (
        gift and user.is_normal_account() and
        order.status is ZhiwangOrder.Status.success
    ):
        return

    product = get_placebo_product()
    try:
        order = PlaceboOrder.add(
            user_id=user.id_,
            product_id=product.id_,
            bankcard_id=order.bankcard.id_,
            amount=SpringGift.placebo_order_amount)
    except InvalidProductError:
        return

    is_affected = gift.mark_as_obtained(user.id_, order.id_)
    if is_affected:
        notify_spring_gift(user, gift)
    else:
        order.transfer_status(PlaceboOrder.Status.failure)


def upgrade_spring_gift(user):
    """微信分享为体验金加息."""
    gift = SpringGift.get_by_user(user)
    order = get_placebo_order(user.id_)
    if not (
        gift and order and user.is_normal_account()
    ):
        return

    is_affected = gift.mark_as_upgraded()
    if not is_affected:
        return
    if order.assign_annual_rate_hike(SpringGift.placebo_hike_amount):
        return order


@user_register_completed.connect
def after_user_register_completed(user):
    gift = SpringGift.get_by_user(user)
    if gift:
        # 用户完成注册领取到体验金资格，创建通知
        notify_spring_gift(user, gift)


@zw_order_succeeded.connect
def after_zw_order_succeeded(order):
    obtain_spring_gift(order.user, order)
