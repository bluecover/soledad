# coding: utf-8

from flask import request, jsonify, abort, g
from marshmallow import Schema, fields

from core.models.hoard.zhiwang import (
    ZhiwangAsset, ZhiwangOrder,
    ZhiwangProduct, ZhiwangWrappedProduct)
from core.models.utils.switch import zhiwang_offline_switch
from core.models.hoard.zhiwang.consts import ZWLIB_OFFLINE_TEXT
from core.models.hoard.zhiwang.transaction import (
    subscribe_product, register_zhiwang_account, pay_order as zw_pay_order)
from core.models.hoard.zhiwang.errors import (
    SoldOutError, SuspendedError, OffShelfError, OutOfRangeError,
    RepeatlyRegisterError, SubscribeProductError, ExceedBankAmountLimitError,
    MismatchUserError, DealingError, PayTerminatedError,
    ContractFetchingError, MissingMobilePhoneError, MissingIdentityError,
    UnboundAccountError)
from core.models.hoard.zhiwang.transaction import fetch_asset_contract
from core.models.hoard.zhiwang.utils import get_expect_payback_date
from core.models.bank import Partner
from core.models.profile.signals import before_deleting_bankcard
from core.models.hoard.errors import InvalidIdentityError
from core.models.welfare.coupon.errors import CouponBusinessError
from core.models.welfare.firewood.errors import FirewoodBusinessError
from core.models.hoard.zhiwang.profit_hike import ProfitHikeLockedError

from jupiter.views.api.decorators import require_oauth
from jupiter.views.api.track import events
from ..profile import inject_bankcard_amount_limit
from ..savings import (bp, obtain_bankcard, obtain_coupon, ZhiwangOrderSchema, warning)


@bp.route('/zw/auth', methods=['POST'])
@require_oauth(['savings_w'])
def zhiwang_auth():
    """绑定指旺账户.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 用户已经有指旺账户, 返回 None
    :status 201: 用户自动注册了指旺账户, 返回 None
    :status 403: 绑定账号失败
    """
    if g.zhiwang_account:
        return jsonify(success=True, data=None)

    if zhiwang_offline_switch.is_enabled:
        abort(403, ZWLIB_OFFLINE_TEXT)

    try:
        register_zhiwang_account(request.oauth.user.id_)
    except (MismatchUserError, RepeatlyRegisterError) as e:
        abort(403, u'绑定账号失败: %s' % e.args[0])
    except (MissingMobilePhoneError, MissingIdentityError) as e:
        abort(403, u'绑定账号失败')

    return jsonify(success=True, data=None), 201


@bp.route('/zw/order/<int:order_id>/contract', methods=['GET'])
@require_oauth(['savings_r'])
def zhiwang_contract(order_id):
    """指旺购买合同.

    reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回 :class:`.ZhiwangContractSchema`
    :status 403: 获取合同失败
    """
    contract_schema = ZhiwangContractSchema(strict=True)
    order = ZhiwangOrder.get(order_id)
    asset = ZhiwangAsset.get_by_order_code(order.order_code)
    if not asset:
        abort(403, u'资产合同正在准备中')

    if not asset.contract:
        try:
            content = fetch_asset_contract(request.oauth.user.id_, asset)
        except ContractFetchingError as e:
            abort(403, e.args[0])
    else:
        content = asset.contract
    data = {'contract': content}

    return jsonify(success=True, data=contract_schema.dump(data).data)


@bp.route('/zw/value-date/', methods=['POST'])
@require_oauth(['savings_w'])
def zhiwang_purchase_date():
    """指旺非定期产品到期时间.
    :request: :class:`.ZhiwangPurchaseDateSchema`

    reqheader Authorization: OAuth 2.0 Bearer Token
    """
    date_schema = ZhiwangPurchaseDateSchema(strict=True)
    result = date_schema.load(request.get_json(force=True))
    due_date = result.data['due_date']
    _actual_due_date = get_expect_payback_date(due_date)
    data = {'due_date': due_date,
            'actual_due_date': _actual_due_date}
    return jsonify(success=True, data=date_schema.dump(data).data)


@bp.route('/zw/order', methods=['POST'])
@require_oauth(['savings_w'])
def zhiwang_purchase():
    """选购指旺产品, 创建理财单.

    :request: :class:`.PurchaseSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 因为未完成实名认证或指旺方面原因, 购买请求被拒
    :status 400: 产品或金额无效, 其中产品无效可能是因为停售或售罄
    :status 201: 订单已创建, 返回 :class:`.ZhiwangOrderSchema`
    """
    if zhiwang_offline_switch.is_enabled:
        abort(403, ZWLIB_OFFLINE_TEXT)

    purchase_schema = ZhiwangPurchaseSchema(strict=True)
    order_schema = ZhiwangOrderSchema(strict=True)
    result = purchase_schema.load(request.get_json(force=True))

    product = obtain_zw_product(result.data['product_id'])
    bankcard = obtain_bankcard(result.data['bankcard_id'])
    g.bankcard_manager.set_default(bankcard)
    pay_amount = result.data.get('pay_amount', result.data['amount'])
    pocket_deduction_amount = result.data.get('pocket_deduction_amount')
    coupon = obtain_coupon(result.data.get('coupon_id'))

    wrapped_product_id = result.data.get('wrapped_product_id')
    wrapped_product = ZhiwangWrappedProduct.get(wrapped_product_id)
    if wrapped_product and not wrapped_product.is_qualified(request.oauth.user.id_):
        abort(400, u'用户不具备购买资格')

    if product.product_type is ZhiwangProduct.Type.fangdaibao:
        if wrapped_product:
            due_date = wrapped_product.due_date
        else:
            due_date = result.data['due_date']
    else:
        due_date = None

    try:
        order = subscribe_product(
            request.oauth.user,
            product,
            bankcard,
            result.data['amount'],
            pay_amount,
            due_date,
            wrapped_product=wrapped_product,
            coupon=coupon,
            pocket_deduction_amount=pocket_deduction_amount)
        inject_bankcard_amount_limit(Partner.zw, [order.bankcard])
    except SubscribeProductError as e:
        bankcard_results = before_deleting_bankcard.send(
            bankcard_id=bankcard.id_, user_id=request.oauth.user.id_)
        if any(r for _, r in bankcard_results):
            abort(403, u'%s。如需修改银行卡信息，请联系微信客服（plan141）' % e)
        abort(403, unicode(e))
    except (SoldOutError, SuspendedError, OffShelfError, OutOfRangeError,
            InvalidIdentityError, ExceedBankAmountLimitError,
            CouponBusinessError, FirewoodBusinessError) as e:
        abort(403, unicode(e))
    except (UnboundAccountError) as e:
        abort(403, u'未绑定指旺账户')

    return jsonify(success=True, data=order_schema.dump(order).data), 201


@bp.route('/zw/order/<int:order_id>/verify', methods=['POST'])
@require_oauth(['savings_w'])
def zhiwang_purchase_verify(order_id):
    """提供短信验证码, 支付理财单.

    :request: :class:`.ZhiwangPurchaseVerifySchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 支付务出错
    :status 200: 支付成功, 返回 :class:`.ZhiwangOrderSchema`
    """
    if zhiwang_offline_switch.is_enabled:
        abort(403, ZWLIB_OFFLINE_TEXT)

    purchase_verify_schema = ZhiwangVerifySchema(strict=True)
    order_schema = ZhiwangOrderSchema(strict=True)
    result = purchase_verify_schema.load(request.get_json(force=True))
    order = obtain_zw_order(order_id)
    pay_code = result.data['stashed_payment_id']
    sms_code = result.data['sms_code']

    if not order.is_owner(request.oauth.user):
        abort(403, u'该订单不属于此用户')
    if not sms_code:
        abort(400)

    try:
        zw_pay_order(order, pay_code, sms_code)
    except (ProfitHikeLockedError, FirewoodBusinessError, CouponBusinessError,
            DealingError, PayTerminatedError) as e:
        abort(403, unicode(e))
    else:
        inject_bankcard_amount_limit(Partner.zw, [order.bankcard])

        if order.display_status == u'处理中':
            order._confirm_desc = u'支付成功后第二个工作日'
        else:
            order._confirm_desc = order.start_date.date()
        # FIXME: refine fields in model
        order._due_date = order.due_date.date()

        events['savings_success'].send(
            request, user_id=order.user_id, order_id=order.id_, amount=unicode(order.amount),
            period='{0.value}-{0.unit}'.format(order.profit_period))

    return jsonify(success=True, data=order_schema.dump(order).data)


def obtain_zw_order(order_id):
    order = ZhiwangOrder.get(order_id)
    if not order:
        warning('用户访问不存在的订单', order_id=order_id)
        abort(404, u'该订单不存在')
    if not order.is_owner(request.oauth.user):
        warning('用户访问他人的订单', order_id=order_id)
        abort(403, u'该订单不属于当前账号，无法继续查看')
    return order


def obtain_zw_product(product_id):
    product = ZhiwangProduct.get(product_id)
    if not product:
        warning('用户访问不存在的产品', product_id=product_id)
        abort(400, u'该产品不存在')
    return product


class ZhiwangContractSchema(Schema):
    """指旺购买合同实体."""

    #: :class`.String` 指旺购买合同
    contract = fields.String()


class ZhiwangPurchaseDateSchema(Schema):
    """指旺赎回日期实体."""

    #: :class:`~datetime.date` 到期时间
    due_date = fields.Date()
    #: :class`.Date` 指旺赎回日期
    actual_due_date = fields.Date()


class ZhiwangPurchaseSchema(Schema):
    """指旺购买请求实体."""

    #: :class:`int` 购买产品 (:class:`.ZhiwangProductSchema`) 的唯一 ID
    product_id = fields.Integer(required=True)
    #: :class:`int` 购买包装后产品 (:class:`.ZhiwangProductSchema`) 的唯一 ID
    wrapped_product_id = fields.Integer()
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


class ZhiwangVerifySchema(Schema):
    """指旺购买支付请求实体."""

    #: :class:`str` 银行卡预留手机号收到的短信验证码
    sms_code = fields.String(required=True)
    #: :class:`str` 客户端保存在会话中的支付 ID
    stashed_payment_id = fields.String(required=True)
