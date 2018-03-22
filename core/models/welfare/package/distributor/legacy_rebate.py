# coding: utf-8

from datetime import datetime

from libs.db.store import db
from ._base import PackageDistributor


class LegacyRebate(PackageDistributor):
    """历史返现所对应的礼包发放记录"""

    table_name = 'coupon_package_legacy_rebate'

    def can_obtain(self, user, voucher):
        return True

    def bestow(self, user, voucher):
        from ..package import Package

        if not self.can_obtain(user, voucher):
            return

        package = Package.create(self.kind)
        self._add(user, package, voucher)
        return package

    def _add(self, user, package, voucher):
        sql = ('insert into {.table_name} (user_id, package_id, rebate_voucher_id, '
               'creation_time) values (%s, %s, %s)').format(self)
        params = (user.id_, package.id_, voucher.id_, datetime.now())
        db.execute(sql, params)
        db.commit()
