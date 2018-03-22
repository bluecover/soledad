# coding: utf-8

from __future__ import absolute_import

import datetime

from jupiter.ext import yixin
from jupiter.integration.mq import WorkerTaskError
from libs.logger.rsyslog import rsyslog
from core.models.utils import round_half_up
from core.models.user.account import Account
from . import pool


@pool.async_worker('guihua_hoard_confirm_mq')
def hoard_yrd_confirming(order_id):
    """确认宜人贷订单状态"""
    from core.models.hoard import YixinAccount, HoardOrder
    from core.models.hoard.order import RemoteStatus

    order = HoardOrder.get(order_id)
    token = YixinAccount.get_by_local(order.user_id).p2p_token
    response = yixin.query.order_status(token, order.order_id, max_retry=3)
    status = RemoteStatus(response.data.status)

    if status == RemoteStatus.success:
        order.mark_as_confirmed()
    elif status == RemoteStatus.unknown:
        raise WorkerTaskError(hoard_yrd_confirming.tube)  # let it fail
    elif status == RemoteStatus.failure:
        order.mark_as_failure()
        raise WorkerTaskError(hoard_yrd_confirming.tube)  # let it fail
    else:
        raise WorkerTaskError(hoard_yrd_confirming.tube)  # let it fail


@pool.async_worker('guihua_hoard_check_exit_mq')
def hoard_yrd_exiting_checker(order_id):
    """确认宜人贷订单转出状态."""
    from core.models.hoard import HoardOrder, HoardProfile
    from core.models.hoard.profile import clear_account_info_cache

    order = HoardOrder.get(order_id)
    profile = HoardProfile.get(order.user_id)
    orders = profile.orders()

    if order.fetch_status(orders) == u'已转出':
        order.mark_as_exited()
    elif order.fetch_status(orders) == u'已结束':
        order.mark_as_exited()
    else:
        clear_account_info_cache(order.user_id)
        orders = profile.orders()

        if order.fetch_status(orders) == u'已转出':
            order.mark_as_exited()
        if order.fetch_status(orders) == u'已结束':
            order.mark_as_exited()


@pool.async_worker('guihua_hoard_payment_track_mq')
def hoard_yrd_payment_tracking(order_id):
    """同步用户宜人贷订单支付状态"""
    from core.models.hoard import HoardOrder, HoardProfile
    from core.models.hoard.profile import fetch_account_info, clear_account_info_cache

    order = HoardOrder.get(order_id)

    # take account info fetch as payment status sync trick
    profile = HoardProfile.add(order.user_id)
    clear_account_info_cache(order.user_id)
    fetch_account_info(profile)

    order = HoardOrder.get(order_id)
    rsyslog.send('%s\t%s' %
                 (order_id, order.status), tag='yixin_payment_track')

    if not order.is_success and not order.is_failure:
        raise WorkerTaskError(hoard_yrd_payment_tracking.tube)


@pool.async_worker('guihua_hoard_send_exit_sms_mq')
def hoard_yrd_sms_sender(order_id):
    """宜人贷转出订单发送到期短信"""
    from core.models.sms import ShortMessage
    from core.models.sms.kind import savings_order_exited_sms
    from core.models.hoard import HoardOrder, HoardProfile
    from core.models.hoard.profile import clear_account_info_cache

    order = HoardOrder.get(order_id)
    user = Account.get(order.user_id)
    profile = HoardProfile.get(order.user_id)
    if not user.has_mobile():
        return

    # 更新订单最新信息
    clear_account_info_cache(order.user_id)
    orders = profile.orders()
    profit = order.fetch_profit_until(datetime.date.today(), orders)

    # 发送短信
    sms = ShortMessage.create(
        user.mobile, savings_order_exited_sms,
        order_amount=int(order.order_amount),
        profit=str(round_half_up(profit, 2)))
    sms.send_async()


@pool.async_worker('guihua_hoard_withdraw_mq')
def hoard_yrd_withdrawing(order_id):
    """设置宜人贷提现银行卡."""
    from core.models.hoard import YixinAccount, HoardOrder

    order = HoardOrder.get(order_id)
    if order.fetch_status() != u'已转出':
        token = YixinAccount.get_by_local(order.user_id).p2p_token
        order.register_for_withdrawing(yixin.client, token)


@pool.async_worker('guihua_hoard_order_sync_mq')
def hoard_yrd_order_syncronizer(account_id):
    """宜人贷订单每日定时同步"""
    from core.models.hoard.profile import HoardProfile, fetch_account_info

    profile = HoardProfile.get(account_id)
    fetch_account_info(profile)
