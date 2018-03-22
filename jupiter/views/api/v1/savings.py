# coding: utf-8

from __future__ import absolute_import, unicode_literals

from logging import WARNING
from operator import attrgetter, itemgetter
from pkg_resources import parse_version

from flask import request, jsonify, abort, g, url_for, json
from marshmallow import Schema, fields, pre_dump
from arrow import get as arrow_parse

from jupiter.ext import sentry
from core.models.utils import round_half_up
from core.models.bank import Partner
from core.models.profile.bankcard import BankCardManager
from core.models.hoard import HoardProfile
from core.models.hoard.common import ProfitPeriod as OriginProfitPeriod
from core.models.hoard.order import ORDER_STATUS_COLOR_MAP
from core.models.hoard.manager import SavingsManager
from core.models.hoard.zhiwang import (
    ZhiwangProduct, ZhiwangProfile, ZhiwangWrappedProduct)
from core.models.hoard.xinmi import XMProfile
from core.models.hoard.xinmi.product import XMProduct
from core.models.welfare import Coupon, CouponManager
from core.models.hoard import YixinAccount
from core.models.hoard.zhiwang import ZhiwangAccount
from core.models.hoard.xinmi import XMAccount
from core.models.hoarder.product import Product
from core.models.hoarder.asset import Asset
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoarder.account import Account as NewAccount
from core.models.hoarder.transactions import sxb
from core.models.hoarder.errors import RedeemError
from core.models.utils.switch import zhiwang_fdb_product_on_switch
from .accounts import UserSchema
from .profile import BankCardSchema
from .coupons import CouponSchema
from ..blueprint import create_blueprint, conditional_for
from ..decorators import require_oauth
from ..fields import LocalDateTimeField
from ..consts import VERSION_TOO_LOW

bp = create_blueprint('savings', 'v1', __name__, url_prefix='/savings')


@bp.before_request
@require_oauth(['savings_r'])
def initialize_yixin():
    if hasattr(request, 'oauth'):
        g.yixin_account = YixinAccount.get_by_local(request.oauth.user.id_)
    else:
        g.yixin_account = None


@bp.before_request
@require_oauth(['savings_r'])
def initialize_zhiwang():
    if hasattr(request, 'oauth'):
        g.zhiwang_account = ZhiwangAccount.get_by_local(request.oauth.user.id_)
    else:
        g.zhiwang_account = None


@bp.before_request
@require_oauth(['savings_r'])
def initialize_xinmi():
    if hasattr(request, 'oauth'):
        g.xm_account = XMAccount.get_by_local(request.oauth.user.id_)
    else:
        g.xm_account = None


@bp.before_request
@require_oauth(['savings_r'])
def initialize_sxb():
    g.sxb_account = None
    if hasattr(request, 'oauth'):
        vendor = Vendor.get_by_name(Provider.sxb)
        if vendor:
            g.sxb_account = NewAccount.get_by_local(vendor.id_, request.oauth.user.id_)


@bp.before_request
@require_oauth(['user_info'])
def initialize_bankcard_manager():
    if hasattr(request, 'oauth'):
        g.bankcard_manager = BankCardManager(request.oauth.user.id_)
    else:
        g.bankcard_manager = None


@bp.before_request
@require_oauth(['user_info'])
def initialize_coupons():
    if hasattr(request, 'oauth'):
        g.coupon_manager = CouponManager(request.oauth.user.id_)


@bp.route('/products', methods=['GET'])
@require_oauth(['savings_r'])
def products():
    """攒钱助手待售产品.

    :query partner: 可选参数，按合作方支持情况限制返回结果. 目前可为:

                    - ``"zw"``  指旺
                    - ``"xm"``  新米

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.ProductSchema` 列表
    """
    from .products.consts import sale_display_text
    product_schema = ProductSchema(strict=True, many=True)

    partners = frozenset(request.args.getlist('partner'))
    profile = SavingsManager(request.oauth.user.id_)
    profile.refresh_profile()
    services = []

    def product_sale_status_to_text(product):
        is_early_morning_product = isinstance(product, (XMProduct, ZhiwangWrappedProduct))
        if product.in_stock:
            return sale_display_text['on_sale']
        elif product.is_taken_down:
            if is_early_morning_product:
                return sale_display_text['early_morning_off_sale']
            return sale_display_text['late_morning_off_sale']
        elif product.is_either_sold_out:
            if is_early_morning_product:
                return sale_display_text['early_morning_sold_out']
            return sale_display_text['late_morning_sold_out']

    if 'zw' in partners and zhiwang_fdb_product_on_switch.is_enabled:
        zw_services = []
        for s in ZhiwangProduct.get_all():
            if s.product_type is ZhiwangProduct.Type.fangdaibao:
                zw_services.append(s)
            elif s.product_type is ZhiwangProduct.Type.classic:
                if s.profit_period['min'] not in (OriginProfitPeriod(90, 'day'),
                                                  OriginProfitPeriod(180, 'day'),
                                                  OriginProfitPeriod(270, 'day'),
                                                  OriginProfitPeriod(365, 'day')):
                    zw_services.append(s)
        zw_services.sort(key=attrgetter('annual_rate'))
        ZhiwangProfile.add(request.oauth.user.id_)
        for zw_service in zw_services:
            product_text = product_sale_status_to_text(zw_service)
            if product_text:
                zw_service.button_display_text, zw_service.button_click_text = product_text
            zw_service.is_able_purchased = zw_service.in_stock
            zw_service.introduction = ''
            zw_service.title = ''
            zw_service.activity_title = ''
            zw_service.activity_introduction = ''
            zw_service._total_amount = 0
            zw_service.agreement = url_for('savings.landing.agreement_zhiwang', _external=True)
            zw_service.annotations = ZhiwangProduct.get_product_annotations(
                g.coupon_manager, zw_service)
        services.extend(zw_services)
    if 'xm' in partners:
        xm_products = [s for s in XMProduct.get_all()]
        xm_products.sort(key=attrgetter('annual_rate'))
        XMProfile.add(request.oauth.user.id_)
        for xm_product in xm_products:
            product_text = product_sale_status_to_text(xm_product)
            if product_text:
                xm_product.button_display_text, xm_product.button_click_text = product_text
            xm_product.is_able_purchased = xm_product.in_stock
            xm_product.introduction = ''
            xm_product.title = ''
            xm_product.activity_title = ''
            xm_product.activity_introduction = ''
            xm_product._total_amount = 0
            xm_product.agreement = url_for('savings.landing.agreement_xinmi', _external=True)
            xm_product.annotations = XMProduct.get_product_annotations(
                g.coupon_manager, xm_product)
        services.extend(xm_products)

    product_data = product_schema.dump(services).data
    for product in product_data:
        product.update({'is_newcomer': False})

    all_product_data = []

    if 'sxb' in partners:
        from .products.sxb import get_sxb_products

        product_schema = SxbProductSchema(strict=True, many=True)
        sxb_products = get_sxb_products(request.oauth.user.id_)
        services.extend(sxb_products)
        sxb_father_products = [p for p in sxb_products if p.kind is Product.Kind.father]
        sxb_father_product_data = product_schema.dump(sxb_father_products).data
        if SavingsManager(request.oauth.user.id_).is_new_savings_user:
            sxb_child_products = [p for p in sxb_products if p.kind is Product.Kind.child]
            sxb_child_product_data = product_schema.dump(sxb_child_products).data
            for product in sxb_child_product_data:
                product.update({'is_newcomer': True})
            all_product_data.extend(sxb_child_product_data)
        all_product_data.extend(sxb_father_product_data)

    all_product_data.extend(product_data)
    conditional_for(json.dumps(all_product_data))

    return jsonify(success=True, data=all_product_data)


@bp.route('/mine', methods=['GET'])
@require_oauth(['savings_r'])
def mine():
    """用户攒钱概况.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回 :class:`~jupiter.views.api.v1.savings.ProfileSchema`
    """
    profile_schema = ProfileSchema(strict=True)
    profile = SavingsManager(request.oauth.user.id_)
    if request.user_agent.app_info.version <= parse_version('1.0'):
        profile.refresh_profile()
    conditional_for([
        unicode(profile.user_id),
        unicode(profile.on_account_invest_amount),
        unicode(profile.daily_profit),
        unicode(profile.total_profit),
        unicode(profile.total_orders),
    ])

    sxb_account = None
    sxb_vendor = Vendor.get_by_name(Provider.sxb)
    if sxb_vendor:
        sxb_account = NewAccount.get(sxb_vendor.id_, request.oauth.user.id_)
    profile.has_sxb_account = True if sxb_account else False

    return jsonify(success=True, data=profile_schema.dump(profile).data)


@bp.route('/orders', methods=['GET'])
@require_oauth(['savings_r'])
def orders():
    """用户已有订单.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.YixinOrderSchema` 、`.XinmiOrderSchema`  或 `.ZhiwangOrderSchema` 列表
    :query: 可选参数，按订单请求数限制返回结果. 目前可为:

                - ``"offset"`` 开始条数
                - ``"count"`` 每页数量
                - ``"only_due"`` 展示攒钱中的订单

    """
    yixin_order_schema = YixinOrderSchema(strict=True, many=True)
    zhiwang_order_schema = ZhiwangOrderSchema(strict=True, many=True)
    xm_order_schema = XinmiOrderSchema(strict=True, many=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    only_due = request.args.get('only_due', type=bool, default=False)
    order_data = []

    yixin_profile = HoardProfile.add(request.oauth.user.id_)
    yixin_orders = []
    for order, order_info, order_status in yixin_profile.orders(filter_due=only_due):
        order._coupon = None
        order._coupon_benefit = None
        order._order_status = order_status
        order._status_color = ORDER_STATUS_COLOR_MAP.get(
            order_status, '#9B9B9B')
        order._due_date = arrow_parse(order_info['frozenDatetime']).date()
        if order_status == u'确认中':
            order._confirm_desc = u'支付成功后1-3工作日'
        else:
            order._confirm_desc = order_info['startCalcDate']

        yixin_orders.append(order)
    order_data.extend(yixin_order_schema.dump(yixin_orders).data)

    zhiwang_profile = ZhiwangProfile.add(request.oauth.user.id_)
    zhiwang_orders = []
    for order, asset in zhiwang_profile.mixins(filter_due=only_due):
        order._display_status = asset.display_status if asset else order.display_status
        order._status_color = ORDER_STATUS_COLOR_MAP.get(
            order._display_status, '#9B9B9B')
        order._due_date = order.due_date.date()

        if order.display_status == u'处理中':
            order._confirm_desc = u'支付成功后第二个工作日'
        else:
            order._confirm_desc = order.start_date.date()
        zhiwang_orders.append(order)
    order_data.extend(zhiwang_order_schema.dump(zhiwang_orders).data)

    xm_profile = XMProfile.add(request.oauth.user.id_)
    xm_orders = []
    for order, asset in xm_profile.mixins(filter_due=only_due):
        order._display_status = asset.display_status if asset else order.display_status
        order._status_color = ORDER_STATUS_COLOR_MAP.get(order._display_status, '#9B9B9B')
        order._due_date = order.due_date.date()

        if order.display_status == u'处理中':
            order._confirm_desc = u'支付成功后第二个工作日'
        else:
            order._confirm_desc = order.start_date.date()
            xm_orders.append(order)
    order_data.extend(xm_order_schema.dump(xm_orders).data)

    if only_due:
        order_data = sorted(order_data, key=itemgetter('due_date'))
    else:
        order_data = sorted(order_data, key=itemgetter('created_at'), reverse=True)
    order_data = order_data[offset:offset + count]

    conditional_for(u'{0}#{1}#{2}'.format(
        o['uid'], unicode(o['status']), o['status_text']) for o in order_data)

    return jsonify(success=True, data=order_data)


@bp.route('/order', methods=['POST'])
@require_oauth(['savings_w'])
def purchase():
    """[已下线] 选购宜人贷产品, 创建理财单.

    :status 410: Gone
    """
    abort(410, VERSION_TOO_LOW)


@bp.route('/order/<int:order_id>/confirm', methods=['POST'])
@require_oauth(['savings_w'])
def purchase_confirm(order_id):
    """[已下线] 确认宜人贷理财单, 绑定支付银行卡, 创建支付单, 并发送短信验证码.

    :status 410: Gone
    """
    abort(410, VERSION_TOO_LOW)


@bp.route('/order/<int:order_id>/verify', methods=['POST'])
@require_oauth(['savings_w'])
def purchase_verify(order_id):
    """[已下线] 提供宜人贷短信验证码, 支付理财单.

    :status 410: Gone
    """
    abort(410, VERSION_TOO_LOW)


def obtain_bankcard(bankcard_id):
    bankcard = g.bankcard_manager.get(bankcard_id)
    if not bankcard:
        warning('用户访问不存在的银行卡', bankcard_id=bankcard_id)
        abort(400, '该银行卡不存在，请重新添加银行卡')
    if Partner.zw not in bankcard.bank.available_in:
        abort(400, '当前服务暂不支持该银行卡，请您选择其他银行重试')
    return bankcard


def obtain_coupon(coupon_id):
    coupon = Coupon.get(coupon_id)
    if not coupon:
        return
    if not coupon.is_owner(request.oauth.user):
        abort(403, '用户不可使用此券')
    return coupon


def warning(message, **kwargs):
    extra = {'user': request.oauth.user}
    extra.update(kwargs)
    return sentry.captureMessage(message, extra=extra, level=WARNING)


class ProfitPeriod(Schema):
    """攒钱助手封闭期."""

    #: :class:`int` 封闭期的值
    value = fields.Integer()
    #: :class:`str` 封闭期的单位, 可能枚举: ``"day"``/``"month"``
    unit = fields.String()


class ProfitPeriodRange(Schema):
    """攒钱助手封闭期范围."""

    #: :class:`.ProfitPeriod` 最小封闭期
    min = fields.Nested(ProfitPeriod)
    #: :class:`.ProfitPeriod` 最大封闭期, 当产品为固定封闭期时和最小封闭期相等
    max = fields.Nested(ProfitPeriod)


class ProfitPercentRange(Schema):
    """攒钱助手收益率 (百分比) 范围."""

    min = fields.Decimal(places=2)
    max = fields.Decimal(places=2)


class ProfitRate(Schema):
    """指旺非定期产品最小投资期限和收益."""

    #: :class:`~int` 指旺非定期产品的投资最小天数
    min_days = fields.Integer()
    #: :class:`~decimal` 投资收益率
    annual_rate = fields.Decimal(places=2)


class ProductSchema(Schema):
    """攒钱助手产品实体."""

    #: :class:`str` 产品 ID
    uid = fields.String(attribute='unique_product_id')
    #: :class:`str` 包装后的产品 ID, 普通产品始终为`null`
    wrapped_product_id = fields.String()
    #: :class:`str` 合作方，可能为 ``"yrd"`` (宜人贷) 、``"xm"`` (新结算投米) 或 ``"zw"`` (指旺)
    #:
    #: .. note:: 不可向用户露出“指旺”的名字
    partner = fields.Function(lambda o: o.provider.shortcut)
    #: :class:`.ProfitPercentRange` 年收益率 (百分比) 范围
    profit_percent = fields.Nested(
        ProfitPercentRange, attribute='profit_annual_rate')
    #: :class:`.ProfitPeriodRange` 封闭期 (月或日) 范围
    profit_period = fields.Nested(ProfitPeriodRange)
    #: :class:`str` 产品活动类型
    activity_type = fields.String()
    #: :class:`bool` 是否已停售
    is_taken_down = fields.Boolean()
    #: :class:`bool` 是否已售罄
    is_sold_out = fields.Boolean(attribute='is_either_sold_out')
    #: :class:`~decimal.Decimal` 同一封闭期产品累计已购金额, 指旺暂为0
    amount = fields.Decimal(places=2, attribute='_total_amount')
    #: :class:`~decimal.Decimal` 最大可攒金额
    max_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最小可攒金额
    min_amount = fields.Decimal(places=2)
    #: :class:`~int` 增加幅度
    increasing_step = fields.Integer()
    #: :class:`.ProfitRate` 最小购买天数和收益
    annual_rate_layers = fields.Nested(ProfitRate, many=True)
    #: :class:`str` 产品名称
    title = fields.String()
    #: :class:`str` 产品情况介绍
    introduction = fields.String()
    #: :class:`.Date` 起息日
    start_date = fields.Date()
    #: :class:`str` 产品活动页介绍标题
    activity_title = fields.String()
    #: :class:`str` 产品活动介绍内容
    activity_introduction = fields.String()
    #: :class:`.url` 用户协议地址, 宜人贷产品始终为`null`
    agreement = fields.Url()
    #: :class:`list` 礼券可用信息
    annotations = fields.List(fields.String())
    #: :class:`.str` 按钮显示文案(新增)
    button_display_text = fields.String()
    #: :class:`.str` 按钮点击文案(新增)
    button_click_text = fields.String()
    #: :class:`bool` 是否可购买(新增)
    is_able_purchased = fields.Boolean()


class WrappedProductSchema(Schema):
    """在合作方原始产品基础上配置出的本地包装产品"""

    #: :class:`str` 产品 ID
    uid = fields.Function(lambda o: o.raw_product_id)
    #: :class:`str` 包装后的产品 ID
    wrapped_product_id = fields.String(attribute='id_')
    #: :class:`str` 合作方，可能为 ``"zw"`` (指旺)
    #:
    #: .. note:: 不可向用户露出“指旺”的名字
    partner = fields.String()
    #: :class:`.ProfitPercentRange` 年收益率 (百分比) 范围
    profit_percent = fields.Nested(
        ProfitPercentRange, attribute='profit_annual_rate')
    #: :class:`.ProfitPeriodRange` 封闭期 (月或日) 范围
    profit_period = fields.Nested(ProfitPeriodRange)
    #: :class:`str` 产品活动类型
    activity_type = fields.Function(lambda o: o.wrapped_product_type.label)
    #: :class:`bool` 是否已停售
    is_taken_down = fields.Boolean()
    #: :class:`bool` 是否已售罄
    is_sold_out = fields.Boolean(attribute='is_either_sold_out')
    #: :class:`~decimal.Decimal` 同一封闭期产品累计已购金额, 指旺暂为0
    amount = fields.Decimal(places=2, attribute='_total_amount')
    #: :class:`~decimal.Decimal` 最大可攒金额
    max_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最小可攒金额
    min_amount = fields.Decimal(places=2)
    #: :class:`~int` 增加幅度
    increasing_step = fields.Function(lambda o: o.raw_product.increasing_step)
    #: :class:`.ProfitRate` 最小购买天数和收益
    annual_rate_layers = fields.Nested(ProfitRate, many=True)
    #: :class:`str` 产品名称
    title = fields.String()
    #: :class:`str` 产品情况介绍
    introduction = fields.String()
    #: :class:`.Date` 起息日
    start_date = fields.Function(lambda o: str(o.raw_product.start_date))
    #: :class:`str` 产品活动页介绍标题
    activity_title = fields.String()
    #: :class:`str` 产品活动介绍
    activity_introduction = fields.String()
    #: :class:`.url` 用户协议地址, 宜人贷产品始终为`null`
    agreement = fields.Url()
    #: :class:`list` 礼券可用信息
    annotations = fields.List(fields.String())
    #: :class:`.str` 按钮显示文案(新增)
    button_display_text = fields.String()
    #: :class:`.str` 按钮点击文案(新增)
    button_click_text = fields.String()
    #: :class:`bool` 是否可购买(新增)
    is_able_purchased = fields.Boolean()


class ProfileSchema(Schema):
    """攒钱助手用户信息."""

    #: :class:`~decimal.Decimal` 在账已攒金额
    amount = fields.Decimal(places=2, attribute='on_account_invest_amount')
    #: :class:`~decimal.Decimal` 每日收益
    daily_profit = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 累计收益
    total_profit = fields.Decimal(places=2)
    #: :class:`~int` 攒钱总笔数
    total_orders = fields.Integer()
    #: :class:`bool` 是否有随心宝账户
    has_sxb_account = fields.Boolean()


class ZhiwangOrderSchema(Schema):
    """指旺订单实体."""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 资产唯一 ID
    asset_id = fields.Function(lambda o: o.asset.id_)
    #: :class:`.UserSchema` 下单者
    user = fields.Nested(UserSchema)
    #: :class:`.ProductSchema` 对应产品
    product = fields.Nested(ProductSchema)
    #: :class:`.WrappedProductSchema` 对应产品
    wrapped_product = fields.Nested(WrappedProductSchema)
    #: :class:`~datetime.datetime` 创建时间
    created_at = LocalDateTimeField(attribute='creation_time')
    #: :class:`~decimal.Decimal` 金额
    amount = fields.Decimal()
    #: :class:`~decimal.Decimal` 预期的到期总收益
    expected_profit = fields.Decimal(attribute='_expect_interest')
    #: :class:`str` 订单活动类型，比如新手活动
    activity_type = fields.String()
    #: :class:`.BankCardSchema` 支付所用银行卡
    bankcard = fields.Nested(BankCardSchema)
    #: :class:`str` 订单状态。(unpaid/shelved/paying:订单处理中; success:订单成功; failure:订单失败)
    status = fields.Function(lambda o: o.status.name)
    #: :class:`str` 订单状态颜色标识
    status_color = fields.String(attribute='_status_color')
    #: :class:`str` 指旺订单状态 (中文文案)
    status_text = fields.String(attribute='_display_status')
    #: :class:`str` 需要客户端保存在会话中的支付单 ID
    stashed_payment_id = fields.String(attribute='pay_code')
    #: :class:`decimal.Decimal` 礼券福利金额，始终为 ``null``
    coupon_benefit = fields.Decimal(attribute='_coupon_benefit')
    #: :class:`.CouponSchema` 支付所用的礼券实体, 始终为 ``null``
    coupon = fields.Nested(CouponSchema)
    #: :class:`str` 支付时红包抵扣金额
    display_redpacket_amount = fields.String()
    #: :class:`str` 支付时优惠券抵扣金额/加息率
    display_coupon_benefit = fields.Function(lambda o: o.coupon.regulation.display_benefit)
    #: :class:`~datetime.date` 到期时间
    due_date = fields.Date(attribute='_due_date')
    #: :class:`str` 确认时间或提示文案
    confirm_desc = fields.String(attribute='_confirm_desc')
    #: :class:`~decimal.Decimal` 实际年化收益率 (百分比)
    profit_annual_rate = fields.Decimal(
        places=2, attribute='actual_annual_rate')
    #: :class:`.ProfitPeriod` 封闭期 (日)
    profit_period = fields.Nested(ProfitPeriod)

    @pre_dump
    def preprocess(self, order):
        if order.asset:
            order._expect_interest = order.asset.expect_interest
        else:
            order._expect_interest = order.expect_interest

        if order.woods_burning:
            order.display_redpacket_amount = u'减%s元' % round_half_up(
                order.woods_burning.amount, 2)


class YixinOrderSchema(Schema):
    """宜人贷订单实体."""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`.UserSchema` 下单者
    user = fields.Nested(UserSchema, required=True)
    #: :class:`.ProductSchema` 对应产品
    product = fields.Nested(ProductSchema, attribute='service', required=True)
    #: :class:`.WrappedProductSchema` 对应产品
    wrapped_product = fields.Nested(WrappedProductSchema)
    #: :class:`~datetime.datetime` 创建时间
    created_at = LocalDateTimeField(attribute='creation_time', required=True)
    #: :class:`~decimal.Decimal` 金额
    amount = fields.Decimal(attribute='order_amount', required=True)
    #: :class:`~decimal.Decimal` 预期的到期总收益
    expected_profit = fields.Decimal(required=True)
    #: :class:`.BankCardSchema` 支付所用银行卡
    bankcard = fields.Nested(BankCardSchema, required=True)
    #: :class:`str` 订单活动类型，比如新手活动
    activity_type = fields.String()
    #: :class:`str` 订单状态
    status = fields.Function(lambda o: o.status.name, required=True)
    #: :class:`str` 订单状态颜色标识
    status_color = fields.String(attribute='_status_color', required=True)
    #: :class:`str` 宜人贷订单状态 (中文文案)
    status_text = fields.String(attribute='_order_status', required=True)
    #: :class:`str` 需要客户端保存在会话中的支付单 ID
    stashed_payment_id = fields.String(attribute='stashed_order_id')
    #: :class:`decimal.Decimal` 礼券福利金额，可能为`null`
    coupon_benefit = fields.Decimal(attribute='_coupon_benefit')
    #: :class:`.CouponSchema` 支付所用的礼券实体
    coupon = fields.Nested(CouponSchema, attribute='_coupon')
    #: :class:`~datetime.date` 到期时间
    due_date = fields.Date(attribute='_due_date')
    #: :class:`str` 确认时间或提示文案
    confirm_desc = fields.String(attribute='_confirm_desc')
    #: :class:`~decimal.Decimal` 年化收益率 (百分比)
    profit_annual_rate = fields.Decimal(places=2, attribute='annual_rate')
    #: :class:`.ProfitPeriod` 封闭期 (月)
    profit_period = fields.Nested(ProfitPeriod)


class XinmiOrderSchema(Schema):
    """新米订单实体."""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 资产唯一 ID
    asset_id = fields.Function(lambda o: o.asset.id_)
    #: :class:`.UserSchema` 下单者
    user = fields.Nested(UserSchema)
    #: :class:`.ProductSchema` 对应产品
    product = fields.Nested(ProductSchema)
    #: :class:`~datetime.datetime` 创建时间
    created_at = LocalDateTimeField(attribute='creation_time')
    #: :class:`~decimal.Decimal` 金额
    amount = fields.Decimal()
    #: :class:`~decimal.Decimal` 预期的到期总收益
    expected_profit = fields.Decimal(attribute='_expect_interest')
    #: :class:`str` 订单活动类型，比如新手活动
    activity_type = fields.String()
    #: :class:`.BankCardSchema` 支付所用银行卡
    bankcard = fields.Nested(BankCardSchema)
    #: :class:`str` 订单状态。(unpaid/shelved/paying:订单处理中; success:订单成功; failure:订单失败)
    status = fields.Function(lambda o: o.status.name)
    #: :class:`str` 订单状态颜色标识
    status_color = fields.String(attribute='_status_color')
    #: :class:`str` 新米订单状态 (中文文案)
    status_text = fields.String(attribute='_display_status')
    #: :class:`str` 需要客户端保存在会话中的支付单 ID
    # stashed_payment_id = fields.String(attribute='pay_code')
    #: :class:`decimal.Decimal` 礼券福利金额，始终为 ``null``
    coupon_benefit = fields.Decimal(attribute='_coupon_benefit')
    #: :class:`.CouponSchema` 支付所用的礼券实体, 始终为 ``null``
    coupon = fields.Nested(CouponSchema)
    #: :class:`str` 支付时红包抵扣金额
    display_redpacket_amount = fields.String()
    #: :class:`str` 支付时优惠券抵扣金额/加息率
    display_coupon_benefit = fields.Function(lambda o: o.coupon.regulation.display_benefit)
    #: :class:`~datetime.date` 到期时间
    due_date = fields.Date(attribute='_due_date')
    #: :class:`str` 确认时间或提示文案
    confirm_desc = fields.String(attribute='_confirm_desc')
    #: :class:`~decimal.Decimal` 实际年化收益率 (百分比)
    profit_annual_rate = fields.Decimal(
        places=2, attribute='actual_annual_rate')
    #: :class:`.ProfitPeriod` 封闭期 (日)
    profit_period = fields.Nested(ProfitPeriod)

    @pre_dump
    def preprocess(self, order):
        if order.asset:
            order._expect_interest = order.asset.expect_interest
        else:
            order._expect_interest = order.expect_interest

        if order.woods_burning:
            order.display_redpacket_amount = u'减%s元' % round_half_up(
                order.woods_burning.amount, 2)


class PreRedeemResponseSchema(Schema):
    """赎回相关信息请求实体."""
    #: :class:`~decimal.Decimal` 今日可提现金额
    remaining_amount_today = fields.Decimal(places=2, default=0)
    #: :class:`~decimal.Decimal` 最低提现金额
    min_redeem_amount = fields.Decimal(attribute='_min_redeem_amount', places=2)
    #: :class:`~datetime.date` 预计到账时间
    expect_payback_date = fields.Date()
    #: :class:`int` 剩余免费赎回次数
    residual_redemption_times = fields.Integer()
    #: :class:`~decimal.Decimal` 固定手续费
    fixed_service_fee = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 提现手续费费率
    service_fee_rate = fields.Decimal(places=2, attribute='_service_fee_rate')
    #: :class:`str` 手续费提示信息
    service_fee_desc = fields.String(attribute='_service_fee_desc')
    #: :class:`str` 回款银行卡 ID
    bankcard_id = fields.String()
    #: :class:`str` 回款银行卡描述信息
    bankcard_desc = fields.String()
    #: :class:`.url` 提现协议地址
    redeem_rule_url = fields.Url()


@bp.route('/pre_redeem/<int:product_id>', methods=['GET'])
@require_oauth(['savings_r'])
def pre_redeem(product_id):
    """赎回资产前获取用户相关的产品赎回信息

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 请求成功, 返回 :class:`.PreRedeemResponseSchema`
    :status 400: 用户没有该产品的资产
    :status 403: 找不到可赎回产品
    """

    assets = Asset.gets_by_user_id_with_product_id(request.oauth.user.id_, product_id)
    if not assets:
        abort(400, u'用户没有可赎回资产')

    current_asset = assets[0]

    product = Product.get(product_id)
    if not product:
        abort(403, u'找不到可赎回产品')

    bankcard = obtain_bankcard(current_asset.bankcard_id)
    current_asset.bankcard_desc = '{0}({1})'.format(bankcard.bank_name,
                                                    bankcard.tail_card_number)

    current_asset.redeem_rule_url = url_for('hybrid.rules.sxb_withdraw', _external=True)
    current_asset._min_redeem_amount = product.min_redeem_amount
    current_asset._service_fee_rate = current_asset.service_fee_rate * 100
    if current_asset.residual_redemption_times > 0:
        current_asset._service_fee_desc = u'本月还可免费提现 %s 次' % \
                                          current_asset.residual_redemption_times
    else:
        current_asset._service_fee_desc = u'提现费率为 {}%'.format(round_half_up(
            current_asset.service_fee_rate * 100, 2))

    pre_redeem_schema = PreRedeemResponseSchema(strict=True)
    data, errors = pre_redeem_schema.dump(current_asset)
    conditional_for(json.dumps(data))
    return jsonify(success=True, data=data)


class RedeemSchema(Schema):
    """赎回请求实体."""
    #: :class:`str` 赎回产品 ID
    product_id = fields.String(required=True)
    #: :class:`~decimal.Decimal` 赎回金额
    redeem_amount = fields.Decimal(required=True)
    #: :class:`str` 回款银行卡 ID
    bankcard_id = fields.String(required=True)
    #: :class:`bool` 是否加急
    is_express = fields.Boolean(default=False)
    #: :class:`bool` 是否到期转让
    is_expired = fields.Boolean(default=False)
    #: :class:`int` 转让类型 (1:全部转让; 2:保留资产转让; 3:转让部分资产)
    redeem_type = fields.Integer()


class RedeemResponseSchema(Schema):
    """赎回请求返回实体."""
    #: :class:`str` 赎回状态 (applyed:远端申请赎回; redeeming:远端正在赎回; waiting_back:远端待回款; backing:远端回款中)
    status = fields.Function(lambda o: o.status.name)
    #: :class:`str` 赎回产品 ID
    product_id = fields.String(required=True)
    #: :class:`~decimal.Decimal` 赎回金额
    redeem_amount = fields.Decimal(attribute='amount', places=2, required=True)
    #: :class:`~decimal.Decimal` 手续费
    service_fee = fields.Decimal(places=2, required=True)
    #: :class:`~decimal.Decimal` 实际到账金额
    amount = fields.Decimal(attribute='pay_amount', places=2, required=True)
    #: :class:`str` 回款银行卡 ID
    bankcard_id = fields.String()
    #: :class:`~decimal.Decimal` 剩余金额
    remaining_amount = fields.Decimal(places=2)
    #: :class:`str` 回款银行卡描述信息
    bankcard_desc = fields.String()


class SxbProductSchema(ProductSchema):
    """随心宝产品实体."""

    #: :class:`str` 订单唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 合作方
    #:
    #: .. note:: 不可向用户露出“随心宝”的名字
    partner = fields.Function(lambda o: o.vendor.name)
    #: :class:`~decimal.Decimal` 加息年化利率(新增)
    interest_rate_hike = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 同一封闭期产品累计已购金额
    amount = fields.Decimal(places=2, attribute='total_amount')
    #: :class:`.DateTime` 起息日时间
    start_date = fields.Date(attribute='value_date')
    #: :class:`.DateTime`  首次查看收益时间
    check_benifit_date = fields.Date(attribute='check_benifit_date')
    #: :class:`bool` 是否能够被手动赎回(新增)
    is_able_redeemed = fields.Function(lambda o: o.can_redeem)
    #: :class:`~decimal.Decimal` 今日可提现金额
    remaining_amount_today = fields.Decimal(places=2, default=0)
    #: :class:`~decimal.Decimal` 最大赎回金额(新增)
    max_redeem_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最小赎回金额(新增)
    #:
    #: .. note:: 针对允许用户注定发起赎回的产品
    min_redeem_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 每日赎回金额(新增)
    day_redeem_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 剩余可持有金额(新增)
    rest_hold_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 投资收益率(新增)
    annual_rate = fields.Decimal(places=2)
    #: :class:`str` 提现规则
    withdraw_rule = fields.String()


@bp.route('/redeem', methods=['POST'])
@require_oauth(['savings_w'])
def redeem():
    """赎回资产

    :request: :class:`.RedeemSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 赎回请求成功, 返回 :class:`.RedeemResponseSchema`
    :status 400: 产品或金额无效
    :status 403: 第三方错误
    """

    redeem_schema = RedeemSchema(strict=True)
    result = redeem_schema.load(request.get_json(force=True))

    product_id = result.data['product_id']

    bankcard = obtain_bankcard(result.data['bankcard_id'])
    redeem_amount = result.data.get('redeem_amount')
    # 默认到期自动转移 和 加急 均为 否
    is_express = result.data.get('is_express', False)
    is_expired = result.data.get('is_expired', False)

    product = Product.get(product_id)
    if not product:
        abort(400, u'产品无效')

    vendor = product.vendor
    if vendor and vendor.name == 'sxb':
        assets = Asset.gets_by_user_id_with_product_id(request.oauth.user.id_, product_id)
        if not assets:
            abort(400, u'用户没有可赎回资产')

        current_asset = assets[0]
        remaining_amount = (current_asset.uncollected_amount + current_asset.hold_amount -
                            redeem_amount)
        # if remaining_amount != 0 and remaining_amount < 100:
        #     abort(400, u'赎回金额无效: 赎回后余额小于100')

        try:
            redeem_order = sxb.redeem(request.oauth.user, product, redeem_amount, bankcard,
                                      is_expired, is_express)
            redeem_order.remaining_amount = remaining_amount
            redeem_order.bankcard_desc = '{0}({1})'.format(bankcard.bank_name,
                                                           bankcard.tail_card_number)
            redeem_response_schema = RedeemResponseSchema(strict=True)
            data, errors = redeem_response_schema.dump(redeem_order)
            conditional_for(json.dumps(data))
            return jsonify(success=True, data=data)
        except RedeemError as e:
            abort(403, unicode(e))
    else:
        abort(400, '目前只支持随心宝产品赎回')


class SxbUserAssetResponseSchema(Schema):
    #: :class:`str` 随心宝产品 ID
    product_id = fields.String(required=True, default=0)
    #: :class:`~decimal.Decimal` 持有资产金额
    hold_amount = fields.Decimal(required=True, places=2, attribute='total_amount', default=0)
    #: :class:`str` 昨日收益金额
    yesterday_profit = fields.Decimal(required=True, places=2, default=0)
    #: :class:`int` 剩余免费赎回次数
    residual_redemption_times = fields.Integer(required=True, default=0)
    #: :class:`~decimal.Decimal` 今日可提现金额
    remaining_amount_today = fields.Decimal(places=2, default=0)


@bp.route('/sxb/user_asset', methods=['GET'])
@require_oauth(['savings_r'])
def sxb_user_asset():
    """查询用户随心宝资产

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 请求成功, 返回 :class:`.SxbUserAssetResponseSchema`
    :status 403: 查询错误
    """

    assets = Asset.gets_by_user_id(request.oauth.user.id_)

    sxb_asset = None
    for asset in assets:
        product = asset.product
        if product.vendor.name == 'sxb':
            sxb_asset = asset
            break

    response_schema = SxbUserAssetResponseSchema(strict=True)
    data, errors = response_schema.dump(sxb_asset)
    conditional_for(json.dumps(data))
    return jsonify(success=True, data=data)
