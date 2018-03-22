# -*- coding: utf-8 -*-

# Account related


class AccountError(Exception):
    pass


class ForbiddenError(AccountError):
    def __unicode__(self):
        return u'此产品已禁止购入,如有疑问请联系客服'


class RepeatRegisterError(AccountError):
    def __unicode__(self):
        return u'禁止重复绑定账号'


class NotFoundError(AccountError):
    pass


class RemoteAccountOccupiedError(AccountError):
    pass


class MissingMobilePhoneError(AccountError):
    def __unicode__(self):
        return u'未绑定手机号'


class MismatchUserError(AccountError):
    pass


class MissingIdentityError(AccountError):
    def __unicode__(self):
        return u'未绑定身份信息'


# Order related


class OrderError(Exception):
    pass


class NotFoundEntityError(OrderError):
    """The related entity could not be found.

    :param args[0]: the identity provided by the caller.
    :param args[1]: the type of related entity.
    """
    pass


class OrderInProgressingError(OrderError):
    def __unicode__(self):
        return u'您的订单已在处理中，请勿重复提交'


class OrderNotExistError(OrderError):
    def __unicode__(self):
        return u'该订单不存在'


class OrderMissMatchUserError(OrderError):
    def __unicode__(self):
        return u'该订单不属于当前账号，无法继续查看'


class UnboundAccountError(OrderError):
    def __unicode__(self):
        return u'未绑定账号'


class InvalidIdentityError(OrderError):
    def __unicode__(self):
        return u'尚未绑定身份信息或身份信息无效'


class SequenceError(OrderError):
    def __unicode__(self):
        return u'不可原地或反向迁移状态!'


class UnsupportedStatusError(OrderError):
    def __unicode__(self):
        return u'未支持的状态码'


class OrderAmountTooSmallError(OrderError):
    pass


# Product related


class ProductError(Exception):
    pass


class ProductDeprecatedError(ProductError):
    def __unicode__(self):
        return u"产品已停售，无法上架"


class ProductLowQuotaError(ProductError):
    def __unicode__(self):
        return u"配额不足，无法上架"


class ProductDuplicateSaleModeError(ProductError):
    def __unicode__(self):
        return u"产品已上架，请勿重复提交"


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


# Trade related


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


# Payment related


class PayError(Exception):
    pass


class PayWaitError(PayError):
    pass


class PayTerminatedError(PayError):
    pass


class AssetError(Exception):
    pass


class InvalidRedeemBankCardError(AssetError):
    def __unicode__(self):
        return u"更换银行卡错误"


class FetchAssetError(AssetError):
    pass


class AssetEmptyError(FetchAssetError):
    def __unicode__(self):
        return u'资产信息为空'


class AssetNotChangedError(FetchAssetError):
    def __unicode__(self):
        return u'资产未变动'


class RedeemError(Exception):
    pass


class UseGiftError(Exception):
    pass
