# coding: utf-8

from flask import request, jsonify, abort, g
from flask_mako import render_template
from marshmallow import Schema, fields

from libs.utils.string import num2chn
from core.models.utils import round_half_up
from core.models.hoard.xinmi import XMOrder, XMAsset, XMFixedDuedayProduct
from core.models.hoard.xinmi.product import XMProduct
from core.models.hoard.xinmi.transaction import (
    subscribe_product as xm_subscribe_product, register_xm_account, pay_order as xm_pay_order)
from core.models.hoard.xinmi.errors import (OrderUpdateStatusConflictError,
                                            PayTerminatedError as XMPayTerminatedError,
                                            SoldOutError as XMSoldOutError,
                                            SuspendedError as XMSuspendedError,
                                            OffShelfError as XMOffShelfError,
                                            OutOfRangeError as XMOutOfRangeError,
                                            RepeatlyRegisterError as XMRepeatlyRegisterError,
                                            SubscribeProductError as XMSubscribeProductError,
                                            ExceedBankAmountLimitError as
                                            XMExceedBankAmountLimitError,
                                            MismatchUserError as XMMismatchUserError,
                                            MissingMobilePhoneError as XMMissingMobilePhoneError,
                                            MissingIdentityError as XMMissingIdentityError,
                                            UnboundAccountError as XMUnboundAccountError)
from core.models.bank import Partner
from core.models.hoard.errors import (NotFoundError, InvalidIdentityError)
from core.models.profile.signals import before_deleting_bankcard
from core.models.welfare.coupon.errors import (CouponError, CouponUsageError)
from core.models.welfare.firewood.errors import (
    FirewoodException as LocalFirewoodException,
    FirewoodException as RemoteFirewoodException)
from core.models.welfare.firewood.consts import FIREWOOD_ERROR_MAPPINGS
from core.models.hoard.zhiwang.profit_hike import ProfitHikeLockedError
from core.models.profile.identity import Identity

from jupiter.views.api.decorators import require_oauth
from jupiter.views.api.track import events
from ..profile import inject_bankcard_amount_limit
from ..savings import (bp, obtain_bankcard, obtain_coupon, XinmiOrderSchema, warning)


@bp.route('/xm/auth', methods=['POST'])
@require_oauth(['savings_w'])
def xm_auth():
    """绑定新米账户.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 用户已经有指旺账户, 返回 None
    :status 201: 用户自动注册了指旺账户, 返回 None
    :status 403: 绑定账号失败
    """
    if g.xm_account:
        return jsonify(success=True, data=None)

    # TODO: 需要增加服务器维护时间段。
    # if zhiwang_offline_switch.is_enabled:
    #     abort(403, ZWLIB_OFFLINE_TEXT)

    try:
        register_xm_account(request.oauth.user.id_)
    except (XMMismatchUserError, XMRepeatlyRegisterError) as e:
        abort(403, u'绑定账号失败: %s' % e.args[0])
    except (XMMissingMobilePhoneError, XMMissingIdentityError) as e:
        abort(403, u'绑定账号失败')

    return jsonify(success=True, data=None), 201


@bp.route('/xm/order', methods=['POST'])
@require_oauth(['savings_w'])
def xm_purchase():
    """选购新米产品, 创建理财单.

    :request: :class:`.PurchaseSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 因为未完成实名认证或新米方面原因, 购买请求被拒
    :status 400: 产品或金额无效, 其中产品无效可能是因为停售或售罄
    :status 201: 订单已创建, 返回 :class:`.ZhiwangOrderSchema`
    """
    # TODO: 需要增加服务器维护时间段。
    # if zhiwang_offline_switch.is_enabled:
    #     abort(403, ZWLIB_OFFLINE_TEXT)

    purchase_schema = XinmiPurchaseSchema(strict=True)
    order_schema = XinmiOrderSchema(strict=True)
    result = purchase_schema.load(request.get_json(force=True))

    product = obtain_xm_product(result.data['product_id'])
    bankcard = obtain_bankcard(result.data['bankcard_id'])
    g.bankcard_manager.set_default(bankcard)
    pay_amount = result.data.get('pay_amount', result.data['amount'])
    pocket_deduction_amount = result.data.get('pocket_deduction_amount')
    coupon = obtain_coupon(result.data.get('coupon_id'))

    if product.product_type is XMProduct.Type.classic:
        due_date = result.data['due_date']
    else:
        due_date = None

    try:
        order = xm_subscribe_product(
            request.oauth.user,
            product,
            bankcard,
            result.data['amount'],
            pay_amount,
            due_date,
            coupon=coupon,
            pocket_deduction_amount=pocket_deduction_amount)
        inject_bankcard_amount_limit(Partner.xm, [order.bankcard])
    except NotFoundError:
        abort(400, u'未知错误')
    except XMSubscribeProductError as e:
        bankcard_results = before_deleting_bankcard.send(
            bankcard_id=bankcard.id_, user_id=request.oauth.user.id_)
        if any(r for _, r in bankcard_results):
            abort(403, u'%s。如需修改银行卡信息，请联系微信客服（plan141）' % e)
        abort(403, unicode(e))
    except (CouponError, CouponUsageError) as e:
        abort(403, unicode(e))
    except (XMSoldOutError, XMSuspendedError, XMOffShelfError, XMOutOfRangeError,
            InvalidIdentityError, XMExceedBankAmountLimitError) as e:
        abort(403, unicode(e))
    except (LocalFirewoodException, NotFoundError):
        abort(403, u'红包出现错误，请稍后再试或联系客服')
    except (XMUnboundAccountError):
        abort(403, u'未绑定新米账户')

    return jsonify(success=True, data=order_schema.dump(order).data), 201


@bp.route('/xm/order/<int:order_id>/verify', methods=['POST'])
@require_oauth(['savings_w'])
def xm_purchase_verify(order_id):
    """提供短信验证码, 支付理财单.

    :request: :class:`.XinmiPurchaseVerifySchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 支付务出错
    :status 200: 支付成功, 返回 :class:`.XinmiOrderSchema`
    """
    # TODO: 增加新米不可用时间控制。
    # if zhiwang_offline_switch.is_enabled:
    #     abort(403, ZWLIB_OFFLINE_TEXT)

    purchase_verify_schema = XinmiVerifySchema(strict=True)
    order_schema = XinmiOrderSchema(strict=True)
    result = purchase_verify_schema.load(request.get_json(force=True))
    order = obtain_xm_order(order_id)
    # pay_code = result.data['stashed_payment_id']
    sms_code = result.data['sms_code']

    if not order.is_owner(request.oauth.user):
        abort(403, u'该订单不属于此用户')
    if order.status in [XMOrder.Status.committed, XMOrder.Status.shelved]:
        abort(403, u'您的订单已在处理中，请勿重复提交')
    if not sms_code:
        abort(400)

    try:
        xm_pay_order(order, sms_code)
    except LocalFirewoodException:
        abort(403, u'红包出现错误，请稍后再试或联系客服')
    except RemoteFirewoodException as e:
        abort(403, FIREWOOD_ERROR_MAPPINGS[e.errors[0].kind])
    except (CouponError, ProfitHikeLockedError, XMPayTerminatedError,
            OrderUpdateStatusConflictError) as e:
        abort(403, unicode(e))
    else:
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

    return jsonify(success=True, data=order_schema.dump(order).data)


@bp.route('/xm/order/<int:order_id>/contract', methods=['GET'])
@require_oauth(['savings_r'])
def xm_contract(order_id):
    """新米购买合同.

    reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回 :class:`.XinmiContractSchema`
    :status 403: 获取合同失败
    :status 404: 无相应产品
    """
    contract_schema = XinmiContractSchema(strict=True)
    order = obtain_xm_order(order_id)
    asset = XMAsset.get_by_order_code(order.order_code)
    if not asset or not g.xm_account:
        abort(401)
    identity = Identity.get(asset.user_id)
    upper_amount = num2chn(asset.create_amount)
    product = XMFixedDuedayProduct.get(asset.product_id)
    if not product:
        abort(404)
    expect_rate = 100
    if product.product_type is XMFixedDuedayProduct.Type.classic:
        expect_rate = round_half_up((asset.actual_annual_rate * 90 / 365 + 1) * 100, 4)
    if not asset:
        abort(403, u'资产合同正在准备中')

    contract = render_template('savings/agreement_xinmi.html', asset=asset,
                               identity=identity, expect_rate=expect_rate,
                               product_name=product.name,
                               product_frozen_days=product.frozen_days,
                               upper_amount=upper_amount)
    data = {'contract': contract}

    return jsonify(success=True, data=contract_schema.dump(data).data)


def obtain_xm_order(order_id):
    order = XMOrder.get(order_id)
    if not order:
        warning('用户访问不存在的订单', order_id=order_id)
        abort(404, u'该订单不存在')
    if not order.is_owner(request.oauth.user):
        warning('用户访问他人的订单', order_id=order_id)
        abort(403, u'该订单不属于当前账号，无法继续查看')
    return order


def obtain_xm_product(product_id):
    product = XMProduct.get(product_id)
    if not product:
        warning('用户访问不存在的产品', product_id=product_id)
        abort(400, u'该产品不存在')
    return product


class XinmiContractSchema(Schema):
    """新米购买合同实体."""

    #: :class`.String` 新米购买合同
    contract = fields.String()


class XinmiPurchaseDateSchema(Schema):
    """新米赎回日期实体."""

    #: :class:`~datetime.date` 到期时间
    due_date = fields.Date()
    #: :class`.Date` 新米赎回日期
    actual_due_date = fields.Date()


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


class XinmiVerifySchema(Schema):
    """新米购买支付请求实体."""

    #: :class:`str` 银行卡预留手机号收到的短信验证码
    sms_code = fields.String(required=True)
    #: :class:`str` 客户端保存在会话中的支付 ID
    # stashed_payment_id = fields.String(required=True)
