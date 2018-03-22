# coding: utf-8

from __future__ import absolute_import, unicode_literals

from pkg_resources import parse_version

from flask import request, jsonify, abort
from marshmallow import Schema, fields

from core.models.profile.division import (
    get_division, get_provinces, get_children)
from core.models.bank import bank_collection, Partner
from ..blueprint import create_blueprint, conditional_for
from ..decorators import require_oauth


bp = create_blueprint('data', 'v1', __name__, url_prefix='/data')


@bp.route('/banks', methods=['GET'])
@require_oauth(['basic'])
def banks():
    """好规划支持的银行列表.

    :query partner: 可选参数, 按合作方支持情况限制返回结果. 目前可为:

                    - ``"zw"`` 指旺 (攒钱助手)
                    - ``"xm"`` 新米 (攒钱助手)
                    - ``"zs"`` 中山证券 (零钱包)

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.BankSchema` 列表
    """
    bank_schema = BankSchema(strict=True, many=True)
    partner = request.args.get('partner', type=Partner)
    banks = bank_collection.banks

    # 检查用户版本, 因为客服端bug没有传指旺partner, 此版本银行列表全部返回指旺可购买银行列表
    if request.user_agent.app_info.version == parse_version('1.3.0'):
        partner = Partner.zw

    if partner:
        banks = [b for b in banks if partner in b.available_in]
    conditional_for(b.id_ for b in banks)
    return jsonify(success=True, data=bank_schema.dump(banks).data)


@bp.route('/division/<int:year>/provinces', methods=['GET'])
@require_oauth(['basic'])
def provinces(year):
    """国家行政区划中的省份.

    :param year: 修订年份. 例如攒钱助手 (宜人贷) 需要使用 2012 年的数据.
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.DivisionSchema` 列表
    :status 404: 修订年份无效
    """
    provinces = get_provinces(year)
    if not provinces:
        abort(404, '城市信息有误')
    conditional_for('{revision}{code}'.format(**p) for p in provinces)
    return jsonify(success=True, data=provinces)


@bp.route('/division/<int:year>/<int:province_id>/prefectures')
@require_oauth(['basic'])
def prefectures(year, province_id):
    """国家行政区划中的地级市.

    :param year: 修订年份.
    :param province_id: 上级省份的区划 ID.
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.DivisionSchema` 列表
    :status 404: 修订年份或上级行政区划无效
    """
    province = get_division(province_id, year)
    if not province or not province.is_province:
        abort(404, '城市信息有误')
    prefectures = get_children(province)
    conditional_for('{revision}{code}'.format(**p) for p in prefectures)
    return jsonify(success=True, data=prefectures)


@bp.route('/division/<int:year>/<int:prefecture_id>/counties')
@require_oauth(['basic'])
def counties(year, prefecture_id):
    """国家行政区划中的县级市.

    :param year: 修订年份.
    :param province_id: 上级地级市的区划 ID.
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.DivisionSchema` 列表
    :status 404: 修订年份或上级行政区划无效
    """
    prefecture = get_division(prefecture_id, year)
    if not prefecture or not prefecture.is_prefecture:
        abort(404, '城市信息有误')
    counties = get_children(prefecture)
    conditional_for('{revision}{code}'.format(**c) for c in counties)
    return jsonify(success=True, data=counties)


class BankIconSchema(Schema):
    """银行图标实体."""

    #: :class:`str` 中分辨率图标 URL
    mdpi = fields.URL(required=True)
    #: :class:`str` 高分辨率图标 URL
    hdpi = fields.URL(required=True)


class BankSchema(Schema):
    """银行实体."""

    #: :class:`str` 银行唯一 ID
    uid = fields.String(attribute='id_', required=True)
    #: :class:`str` 银行中文名
    name = fields.String(required=True)
    #: :class:`str` 官方电话
    telephone = fields.String(required=True)
    #: :class:`.BankIconSchema` 银行图标 URL
    icon_url = fields.Nested(BankIconSchema, required=True)


class DivisionSchema(Schema):
    """行政区划实体."""

    #: :class:`int` 行政区划编号
    code = fields.Integer()
    #: :class:`int` 区划名
    name = fields.String()
    #: :class:`int` 修订年
    revision = fields.String()
