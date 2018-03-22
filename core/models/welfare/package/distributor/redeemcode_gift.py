# coding: utf-8

from datetime import datetime

from libs.db.store import db
from ._base import PackageDistributor


class RedeemCodeGift(PackageDistributor):
    """The gift package strategy for redeemcode."""

    table_name = 'coupon_package_redeem_code'

    def can_obtain(self, user, redeem_code_usage):
        return True

    def bestow(self, user, redeem_code_usage):
        from ..package import Package
        if not self.can_obtain(user, redeem_code_usage):
            return

        package = Package.create(self.kind)
        self._add(redeem_code_usage, package)
        return package

    def _add(self, redeem_code_usage, package):
        sql = ('insert into {.table_name} (redeem_code_usage_id, package_id,'
               'creation_time) values (%s, %s, %s)').format(self)
        params = (redeem_code_usage.id_, package.id_, datetime.now())
        db.execute(sql, params)
        db.commit()
