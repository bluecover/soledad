# coding:utf-8

from __future__ import absolute_import, unicode_literals

from flask import request, jsonify, abort
from marshmallow import Schema, fields

from core.models.redeemcode.redeemcode import RedeemCode
from core.models.redeemcode.errors import RedeemCodeException

from ..blueprint import create_blueprint
from ..decorators import require_oauth
from ..fields import RedeemCodeField


bp = create_blueprint('redeemcode', 'v1', __name__, url_prefix='/redeemcode')


@bp.route('/code', methods=['POST'])
@require_oauth(['user_info'])
def redeem():
    """使用兑换码兑换礼包

    使用本接口，客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.RedeemCodeVerifySchema`
    :response: :class:`.WelfareInfoSchema`

    :status 200: 兑换成功
    :status 403: 兑换失败
    """
    redeem_code_schema = RedeemCodeVerifySchema(strict=True)
    welfare_info_schema = WelfareInfoSchema(strict=True)
    result = redeem_code_schema.load(request.get_json(force=True))
    redeem_code = RedeemCode.get_by_code(result.data['redeem_code'].upper())
    if redeem_code:
        try:
            redeem_code.redeem(request.oauth.user)
            welfare_info = welfare_info_schema.dump(
                redeem_code.activity.reward_welfare_package_kind.welfare_summary)
            return jsonify(success=True, data=welfare_info.data)
        except RedeemCodeException as e:
            abort(403, unicode(e))
    abort(404, u'您输入的兑换码不存在')


class RedeemCodeVerifySchema(Schema):
    """兑换码请求实体."""

    #: :class:`str` 兑换码
    redeem_code = RedeemCodeField(required=True)


class FirewoodInfoSchema(Schema):
    """攒钱红包实体"""

    #: :class:`str` 红包简介
    introduction = fields.String(required=True)
    #: :class:`~decimal.Decimal` 红包金额
    worth = fields.Decimal(required=True)


class CouponInfoSchema(Schema):
    """攒钱礼券实体"""

    #: :class:`str` 礼券名称
    name = fields.String(required=True)
    #: :class:`int` 礼券数量
    amount = fields.Integer(required=True)


class WelfareInfoSchema(Schema):
    """兑换码所兑换的礼包实体."""

    #: :class:`.FirewoodInfoSchema`
    firewood_info = fields.Nested(FirewoodInfoSchema, many=True)
    #: :class:`.CouponInfoSchema`
    coupon_info = fields.Nested(CouponInfoSchema, many=True)
