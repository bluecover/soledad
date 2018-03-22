# coding: utf-8

from datetime import date, time, timedelta, datetime

from core.models.base import EntityModel
from core.models.consts import Platform
from core.models.welfare.matcher.kind import ProductMatcherKind, all_products
from .kind import CouponKind
from .consts import DEFAULT_LIFE_SPAN


class CouponWrapper(EntityModel):
    """礼券的包装配置

    礼券默认的适用条件是全平台、全产品、15天有效期
    """

    def __init__(self, kind, name, amount, product_matcher_kind=None,
                 platforms=None, expires_in=DEFAULT_LIFE_SPAN, expires_at=None):
        assert isinstance(kind, CouponKind)
        assert product_matcher_kind is None or isinstance(
            product_matcher_kind, ProductMatcherKind)
        assert platforms is None or all(isinstance(p, Platform) for p in platforms)
        assert expires_in is None or isinstance(expires_in, timedelta)
        assert expires_at is None or isinstance(expires_at, date)

        if expires_in is not None and expires_in.days < 1:
            raise ValueError('coupon should has at least one day life')

        if not (expires_in or expires_at):
            raise ValueError('coupon should be assigned expiration setting')

        # 礼券类型（决定是加息券、满减券）
        self.kind = kind
        # 礼券名称
        self.name = name
        # 礼券数量
        self.amount = amount
        # 礼券的适用产品，None则代表全产品
        self.product_matcher_kind = product_matcher_kind or all_products
        # 礼券的适用平台，None则代表全平台
        self.platforms = platforms or [Platform.web, Platform.ios, Platform.android]
        # 礼券的生存时间
        self.expires_in = expires_in
        # 礼券的指定过期时间
        self.expires_at = expires_at

    @property
    def expire_time(self):
        # 过期时间的计算以expires_at为最高优先级
        if self.expires_at is not None:
            expire_date = self.expires_at
        else:
            expire_date = date.today() + self.expires_in
        return datetime.combine(expire_date, time(23, 59, 59))
