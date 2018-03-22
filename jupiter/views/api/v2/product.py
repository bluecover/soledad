# coding: utf-8

from __future__ import absolute_import, unicode_literals

from flask import jsonify, url_for, request, g, json

from jupiter.views.api.decorators import anonymous_oauth
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoarder.product import Product
from core.models.hoard.xinmi.product import XMFixedDuedayProduct
from core.models.welfare import CouponManager
from .strategy import get_recommend_products
from core.models.wallet.providers import zhongshan
from core.models.wallet import PublicDashboard
from ..blueprint import create_blueprint_v2, conditional_for_v2
from .consts import COMMON_PRODUCT_PROFILE, PRODUCT_STATUS, PERIODS
from .schema.product import ProductResponseSchema

bp = create_blueprint_v2('products', 'v2', __name__, url_prefix='/products')


@bp.before_request
@anonymous_oauth(['basic'])
def initialize_user():
    if hasattr(request, 'oauth'):
        g.user = request.oauth.user
    else:
        g.user = None


def get_products(user=None):
    enabled_vendors = Vendor.get_enabled_vendors()
    matched_coupons = []
    coupon_manager = None
    product_obj = {'wallet': [], 'hoarder': [],
                   'help_url': url_for('activity.cake.index', _external=True)}
    if user:
        coupon_manager = CouponManager(user.id_)
    for vendor in enabled_vendors:
        products = [p for p in Product.get_products_by_vendor_id(vendor.id_)]
        for product in products:
            profile = COMMON_PRODUCT_PROFILE.get(vendor.provider)
            product.uid = product.id_
            product.title = profile.get('title')
            product.activity_title = profile.get('activity_title')
            product.activity_introduction = profile.get('activity_introduction')
            product.annual_rate = product.rate * 100
            product.tags = profile.get('tags')
            product.start_date = product.value_date
            rule_url = profile.get('withdraw_rule_url')
            product.withdraw_rule = url_for(rule_url, _external=True) if rule_url else ''
            if product.ptype is Product.Type.unlimited:
                product.annotations = {'has_coupons': False}
                product.period = profile.get('period')
            else:
                product.period = PERIODS.get(str(product.frozen_days))
                if product.vendor.name == Provider.xm.value:
                    product.uid = product.remote_id
                if coupon_manager:
                    if product.vendor.name == Provider.xm.value:
                        xm_product = XMFixedDuedayProduct.get(product.remote_id)
                        matched_coupons = XMFixedDuedayProduct.get_product_annotations(
                            coupon_manager, xm_product)

                product.annotations = {'has_coupons': len(matched_coupons) > 0}
            if product.is_sold_out:
                key = 'soldout'
            elif product.is_taken_down:
                key = 'offsale'
            elif product.is_pre_sale:
                key = 'presale'
            else:
                if product.ptype is Product.Type.unlimited:
                    key = 'wallet_onsale'
                else:
                    key = 'hoarder_onsale'
            product.display_status = PRODUCT_STATUS.get(key)
            if product.ptype is Product.Type.unlimited:
                product_obj['wallet'].append(product)
            else:
                product_obj['hoarder'].append(product)
    product_obj['wallet'].append(get_fund_product())
    return product_obj


def get_fund_product():
    """基金产品"""

    dashboard = PublicDashboard.today()
    profile = COMMON_PRODUCT_PROFILE.get(Provider.ms)
    product = dict(name=zhongshan.fund_name,
                   title=profile.get('title'),
                   vendor=Vendor.get_by_name(Provider.ms),
                   activity_title=profile.get('activity_title'),
                   activity_introduction=profile.get('activity_introduction'),
                   annual_rate=dashboard.latest_annual_rate.annual_rate,
                   tags=profile.get('tags'),
                   display_status=PRODUCT_STATUS.get('wallet_onsale'),
                   company=zhongshan.fund_company_name,
                   period=profile.get('period'),
                   code=zhongshan.fund_code,
                   bank_name=zhongshan.fund_bank_name)
    return product


@bp.route('/all', methods=['GET'])
@anonymous_oauth(['basic'])
def products_on_sale():
    """所有待售产品

    要使用本接口, 客户端必须有权以 ``basic`` 作为 scope.

    :reqheader Authorization: OAuth 2.0 Bearer Token(``仅登录成功后使用``)
    :reqheader X-Client-ID: OAuth 2.0 Client ID(``仅匿名访问时使用``)
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret(``仅匿名访问时使用``)
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.ProductResponseSchema` 列表
    """
    product_schema = ProductResponseSchema(strict=True)
    products = get_products(g.user)
    data, errors = product_schema.dump(products)
    conditional_for_v2(json.dumps(data))
    return jsonify(success=True, data=data, errors=errors)


@bp.route('/recommend', methods=['GET'])
@anonymous_oauth(['basic'])
def products_recommended():
    """推荐产品.

    要使用本接口, 客户端必须有权以 ``basic`` 作为 scope.

    :reqheader Authorization: OAuth 2.0 Bearer Token(``仅登录成功后使用``)
    :reqheader X-Client-ID: OAuth 2.0 Client ID(``仅匿名访问时使用``)
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret(``仅匿名访问时使用``)
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 200: 返回 :class:`.ProductResponseSchema` 列表
    """
    product_schema = ProductResponseSchema(strict=True)

    recommend_products = get_recommend_products(g.user)
    data, errors = product_schema.dump(recommend_products)
    conditional_for_v2(json.dumps(data))
    return jsonify(success=True, data=data, errors=errors)
