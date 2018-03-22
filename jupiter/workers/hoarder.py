# coding: utf-8

import datetime

from babel.dates import format_timedelta
from babel.numbers import format_number

from jupiter.integration.bearychat import BearyChat
from jupiter.integration.mq import WorkerTaskError
from . import pool

bearychat = BearyChat('savings_xm')


@pool.async_worker('guihua_hoarder_payment_track_mq')
def hoarder_payment_tracking(order_id):
    from core.models.hoarder.order import HoarderOrder
    from jupiter.ext import sxb

    expected_status_set = frozenset([
        HoarderOrder.Status.success,
        HoarderOrder.Status.failure,
        HoarderOrder.Status.backed
    ])

    order = HoarderOrder.get(order_id)
    origin_status = order.status

    # 当订单属于自然失败时不再更新状态
    if origin_status in expected_status_set:
        return

    result = sxb.query_order(order.order_code)

    order.update_by_remote_status(result.order_status)
    if origin_status not in [HoarderOrder.Status.committed, HoarderOrder.Status.paying,
                             HoarderOrder.Status.shelved]:
        return

    # 长时间未被结算中心处理的订单将发往BC提醒
    since_delta = datetime.datetime.now() - order.creation_time
    if since_delta > datetime.timedelta(hours=6):
        from core.models.hoarder.transactions import sxb
        if sxb.cancel_order(order.order_code):
            order = HoarderOrder.get_by_order_code(order.order_code)
            if order.status in [HoarderOrder.Status.failure, HoarderOrder.Status.success]:
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
                    quota, result, order.status.display_text)
                txt = u'**用户：** ( {} ) 已经 **{}** 了, **随心攒订单** *{}* (*{}*) 状态仍为 **{}**.'.format(
                    order.user_id,
                    format_timedelta(since_delta, locale='zh_CN'), order.id_,
                    order.order_code, origin_status.display_text, )
                attachment = bearychat.attachment(title=None, text=message, color=color, images=[])
                bearychat.say(txt, attachments=[attachment])

    error_msg = (
        u'tube:{0}, order_id:{1}, order code:{2}, '
        u'new status:{3},user_id:{4}')

    raise WorkerTaskError(error_msg.format(hoarder_payment_tracking.tube, order.id_,
                                           order.order_code, origin_status.name, order.user_id))


@pool.async_worker('guihua_hoarder_asset_fetch_mq')
def hoarder_asset_fetching(order_id):
    from core.models.hoarder.transactions import sxb
    from core.models.hoarder.order import HoarderOrder
    from core.models.hoarder.errors import FetchAssetError, AssetNotChangedError
    order = HoarderOrder.get(order_id)
    try:
        sxb.fetch_asset(order)
    except FetchAssetError as e:
        if isinstance(e, AssetNotChangedError):
            since_delta = datetime.datetime.now() - order.creation_time
            if since_delta > datetime.timedelta(hours=6):
                if bearychat.configured:
                    # 长时间资产未发生变化将发往BC提醒，并从队列中跳出
                    quota = format_number(order.amount, locale='en_US')
                    result = u'`成功`:clap: '
                    color = '#00FF00'
                    message = u'已执行 **自动取消同步资产信息 ￥{}** {}，当前状态 `{}`'.format(
                        quota, result, order.status.display_text)
                    txt = u'**用户：** ( {} ) 已经 **{}** 了, **随心攒订单** *{}* (*{}*) 资产已同步.'.format(
                        order.user_id,
                        format_timedelta(since_delta, locale='zh_CN'), order.id_,
                        order.order_code, )
                    attachment = bearychat.attachment(title=None, text=message, color=color,
                                                      images=[])
                    bearychat.say(txt, attachments=[attachment])
                return
        raise WorkerTaskError(unicode(e))


@pool.async_worker('guihua_hoarder_async_asset_mq')
def hoarder_async_asset(asset_id):
    from core.models.hoarder.transactions import sxb
    from core.models.hoarder.asset import Asset
    from core.models.hoarder.errors import FetchAssetError
    asset = Asset.get(asset_id)
    try:
        sxb.async_asset(asset)
    except FetchAssetError as e:
        raise WorkerTaskError(unicode(e))


@pool.async_worker('guihua_hoarder_cancel_order_mq')
def hoarder_order_canceling(order_code):
    from core.models.hoarder.order import HoarderOrder
    from core.models.hoarder.transactions.sxb import cancel_order
    expected_status_set = frozenset([
        HoarderOrder.Status.success,
        HoarderOrder.Status.failure,
    ])

    order = HoarderOrder.get_by_order_code(order_code)
    if order and order.status in expected_status_set:
        return
    cancel_order(order_code)


@pool.async_worker('guihua_hoarder_redeem_track_mq')
def hoarder_redeem_tracking(order_code):
    from core.models.hoarder.order import HoarderOrder
    from jupiter.ext import sxb

    expected_status_set = frozenset([
        HoarderOrder.Status.failure,
        HoarderOrder.Status.backed
    ])

    order = HoarderOrder.get_by_order_code(order_code)
    if not order:
        return
    if order.status in expected_status_set:
        return

    redeem_results = sxb.query_redeems(order.user_id, order.product.remote_id, order.id_)
    for result in redeem_results:
        if result.app_redeem_id:
            if order_code in result.app_redeem_id:
                order.update_by_remote_status(result.redeem_status)
                return

    raise WorkerTaskError()


@pool.async_worker('guihua_hoarder_new_comer_use_gift_track_mq')
def hoarder_order_use_gift_tracking(order_id):
    from core.models.hoarder.transactions.sxb import apply_gift
    from core.models.hoarder.order import HoarderOrder
    from core.models.hoarder.errors import UseGiftError

    order = HoarderOrder.get(order_id)
    if not order:
        return

    current_date = datetime.datetime.now().date
    effective_date = order.value_date if current_date < order.value_date else current_date

    try:
        apply_gift(order, effective_date)
    except UseGiftError:
        raise WorkerTaskError()
