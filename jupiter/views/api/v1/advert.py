# coding: utf-8

from flask import request, jsonify
from marshmallow import Schema, fields

from core.models.advert.record import AdvertRecord
from core.models.advert import advert_list
from jupiter.utils.inhouse import check_is_inhouse
from ..blueprint import create_blueprint
from ..decorators import require_oauth


bp = create_blueprint('advert', 'v1', __name__, url_prefix='/advert')


@bp.route('/show', methods=['GET'])
@require_oauth(['user_info'])
def show_advert():
    """好规划弹窗广告

    使用本接口，客户端必须有权以 ``user_info`` 作为 scope.

    :response: :class:`.PopUpSchema`
    :status 200: 返回弹窗广告
    """
    pop_up_schema = PopUpSchema(strict=True)
    data = {
        'is_read': False,
        'advert': None
        }

    advert_available = (
        [advert for advert in advert_list if advert.is_effective] if check_is_inhouse() else [])
    if len(advert_available) == 1:
        for advert in advert_available:
            advert_record = AdvertRecord.get_by_user_and_kind(
                request.oauth.user.id_, advert.id_)
            if advert_record:
                data['is_read'] = True
            else:
                data['advert'] = advert
    return jsonify(success=True, data=pop_up_schema.dump(data).data)


@bp.route('/mark', methods=['POST'])
@require_oauth(['user_info'])
def mark_as_read():
    """好规划弹窗广告点击

    使用本接口，客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.MarkedAsReadSchema`
    :response: :class:`.AdvertSchema`
    :status 200: 返回标记为已读弹窗广告ID
    """
    mark_as_read_schema = MarkedAsReadSchema(strict=True)

    result = mark_as_read_schema.load(request.get_json(force=True))
    user_id = request.oauth.user.id_
    advert_id = result.data['advert_id']
    record = AdvertRecord.get_by_user_and_kind(user_id, result.data['advert_id'])
    if not record:
        AdvertRecord.add(user_id, advert_id)
    return jsonify(success=True, data=mark_as_read_schema.dump({'advert_id': advert_id}).data)


class AdvertSchema(Schema):
    """广告实体"""

    #: :class:`string` 点击后跳转链接
    advert_id = fields.String(attribute='id_')
    #: :class:`string` 点击后跳转链接
    target_link = fields.String(attribute='target_link')
    #: :class:`string` 展示图片链接
    pic_link = fields.String(attribute='pic_link')


class PopUpSchema(Schema):
    """弹窗广告 - 请求实体"""

    #: :class:`bool` 是否已读
    is_read = fields.Boolean(default=False)
    #: :class:`.AdvertSchema` 广告实体
    advert = fields.Nested(AdvertSchema, default=None)


class MarkedAsReadSchema(Schema):
    """点击广告 - 请求实体 """

    #: :class:`string` 广告ID
    advert_id = fields.String(required=True)
