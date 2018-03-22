# coding: utf-8

from datetime import datetime

from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.personel import staff
from ._base import PackageDistributor


class MaidenInvestmentAward(PackageDistributor):
    """The award for user who completed first investment(except newcomer order)."""

    table_name = 'coupon_package_investment_award'
    cache_records_count_by_user_key = 'coupon_package:investment_award:count:user:{user_id}'
    cache_package_id_by_order_key = 'coupon_package:investment_award:package_id:order:{order_id}'

    def can_obtain(self, user, xm_order):
        """完成新手标之外的一笔投资后，赠送礼包

        现在线上产品为新结算常规产品和新手标(随心宝目前不在考虑之列)，新手标为房贷宝包装出来的产品，
        用户完成新手标之后，再次投资时已变为新结算产品，所以本表中zhiwang_order_id字段自2016年5月14日起
        对应的是xm_order_id(暂时先这样处理)，之后还会因随心宝变动，届时更改一个统一字段
        """
        from core.models.hoard.xinmi.order import XMOrder
        from core.models.hoard.zhiwang.order import ZhiwangOrder

        assert isinstance(xm_order, XMOrder)

        # 非订单所属者不发
        if not xm_order.is_owner(user):
            return False

        # 员工不发
        if str(user.id_) in staff.users:
            return False

        if xm_order.status is not XMOrder.Status.success:
            return False

        if self.get_records_count_by_user(user.id_) > 0:
            return False

        new_comer_orders = [o for o in ZhiwangOrder.get_multi_by_user(user.id_) if (
            o.status is ZhiwangOrder.Status.success) and o.wrapped_product]
        xm_orders = [o for o in XMOrder.get_multi_by_user(user.id_)
                     if o.status is XMOrder.Status.success]

        return len(new_comer_orders) == 1 and len(xm_orders) == 1

    def bestow(self, user, xm_order):
        from ..package import Package

        if not self.can_obtain(user, xm_order):
            return

        package = Package.create(self.kind)
        self._add(xm_order, package)
        return package

    def _add(self, xm_order, package):
        sql = ('insert into {.table_name} (user_id, zhiwang_order_id, '
               'package_id, creation_time) values (%s, %s, %s, %s)').format(self)
        params = (xm_order.user_id, xm_order.id_, package.id_, datetime.now())
        db.execute(sql, params)
        db.commit()

        self.clear_package_id_by_order_key(xm_order.id_)
        self.clear_records_count_by_user_cache(xm_order.user_id)

    @classmethod
    @cache(cache_records_count_by_user_key)
    def get_records_count_by_user(cls, user_id):
        sql = 'select count(package_id) from {.table_name} where user_id=%s'.format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return rs[0][0]

    @classmethod
    @cache(cache_package_id_by_order_key)
    def get_package_id_by_order_id(cls, order_id):
        sql = 'select package_id from {.table_name} where zhiwang_order_id=%s'.format(cls)
        params = (order_id,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def clear_records_count_by_user_cache(cls, user_id):
        mc.delete(cls.cache_records_count_by_user_key.format(**locals()))

    @classmethod
    def clear_package_id_by_order_key(cls, order_id):
        mc.delete(cls.cache_package_id_by_order_key.format(**locals()))
