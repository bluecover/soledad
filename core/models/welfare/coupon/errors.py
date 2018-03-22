# coding: utf-8

# 礼券错误


class CouponError(Exception):
    pass


class CouponSystemError(CouponError):
    pass


class UnsupportedProductError(CouponSystemError):
    def __unicode__(self):
        return u'抱歉，礼券不适用于该产品'


class CouponBusinessError(CouponError):
    pass


class IneligibleOrderError(CouponBusinessError):
    def __unicode__(self):
        return u'抱歉，该订单无法使用该礼券，请修改订单信息'


class InvalidCouponStatusTransferError(CouponBusinessError):
    def __unicode__(self):
        return u'抱歉，礼券当前异常，请联系客服处理'


class CouponFreezedError(CouponBusinessError):
    def __unicode__(self):
        return u'抱歉，该礼券已被其他订单使用，请尝试重新下单'


class CouponOutdatedError(CouponBusinessError):
    def __unicode__(self):
        return u'抱歉，该礼券已过期'


class CouponUsageError(Exception):
    pass
