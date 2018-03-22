# coding: utf-8
from core.models.utils import round_half_up

from flask import g, abort, request, redirect, url_for
from flask_mako import render_template

from libs.utils.string import num2chn
from core.models.hoard.zhiwang.utils import iter_banks
from core.models.hoard.xinmi import XMFixedDuedayProduct, XMOrder, XMAsset
from core.models.profile.identity import Identity, has_real_identity
from core.models.hoard.xinmi import XMAccount
from core.models.hoard.xinmi.profile import XMProfile
from core.models.welfare import FirewoodWorkflow, CouponManager
from core.models.bank import Partner
from ._blueprint import create_blueprint

bp = create_blueprint('xinmi', __name__, url_prefix='/xm')


def get_order(order_id):
    order = XMOrder.get(order_id)
    if not order:
        abort(404)
    if not order.is_owner(g.user):
        abort(403)
    return order


@bp.before_request
def initialize():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))
    g.xinmi_profile = XMProfile.add(g.user.id_)
    g.coupon_manager = CouponManager(g.user.id_)
    g.firewood_flow = FirewoodWorkflow(g.user.id_)


@bp.before_request
def check_identity():
    if XMAccount.get_by_local(g.user.id_):
        if not has_real_identity(g.user):
            # 当用户有新米账号却没有身份信息时跳转完善信息（基本不可能发生）
            return redirect(url_for('profile.auth.supply', next=request.path))
    else:
        # 没有新米账号则跳转注册页
        return redirect(url_for('savings.auth.xinmi', next=request.path))

    g.identity = Identity.get(g.user.id_)


@bp.route('/contract/asset/<string:asset_no>')
def asset_contract(asset_no):
    asset = XMAsset.get_by_asset_no(asset_no)
    if not asset or not asset.is_owner(g.user):
        abort(401)
    identity = Identity.get(asset.user_id)
    upper_amount = num2chn(asset.create_amount)
    product = XMFixedDuedayProduct.get(asset.product_id)
    if not product:
        abort(404)
    expect_rate = 100
    if product.product_type is XMFixedDuedayProduct.Type.classic:
        expect_rate = round_half_up((asset.annual_rate * product.frozen_days / 365 + 1) * 100, 4)
    return render_template(
        'savings/agreement_xinmi.html', asset=asset, identity=identity, expect_rate=expect_rate,
        product_name=product.name, product_frozen_days=product.frozen_days,
        upper_amount=upper_amount)


@bp.route('/product/<string:product_id>')
def purchase(product_id):
    cur_path = 'record'
    partner = Partner.xm
    agreement_url = url_for('savings.landing.agreement_xinmi')

    banks = iter_banks(g.user.id_)
    bankcards = g.xinmi_profile.bankcards.get_all()
    raw_product = XMFixedDuedayProduct.get(product_id) or abort(404)

    coupons = [c.to_dict() for c in g.coupon_manager.available_coupons
               if c.is_available_for_product(raw_product)]

    context = {'coupons': coupons, 'banks': banks, 'bankcards': bankcards, 'partner': partner,
               'product_type': 'regular', 'user_balance': g.firewood_flow.balance,
               'cur_path': cur_path, 'product': raw_product, 'agreement_url': agreement_url}
    return render_template('savings/order.html', **context)


@bp.route('/order/<int:order_id>/complete')
def order_complete(order_id):
    cur_path = 'savings'
    order = get_order(order_id)

    return render_template(
        'savings/complete_xinmi.html', order=order, cur_path=cur_path,
        is_new_savings_user=g.savings_manager.is_new_savings_user)
