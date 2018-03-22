# coding: utf-8

from __future__ import absolute_import

from thriftpy.thrift import TException

from jupiter.ext import sentry
from jupiter.integration.jpush import jpush
from . import pool


@pool.async_worker('guihua_notification_unicast_push')
def notification_unicast_push(notification_id):
    """通知(Notification)的单播

    适用于用户行为触发性、面向用户、与用户个体有关的通知
    """
    from core.models.notification import Notification
    from core.models.pusher import DeviceBinding, UserPushRecord
    from core.models.pusher.element import SingleDeviceAudience

    notice = Notification.get(notification_id)

    if not notice.allow_push:
        return

    bindings = DeviceBinding.get_multi_by_user(notice.user_id)
    bindings = [b for b in bindings if b.platform in notice.push_platforms]
    for binding in bindings:
        # 如已推送，则跳过
        record = UserPushRecord.get_by_device_and_notification(
            binding.device_id, notice.id_)
        if record and record.is_pushed:
            continue

        pack = notice.make_push_pack(
            audience=SingleDeviceAudience(binding.device_id),
            platform=binding.platform
        )

        # 如未创建记录则新建推送
        if not record:
            record = UserPushRecord.create(notice.user, binding, notice)
        response = jpush.push(**pack.payload)
        record.mark_as_pushed(response.msg_id)


@pool.async_worker('guihua_notifications_multicast_push')
def notifications_multicast_push(multicast_info):
    """通知(Notification)面向用户群的组播

    """
    from core.models.pusher import PushController
    from core.models.pusher.element.audience import MultiUsersAudience
    from core.models.notification import NotificationKind

    notification_kind_id, user_ids = multicast_info.split(':')
    audience = MultiUsersAudience(user_ids.split(','))
    notification_kind = NotificationKind.get(notification_kind_id)

    # 鉴于群体推送业务的特殊性，与其worker因为服务出错重新启动向用户发送多次
    # 过时通知，不如在发生服务请求错误时忽略
    try:
        PushController.multicast(notification_kind, audience=audience)
    except TException:
        sentry.captureException(**locals())
