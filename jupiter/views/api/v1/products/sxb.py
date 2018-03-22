# coding: utf-8

from datetime import timedelta

from flask import request, jsonify, abort, g, url_for
from marshmallow import Schema, fields

from core.models.hoarder.product import Product, NewComerProduct
from core.models.hoarder.transactions import sxb
from core.models.hoarder.asset import Asset
from core.models.hoarder.vendor import Vendor, Provider
from core.models.bank.partners import Partner
from core.models.hoarder.errors import (PayTerminatedError, OrderInProgressingError,
                                        NotFoundEntityError, OrderUpdateStatusConflictError,
                                        SoldOutError, OrderNotExistError,
                                        OrderMissMatchUserError, RepeatRegisterError,
                                        SuspendedError, MismatchUserError,
                                        OffShelfError, MissingMobilePhoneError,
                                        InvalidIdentityError, UnboundAccountError,
                                        OutOfRangeError, MissingIdentityError,
                                        SubscribeProductError,
                                        ExceedBankAmountLimitError)
from core.models.welfare.coupon.errors import (CouponError, CouponUsageError)
from core.models.welfare.firewood.errors import FirewoodException
from core.models.utils import round_half_up
from jupiter.views.api.track import events
from .consts import PRODUCT_PROFILE, sale_display_text
from ...decorators import require_oauth
from ...fields import LocalDateTimeField
from ..profile import inject_bankcard_amount_limit
from ..savings import (bp, obtain_bankcard, obtain_coupon, warning)


@bp.route('/sxb/auth', methods=['POST'])
@require_oauth(['savings_w'])
def sxb_auth():
    """绑定账户.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 用户已经有账户, 返回 None
    :status 201: 用户自动注册了账户, 返回 None
    :status 403: 绑定账号失败
    """
    if g.sxb_account:
        return jsonify(success=True, data=None)

    # TODO: 需要增加服务器维护时间段。

    try:
        sxb.register_account(request.oauth.user.id_)
    except (MismatchUserError, RepeatRegisterError) as e:
        abort(403, u'绑定账号失败: %s' % e.args)
    except (MissingMobilePhoneError, MissingIdentityError) as e:
        abort(403, u'绑定账号失败')

    return jsonify(success=True, data=None), 201


def get_sxb_products(user_id):
    vendor = Vendor.get_by_name(Provider.sxb)
    vendor_product_profile = PRODUCT_PROFILE[vendor.provider]
    products = [p for p in Product.get_products_by_vendor_id(vendor.id_)
                if p.kind is Product.Kind.father]
    new_products = [p for p in NewComerProduct.get_products_by_vendor_id(vendor.id_)
                    if p.kind is Product.Kind.child]
    products.extend(new_products)

    for product in products:
        if product.kind is Product.Kind.child:
            father_product = NewComerProduct.get_father_product_by_vendor_id(product.vendor.id_)
            product_id = father_product.id_
        else:
            product_id = product.id_
        assets = Asset.gets_by_user_id_with_product_id(user_id, product_id)
        product.rest_hold_amount = round_half_up(product.max_amount, 2)
        if assets:
            rest_hold_amount = product.max_amount - sum(asset.total_amount for asset in assets)
            product.rest_hold_amount = rest_hold_amount if rest_hold_amount > 0 else 0
            product.remaining_amount_today = sum(
                [asset.remaining_amount_today for asset in assets])
        if product.is_on_sale:
            product.button_display_text, product.button_click_text = (
                sale_display_text['on_sale'])
        elif product.is_taken_down:
            product.button_display_text, product.button_click_text = (
                sale_display_text['late_morning_off_sale'] if product.kind is Product.Kind.father
                else sale_display_text['middle_morning_off_sale'])
        elif product.is_sold_out:
            product.button_display_text, product.button_click_text = (
                sale_display_text['late_morning_sold_out'] if product.kind is Product.Kind.father
                else sale_display_text['late_morning_sold_out'])
        if product.kind is Product.Kind.child:
            product.rest_hold_amount = 10000
            product.max_amount = 10000
            product.introduction = vendor_product_profile['new_comer']['product_introduction']
            product.title = vendor_product_profile['new_comer']['product_title']
            product.activity_title = vendor_product_profile['new_comer']['activity_title']
            product.activity_introduction = (
                vendor_product_profile['new_comer']['activity_introduction'])
            product.annual_rate = product.operation_num * 100
        else:
            product.introduction = vendor_product_profile['sxb']['product_introduction']
            product.title = vendor_product_profile['sxb']['product_title']
            product.activity_title = vendor_product_profile['sxb']['activity_title']
            product.activity_introduction = vendor_product_profile['sxb']['activity_introduction']
            product.annual_rate = product.rate * 100
        # is_either_sold_out, unique_product_id 为兼容老产品字段
        product.is_either_sold_out = product.is_sold_out
        product.unique_product_id = product.remote_id
        product.is_able_purchased = product.is_on_sale
        product.check_benifit_date = product.value_date + timedelta(days=1)
        product.withdraw_rule = url_for('hybrid.rules.sxb_withdraw', _external=True)
        product.agreement = url_for('savings.landing.agreement_xinmi', _external=True)
        product._total_amount = 0
        product.annotations = []

    return products


@bp.route('/sxb/order', methods=['POST'])
@require_oauth(['savings_w'])
def sxb_purchase():
    """选购产品, 创建理财单.

    :request: :class:`.PurchaseSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 因为未完成实名认证或第三方方面原因, 购买请求被拒
    :status 400: 产品或金额无效, 其中产品无效可能是因为停售或售罄
    :status 201: 订单已创建, 返回 :class:`.ProductSchema`
    """
    # TODO: 需要增加服务器维护时间段。

    purchase_schema = PurchaseSchema(strict=True)
    response_schema = PurchaseResponseSchema()
    result = purchase_schema.load(request.get_json(force=True))

    product_id = result.data['product_id']
    bankcard = obtain_bankcard(result.data['bankcard_id'])
    g.bankcard_manager.set_default(bankcard)
    amount = result.data.get('amount', 0) or 0
    pocket_deduction_amount = result.data.get('pocket_deduction_amount', 0) or 0
    coupon = obtain_coupon(result.data.get('coupon_id'))
    p = Product.get(product_id)
    if not p:
        abort(400, u'产品已下架')
    if amount < p.min_amount:
        abort(400, u'申购金额不能少于%s元' % round_half_up(p.min_amount, 2))
    try:
        order = sxb.subscribe_product(
            request.oauth.user,
            product_id,
            bankcard,
            amount,
            coupon,
            pocket_deduction_amount)
        inject_bankcard_amount_limit(Partner.xm, [order.bankcard])
    except NotFoundEntityError as e:
        warning('随心宝未找到相应实体', exception=e)
        abort(400, '未知错误')
    except (SubscribeProductError, UnboundAccountError) as e:
        abort(403, unicode(e))
    except (CouponError, CouponUsageError) as e:
        abort(403, unicode(e))
    except (SoldOutError, SuspendedError, OffShelfError, OutOfRangeError,
            InvalidIdentityError, ExceedBankAmountLimitError) as e:
        abort(403, unicode(e))
    except FirewoodException:
        abort(403, u'红包出现错误，请稍后再试或联系客服')

    order._display_status = order.status.display_text

    return jsonify(success=True, data=response_schema.dump(order).data), 201


@bp.route('/sxb/orders', methods=['GET'])
@require_oauth(['savings_r'])
def sxb_orders():
    """用户已有订单.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 403: 不合法用户，禁止访问
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 `.SxbOrderSchema` 列表
    :query: 可选参数，按订单请求数限制返回结果. 目前可为:

                - ``"offset"`` 开始条数
                - ``"count"`` 每页数量

    """

    orders_schema = OrderSchema(strict=True, many=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    if g.sxb_account:
        orders = sxb.get_orders(g.sxb_account, offset, count)
    else:
        orders = []
    return jsonify(success=True, data=orders_schema.dump(orders).data)


@bp.route('/sxb/order/<int:order_id>/verify', methods=['POST'])
@require_oauth(['savings_w'])
def sxb_purchase_verify(order_id):
    """提供短信验证码, 支付理财单.

    :request: :class:`.PurchaseVerifySchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 支付事务出错
    :status 200: 支付成功, 返回 :class:`.OrderSchema`
    """
    # TODO: 增加不可用时间控制。

    purchase_verify_schema = VerifySchema(strict=True)
    response_schema = PurchaseVerifyResponseSchema(strict=True)
    result = purchase_verify_schema.load(request.get_json(force=True))
    sms_code = result.data['sms_code']

    if not sms_code:
        abort(400)
    try:
        order = sxb.pay_order(order_id, request.oauth.user, sms_code)
    except (CouponError, FirewoodException, PayTerminatedError, OrderInProgressingError,
            OrderUpdateStatusConflictError, OrderMissMatchUserError,
            OrderNotExistError) as e:
        abort(403, unicode(e))

    if order.status.display_text == u'已存入':
        order._display_status = u'您已支付成功'
    else:
        order._display_status = order.status.display_text

    if order.product.kind is Product.Kind.child:
        new_comer_product = NewComerProduct.get(order.product.id_)
        # 年化率
        order._annual_rate = new_comer_product.operation_num * 100
        # 首日收益
        order._expect_interest_first_day = new_comer_product.operation_num * order.amount / 365
    else:
        order._annual_rate = order.product.rate * 100
        order._expect_interest_first_day = order.product.rate * order.amount / 365

    events['savings_success'].send(
        request, user_id=order.user_id, order_id=order.id_, amount=unicode(order.amount),
        period='dynamic')
    return jsonify(success=True, data=response_schema.dump(order).data)


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


class VerifySchema(Schema):
    """支付请求参数."""

    #: :class:`str` 银行卡预留手机号收到的短信验证码
    sms_code = fields.String(required=True)


class ProductSchema(Schema):
    """产品"""

    #: :class: `str` 产品 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 产品名称 ID
    name = fields.String()


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
