# coding: utf-8

from __future__ import absolute_import, unicode_literals

import decimal
from operator import attrgetter

from marshmallow import Schema, fields
from flask import g, jsonify, abort, request

from core.models.hoard.zhiwang import ZhiwangProduct, ZhiwangWrappedProduct
from core.models.hoard.xinmi import XMFixedDuedayProduct
from core.models.welfare import CouponManager, FirewoodWorkflow, FirewoodPiling, FirewoodBurning
from ..blueprint import create_blueprint
from ..decorators import require_oauth
from ..fields import LocalDateTimeField


bp = create_blueprint('welfare', 'v1', __name__, url_prefix='/welfare')


SPEC_DESCRIPTION = '''
1.攒钱时，可按5‰比例抵扣，最小抵扣单位1元
2.攒钱红包无有效期限制
3.攒钱红包可用于“自由期限”及“固定期限产品”
4.好规划网保留最终解释权'''.strip()


@bp.before_request
@require_oauth(['user_info'])
def initiaize():
    if hasattr(request, 'oauth'):
        g.coupon_manager = CouponManager(request.oauth.user.id_)
        g.firewood_flow = FirewoodWorkflow(request.oauth.user.id_)
        # TODO: 此处应根据用户所处平台进行礼券过滤
        g.available_coupons = g.coupon_manager.available_coupons


@bp.route('/red-packets/record', methods=['GET'])
@require_oauth(['user_info'])
def redpackets_record():
    """红包使用记录.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.RedPacketListSchema`
    :query offset: 可选参数, 开始条数，按请求数限制返回结果.
    :query count: 可选参数, 每页数量，按请求数限制返回结果.
    """
    record_schema = RedPacketListSchema(strict=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    pileds = FirewoodPiling.get_multi_by_user(request.oauth.user.id_)
    burneds = FirewoodBurning.get_multi_by_user(request.oauth.user.id_)
    records = sorted(
        pileds + burneds, key=attrgetter('creation_time'), reverse=True)[offset:offset + count]
    data = {'records': records}
    return jsonify(success=True, data=record_schema.dump(data).data)


@bp.route('/mine/red-packets', methods=['GET'])
@require_oauth(['user_info'])
def red_packets():
    """我的红包

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.RedPacketsSchema`
    """
    data = {'balance': g.firewood_flow.balance,
            'spec_description': SPEC_DESCRIPTION}
    return jsonify(success=True, data=data)


@bp.route('/mine/coupons', methods=['GET'])
@require_oauth(['user_info'])
def coupons():
    """我的礼券

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.CouponCollectionSchema`
    :query offset: 可选参数, 开始条数，按请求数限制返回结果.
    :query count: 可选参数, 每页数量，按请求数限制返回结果.
    """
    coupon_schema = CouponCollectionSchema(strict=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    coupons = (g.available_coupons + g.coupon_manager.history_coupons)[offset:offset + count]
    data = {
        'total_available_coupons': len(g.available_coupons),
        'coupons': coupons}
    return jsonify(success=True, data=coupon_schema.dump(data).data)


@bp.route('/savings/coupon/<int:product_id>', methods=['GET'])
@bp.route('/savings/coupon/<int:product_id>/<int:wrapped_product_id>', methods=['GET'])
@require_oauth(['user_info'])
def get_available_coupons_and_redpackets(product_id, wrapped_product_id=None):
    """产品可用礼券和红包

    :param product: 产品ID.
    :param wrapped_product_id: 包装后产品ID.
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.CouponCollectionSchema`
    :status 200: 返回  :class:`.RedPacketsSchema`
    """
    coupon_schema = CouponCollectionSchema(strict=True)
    redpacket_schema = RedPacketsSchema(strict=True)

    xm_product = XMFixedDuedayProduct.get(product_id)
    if xm_product:
        welfare_data = dict()
        coupons = [c for c in g.available_coupons
                   if c.is_available_for_product(xm_product)]
        welfare_data.update(coupon_schema.dump({'coupons': coupons}).data)
        welfare_data.update(redpacket_schema.dump({
            'balance': g.firewood_flow.balance,
            'start_amount': decimal.Decimal(200),
            'deduct_amount': decimal.Decimal(1),
            'is_accepting_bonus': xm_product.is_accepting_bonus,
            'unavailable_text': '该产品暂无可用红包',
            'firewood_rate': decimal.Decimal(0)}).data)
        return jsonify(success=True, data=welfare_data)

    product = ZhiwangProduct.get(product_id)
    wrapped_product = ZhiwangWrappedProduct.get(wrapped_product_id)
    welfare_data = dict()
    if wrapped_product_id is not None and not wrapped_product:
        abort(404)

    coupons = [c for c in g.available_coupons
               if c.is_available_for_product(wrapped_product or product)]
    welfare_data.update(coupon_schema.dump({'coupons': coupons}).data)
    welfare_data.update(redpacket_schema.dump({
        'balance': g.firewood_flow.balance,
        'start_amount': decimal.Decimal(200),
        'deduct_amount': decimal.Decimal(1),
        'is_accepting_bonus': (wrapped_product or product).is_accepting_bonus,
        'unavailable_text': '该产品暂无可用红包',
        'firewood_rate': decimal.Decimal(0)}).data)
    return jsonify(success=True, data=welfare_data)


class CouponBenefitSchema(Schema):
    """礼券收益利率或抵扣金额"""

    #: :class:`decimal` 礼券额外增加收益率
    extra_rate = fields.Decimal(places=2)
    #: :class:`decimal` 礼券抵扣金额(元)
    deduct_amount = fields.Decimal(places=2)


class CouponSpecSchema(Schema):
    """礼券使用限制"""

    #: :class:`decimal` 礼券最低使用金额限制(元)
    fulfill_amount = fields.Decimal(places=2)


class RedPacketsRecordSchema(Schema):
    """用户红包使用记录"""

    #: :class:`decimal` 变动金额(元)
    amount = fields.Decimal(places=2)
    #: :class:`str` 红包使用金额
    simplified_display_amount = fields.String()
    #: :class:`~datetime.datetime` 使用时间
    creation_time = LocalDateTimeField()
    #: :class:`str` 备注
    display_remark = fields.String()


class RedPacketListSchema(Schema):
    """用户红包使用列表实体"""

    #: :class:`.RedPacketsRecordSchema`
    records = fields.Nested(RedPacketsRecordSchema, many=True)


class RedPacketsSchema(Schema):
    """用户红包实体"""

    #: :class:`decimal` 红包余额
    balance = fields.Decimal(places=2)
    #: :class:`str` 红包使用规则
    spec_description = fields.String()
    #: :class:`decimal` 红包起始限额(满xx)
    start_amount = fields.Decimal(places=2)
    #: :class:`decimal` 红包抵扣额度(减x)
    deduct_amount = fields.Decimal(places=2)
    #: :class:`str` 红包不可用时文案
    unavailable_text = fields.String()
    #: :class:`bool` 是否可用礼券
    is_accepting_bonus = fields.Boolean()
    #: :class:`~decimal.Decimal` 动态红包利率
    #:
    #: .. note:: 若值不为0，则可以根据利率计算(规则请ping PM)出应返红包金额
    firewood_rate = fields.Decimal(places=3)


class CouponRegulationSchema(Schema):
    """产品可用礼券实体"""

    #: :class:`.CouponBenefitSchema` 礼券收益
    benefit = fields.Nested(CouponBenefitSchema, attribute='benefit_dict')
    #: :class:`.CouponSpecSchema` 礼券使用最低限制
    usage_requirement_dict = fields.Nested(CouponSpecSchema)


class CouponKindSchema(Schema):
    """礼券类型实体."""

    #: :class:`str` 礼券类型名称(加息率: ``RS``, 抵扣金额: ``QD``)
    name = fields.String()
    #: :class:`str` 礼券收益类型
    display_text = fields.String()
    #: :class:`.CouponRegulationSchema` 礼券信息
    regulation = fields.Nested(CouponRegulationSchema)


class CouponSchema(Schema):
    """礼券实体"""

    #: :class:`int` 礼券ID
    coupon_id = fields.Integer(attribute='id_', required=True)
    #: :class:`str` 礼券名字
    name = fields.String()
    #: :class:`str` 礼券使用状态(未使用: ``"W"``;已接受使用（如已发起支付,被锁定: ``"S"``;已被使用: ``"M"``))
    status = fields.Function(lambda o: o.status.value)
    #: :class:`bool` 礼券是否过期
    outdated = fields.Boolean()
    #: :class:`.CouponKindSchema` 礼券信息
    kind = fields.Nested(CouponKindSchema)
    #: :class:`str` 礼券限制
    display_product_requirement = fields.String()
    #: :class:`str` 礼券适用平台(WEB: ``1``, IOS: ``2``, ANDROID: ``3``)
    platforms = fields.Function(lambda o: [p.value for p in o.platforms])
    #: :class:`~datetime.datetime` 礼券开始时间
    creation_time = LocalDateTimeField()
    #: :class:`~datetime.datetime` 礼券到期时间
    expire_time = LocalDateTimeField()


class CouponCollectionSchema(Schema):
    """礼券管理"""

    #: :class:`int` 可用礼券(张)
    total_available_coupons = fields.Integer()
    #: :class:`.CouponSchema` 礼券信息
    coupons = fields.Nested(CouponSchema, many=True)
