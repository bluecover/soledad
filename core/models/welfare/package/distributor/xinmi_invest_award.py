# coding: utf-8

import MySQLdb

from datetime import datetime

from libs.db.store import db
from ._base import PackageDistributor
from core.models.hoard.xinmi.order import XMOrder

from jupiter.ext import sentry


class XinmiInvestAward(PackageDistributor):
    """The gift package strategy for xinmi."""

    table_name = 'coupon_package_xm'

    def can_obtain(self, user, order):
        if isinstance(order, XMOrder):
            return True

    def bestow(self, user, order):
        from ..package import Package
        if not self.can_obtain(user, order):
            return

        package = Package.create(self.kind)
        self._add(order, package)
        return package

    def _add(self, order, package):
        sql = ('insert into {.table_name} (order_id, package_id,'
               'creation_time) values (%s, %s, %s)').format(self)
        params = (order.id_, package.id_, datetime.now())
        try:
            db.execute(sql, params)
        except MySQLdb.IntegrityError:
            sentry.captureMessage('Error: repeatedly distribute package to %s ' % order.id_)
            return
        db.commit()
