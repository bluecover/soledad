# -*- coding: utf-8 -*-


class FirewoodException(Exception):
    def __unicode__(self):
        return u'红包出现错误，请稍后再试或联系客服'


class FirewoodSystemError(FirewoodException):
    pass


class AccountCreationError(FirewoodSystemError):
    pass


class AccountUncreatedError(FirewoodSystemError):
    pass


class ProductUnsupportedError(FirewoodSystemError):
    pass


class ServiceValidationError(FirewoodSystemError):
    pass


class FirewoodBusinessError(FirewoodException):
    pass


class DealingError(FirewoodBusinessError):
    def __unicode__(self):
        return u'您正在使用抵扣金的订单正在处理中，请勿重复提交'


class BalanceUnenjoyableError(FirewoodBusinessError):
    def __unicode__(self):
        return u'抱歉，您的抵扣金暂时无法使用'


class InsufficientBalanceError(FirewoodBusinessError):
    def __unicode__(self):
        return u'您的红包余额不足，请检查是否有其他操作中的交易'
