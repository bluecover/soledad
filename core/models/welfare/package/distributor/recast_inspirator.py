# coding: utf-8

from datetime import datetime

from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.personel import staff
from ._base import PackageDistributor


class RecastInspirator(PackageDistributor):
    """首笔非新手资产到期礼包分发策略"""

    table_name = 'coupon_package_recast_inspirator'
    cache_records_count_by_user_key = 'coupon_package:recast_inspirator:count:user_id:{user_id}'

    def can_obtain(self, user, asset):
        """首笔非新手资产到期后，赠送礼包"""
        from core.models.hoard.zhiwang.asset import ZhiwangAsset
        from core.models.hoard.xinmi.asset import XMAsset

        assert isinstance(asset, XMAsset) or isinstance(asset, ZhiwangAsset)

        # 非订单所属者不发
        if not asset.is_owner(user):
            return False

        if str(user.id_) in staff.users:
            return False

        if asset.status not in (XMAsset.Status.redeemed, ZhiwangAsset.Status.redeemed):
            return False

        if self.get_records_count_by_user(user.id_) > 0:
            return False

        first_redeemed_asset = ZhiwangAsset.get_first_redeemed_asset_by_user_id(user.id_)
        if first_redeemed_asset:
            return first_redeemed_asset and first_redeemed_asset.id_ == asset.id_
        else:
            first_redeemed_asset = XMAsset.get_first_redeemed_asset_by_user_id(user.id_)
            return first_redeemed_asset and first_redeemed_asset.id_ == asset.id_

    def bestow(self, user, asset):
        from ..package import Package

        if not self.can_obtain(user, asset):
            return

        package = Package.create(self.kind)
        self._add(asset, package)
        return package

    def _add(self, asset, package):
        sql = ('insert into {.table_name} (user_id, zhiwang_asset_id, '
               'package_id, creation_time) values (%s, %s, %s, %s)').format(self)
        params = (asset.user_id, asset.id_, package.id_, datetime.now())
        db.execute(sql, params)
        db.commit()

        self.clear_cache(asset.user_id)

    @classmethod
    @cache(cache_records_count_by_user_key)
    def get_records_count_by_user(cls, user_id):
        sql = 'select count(package_id) from {.table_name} where user_id=%s'.format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return rs[0][0]

    @classmethod
    def clear_cache(cls, user_id):
        mc.delete(cls.cache_records_count_by_user_key.format(**locals()))
