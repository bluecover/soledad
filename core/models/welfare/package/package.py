# coding: utf-8

from hashlib import sha1
from random import random
from datetime import datetime

from enum import Enum
from werkzeug.utils import cached_property
from werkzeug.security import safe_str_cmp

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.user.signals import user_register_completed
from core.models.hoard.signals import (
    yrd_order_exited, xm_order_succeeded, xm_asset_redeemed, zw_asset_redeemed)
from core.models.invitation.signals import invitation_accepted
from .kind import PackageKind
from .errors import (
    InvalidPackageStatusTransferError, PackageDistributorDenied,
    WrongPackageTokenError)


class Package(EntityModel):

    table_name = 'coupon_package'
    cache_package_key = 'coupon:package:v7:{id_}'
    cache_user_package_ids_key = 'coupon:package:v7:user:{user_id}'

    class Status(Enum):
        in_air = 'A'
        under_foot = 'F'
        in_pocket = 'P'

    Status.under_foot.pre_statuses = (Status.in_air,)
    Status.in_pocket.pre_statuses = (Status.in_air, Status.under_foot)

    def __init__(self, id_, user_id, kind_id, status, creation_time,
                 reserved_sha1, reserved_time, unpacked_time):
        self.id_ = str(id_)
        self.user_id = user_id and str(user_id)
        self.kind_id = kind_id
        self._status = status
        self.creation_time = creation_time
        self.reserved_sha1 = reserved_sha1
        self.reserved_time = reserved_time
        self.unpacked_time = unpacked_time

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        self._status = item.value

    @cached_property
    def kind(self):
        return PackageKind.get(self.kind_id)

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @classmethod
    def create(cls, kind):
        """Creates new coupon package.

        :param kind: the kind of coupon package.
        :type kind: :class:`~core.models.welfare.package.PackageKind`
        """
        sql = ('insert into {.table_name} (user_id, kind_id, status, creation_time)'
               'values (%s, %s, %s, %s)').format(cls)
        params = (None, kind.id_, cls.Status.in_air.value, datetime.now())

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_package_key)
    def get(cls, id_):
        sql = ('select id, user_id, kind_id, status, creation_time, reserved_sha1, '
               'reserved_time, unpacked_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_user(cls, user):
        id_list = cls.get_ids_by_user(user.id_)
        return cls.get_multi(id_list)

    @classmethod
    @cache(cache_user_package_ids_key)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        rs = db.execute(sql, (user_id,))
        return [r[0] for r in rs]

    def _check_status_transfer(self, pre_statuses, post_status):
        if self.status not in pre_statuses:
            # 当前状态不符合规则
            raise InvalidPackageStatusTransferError(self.status, post_status)
        if not all(status in post_status.pre_statuses for status in pre_statuses):
            # 状态跳转不符合规则
            raise InvalidPackageStatusTransferError(self.status, post_status)

    def reserve(self):
        """Reserves this package to a anonymous user.

        :return: the SHA1 token for unpacking it later.
        """
        self._check_status_transfer((self.Status.in_air,), self.Status.under_foot)

        self.reserved_sha1 = sha1(bytes(random())).hexdigest()
        self.reserved_time = datetime.now()
        self.status = self.Status.under_foot

        sql = ('update {.table_name} set reserved_sha1=%s, reserved_time=%s, '
               'status=%s where id=%s').format(self)
        params = (self.reserved_sha1, self.reserved_time, self.status.value,
                  self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)

        return self.reserved_sha1

    def unpack(self, user, reserved_sha1=None,
               allow_piling_firewood=True, dynamic_firewood_worth=None):
        """Unpacks package to get coupons.

        :param user: The user who gained this package.
        :param reserved_sha1: Optional. The reserved SHA1 token.
        """
        from core.models.welfare import Coupon, FirewoodWorkflow
        self._check_status_transfer(
            (self.Status.in_air, self.Status.under_foot), self.Status.in_pocket)

        # checks for reserved package
        if self.status is self.Status.under_foot:
            if reserved_sha1 is None:
                raise ValueError('reserved_sha1 is required')
            if not safe_str_cmp(reserved_sha1, self.reserved_sha1):
                raise WrongPackageTokenError('reserved_sha1 is wrong')
        if self.status is self.Status.in_air and reserved_sha1 is not None:
            raise ValueError('coupon package has not been reserved')

        # checks with strategy
        if self.kind.distributor and not self.kind.distributor.can_unpack(user=user, package=self):
            raise PackageDistributorDenied('distributor denied', self.id_)

        self.user_id = user.id_
        self.status = self.Status.in_pocket
        self.unpacked_time = datetime.now()
        sql = ('update {.table_name} set user_id=%s, status=%s, '
               'unpacked_time=%s where id=%s').format(self)
        params = (self.user_id, self.status.value, self.unpacked_time, self.id_)
        db.execute(sql, params)
        db.commit()

        # release coupon here
        if self.kind.coupon_wrappers:
            try:
                for wrapper in self.kind.coupon_wrappers:
                    for _ in xrange(wrapper.amount):
                        Coupon.create(
                            wrapper.name, wrapper.kind, self, wrapper.product_matcher_kind,
                            wrapper.platforms, wrapper.expire_time, _commit=False)
            except:
                db.rollback()
                raise
            else:
                db.commit()

        # pile fire woods
        if allow_piling_firewood and self.kind.firewood_wrapper:
            FirewoodWorkflow(user.id_).pile(
                user, self.kind.firewood_wrapper.worth, self,
                tags=[self.kind.firewood_wrapper.name])

        self.clear_cache(self.id_)
        self.clear_cache_by_user(self.user_id)

    def get_related_coupons(self):
        from ..coupon import Coupon
        return Coupon.get_multi_by_package(self)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_package_key.format(id_=id_))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_user_package_ids_key.format(user_id=user_id))


def distribute_welfare_gift(user, welfare_package_kind, voucher=None, allow_piling_firewood=True):
    # voucher是获取礼包的凭证根据（如用户、订单、资产等），亦可无条件发放
    from core.models.group import welfare_reminder_group
    from core.models.notification import Notification
    from core.models.notification.kind import welfare_gift_notification

    package = welfare_package_kind.distributor.bestow(user, voucher)
    if package:
        # 拆包发礼券
        # 针对新结算产品，动态分配抵扣金
        package.unpack(user, allow_piling_firewood=allow_piling_firewood)

        # 本地记录
        rsyslog.send('\t'.join([user.id_, package.id_]), tag='welfare_package_distribution')

        notification_voucher = (welfare_package_kind.coupon_wrappers or
                                welfare_package_kind.firewood_wrapper.worth)
        if notification_voucher:
            # 提醒用户新增福利
            welfare_reminder_group.add_member(user.id_)

            # 添加消息通知
            Notification.create(
                user.id_, welfare_gift_notification,
                dict(welfare_package_id=package.id_))
    return package


@user_register_completed.connect
def on_user_register_completed(user):
    # 新人注册发放礼包
    from .kind import newcomer_package
    from core.models.sms.kind import register_package_sms
    from core.models.sms.sms import ShortMessage
    distribute_welfare_gift(user, newcomer_package)

    # 向用户手机发送提醒赠送注册红包短信
    if user.has_mobile():
        sms = ShortMessage.create(user.mobile, register_package_sms)
        sms.send_async()


@invitation_accepted.connect
def on_invitaion_accepted(invite):
    # 邀请接受（被邀请者投资）后向邀请者发放礼包
    distribute_welfare_gift(invite.inviter, invite.kind.award_package, voucher=invite)


@yrd_order_exited.connect
def on_yrd_order_exited(order):
    from .kind import redeem_celebration_package
    # 向用户发放宜人贷到期礼包
    distribute_welfare_gift(order.user, redeem_celebration_package, voucher=order)


@xm_order_succeeded.connect
def on_xm_order_succeeded(order):
    # 如果是新人第一笔资产到期，则分发礼券和红包
    from .kind import first_purchase_package
    distribute_welfare_gift(order.user, first_purchase_package, voucher=order)


@zw_asset_redeemed.connect
@xm_asset_redeemed.connect
def on_xm_asset_redeemed(asset):
    from .kind import recast_inspire_package, redeem_celebration_package
    # 首先判断用户是否可获得首笔指旺到期礼包
    award = distribute_welfare_gift(asset.user, recast_inspire_package, voucher=asset)
    if not award:
        # 否则向用户发放普通到期礼包
        distribute_welfare_gift(asset.user, redeem_celebration_package, voucher=asset.order)
