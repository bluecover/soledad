# coding: utf-8

from marshmallow import Schema, fields

from core.models.hoard.xinmi import XMOrder
from core.models.hoard.xinmi.product import XMProduct
from core.models.hoard.xinmi.transaction import (
    subscribe_product as xm_subscribe_product, register_xm_account, pay_order as xm_pay_order)
from core.models.bank import Partner
from core.models.profile.signals import before_deleting_bankcard
from jupiter.views.api.track import events
from jupiter.views.api.v1.profile import inject_bankcard_amount_limit
from jupiter.views.api.v1.savings import XinmiOrderSchema, warning
from .common import obtain_bankcard, obtain_coupon
from core.models.hoard.xinmi.errors import SubscribeProductError as XMSubscribeProductError
from .errors import (
    XMOrderOwnershipError, XMOrderInProcessingError, SmsEmptyError,
    XMOrderNotExistedError, XMProductNotExistedError)


def xm_auth(user_id):
    """绑定新米账户."""

    register_xm_account(user_id)


def purchase(json_data, g):
    """选购新米产品, 创建理财单"""

    purchase_schema = XinmiPurchaseSchema(strict=True)
    order_schema = XinmiOrderSchema(strict=True)
    result = purchase_schema.load(json_data)

    product = obtain_xm_product(result.data['product_id'])
    coupon = obtain_coupon(result.data.get('coupon_id'), g.user)
    bankcard = obtain_bankcard(result.data['bankcard_id'], g)
    g.bankcard_manager.set_default(bankcard)
    pay_amount = result.data.get('pay_amount', result.data['amount'])
    pocket_deduction_amount = result.data.get('pocket_deduction_amount')

    if product.product_type is XMProduct.Type.classic:
        due_date = result.data['due_date']
    else:
        due_date = None

    try:
        order = xm_subscribe_product(
            g.user,
            product,
            bankcard,
            result.data['amount'],
            pay_amount,
            due_date,
            coupon=coupon,
            pocket_deduction_amount=pocket_deduction_amount)
        inject_bankcard_amount_limit(Partner.xm, [order.bankcard])
    except XMSubscribeProductError as e:
        bankcard_results = before_deleting_bankcard.send(
            bankcard_id=bankcard.id_, user_id=g.user.id_)
        if any(r for _, r in bankcard_results):
            raise XMSubscribeProductError(u'%s。如需修改银行卡信息，请联系微信客服（plan141）' % e)
        raise XMSubscribeProductError()

    return order_schema.dump(order).data


def purchase_verify(order_id, json_data, request):
    """提供短信验证码, 支付理财单"""

    purchase_verify_schema = XinmiVerifySchema(strict=True)
    order_schema = XinmiOrderSchema(strict=True)
    result = purchase_verify_schema.load(json_data)
    order = obtain_xm_order(order_id, request)
    # pay_code = result.data['stashed_payment_id']
    sms_code = result.data['sms_code']

    if not order.is_owner(request.oauth.user):
        raise XMOrderOwnershipError()
    if order.status in [XMOrder.Status.committed, XMOrder.Status.shelved]:
        raise XMOrderInProcessingError()
    if not sms_code:
        raise SmsEmptyError()

    xm_pay_order(order, sms_code)

    inject_bankcard_amount_limit(Partner.xm, [order.bankcard])

    if order.display_status == u'处理中':
        order._confirm_desc = u'支付成功后第二个工作日'
    else:
        order._confirm_desc = order.start_date.date()
    # FIXME: refine fields in model
    order._due_date = order.due_date.date()

    events['savings_success'].send(
        request, user_id=order.user_id, order_id=order.id_, amount=unicode(order.amount),
        period='{0.value}-{0.unit}'.format(order.profit_period))

    return order_schema.dump(order).data


def obtain_xm_order(order_id, request):
    order = XMOrder.get(order_id)
    if not order:
        warning('用户访问不存在的订单', order_id=order_id)
        raise XMOrderNotExistedError()
    if not order.is_owner(request.oauth.user):
        warning('用户访问他人的订单', order_id=order_id)
        raise XMOrderOwnershipError()
    return order


def obtain_xm_product(product_id):
    product = XMProduct.get(product_id)
    if not product:
        warning('用户访问不存在的产品', product_id=product_id)
        raise XMProductNotExistedError()
    return product


class XinmiPurchaseSchema(Schema):
    """新米购买请求实体."""

    #: :class:`int` 购买产品 (:class:`.XinMiPurchaseSchema`) 的唯一 ID
    product_id = fields.Integer(required=True)
    #: :class:`~decimal.Decimal` 购买金额 (100 的整数倍)
    amount = fields.Decimal(places=0, required=True)
    #: :class:`~decimal.Decimal` 实际支付金额
    pay_amount = fields.Decimal(places=2)
    #: :class:`in` 使用优惠券ID
    coupon_id = fields.Integer()
    #: :class:`~datetime.date` 到期时间
    due_date = fields.Date(attribute='due_date')
    #: :class:`str` 支付所用银行卡 ID
    bankcard_id = fields.String(required=True)
    #: :class:`~decimal.Decimal` 抵扣金额
    pocket_deduction_amount = fields.Decimal(places=2)
    #: :class:`str` 产品供应商
    vendor = fields.String(required=True)


class XinmiVerifySchema(Schema):
    """新米购买支付请求实体."""

    #: :class:`str` 银行卡预留手机号收到的短信验证码
    sms_code = fields.String(required=True)
    #: :class:`str` 产品供应商
    vendor = fields.String(required=True)
