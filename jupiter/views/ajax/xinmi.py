# coding: utf-8

from flask import jsonify, g, request, abort, url_for
from flask_wtf import Form

from core.models.bank import Partner
from core.models.welfare import Coupon
from core.models.welfare.coupon.errors import CouponBusinessError
from core.models.hoard.errors import InvalidIdentityError
from core.models.hoard.xinmi import (
    XMProfile, XMAccount, XMFixedDuedayProduct, XMOrder)
from core.models.hoard.zhiwang.profit_hike import ProfitHikeLockedError
from core.models.hoard.xinmi.transaction import subscribe_product, pay_order
from core.models.hoard.xinmi.errors import (
    PayTerminatedError, SoldOutError, SuspendedError, OffShelfError,
    OutOfRangeError, SubscribeProductError, ExceedBankAmountLimitError,
    OrderUpdateStatusConflictError)
from core.models.welfare.firewood.errors import FirewoodBusinessError
from .blueprint import create_blueprint
from ._transaction import transaction_mixin


bp = create_blueprint('xinmi', __name__, url_prefix='/j/savings/xm')


@bp.before_request
def checkin():
    if not g.user:
        abort(401)
    if not XMAccount.get_by_local(g.user.id):
        abort(400)


@bp.route('/subscribe', methods=['POST'])
def order():
    """认购产品"""
    # 基础数据
    profile = XMProfile.add(g.user.id_) if g.user else abort(401)
    bankcard_id = request.form.get('bankcard_id', type=int) or abort(400)
    bankcard = profile.bankcards.get(bankcard_id) or abort(400)
    if Partner.xm not in bankcard.bank.available_in:
        abort(400, 'unsupported bankcard')
    coupon_id = request.form.get('coupon_id', type=int, default=0)
    coupon = Coupon.get(coupon_id)
    if coupon and not coupon.is_owner(g.user):
        abort(403)
    product_id = request.form.get('product_id', type=int, default=0)
    product = XMFixedDuedayProduct.get(product_id) or abort(404)

    # 选择表单验证
    form = select_subscribe_form(product)()
    if not form.validate():
        return jsonify(r=False, error=form.errors.values()[0][0])

    # 设置购买卡为默认卡
    profile.bankcards.set_default(bankcard)

    # 申购产品
    try:
        order = subscribe_product(
            g.user,
            product,
            bankcard,
            form.data['order_amount'],
            form.data['pay_amount'],
            product.due_date,
            coupon=coupon,
            pocket_deduction_amount=form.data['pocket_deduction_amount'])
    except (SoldOutError, SuspendedError, OffShelfError, OutOfRangeError,
            InvalidIdentityError, ExceedBankAmountLimitError, SubscribeProductError,
            CouponBusinessError, FirewoodBusinessError) as e:
        return jsonify(r=False, error=unicode(e))

    payment_url = url_for('.pay', order_code=order.order_code, pay_code=order.pay_code)
    return jsonify(r=True, payment_url=payment_url)


@bp.route('/order/<string:order_code>/payment/<string:pay_code>', methods=['POST'])
def pay(order_code, pay_code):
    """支付订单"""
    sms_code = request.form.get('sms_code').strip()
    order = XMOrder.get_by_order_code(order_code) or abort(404)

    if not order.is_owner(g.user):
        abort(403, u'该订单不属于此用户')
    if order.status in [XMOrder.Status.committed, XMOrder.Status.shelved]:
        abort(403, u'您的订单已在处理中，请勿重复提交')
    if not sms_code:
        abort(400)

    # 向新米发起支付请求
    try:
        pay_order(order, sms_code)
    except (ProfitHikeLockedError, FirewoodBusinessError, CouponBusinessError,
            OrderUpdateStatusConflictError, PayTerminatedError) as e:
        # 优惠被冻结、抵扣金使用错误、礼券无法使用、订单正在被处理或支付被告知失败
        abort(403, unicode(e))

    redirect_url = url_for('savings.xinmi.order_complete', order_id=order.id_)
    return jsonify(r=True, redirect_url=redirect_url)


def select_subscribe_form(product):
        return transaction_mixin(ClassicalOrderSubscribeForm)


class ClassicalOrderSubscribeForm(Form):
    pass
