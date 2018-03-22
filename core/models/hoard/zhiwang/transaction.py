# coding: utf-8

from decimal import Decimal

from gb2260 import Division
from flask import current_app
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

from zwlib.client import RemoteError

from jupiter.ext import zhiwang, sentry
from libs.logger.rsyslog import rsyslog
from core.models.welfare import (
    CouponUsageRecord, CouponRegulation, FirewoodWorkflow, FirewoodBurning)
from core.models.user.account import Account
from core.models.profile.identity import Identity
from .account import ZhiwangAccount
from .order import ZhiwangOrder
from .consts import ZWLIB_ERROR_MAPPING
from .profit_hike import ZhiwangOrderProfitHike as Hike, ProfitHikeItem as HikeItem
from .errors import (
    MismatchUserError, SubscribeProductError, ContractFetchingError, PayTerminatedError,
    MissingIdentityError, MissingMobilePhoneError,
    FetchLoansDigestError)
from ..providers import zhiwang as provider_zhiwang
from .loan import ZhiwangLoansDigest


def register_zhiwang_account(user_id):
    identity = Identity.get(user_id)
    local_account = Account.get(user_id)
    zhiwang_account = ZhiwangAccount.get_by_local(user_id)
    if not local_account.mobile:
        raise MissingMobilePhoneError
    if not identity:
        raise MissingIdentityError
    if zhiwang_account:
        return zhiwang_account

    try:
        response = zhiwang.user_create(
            user_id, identity.person_ricn, identity.person_name, local_account.mobile)
    except RemoteError as e:
        raise MismatchUserError(u'绑定账号失败: %s，如有问题，请联系客服' % e.args[1])
    else:
        if not response.is_new:
            if not current_app.debug:
                rsyslog.send(
                    u'您的身份信息(%s,%s,%s,%s) 已经被注册过，如有问题，请联系客服' %
                    (user_id, identity.person_ricn, identity.person_name, local_account.mobile),
                    'zhiwang_dup_register')
        return ZhiwangAccount.bind(user_id, response.zw_user_code)


def fetch_asset_contract(user_id, asset):
    zw_ucode = ZhiwangAccount.get_by_local(user_id).zhiwang_id
    try:
        response = zhiwang.asset_contract(zw_ucode, asset.asset_no)
    except RemoteError as e:
        raise ContractFetchingError(u'获取合同失败: %s，请刷新重试或联系客服处理' % e.args[1])
    else:
        return response


def collect_profit_hikes(user, coupon, pocket_deduction_amount, wrapped_product):
    hike_list = list()

    # 检查产品优惠
    if wrapped_product:
        extra_rate = wrapped_product.get_profit_hike(user.id_)
        if extra_rate and wrapped_product.profit_hike_kind is Hike.Kind.newcomer:
            hike_list.append(HikeItem(Hike.Kind.newcomer, annual_rate=extra_rate))

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


def subscribe_product(user, product, bankcard, order_amount, pay_amount, due_date,
                      wrapped_product=None, coupon=None, pocket_deduction_amount=0):
    """申购产品"""
    # 检查礼券是否可用、返现账户抵扣是否可用、订单是否可建
    if coupon:
        coupon.check_before_use(wrapped_product or product, order_amount)
    if pocket_deduction_amount > 0:
        FirewoodWorkflow(user.id_).check_deduction_enjoyable(
            wrapped_product or product, order_amount, pocket_deduction_amount)
    wrapped_product_id = wrapped_product.id_ if wrapped_product else None
    ZhiwangOrder.check_before_adding(
        user.id_, bankcard.id_, product.product_id, order_amount, wrapped_product_id)

    # 获取订单优惠信息并检查合法性
    hike_list = collect_profit_hikes(user, coupon, pocket_deduction_amount, wrapped_product)
    rate_bonus = max([h.annual_rate for h in hike_list]) if hike_list else Decimal('0')
    deduction_bonus = sum([h.deduction_amount for h in hike_list])
    assert rate_bonus < Decimal('5.0')  # 指旺最高加息限制
    assert order_amount - deduction_bonus == pay_amount

    try:
        # 向指旺发起申购请求
        response = zhiwang.order_apply_with_coupon(
            ZhiwangAccount.get_by_local(user.id_).zhiwang_id,  # 用户的指旺ID
            product.product_id,  # 用户认购的产品
            rate_bonus,  # 加息值
            order_amount,  # 订单金额
            pay_amount,  # 实际支付金额
            bankcard.card_number,  # 银行卡号
            int(bankcard.bank.zwlib_id),  # 银行ID
            bankcard.mobile_phone,  # 银行预留手机号
            due_date.strftime('%Y-%m-%d') if due_date else None,  # TODO: 认购产品到期日
            Division.get(bankcard.province_id, year=2006).name,  # 银行卡开卡省份
            Division.get(bankcard.city_id, year=2006).name)  # 银行卡开卡市
    except RemoteError as e:
        err_msg = e.args[1]
        err_msg = ZWLIB_ERROR_MAPPING.get(err_msg, err_msg)
        raise SubscribeProductError(u'申购产品失败: %s' % err_msg)

    assert pay_amount == response.pay_amount

    # 创建订单
    order = ZhiwangOrder.add(
        user.id_, product.product_id, bankcard.id_, order_amount, response.pay_amount,
        response.expect_interest, response.interest_start_date, response.interest_end_date,
        response.order_code, response.pay_code, wrapped_product_id)
    # 创建优惠记录
    for hike in hike_list:
        # FIXME: the operation of hikes should be managed in one session
        Hike.add(user.id_, order.id_, hike.kind, hike.annual_rate, hike.deduction_amount)
    # 订单预绑定礼券
    if coupon:
        CouponUsageRecord.add(coupon, user, provider_zhiwang, order)
    # 创建抵扣使用记录
    if pocket_deduction_amount > 0:
        FirewoodBurning.add(
            user, pocket_deduction_amount, FirewoodBurning.Kind.deduction,
            provider_zhiwang, order.id_)
    return order


def pay_order(order, pay_code, sms_code):
    """发起支付"""
    # 对订单涉及到的礼券、抵扣优惠开启业务排斥锁
    order.lock_bonus()

    # 更新订单状态为已请求并为支付开启事务排斥锁
    # order.update_status(ZhiwangOrder.Status.committed)

    try:
        # 调用第三方接口发起支付
        zhiwang.order_pay(
            ZhiwangAccount.get_by_local(order.user_id).zhiwang_id,  # 用户指旺ID
            order.order_code,  # 订单流水号
            order.pay_code,  # 订单支付单号
            sms_code,  # 手机验证码
            order.pay_amount  # 实际支付金额
        )
    except RemoteError as e:
        status, msg = e.args
        if status == 'pay_wait':
            # 订单支付仍在进行，订单、优惠、礼券依旧被冻结
            order.update_status(ZhiwangOrder.Status.paying)
        elif status == 'pay_success_before':
            # 支付被告知已成功过，前往结束页
            pass
        else:
            # 释放被冻结的礼券、抵扣金
            order.unlock_bonus()
            # FIXME(Justin) 太暴力，需要改进,
            if status == 'pay_verify_code_wrong' and msg == u'错误次数太多，请明日再试':
                # 订单失败时会接收到信号来unlock bonus, 所以先lock bonus
                order.lock_bonus()
                order.update_status(ZhiwangOrder.Status.failure)
            else:
                raise PayTerminatedError(u'支付执行失败: %s' % msg)
    except (ConnectionError, HTTPError, ReadTimeout):
        # 支付接口超时或其他网络错误,mq追踪状态
        sentry.captureException()
        order.track_for_payment()
    else:
        # 支付成功
        order.update_status(ZhiwangOrder.Status.success)


def fetch_loans_digest(asset):
    zhiwang_account = ZhiwangAccount.get_by_local(asset.user_id)
    try:
        data = zhiwang.client.asset_invest_info(
            zhiwang_account.zhiwang_id, asset.asset_no)
    except RemoteError:
        sentry.captureException()
        raise FetchLoansDigestError()
    else:
        return ZhiwangLoansDigest.create_or_update(asset, data)
