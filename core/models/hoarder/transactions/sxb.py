# coding: utf-8

from decimal import Decimal
from datetime import timedelta
from flask import current_app

from sxblib.errors import BusinessError
from sxblib.consts import OrderStatus, RedeemType, ProductType, UseGiftType

from core.models.profile.identity import Identity
from libs.logger.rsyslog import rsyslog
from core.models.utils import round_half_up
from core.models.hoard.xinmi.product import get_work_day, get_next_work_day
from ..vendor import Vendor, Provider
from ..account import Account as SxbAccount
from ..order import HoarderOrder
from ..product import Product, NewComerProduct
from ..asset import Asset
from ..errors import (SubscribeProductError, PayTerminatedError, RedeemError, OrderNotExistError,
                      OrderInProgressingError, OrderMissMatchUserError, MismatchUserError,
                      MissingIdentityError, MissingMobilePhoneError, FetchAssetError,
                      AssetEmptyError, AssetNotChangedError, UseGiftError)
from ..signal import hoarder_asset_redeemed
from ..gift import GiftUsageRecord
from jupiter.workers.hoarder import (hoarder_order_canceling, hoarder_asset_fetching,
                                     hoarder_redeem_tracking)
from jupiter.ext import sxb, sentry
from core.models.user.account import Account

ORDER_TIME_OUT_SECONDS = 180


def register_account(user_id):
    identity = Identity.get(user_id)
    local_account = Account.get(user_id)
    if not local_account.mobile:
        raise MissingMobilePhoneError
    if not identity:
        raise MissingIdentityError
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_account = SxbAccount.get_by_local(vendor.id_, user_id)

    if sxb_account:
        return sxb_account

    try:
        response = sxb.create_account(user_id=user_id, person_name=identity.person_name,
                                      id_card_no=identity.person_ricn,
                                      mobile=local_account.mobile)
    except BusinessError as e:
        raise MismatchUserError(u'%s，如有问题，请联系客服' % e)
    else:
        if not response.is_new:
            if not current_app.debug:
                rsyslog.send(
                    u'您的身份信息(%s,%s,%s,%s) 已经被注册过，如有问题，请联系客服' %
                    (user_id, identity.person_ricn, identity.person_name, local_account.mobile),
                    'sxb_dup_register')
        return SxbAccount.bind(vendor.id_, user_id, response.user_id)


def subscribe_product(user, product_id, bankcard, buy_amount, coupon=None,
                      pocket_deduction_amount=0):
    """申购产品"""
    #: TODO 检查礼券是否可用、返现账户抵扣是否可用、订单是否可建

    product = Product.get(product_id)
    if not product:
        raise SubscribeProductError(u'申购产品失败: 找不到指定的产品')

    assert product.ptype == Product.Type.unlimited
    vendor = Vendor.get_by_name(Provider.sxb)
    HoarderOrder.check_before_adding(vendor, user.id_, bankcard.id_, product.id_, buy_amount)
    identity = Identity.get(user.id_)
    order_code = sxb.gen_order_id()
    try:
        response = sxb.order_apply(
            order_id=order_code,
            product_id=product.remote_id, buy_amount=buy_amount,
            discount_fee=pocket_deduction_amount,
            user_id=user.id_, province=bankcard.province_id,
            city=bankcard.city_id, person_name=identity.person_name,
            person_ricn=identity.person_ricn,
            mobile=bankcard.mobile_phone, bank_code=bankcard.bank.xm_id,
            redeem_confirm=1, bank_account=bankcard.card_number,
            account_name=identity.person_name)
    except BusinessError as e:
        raise SubscribeProductError(u'申购产品失败: %s' % e)
    finally:
        hoarder_order_canceling.produce(order_code, delay=ORDER_TIME_OUT_SECONDS)

    assert buy_amount == round_half_up(response.buy_amount, 2)

    # 临时性起息日跳过周六日
    effect_day = product.effect_day
    # effect_day_unit = response.effect_day_unit 临时性只以日为单位计算起息日。
    if effect_day > 0:
        start_date = get_work_day(delta=effect_day)
    else:
        start_date = get_next_work_day()
    effect_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
    order = HoarderOrder.add(
        user_id=user.id_,
        product_id=product.id_,
        bankcard_id=bankcard.id_,
        amount=buy_amount,
        pay_amount=response.buy_amount,
        expect_interest=response.return_amount,
        order_code=response.order_id,
        pay_code=response.pay_code,
        direction=HoarderOrder.Direction.save,
        status=HoarderOrder.Status.unpaid,
        remote_status=response.order_status,
        start_time=effect_date,
        due_time=None
    )
    return order


def pay_order(order_id, user, sms_code, description=None):
    """支付订单"""
    #: TODO 支付过程需进行礼券，优惠的锁检查
    order = HoarderOrder.get(order_id)
    if not order:
        raise OrderNotExistError()
    if order.owner != user:
        raise OrderMissMatchUserError()
    if order.status is not HoarderOrder.Status.unpaid:
        raise OrderInProgressingError()
    try:
        # 调用第三方接口发起支付
        order_result = sxb.confirm_apply(
            product_id=order.product.remote_id,
            order_id=order.order_code,  # 订单流水号
            buy_amount=order.pay_amount,  # 实际支付金额
            discount_fee=0,
            user_id=order.user_id,
            pay_code=order.pay_code,  # 订单支付单号
            sms_code=sms_code,  # 手机验证码
            remark=description
        )
        if order_result and order:
            order.update_by_remote_status(order_result.order_status)
    except BusinessError as e:
        raise PayTerminatedError(u'支付执行失败: %s' % e)
    return order


def cancel_order(order_code):
    """取消订单"""
    try:
        # 调用第三方接口取消订单
        result = sxb.cancel_order(order_code)
        if result:
            if result.order_status is OrderStatus.user_cancel:
                order = HoarderOrder.get_by_order_code(order_code)
                if order:
                    order.update_by_remote_status(result.order_status)
                    return True
    except BusinessError:
        sentry.captureException()
    return False


def redeem(user, product, redeem_amount, bankcard, is_expired, is_express):
    """赎回"""
    try:
        # TODO: 在sxb sdk中验证和处理数据类型
        result = sxb.redeem(user.id_, product.remote_id, round(redeem_amount, 2),
                            is_expired, is_express, RedeemType.all_)
        redeem_order = HoarderOrder.add(
            user_id=user.id_, product_id=product.id_, bankcard_id=bankcard.id_,
            amount=result.pay_amount, order_code=result.redeem_id, expect_interest=0,
            direction=HoarderOrder.Direction.redeem, pay_amount=result.repay_amount,
            status=HoarderOrder.Status.applyed, remote_status=result.redeem_status,
            repay_amount=result.repay_amount, redeem_pay_amount=result.pay_amount,
            service_fee=result.service_fee, exp_sell_fee=result.exp_sell_fee,
            fixed_service_fee=result.fixed_service_fee)
        hoarder_asset_fetching.produce(redeem_order.id_)
        hoarder_redeem_tracking.produce(str(redeem_order.order_code))
        hoarder_asset_redeemed.send(redeem_order)
        return redeem_order
    except BusinessError as e:
        raise RedeemError(u'赎回失败: %s' % e)


def get_orders(user, offset, count=20):
    return HoarderOrder.gets_by_user_with_page(user.account_id, offset, count)


def fetch_asset(order):
    try:

        assets = sxb.query_assets(app_uid=order.user_id,
                                  product_type=ProductType.ririying,
                                  product_id=order.product.remote_id)
        if not assets:
            raise AssetEmptyError()

        for asset in assets:
            if order.product.kind is Product.Kind.child:
                father_product = (
                    NewComerProduct.get_father_product_by_vendor_id(order.product.vendor.id_))
                product_id = father_product.id_
            else:
                product_id = order.product.id_
            existences = Asset.gets_by_user_id_with_product_id(order.user_id, product_id)
            if not existences:
                existence = Asset.add(asset_no=None, order_code=None,
                                      bankcard_id=order.bankcard.id_,
                                      bank_account=order.bankcard.display_card_number,
                                      product_id=product_id,
                                      user_id=order.user_id, status=Asset.Status.earning,
                                      remote_status='00',
                                      fixed_service_fee=asset.fixed_service_fee,
                                      service_fee_rate=asset.service_fee_rate,
                                      annual_rate=asset.return_rate,
                                      create_amount=order.pay_amount,
                                      current_amount=asset.hold_amount,
                                      base_interest=asset.total_profit,
                                      expect_interest=asset.yesterday_profit,
                                      current_interest=asset.yesterday_profit,
                                      interest_start_date=order.start_time,
                                      interest_end_date=None,
                                      expect_payback_date=None,
                                      buy_time=order.creation_time)
            else:
                existence = existences[0]
            # 当申购或赎回成功时，资金应该发生变化，当未变化时，可能资产信息未生成，需要隔一段时间继续同步。
            if abs(Decimal(existence.uncollected_amount + existence.hold_amount) - Decimal(
                    asset.uncollected_amount + asset.hold_amount)) <= Decimal(0.000001):
                raise AssetNotChangedError()
            existence.yesterday_profit = asset.yesterday_profit
            existence.hold_profit = asset.total_profit
            existence.hold_amount = asset.hold_amount
            existence.uncollected_amount = asset.uncollected_amount
            existence.actual_annual_rate = asset.return_rate
            existence.residual_redemption_times = asset.free_redemption_sum
    except BusinessError as e:
        raise FetchAssetError(u'获取资产失败：%s' % e)


def async_asset(asset):
    try:
        assets = sxb.query_assets(app_uid=asset.user_id,
                                  product_type=ProductType.ririying,
                                  product_id=asset.product.remote_id)
        for a in assets:
            asset.yesterday_profit = a.yesterday_profit
            asset.hold_profit = a.total_profit
            asset.hold_amount = a.hold_amount
            asset.uncollected_amount = a.uncollected_amount
            asset.actual_annual_rate = a.return_rate
            asset.residual_redemption_times = a.free_redemption_sum
            asset.update_service_fee(a.fixed_service_fee, a.service_fee_rate)
    except BusinessError as e:
        raise FetchAssetError(u'同步资产失败：%s' % e)


def apply_gift(order, effective_date):
    new_comer_product = NewComerProduct.get(order.product.id_)
    gift_type = UseGiftType.const_rate.value
    end_date = effective_date + timedelta(days=7)

    if order.status is not HoarderOrder.Status.success:
        raise UseGiftError()
    try:
        sxb.use_gift(
            app_uid=order.user_id,
            product_id=new_comer_product.id_,
            order_id=order.order_code,
            gift_type=gift_type,
            effective_amount=float(order.amount),
            operation_num=float(new_comer_product.operation_num),
            effective_time=str(effective_date),
            end_time=str(end_date),
            remark=None)

    except BusinessError:
        gift_usage_record = GiftUsageRecord.get_by_product_and_order_id(
            new_comer_product.id_, order.id_)
        if not gift_usage_record:
            GiftUsageRecord.add(
                product_id=new_comer_product.id_,
                order_id=order.id_,
                gift_type=gift_type,
                effective_amount=order.amount,
                status=GiftUsageRecord.Status.dealing,
                effective_time=effective_date,
                end_time=end_date)
        raise UseGiftError()
    else:
        gift_usage_record = GiftUsageRecord.get_by_product_and_order_id(
            new_comer_product.id_, order.id_)
        if not gift_usage_record:
            GiftUsageRecord.add(
                product_id=new_comer_product.id_,
                order_id=order.id_,
                gift_type=gift_type,
                effective_amount=order.amount,
                status=GiftUsageRecord.Status.success,
                effective_time=effective_date,
                end_time=end_date)
        else:
            if gift_usage_record.status is GiftUsageRecord.Status.dealing:
                gift_usage_record.status = GiftUsageRecord.Status.success
