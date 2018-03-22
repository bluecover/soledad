# coding: utf-8


# 产品错误


class ProductError(Exception):
    pass


class InvalidProductError(ProductError):
    def __unicode__(self):
        return u'无法识别的产品'


class SoldOutError(ProductError):
    def __unicode__(self):
        return u'抱歉, 您所选择的产品已售罄, 请明天再来'


class SuspendedError(ProductError):
    def __unicode__(self):
        return u'抱歉, 您所选择的产品已售罄, 请明天再来'


class OffShelfError(ProductError):
    def __unicode__(self):
        return u'抱歉，该产品已下架。'


class OutOfRangeError(ProductError):
    def __unicode__(self):
        return u'订单金额不在允许的范围内'
