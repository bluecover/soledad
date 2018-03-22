# coding: utf-8

from flask import g, abort, request, redirect, url_for
from flask_mako import render_template

from core.models.welfare import CouponManager, FirewoodWorkflow
from core.models.hoard.zhiwang import (
    ZhiwangAsset, ZhiwangAccount, ZhiwangProfile,
    ZhiwangProduct, ZhiwangWrappedProduct, ZhiwangOrder)
from core.models.hoard.zhiwang.utils import iter_banks
from core.models.hoard.zhiwang.errors import ContractFetchingError
from core.models.hoard.zhiwang.transaction import fetch_asset_contract
from core.models.profile.identity import Identity, has_real_identity
from core.models.promotion.festival.spring import SpringGift
from core.models.bank import Partner
from ._blueprint import create_blueprint

bp = create_blueprint('zhiwang', __name__, url_prefix='/zw')


def get_order(order_id):
    order = ZhiwangOrder.get(order_id)
    if not order:
        abort(404)
    if not order.is_owner(g.user):
        abort(403)
    return order


@bp.before_request
def initialize():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))
    g.zhiwang_profile = ZhiwangProfile.add(g.user.id_)
    g.coupon_manager = CouponManager(g.user.id_)
    g.firewood_flow = FirewoodWorkflow(g.user.id_)


@bp.before_request
def check_identity():
    if ZhiwangAccount.get_by_local(g.user.id_):
        if not has_real_identity(g.user):
            # 当用户有指旺账号却没有身份信息时跳转完善信息（基本不可能发生）
            return redirect(url_for('profile.auth.supply', next=request.path))
    else:
        # 没有指旺账号则跳转注册页
        return redirect(url_for('savings.auth.zhiwang', next=request.path))

    g.identity = Identity.get(g.user.id_)


@bp.route('/contract/asset/<int:asset_no>')
def asset_contract(asset_no):
    asset = ZhiwangAsset.get_by_asset_no(asset_no)
    if not asset or not asset.is_owner(g.user):
        abort(401)

    error = ''
    if not asset.contract:
        try:
            content = fetch_asset_contract(g.user.id_, asset)
        except ContractFetchingError as e:
            error = e.args[0]
        else:
            asset.contract = content
    return render_template(
        'savings/contract_zhiwang.html', contract=asset.contract, error=error)


@bp.route('/product/<int:product_id>')
@bp.route('/product/<int:product_id>/<int:wrapped_product_id>')
def purchase(product_id, wrapped_product_id=None):
    cur_path = 'record'
    partner = Partner.zw
    agreement_url = url_for('savings.landing.agreement_zhiwang')

    banks = iter_banks(g.user.id_)
    bankcards = g.zhiwang_profile.bankcards.get_all()
    raw_product = ZhiwangProduct.get(product_id) or abort(404)
    spring_gift = SpringGift.get_by_user(g.user)

    wrapped_product = ZhiwangWrappedProduct.get(wrapped_product_id)
    if wrapped_product_id is not None and not wrapped_product:
        abort(404)

    coupons = [c.to_dict() for c in g.coupon_manager.available_coupons
               if c.is_available_for_product(wrapped_product or raw_product)]

    context = {'coupons': coupons, 'banks': banks, 'bankcards': bankcards, 'partner': partner,
               'user_balance': g.firewood_flow.balance, 'cur_path': cur_path,
               'product': raw_product, 'spring_gift': spring_gift, 'agreement_url': agreement_url}

    if wrapped_product and wrapped_product.is_qualified(g.user.id_):
        context.update(dict(product=wrapped_product))
        context['product_type'] = 'newcomer'
        return render_template('savings/order.html', **context)

    if raw_product.product_type is ZhiwangProduct.Type.fangdaibao:
        context['annual_rate_layers'] = raw_product.annual_rate_layers
        context['product_type'] = 'ladder'
    elif raw_product.product_type is ZhiwangProduct.Type.classic:
        context['product_type'] = 'regular'
    else:
        abort(404)

    return render_template('savings/order.html', **context)


@bp.route('/order/<int:order_id>/complete')
def order_complete(order_id):
    cur_path = 'savings'
    order = get_order(order_id)

    return render_template(
        'savings/complete_zhiwang.html', order=order, cur_path=cur_path,
        is_new_savings_user=g.savings_manager.is_new_savings_user)
