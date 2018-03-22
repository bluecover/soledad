# coding: utf-8

from __future__ import absolute_import, unicode_literals

from flask import abort, jsonify
from marshmallow import Schema, fields

from core.models.welfare.package.kind import newcomer_package
from ..blueprint import create_blueprint
from ..decorators import require_oauth
from ..fields import LocalDateTimeField
from ..consts import VERSION_TOO_LOW


bp = create_blueprint('coupons', 'v1', __name__, url_prefix='/coupons')


@bp.before_request
@require_oauth(['user_info'])
def initialize_coupon_manager():
    pass


@bp.route('/mine', methods=['GET'])
def coupons():
    """[已下线] 用户已有礼券列表."""
    abort(410, VERSION_TOO_LOW)


@bp.route('/optimum', methods=['GET'])
def optimum_coupon():
    """[已下线] 选择最佳礼券."""
    abort(410, VERSION_TOO_LOW)


@bp.route('/new', methods=['GET'])
def new_coupon():
    """新手礼券.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回 :class:`.NewCouponSchema`
    """
    new_coupon = NewCouponSchema(strict=True)
    data = {'amount': newcomer_package.sum_deduct}
    return jsonify(success=True, data=new_coupon.dump(data).data)


class NewCouponSchema(Schema):
    """新手礼券类型实体."""

    #: :class:`~decimal.Decimal` 新手礼券金额
    amount = fields.Decimal(places=2)


class CouponKindSchema(Schema):
    """礼券类型实体."""

    #: :class:`str` 礼券类型唯一 ID
    uid = fields.String(attribute='id_', required=True)
    #: :class:`str` 福利描述
    benefit_desc = fields.String(required=True)
    #: :class:`str` 福利描述, 形如 ``收益加<percentage>0.6%</percentage>``
    #: 的 XML 富文本格式. 目前为止可能的内嵌 Tag 有:
    #:
    #: - ``percentage``
    #:
    #: 为保证正确性, 使用者应该使用标准 XML 解析器解析, 而非自行构造正则表达式.
    #: 如需保证向后兼容 (以后增加更多的 Tag), 需要忽略未知的 Tag 名.
    benefit_rich_desc = fields.String(required=True)
    #: :class:`str` 获取条件描述
    obtention_desc = fields.String(required=True)
    #: :class:`int` 有效期 (天)
    expire_days = fields.Integer(required=True)


class CouponSchema(Schema):
    """礼券实体."""

    #: :class:`str` 礼券唯一 ID
    uid = fields.String(attribute='id_', required=True)
    #: :class:`str` 对应的礼包唯一 ID
    package_id = fields.String(required=True)
    #: :class:`str` 使用礼券的用户唯一 ID
    consumer_id = fields.String(required=True)
    #: :class:`CouponKindSchema` 礼券类型
    kind = fields.Nested(CouponKindSchema)
    #: :class:`str` 礼券状态
    status = fields.Function(lambda x: x.status.name, required=True)
    #: :class:`datetime.datetime` 创建时间
    created_at = LocalDateTimeField(attribute='creation_time', required=True)
    #: :class:`datetime.datetime` 过期时间
    expired_at = LocalDateTimeField(attribute='expire_time', required=True)
    #: :class:`datetime.datetime` 启用时间
    consumed_at = LocalDateTimeField(attribute='consumed_time', required=True)
