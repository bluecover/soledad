# coding: utf-8

from marshmallow import Schema, fields

from core.models.hoarder.product import Product
from core.models.hoarder.transactions import sxb
from core.models.bank.partners import Partner
from core.models.utils import round_half_up
from core.models.hoarder.errors import OffShelfError, OrderAmountTooSmallError
from jupiter.views.api.track import events
from jupiter.views.api.fields import LocalDateTimeField
from jupiter.views.api.v1.profile import inject_bankcard_amount_limit
from .errors import SmsEmptyError
from .common import obtain_bankcard, obtain_coupon


def sxb_auth(user_id):
    """绑定账户."""
    sxb.register_account(user_id)


def purchase(json_data, g):
    """选购产品, 创建理财单."""

    purchase_schema = PurchaseSchema(strict=True)
    response_schema = PurchaseResponseSchema()
    result = purchase_schema.load(json_data)

    product_id = result.data['product_id']
    bankcard = obtain_bankcard(result.data['bankcard_id'], g)
    g.bankcard_manager.set_default(bankcard)
    amount = result.data.get('amount', 0) or 0
    pocket_deduction_amount = result.data.get('pocket_deduction_amount', 0) or 0
    coupon = obtain_coupon(result.data.get('coupon_id'), g.user)
    p = Product.get(product_id)
    if not p:
        raise OffShelfError()
    if amount < p.min_amount:
        raise OrderAmountTooSmallError(u'申购金额能少于{}元'.format(round_half_up(p.min_amount, 2)))

    order = sxb.subscribe_product(
        g.user,
        product_id,
        bankcard,
        amount,
        coupon,
        pocket_deduction_amount)

    inject_bankcard_amount_limit(Partner.xm, [order.bankcard])

    order._display_status = order.status.display_text

    return response_schema.dump(order).data


def purchase_verify(order_id, json_data, request):
    """提供短信验证码, 支付理财单."""

    purchase_verify_schema = VerifySchema(strict=True)
    response_schema = PurchaseVerifyResponseSchema(strict=True)
    result = purchase_verify_schema.load(json_data)
    sms_code = result.data['sms_code']

    if not sms_code:
        raise SmsEmptyError()
    order = sxb.pay_order(order_id, request.oauth.user, sms_code)

    if order.status.display_text == u'已存入':
        order._display_status = u'您已支付成功'
    else:
        order._display_status = order.status.display_text
    # 年化率
    order._annual_rate = order.product.rate * 100

    # 首日收益
    order._expect_interest_first_day = order.product.rate * order.amount / 365
    events['savings_success'].send(
        request, user_id=order.user_id, order_id=order.id_, amount=unicode(order.amount),
        period='dynamic')
    return response_schema.dump(order).data


class PurchaseSchema(Schema):
    """申购请求参数."""

    #: :class:`int` 购买产品 (:class:`.PurchaseSchema`) 的唯一 ID
    product_id = fields.Integer(required=True)
    #: :class:`~decimal.Decimal` 购买金额 (100 的整数倍)
    amount = fields.Decimal(places=0, required=True)
    #: :class:`in` 使用优惠券ID
    coupon_id = fields.Integer()
    #: :class:`str` 支付所用银行卡 ID
    bankcard_id = fields.String(required=True)
    #: :class:`~decimal.Decimal` 抵扣金额
    pocket_deduction_amount = fields.Decimal(places=2)
    #: :class:`str` 产品供应商
    vendor = fields.String(required=True)


class VerifySchema(Schema):
    """支付请求参数."""

    #: :class:`str` 银行卡预留手机号收到的短信验证码
    sms_code = fields.String(required=True)
    #: :class:`str` 产品供应商
    vendor = fields.String(required=True)


class PurchaseResponseSchema(Schema):
    """申购结果"""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 产品名称
    display_name = fields.String()
    #: :class:`str` 订单状态。(unpaid/shelved/paying:订单处理中; success:订单成功; failure:订单失败)
    status = fields.Function(lambda o: o.status.name)
    #: :class:`str` 订单状态 (中文文案)
    status_text = fields.String(attribute='_display_status')


class PurchaseVerifyResponseSchema(Schema):
    """支付结果"""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 产品名称
    display_name = fields.String()
    #: :class:`~decimal.Decimal`  购买金额
    amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 年化收益率
    annual_rate = fields.Decimal(places=2, attribute='_annual_rate')
    #: :class:`~decimal.Decimal` 预期首日收益
    expected_profit = fields.Decimal(places=2, attribute='_expect_interest_first_day')
    #: :class:`str` 订单状态。(unpaid/shelved/paying:订单处理中; success:订单成功; failure:订单失败)
    status = fields.Function(lambda o: o.status.name)
    #: :class:`str` 订单状态 (中文文案)
    status_text = fields.String(attribute='_display_status')


class OrderSchema(Schema):
    """订单实体."""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`~datetime.datetime` 创建时间
    created_at = LocalDateTimeField(attribute='creation_time')
    #: :class:`~decimal.Decimal` 金额
    amount = fields.Decimal(places=2)
    #: :class:`str` 存取状态 （`save` 存入，`redeem` 赎回)
    direction = fields.Function(lambda o: o.direction.name)
    #: :class:`str` 订单状态。(shelved/paying:订单处理中; success:订单成功; failure:订单失败
    #  applyed/redeeming/waiting_back/backing: 转出中)
    status = fields.Function(lambda o: o.status.name)
    #: :class:`str` 订单状态颜色标识
    status_color = fields.String()
    #: :class:`str` 订单状态 (中文文案)
    status_text = fields.String(attribute='display_status')
