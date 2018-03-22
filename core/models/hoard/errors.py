# coding: utf-8


class HoardException(Exception):
    """The base exception of "savings" realm."""


class NotFoundError(HoardException):
    """The related entity could not be found.

    :param args[0]: the identity provided by the caller.
    :param args[1]: the type of related entity.
    """


# 订单异常

class DuplicatePaymentError(HoardException):
    """The order has been paid."""


class OutOfRangeError(HoardException, ValueError):
    def __unicode__(self):
        return u'订单金额不在允许的范围内'


class CreateUserRebateError(HoardException):
    """Can not create user rebate."""


class SellOutError(HoardException):
    """Product has been sold out"""

    def __unicode__(self):
        return u'抱歉，该期限产品暂时售罄，请选购其他产品'


class TakeDownError(HoardException):
    """Product has been took down"""

    def __unicode__(self):
        return u'抱歉，该期限产品暂时售罄，请选购其他产品'


class MissingOrderError(HoardException):
    """The order is missing"""


# 帐号绑定异常

class YixinBindException(HoardException):
    """The base exception for binding yixin account."""


class HoarderReboundError(YixinBindException):
    """The user has hoarded so that can't be bound with yixin again."""

    def __unicode__(self):
        return u'该账号已绑定宜人贷账号，无法重复绑定，请联系客服处理'


class RemoteAccountUsedError(YixinBindException):
    """The remote account has been used."""

    def __unicode__(self):
        return u'该宜人贷账号已绑定其他好规划账号，请登录对应账号或联系客服处理'


# 订单支付异常

class IndentityUnverifiedError(HoardException):
    pass


class UnboundAccountError(IndentityUnverifiedError):
    def __unicode__(self):
        return u'尚未绑定宜人贷账号'


class InvalidIdentityError(IndentityUnverifiedError):
    def __unicode__(self):
        return u'尚未绑定身份信息或身份信息无效'


class WithdrawPayingError(HoardException):
    """The cash back is in progress, do not repeat submission."""


# 自动注册异常

class RegisterException(HoardException):
    """The base class for exceptions during registering yixin account."""


class MissingIdentityError(RegisterException):
    """The registering user has not identity information."""

    def __unicode__(self):
        return u'该账号尚未绑定身份证'


class MissingMobilePhoneError(RegisterException):
    """The registering user has not mobile phone number."""

    def __unicode__(self):
        return u'该账号尚未绑定手机号'


class RemoteConflictError(RegisterException):
    """The identity or mobile phone exists in remote side."""


class RemoteBusyError(RegisterException):
    def __unicode__(self):
        return u'抱歉，宜人贷暂无响应, 请稍后重试或联系客服处理'


class RemoteUnknownError(RegisterException):
    def __unicode__(self):
        return u'抱歉，宜人贷发生未知错误，请稍后重试或联系客服处理'


class RegisterTooYoungError(RegisterException):
    def __unicode__(self):
        return u'抱歉，未满 16 周岁的用户依照规定无法注册宜人贷'


# 银行卡验证异常


class BankNotMatchedError(HoardException):
    """The bankcard has been related to a wrong bank."""

    def __init__(self, bankcard, actual_bank):
        super(BankNotMatchedError, self).__init__(bankcard, actual_bank)

    def __unicode__(self):
        return u'该银行卡属于%s，请重选银行' % self.args[1].name


# 礼券异常

class CouponBoundError(HoardException):
    def __unicode__(self):
        return u'抱歉，该礼券已被其他订单占用，请重新下单'
