# coding: utf-8

import datetime
from decimal import Decimal

from flask import current_app

from xmlib.errors import BusinessError
from xmlib.consts import OrderStatus
from envcfg.json.solar import DEBUG

from jupiter.ext import xinmi, sentry
from libs.logger.rsyslog import rsyslog
from core.models.user.account import Account
from core.models.profile.identity import Identity
from core.models.welfare import (FirewoodWorkflow, FirewoodBurning,
                                 CouponUsageRecord, CouponRegulation)
from core.models.hoard.xinmi.product import XMProduct, get_next_work_day
from jupiter.workers.hoard_xm import xm_cancel_order_prepare
from core.models.utils import round_half_up
from .account import XMAccount
from .order import XMOrder
from .errors import (
    MismatchUserError, PayTerminatedError, SubscribeProductError,
    MissingIdentityError, MissingMobilePhoneError,
    FetchLoansDigestError)
from .loan import XMLoansDigest
from ..providers import xmpay as provider_xinmi
from .profit_hike import XMOrderProfitHike as Hike, ProfitHikeItem as HikeItem

# 订单超时180秒自动取消订单
TIME_OUT_SECONDS = 180


def register_xm_account(user_id):
    identity = Identity.get(user_id)
    local_account = Account.get(user_id)
    xm_account = XMAccount.get_by_local(user_id)
    if not local_account.mobile:
        raise MissingMobilePhoneError
    if not identity:
        raise MissingIdentityError
    if xm_account:
        return xm_account

    try:
        response = xinmi.create_account(user_id=user_id, person_name=identity.person_name,
                                        person_ricn=identity.person_ricn,
                                        mobile=local_account.mobile)
    except BusinessError as e:
        raise MismatchUserError(u'%s，如有问题，请联系客服' % e)
    else:
        if not response.is_new:
            if not current_app.debug:
                rsyslog.send(
                    u'您的身份信息(%s,%s,%s,%s) 已经被注册过，如有问题，请联系客服' %
                    (user_id, identity.person_ricn, identity.person_name, local_account.mobile),
                    'xm_dup_register')
        return XMAccount.bind(user_id, response.user_id)


def collect_profit_hikes(user, coupon, pocket_deduction_amount):
    hike_list = list()

    # 检查礼券优惠
    if coupon:
        if coupon.regulation.kind is CouponRegulation.Kind.annual_rate_supplement:
            # 加息券
            hike_list.append(HikeItem(
                Hike.Kind.coupon_rate, annual_rate=coupon.regulation.supply_rate))
        elif coupon.regulation.kind is CouponRegulation.Kind.quota_deduction:
            # 抵扣券
            hike_list.append(HikeItem(
                Hike.Kind.coupon_deduction, deduction_amount=coupon.regulation.deduct_quota))
        else:
            raise

    # 检查红包抵扣优惠
    if pocket_deduction_amount:
        hike_list.append(
            HikeItem(Hike.Kind.firewood_deduction, deduction_amount=pocket_deduction_amount))

    return hike_list


def subscribe_product(user, product, bankcard, order_amount, pay_amount, due_date=None,
                      coupon=None, pocket_deduction_amount=0):
    """申购产品"""
    # 检查礼券是否可用、返现账户抵扣是否可用、订单是否可建
    if coupon:
        coupon.check_before_use(product, order_amount)
    if pocket_deduction_amount > 0:
        FirewoodWorkflow(user.id_).check_deduction_enjoyable(
            product, order_amount, pocket_deduction_amount)
    XMOrder.check_before_adding(
        user.id_, bankcard.id_, product.product_id, order_amount)

    # 获取订单优惠信息并检查合法性
    hike_list = collect_profit_hikes(user, coupon, pocket_deduction_amount)
    rate_bonus = max([h.annual_rate for h in hike_list]) if hike_list else Decimal('0')
    discount_fee = sum([h.deduction_amount for h in hike_list])
    assert rate_bonus < Decimal('5.0')  # 新米最高加息限制
    assert order_amount - discount_fee == pay_amount
    # 新米使用加息券需要在赎回确认里加入
    redeem_confirm = u'1' if rate_bonus > Decimal('0.0') else None
    rate_fee = float(order_amount * rate_bonus * product.frozen_days / 100 / 365)

    order_code = XMOrder.gen_order_code()

    xm_cancel_order_prepare.produce(order_code, delay=TIME_OUT_SECONDS)

    identity = Identity.get(user.id_)

    buy_amount = order_amount
    try:
        # 向投米发起申购请求
        if DEBUG:
            # 测试环境要求 购买金额x100后为偶数 => 购买成功，否则失败。
            if int(buy_amount) % 2 != 0:
                buy_amount += round_half_up(0.01, 2)
            buy_amount = round_half_up(buy_amount, 2)
        response = xinmi.order_apply(product_id=product.product_id,
                                     order_id=order_code,
                                     buy_amount=buy_amount,
                                     discount_fee=discount_fee,
                                     user_id=user.id_, province=bankcard.province_id,
                                     city=bankcard.city_id, person_name=identity.person_name,
                                     person_ricn=identity.person_ricn,
                                     mobile=bankcard.mobile_phone, bank_code=bankcard.bank.xm_id,
                                     bank_account=bankcard.card_number,
                                     account_name=identity.person_name,
                                     redeem_confirm=redeem_confirm)

    except BusinessError as e:
        raise SubscribeProductError(u'申购产品失败: %s' % e)

    assert buy_amount == round_half_up(response.buy_amount, 2)

    if product.product_type == XMProduct.Type.classic:
        due_date = get_next_work_day(response.buy_time) + datetime.timedelta(
            days=product.frozen_days)
    # 创建订单
    order = XMOrder.add(user_id=user.id_, product_id=product.product_id,
                        bankcard_id=bankcard.id_, amount=buy_amount,
                        pay_amount=response['total_amount'],
                        expect_interest=response.return_amount + rate_fee,
                        start_date=get_next_work_day(response.buy_time),
                        due_date=due_date, order_code=order_code,
                        pay_code=response.pay_code)
    # 创建优惠记录
    for hike in hike_list:
        # FIXME: the operation of hikes should be managed in one session
        Hike.add(user.id_, order.id_, hike.kind, hike.annual_rate, hike.deduction_amount)
    # 订单预绑定礼券
    if coupon:
        CouponUsageRecord.add(coupon, user, provider_xinmi, order)
    # 创建抵扣使用记录
    if pocket_deduction_amount > 0:
        FirewoodBurning.add(
            user, pocket_deduction_amount, FirewoodBurning.Kind.deduction,
            provider_xinmi, order.id_)

    return order


def pay_order(order, sms_code, description=None):
    """最终支付过程需进行礼券，优惠的锁检查"""
    # lock firewoods&coupons&hikes
    order.lock_bonus()

    try:
        # 调用第三方接口发起支付
        order_result = xinmi.confirm_apply(
            product_id=order.product_id,
            order_id=order.order_code,  # 订单流水号
            buy_amount=order.amount,  # 认购金额
            discount_fee=order.amount-order.pay_amount,  # 优惠金额
            user_id=order.user_id,
            pay_code=order.pay_code,  # 订单支付单号
            sms_code=sms_code,  # 手机验证码
            remark=description
        )
        if order_result:
            if order:
                order.status = XMOrder.MUTUAL_STATUS_MAP[order_result.order_status]
    except BusinessError as e:
        order.unlock_bonus()
        raise PayTerminatedError(u'支付执行失败: %s' % e)

    return order_result


def cancel_order(order_code):
    """取消订单"""
    try:
        # 调用第三方接口取消订单
        result = xinmi.cancel(order_code)
        if result:
            if result.order_status is OrderStatus.user_cancel:
                order = XMOrder.get_by_order_code(order_code)
                if order:
                    order.status = XMOrder.MUTUAL_STATUS_MAP[result.order_status]
    except BusinessError:
        sentry.captureException()


def fetch_loans_digest(asset):
    try:
        data = xinmi.get_creditor_rights(order_id=asset.order_code)
    except BusinessError:
        sentry.captureException()
        raise FetchLoansDigestError()
    else:
        return XMLoansDigest.create_or_update(asset, data)
