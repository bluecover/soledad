# coding: utf-8


class BankException(Exception):
    """The base exception class for bank issues."""

    def __unicode__(self):
        raise NotImplementedError


class UnknownBankError(BankException):
    """The name is pointed to an unknown bank."""

    def __unicode__(self):
        return u'抱歉，暂时无法识别该卡号所属银行，您可以联系微信客服获取帮助'


class UnavailableBankError(BankException):
    """The bank is unavailable in specific product line."""

    def __unicode__(self):
        return u'抱歉，当前服务暂不支持该银行，请您换卡重试'


class UnsupportedBankError(UnavailableBankError):
    """The bank is unsupported in any product line."""

    def __unicode__(self):
        return u'抱歉，暂不支持该银行'
