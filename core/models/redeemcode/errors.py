# coding:utf-8


class RedeemCodeException(Exception):
    """兑换码异常"""


class NotFoundError(RedeemCodeException):
    def __unicode__(self):
        return u'您输入的兑换码不存在'


class RedeemCodeUsedError(RedeemCodeException):
    def __unicode__(self):
        return u'您输入的兑换码已使用'


class RedeemCodeIneffectiveError(RedeemCodeException):
    def __unicode__(self):
        return u'您输入的兑换码未生效，请在活动期间使用'


class RedeemCodeExpiredError(RedeemCodeException):
    def __unicode__(self):
        return u'您输入的兑换码已失效'


class RedemptionBeyondLimitPerCodeError(RedeemCodeException):
    """超过单个兑换码允许被不同用户使用的最大次数时报此异常
    """
    def __unicode__(self):
        return u'该兑换码允许使用的次数已用完'


class RedemptionBeyondLimitPerUserError(RedeemCodeException):
    """超过每次活动允许单个用户累计使用的兑换码个数时报此异常
    """
    def __unicode__(self):
        return u'您使用兑换码的次数已超过本次活动上限'


class RedeemCodeExistedError(RedeemCodeException):
    def __unicode__(self):
        return u'兑换码已存在'
