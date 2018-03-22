# coding: utf-8

from datetime import datetime

from libs.db.store import db
from ._base import PackageDistributor


class NewcomerCenter(PackageDistributor):
    """The gift package strategy for new comer."""

    table_name = 'coupon_package_newcomer_center'

    def can_obtain(self, user, voucher=None):
        return True

    def bestow(self, user, voucher=None):
        from ..package import Package

        if not self.can_obtain(user, voucher):
            return

        package = Package.create(self.kind)
        self._add(user, package)
        return package

    def _add(self, user, package):
        sql = ('insert into {.table_name} (user_id, package_id, '
               'creation_time) values (%s, %s, %s)').format(self)
        params = (user.id_, package.id_, datetime.now())
        db.execute(sql, params)
        db.commit()
