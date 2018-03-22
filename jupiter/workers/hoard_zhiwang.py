# coding: utf-8

from __future__ import absolute_import

import datetime
import operator

from babel.dates import format_timedelta

from jupiter.ext import zhiwang
from jupiter.integration.mq import WorkerTaskError
from jupiter.integration.bearychat import BearyChat
from core.models.utils import round_half_up
from . import pool


bearychat = BearyChat('savings')


@pool.async_worker('guihua_zhiwang_asset_fetch_mq')
def zhiwang_asset_fetching(order_id):
    """为指旺资产找到匹配订单"""
    from core.models.hoard.zhiwang import ZhiwangOrder, ZhiwangAccount, ZhiwangAsset

    order = ZhiwangOrder.get(order_id)
    asset = ZhiwangAsset.get_by_order_code(order.order_code)
    if asset:
        return

    user_id = order.user_id
    zw_ucode = ZhiwangAccount.get_by_local(user_id).zhiwang_id
    all_assets = sorted(
        zhiwang.asset_list(zw_ucode), key=operator.attrgetter('created_at'),
        reverse=True)
    for asset_info in all_assets:
        detail = zhiwang.asset_details(zw_ucode, asset_info.asset_code)
        if detail.order_code == order.order_code:
            # find the matcher
            ZhiwangAsset.add(
                asset_info.asset_code,
                detail.order_code,
                order.bankcard_id,
                detail.user_bank_account,
                detail.product_id,
                user_id,
                ZhiwangAsset.MUTUAL_STATUS_MAP.get(detail.status),
                detail.annual_rate,
                detail.actual_annual_rate,
                detail.create_amount,
                detail.current_amount,
                detail.base_interest,
                detail.actual_interest,  # actual = expect
                detail.current_interest,
                detail.interest_start_date,
                detail.interest_end_date,
                detail.expected_payback_date,
                detail.created_at.naive)
            return

    raise WorkerTaskError(zhiwang_asset_fetching.tube)


@pool.async_worker('guihua_zhiwang_payment_track_mq')
def zhiwang_payment_tracking(order_id):
    """同步指旺用户订单支付状态"""
    from core.models.hoard.zhiwang import ZhiwangOrder, ZhiwangAccount

    expected_status_set = frozenset([
        ZhiwangOrder.Status.success,
        ZhiwangOrder.Status.failure,
    ])

    order = ZhiwangOrder.get(order_id)
    origin_status = order.status
    if origin_status in expected_status_set:
        return

    zw_ucode = ZhiwangAccount.get_by_local(order.user_id).zhiwang_id
    response = zhiwang.order_status(zw_ucode, order.order_code)
    assert response.order_code == order.order_code
    assert int(response.pay_amount) == int(order.amount)
    new_status = ZhiwangOrder.MUTUAL_STATUS_MAP.get(response.order_status)

    if new_status is not origin_status:
        # 当订单属于自然失败时不再更新状态
        if new_status is ZhiwangOrder.Status.failure and origin_status in (
                ZhiwangOrder.Status.unpaid, ZhiwangOrder.Status.committed):
            return

        # 只有当订单状态发生变化时才更新状态
        order.update_status(new_status)
        if new_status in expected_status_set:
            return

    if bearychat.configured:
        # 长时间未被结算中心处理的订单将发往BC提醒
        since_delta = datetime.datetime.now() - order.creation_time
        if since_delta > datetime.timedelta(hours=6):
            message = (
                u'已经**{}**了, 指旺订单 {}({}) 状态仍为 {}. '
                u'[[查看详情]](http://earth.guihua.com/hoard/user/{})')
            bearychat.say(message.format(
                format_timedelta(since_delta, locale='zh_CN'), order.id_,
                order.order_code, new_status.name, order.user_id))

    error_msg = (
        u'tube:{0}, order_id:{1}, order code:{2}, '
        u'new status:{3},user_id:{4}')
    raise WorkerTaskError(error_msg.format(zhiwang_payment_tracking.tube, order.id_,
                          order.order_code, new_status.name, order.user_id))


@pool.async_worker('guihua_zhiwang_send_exit_sms_mq')
def zhiwang_send_exit_sms(asset_id):
    """指旺转出订单发送到期短信"""
    from core.models.sms import ShortMessage
    from core.models.sms.kind import savings_order_exited_sms, savings_first_asset_exited_sms
    from core.models.hoard.zhiwang import ZhiwangAsset

    asset = ZhiwangAsset.get(asset_id)
    first_asset = ZhiwangAsset.get_first_redeemed_asset_by_user_id(asset.user_id)

    sms_kind = (savings_first_asset_exited_sms if first_asset and
                first_asset.id_ == asset.id_ else savings_order_exited_sms)

    sms = ShortMessage.create(
        asset.user.mobile, sms_kind,
        order_amount=str(round_half_up(asset.create_amount, 2)),
        profit=str(round_half_up(asset.current_interest, 2)))

    sms.send_async()
