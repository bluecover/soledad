# coding: utf-8

from datetime import datetime

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.consts import Platform
from core.models.decorators import DelegatedProperty
from core.models.user.account import Account
from .kind import CouponKind
from .errors import (
    CouponOutdatedError, CouponFreezedError, UnsupportedProductError,
    IneligibleOrderError, InvalidCouponStatusTransferError)


class Coupon(EntityModel):
    """
    新礼券
    """

    # status
    class Status(Enum):
        in_wallet = 'W'  # 未使用状态
        stocktaking = 'S'  # 已接受使用（如已发起支付），被锁定
        consumed = 'M'  # 已被使用

    Status.in_wallet.prestatus = Status.stocktaking
    Status.stocktaking.prestatus = Status.in_wallet
    Status.consumed.prestatus = Status.stocktaking

    # storage
    table_name = 'coupon'
    cache_coupon_key = 'coupon:coupon:v7:{id_}'
    cache_user_coupon_ids_key = 'coupon:coupon:v7:user:{user_id}'
    cache_package_coupon_ids_key = 'coupon:coupon:v7:package:{package_id}'

    # delegation
    regulation = DelegatedProperty('regulation', to='kind')
    description = DelegatedProperty('display_text', to='kind')
    display_product_requirement = DelegatedProperty('description', to='product_matcher')
    is_available_for_order = DelegatedProperty('is_available_for_order', to='regulation')
    is_available_for_product = DelegatedProperty('is_available_for_product', to='product_matcher')

    def __init__(self, id_, name, user_id, kind_id, package_id, status, platforms,
                 product_matcher_kind_id, creation_time, consumed_time, expire_time):
        self.id_ = str(id_)
        self.name = name
        self.user_id = str(user_id)
        self.kind_id = str(kind_id)
        self.package_id = str(package_id)
        self._status = status
        self._platforms = platforms.split(',')
        self.product_matcher_kind_id = product_matcher_kind_id
        self.creation_time = creation_time
        self.consumed_time = consumed_time
        self.expire_time = expire_time

    def __eq__(self, other):
        if not isinstance(other, Coupon):
            return NotImplemented
        return self.id_ == other.id_

    def is_owner(self, user):
        return user.id_ == self.user_id

    @property
    def display_expire_time(self):
        return unicode(self.expire_time.date())

    @property
    def sort_key(self):
        return (self.regulation.sort_key, self.expire_time)

    @property
    def outdated(self):
        return self.expire_time < datetime.now()

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        self._status = item.value

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def kind(self):
        return CouponKind.get(self.kind_id)

    @cached_property
    def package(self):
        from core.models.welfare.package import Package
        return Package.get(self.package_id)

    @cached_property
    def platforms(self):
        return [Platform(p) for p in self._platforms]

    @cached_property
    def product_matcher(self):
        from core.models.welfare.matcher import ProductMatcherKind
        return ProductMatcherKind.get(self.product_matcher_kind_id).matcher

    @classmethod
    def create(cls, name, kind, package, product_matcher_kind, available_platforms,
               expire_time, _commit=True):
        """添加新礼券.

        :param name: 礼券具体名称.
        :param kind: 礼券类型.
        :param package: 包含所添加礼券的礼包.
        :param expire_date: 礼券过期日期（默认在当天23点59分59秒过期）.
        """
        from core.models.welfare.package import Package
        from core.models.welfare.matcher import ProductMatcherKind

        assert isinstance(kind, CouponKind)
        assert isinstance(package, Package)
        assert isinstance(product_matcher_kind, ProductMatcherKind)
        assert all(isinstance(p, Platform) for p in available_platforms)
        assert isinstance(expire_time, datetime)

        sql = ('insert into {.table_name} (name, user_id, kind_id, package_id, status, '
               'platforms, product_matcher_kind_id, creation_time, expire_time) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (name, package.user.id_, kind.id_, package.id_, cls.Status.in_wallet.value,
                  ','.join(sorted([p.value for p in available_platforms])),
                  product_matcher_kind.id_, datetime.now(), expire_time)
        id_ = db.execute(sql, params)
        if _commit:
            db.commit()

        cls.clear_cache(id_)
        cls.clear_user_coupon_ids_cache(package.user.id_)
        cls.clear_package_coupon_ids_cache(package.id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_coupon_key)
    def get(cls, id_):
        sql = ('select id, name, user_id, kind_id, package_id, status, platforms, '
               'product_matcher_kind_id, creation_time, consumed_time, expire_time '
               'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_user_coupon_ids_key)
    def get_ids_by_user(cls, user_id):
        """根据创建时间倒序获取所有用户的礼券"""
        sql = ('select id from {.table_name} where user_id=%s '
               'order by creation_time desc').format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        ids = cls.get_ids_by_user(user_id)
        return cls.get_multi(ids)

    @classmethod
    @cache(cache_package_coupon_ids_key)
    def get_ids_by_package(cls, package_id):
        sql = 'select id from {.table_name} where package_id=%s'.format(cls)
        params = (package_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_package(cls, package):
        ids = cls.get_ids_by_package(package.id_)
        return cls.get_multi(ids)

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    def to_dict(self):
        return {
            'id_': self.id_,
            'name': self.name,
            'description': self.description,
            'product_requirement': self.display_product_requirement,
            'usage_requirement': self.regulation.usage_requirement_dict,
            'benefit': self.regulation.benefit_dict,
            'expire_time': self.display_expire_time,
        }

    def check_before_use(self, product=None, amount=None):
        """检查礼券是否可用"""
        if self.outdated:
            raise CouponOutdatedError()

        if self.status is not self.Status.in_wallet:
            raise CouponFreezedError()

        # 判断产品适用范围
        if product is not None and not self.is_available_for_product(product):
            raise UnsupportedProductError()

        # 判断订单是否满足礼券需求
        if amount is not None and not self.is_available_for_order(amount):
            raise IneligibleOrderError()

    def _check_status_transfer(self, pre_status, post_status):
        if self.status is not pre_status:
            # 当前状态不符合规则
            raise InvalidCouponStatusTransferError(self.status, pre_status)
        if self.status is not post_status.prestatus:
            # 状态跳转不符合规则
            raise InvalidCouponStatusTransferError(self.status, post_status)

    def _commit_and_refresh(self, sql, params):
        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)
        self.clear_user_coupon_ids_cache(self.user_id)
        self.clear_package_coupon_ids_cache(self.package_id)

        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

    def shell_out(self, product=None, amount=None):
        """礼券已随交易一起提交使用，进入冻结状态"""
        self.check_before_use(product, amount)
        self._check_status_transfer(self.Status.in_wallet, self.Status.stocktaking)

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.stocktaking.value, self.id_)
        self._commit_and_refresh(sql, params)

    def confirm_consumption(self):
        """交易成功，礼券被使用掉"""
        self._check_status_transfer(self.Status.stocktaking, self.Status.consumed)

        sql = 'update {.table_name} set status=%s, consumed_time=%s where id=%s'.format(self)
        params = (self.Status.consumed.value, datetime.now(), self.id_)
        self._commit_and_refresh(sql, params)

    def put_back_wallet(self):
        """如果长时间未支付，订单取消或者支付最终失败，礼券将会被重新释放出来"""
        self._check_status_transfer(self.Status.stocktaking, self.Status.in_wallet)

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.in_wallet.value, self.id_)
        self._commit_and_refresh(sql, params)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_coupon_key.format(**locals()))

    @classmethod
    def clear_user_coupon_ids_cache(cls, user_id):
        mc.delete(cls.cache_user_coupon_ids_key.format(**locals()))

    @classmethod
    def clear_package_coupon_ids_cache(cls, package_id):
        mc.delete(cls.cache_package_coupon_ids_key.format(**locals()))
