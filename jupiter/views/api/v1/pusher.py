# coding: utf-8

from __future__ import absolute_import, unicode_literals

from flask import request, jsonify
from marshmallow import Schema, fields

from core.models.pusher import PushController, UserPushRecord
from ..decorators import require_oauth
from ..blueprint import create_blueprint

bp = create_blueprint('pusher', 'v1', __name__, url_prefix='/pusher')


@bp.route('/device/claim', methods=['POST'])
@require_oauth(['user_info'])
def claim_device():
    """设备声明.

    :request: :class:`.DeviceSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 201: 声明成功
    """
    device_schema = DeviceSchema(strict=True)
    result = device_schema.load(request.get_json(force=True))
    device_id = result.data['device_id']

    app_version = request.user_agent.app_info.version
    platform = request.user_agent.app_info.origin
    PushController.hook_up(request.oauth.user.id_, device_id, platform, app_version)
    return jsonify(success=True, data=None), 200


@bp.route('/device/sleep', methods=['POST'])
@require_oauth(['user_info'])
def sleep_device():
    """设备声明.

    :request: :class:`.DeviceSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 休眠成功
    """
    device_schema = DeviceSchema(strict=True)
    result = device_schema.load(request.get_json(force=True))
    device_id = result.data['device_id']

    controller = PushController(request.oauth.user.id_)
    controller.sleep_device(device_id)
    return jsonify(success=True, data=None), 200


@bp.route('/sensible_push/inform_received', methods=['POST'])
@require_oauth(['user_info'])
def inform_push_received():
    """告知单播推送已被接收.

    :request: :class:`.PushStatusInformingSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 标记推送接收成功
    """
    informing_schema = PushStatusInformingSchema(strict=True)
    voucher = informing_schema.load(request.get_json(force=True))
    message_id = voucher.data['jpush_msg_id']

    push_record = UserPushRecord.get_by_jmsg_id(message_id)
    if push_record:
        push_record.mark_as_received()
    return jsonify(success=True, data=None), 200


@bp.route('/sensible_push/inform_clicked', methods=['POST'])
@require_oauth(['user_info'])
def inform_push_clicked():
    """告知单播推送已被查阅.

    :request: :class:`.PushStatusInformingSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 标记推送查阅成功
    """
    informing_schema = PushStatusInformingSchema(strict=True)
    voucher = informing_schema.load(request.get_json(force=True))
    message_id = voucher.data['jpush_msg_id']

    push_record = UserPushRecord.get_by_jmsg_id(message_id)
    if push_record:
        push_record.mark_as_clicked()
    return jsonify(success=True, data=None), 200


class DeviceSchema(Schema):
    """设备声明."""

    #: :class:`str` 设备的极光注册ID
    device_id = fields.String(required=True)


class PushStatusInformingSchema(Schema):
    """推送状态通知."""

    #: :class:`str` 设备的极光注册ID
    device_id = fields.String(required=True)

    #: :class:`str` 极光的推送消息ID
    jpush_msg_id = fields.String(required=True)
