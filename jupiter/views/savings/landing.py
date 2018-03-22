# -*- coding: utf-8 -*-

from operator import attrgetter

from more_itertools import first
from flask import g, url_for, redirect
from flask_mako import render_template

from core.models.plan.report import get_user_count
from core.models.hoard.zhiwang import ZhiwangProduct, ZhiwangAccount
from core.models.hoard.xinmi.product import XMFixedDuedayProduct
from core.models.hoarder.product import Product
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoard.stats import get_savings_amount
from core.models.hoard.profile import HoardProfile
from core.models.profile.identity import has_real_identity
from ._blueprint import create_blueprint

bp = create_blueprint('landing', __name__, for_anonymous=True)


@bp.route('/')
def index():
    if g.user and HoardProfile.get(g.user.id_):
        return redirect(url_for('savings.mine.index'))

    amount = get_savings_amount()
    user_count = get_user_count()
    xm_products = XMFixedDuedayProduct.get_all()
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = Product.get_products_by_vendor_id(vendor.id_)
    return render_template(
        'savings/index.html', amount=amount,
        user_count=user_count, xm_products=xm_products,
        sxb_products=sxb_products, cur_path='savings')


@bp.route('/activity')
@bp.route('/activity/')
def activity():
    return redirect(url_for('savings.mine.index'))


@bp.route('/agreement/c02')
def agreement_zhiwang():
    return render_template('savings/agreement_zhiwang.html', cur_path='savings')


@bp.route('/agreement/c03')
def agreement_xinmi():
    return render_template('savings/agreement_chunqi.html', cur_path='savings')


@bp.route('/entrust')
def entrust():
    return render_template('savings/entrust.html', cur_path='savings')


@bp.route('/risk')
def risk():
    return render_template('savings/risk.html', cur_path='savings')


@bp.route('/suixinzan')
def suixinzan():
    return render_template('savings/suixinzan.html', cur_path='savings')


@bp.route('/publicity')
def publicity():
    # 指旺活动产品
    products = [p for p in ZhiwangProduct.get_all()
                if p.product_type is ZhiwangProduct.Type.fangdaibao]
    products = sorted(products, key=attrgetter('final_due_date'))
    product = first((p for p in products if p.in_stock), None)
    can_quick_reg_zhiwang = None
    if g.user:
        zhiwang_account = ZhiwangAccount.get_by_local(g.user.id_)
        can_quick_reg_zhiwang = not zhiwang_account and has_real_identity(
            g.user)
    return render_template('savings/publicity.html', cur_path='savings', product=product,
                           can_quick_reg_zhiwang=can_quick_reg_zhiwang)
