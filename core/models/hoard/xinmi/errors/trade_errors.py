# coding: utf-8


# 交易错误


class TradeError(Exception):
    pass


class IneligiblePurchase(TradeError):
    pass


class DuplicateConfirmError(TradeError):
    pass


class SubscribeProductError(TradeError):
    pass


class ReapplyError(TradeError):
    pass


class InvalidStatusTransfer(TradeError):
    pass


class OrderUpdateStatusConflictError(TradeError):
    def __unicode__(self):
        return u'您的订单已在处理中，请勿重复提交'


class ExceedBankAmountLimitError(TradeError):
    def __unicode__(self):
        assert len(self.args) > 0
        assert str(self.args[0]).isdigit()
        return u'订单金额超出银行单笔最高限额(%s元)' % self.args[0]
