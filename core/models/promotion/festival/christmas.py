# coding: utf-8

from __future__ import absolute_import

import datetime

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.user.signals import user_register_completed
from core.models.welfare.firewood import FirewoodWorkflow
from core.models.profile.signals import identity_saved
from core.models.profile.identity import Identity
from core.models.welfare.package.package import Package, distribute_welfare_gift
from core.models.welfare.package.kind import (
    christmas_primary_package, christmas_medium_package, christmas_best_package)


class ChristmasGift(EntityModel):
    """2015 圣诞节烤蛋糕小游戏."""

    table_name = 'promotion_christmas_2015'
    cache_key = 'promotion:christmas_2015:{id_}:v1'
    cache_by_mobile_phone_key = 'promotion:christmas_2015:m:{mobile_phone}:id_:v1'

    class Rank(Enum):
        one_cake = 1
        two_cakes = 2
        three_cakes = 3

    Rank.one_cake.award = christmas_primary_package
    Rank.two_cakes.award = christmas_medium_package
    Rank.three_cakes.award = christmas_best_package

    def __init__(self, id_, mobile_phone, rank, is_awarded, awarded_package_id,
                 updated_time, created_time):
        self.id_ = str(id_)
        self.mobile_phone = mobile_phone
        self._rank = rank
        self.is_awarded = bool(is_awarded)
        self.awarded_package_id = awarded_package_id
        self.updated_time = updated_time
        self.created_time = created_time

    @property
    def awarded_package(self):
        if self.awarded_package_id:
            return Package.get(self.awarded_package_id)

    @cached_property
    def rank(self):
        return self.Rank(self._rank)

    @classmethod
    def add(cls, mobile_phone, rank):
        record = cls.get_by_mobile_phone(mobile_phone)
        if record and record.is_awarded:
            raise GiftAwaredError()

        sql = (
            'insert into {0} (mobile_phone, rank, is_awarded, updated_time, '
            'created_time) values (%s, %s, %s, %s, %s) on duplicate key '
            'update rank = %s, updated_time = %s').format(cls.table_name)
        now = datetime.datetime.now()
        params = (mobile_phone, rank.value, False, now, now, rank.value, now)
        db.execute(sql, params)
        db.commit()
        instance = cls.get_by_mobile_phone(mobile_phone)
        cls.clear_cache(instance.id_)
        cls.clear_cache_by_mobile_phone(instance.mobile_phone)
        return instance

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, mobile_phone, rank, is_awarded, awarded_package_id, updated_time, '
            'created_time from {0} where id=%s').format(cls.table_name)
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
    def get_by_mobile_phone(cls, mobile_phone):
        if not mobile_phone:
            return

        id_ = cls.get_id_by_mobile_phone(mobile_phone)
        if id_:
            return cls.get(id_)

    def award(self):
        """向手机号对应用户发放礼包"""
        if self.is_awarded:
            return

        # lock it
        sql = 'select is_awarded from {.table_name} where mobile_phone = %s for update'.format(self)
        params = (self.mobile_phone,)
        rs = db.execute(sql, params)
        if rs and rs[0][0]:
            db.rollback()  # release lock
            return

        try:
            user = Account.get_by_alias(self.mobile_phone)
            sql = 'update {.table_name} set is_awarded=%s where id=%s'.format(self)
            params = (True, self.id_)
            db.execute(sql, params)
        except:
            db.rollback()  # release lock
            raise
        else:
            db.commit()

        self.is_awarded = True

        # distribute package and record
        package = distribute_welfare_gift(
            user, self.rank.award, allow_piling_firewood=bool(Identity.get(user.id_)))
        sql = 'update {.table_name} set awarded_package_id=%s where id=%s'.format(self)
        params = (package.id_, self.id_)
        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)
        self.clear_cache_by_mobile_phone(self.mobile_phone)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_mobile_phone(cls, mobile_phone):
        mc.delete(cls.cache_by_mobile_phone_key.format(**locals()))


@user_register_completed.connect
def on_user_register_completed(user):
    # 圣诞游戏礼包
    gift = ChristmasGift.get_by_mobile_phone(user.mobile)
    if gift:
        gift.award()


@identity_saved.connect
def on_user_identity_saved(identity):
    """将用户认证身份前的暂存的充值记录进行充值"""
    user = Account.get(identity.id_)
    if not user.has_mobile():
        return

    gift = ChristmasGift.get_by_mobile_phone(user.mobile)
    if gift:
        wrapper = gift.rank.award.firewood_wrapper
        if not wrapper:
            # 如果奖励中没有红包则直接返回
            return
        FirewoodWorkflow(user.id_).pile(
            user, wrapper.worth, gift.awarded_package, tags=[wrapper.name])


class GiftAwaredError(Exception):
    def __unicode__(self):
        return u'对不起，您已经领过奖励了~'
