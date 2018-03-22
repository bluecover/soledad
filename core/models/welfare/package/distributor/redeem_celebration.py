# coding: utf-8

from datetime import datetime

from libs.db.store import db
from core.models.hoard.providers import yirendai, zhiwang
from ._base import PackageDistributor


class RedeemCelebration(PackageDistributor):
    """任意产品到期奖励"""

    table_name = 'coupon_package_redeem_celebration'

    def can_obtain(self, user, order):
        from core.models.hoard.order import HoardOrder, OrderStatus
        from core.models.hoard.zhiwang import ZhiwangOrder, ZhiwangAsset

        assert isinstance(order, (HoardOrder, ZhiwangOrder))

        # 检查派发礼包对象是否是订单所属者
        if not order.is_owner(user):
            return False

        # 检查订单是否都已转出
        if order.provider is yirendai:
            return order.status is OrderStatus.exited
        elif order.provider is zhiwang:
            return order.asset.status is ZhiwangAsset.Status.redeemed
        else:
            return False

    def bestow(self, user, order):
        """为所有合作方到期订单进行复投礼包的发放"""
        from ..package import Package

        if not self.can_obtain(user, order):
            return

        package = Package.create(self.kind)
        self._add(order, package)
        return package

    def _add(self, order, package):
        sql = ('insert into {.table_name} (package_id, user_id, provider_id, '
               'order_id, creation_time) values (%s, %s, %s, %s, %s)').format(self)
        params = (package.id_, order.user_id, order.provider.id_, order.id_, datetime.now())
        db.execute(sql, params)
        db.commit()
