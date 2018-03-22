# coding: utf-8

from __future__ import absolute_import
import datetime

from babel.dates import format_timedelta
from babel.numbers import format_number

from jupiter.integration.bearychat import BearyChat
from jupiter.integration.mq import WorkerTaskError
from core.models.utils import round_half_up
from . import pool

bearychat = BearyChat('savings_xm')


@pool.async_worker('guihua_xm_cancel_order_mq')
def xm_cancel_order_prepare(order_code):
    from core.models.hoard.xinmi import XMOrder
    from core.models.hoard.xinmi.transaction import cancel_order
    expected_status_set = frozenset([
        XMOrder.Status.success,
        XMOrder.Status.failure,
    ])

    order = XMOrder.get_by_order_code(order_code)
    if order and order.status in expected_status_set:
        return
    cancel_order(order_code)


@pool.async_worker('guihua_xm_payment_track_mq')
def xm_payment_tracking(order_id):
    """同步新投米用户订单支付状态"""
    from core.models.hoard.xinmi import XMOrder, XMProfile

    expected_status_set = frozenset([
        XMOrder.Status.success,
        XMOrder.Status.failure,
    ])

    order = XMOrder.get(order_id)
    user_id = order.user_id
    xm_profile = XMProfile.get(user_id)
    xm_profile.assets(pull_remote=True)
    origin_status = order.status
    if origin_status in expected_status_set:
        return

    # 当订单属于自然失败时不再更新状态
    if origin_status not in [XMOrder.Status.paying, XMOrder.Status.shelved]:
        return

    # 长时间未被结算中心处理的订单将发往BC提醒
    since_delta = datetime.datetime.now() - order.creation_time
    if since_delta > datetime.timedelta(hours=6):
        from core.models.hoard.xinmi.transaction import cancel_order
        cancel_order(order.order_code)
        order = XMOrder.get_by_order_code(order.order_code)
        if order.status in [XMOrder.Status.failure, XMOrder.Status.success]:
            if not bearychat.configured:
                return
            result = u'`成功`:clap: '
            color = '#00FF00'
        else:
            result = u'`失败`:eyes: '
            color = '#FF0000'
        if bearychat.configured:
            quota = format_number(order.amount, locale='en_US')
            message = u'已执行 **自动取消订单释放债权￥{}** {}，当前状态 `{}`'.format(
                quota, result, order.status.label)
            txt = u'**用户：** ( {} ) 已经 **{}** 了, **新米订单** *{}* (*{}*) 状态仍为 **{}**.'.format(
                order.user_id,
                format_timedelta(since_delta, locale='zh_CN'), order.id_,
                order.order_code, origin_status.label, )
            attachment = bearychat.attachment(title=None, text=message, color=color, images=[])
            bearychat.say(txt, attachments=[attachment])

    error_msg = (
        u'tube:{0}, order_id:{1}, order code:{2}, '
        u'new status:{3},user_id:{4}')

    raise WorkerTaskError(error_msg.format(xm_payment_tracking.tube, order.id_,
                                           order.order_code, origin_status.name, order.user_id))


@pool.async_worker('guihua_xm_send_exit_sms_mq')
def xm_send_exit_sms(asset_id):
    """新米转出订单发送到期短信"""
    from core.models.sms import ShortMessage
    from core.models.sms.kind import savings_order_exited_sms
    from core.models.hoard.xinmi import XMAsset

    asset = XMAsset.get(asset_id)
    sms = ShortMessage.create(
        asset.user.mobile, savings_order_exited_sms, asset.user.id_,
        order_amount=str(round_half_up(asset.create_amount, 2)),
        profit=str(round_half_up(asset.current_interest, 2)))
    sms.send_async()
