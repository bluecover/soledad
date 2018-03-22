# coding: utf-8


class SmsEmptyError(Exception):
    pass


class CouponOwnershipError(Exception):
    def __unicode__(self):
        return u'用户不可使用该礼券'


class XMError(Exception):
    pass


class XMOrderOwnershipError(XMError):
    def __unicode__(self):
        return u'该订单不属于此用户'


class XMOrderInProcessingError(XMError):
    def __unicode__(self):
        return u'订单正在处理中，请勿重复提交'


class XMOrderNotExistedError(XMError):
    def __unicode__(self):
        return u'订单不存在'


class XMProductNotExistedError(XMError):
    def __unicode__(self):
        return u'产品不存在'


class BankCardError(Exception):
    pass


class BankCardNotExistedError(BankCardError):
    def __unicode__(self):
        return u'该银行卡不存在，请重新添加银行卡'


class UnsupportedBankCardError(BankCardError):
    def __unicode__(self):
        return u'当前服务暂不支持该银行卡，请您选择其他银行重试'
