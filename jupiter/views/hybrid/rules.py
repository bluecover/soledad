# coding: utf-8

from __future__ import absolute_import

from flask import abort
from flask_mako import render_template

from jupiter.utils.hybrid import hybrid_view
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoarder.product import Product
from .blueprint import create_blueprint

bp = create_blueprint('rules', __name__, url_prefix='/hybrid/rules')


@bp.route('/sxb/app', methods=['GET'])
@hybrid_view(['savings_w'])
def sxb_withdraw():
    vendor = Vendor.get_by_name(Provider.sxb)
    products = Product.get_products_by_vendor_id(vendor_id=vendor.id_)
    # 对随心宝产品默认取第一款上线产品为数据来源（只会上线一款随心宝产品）
    for p in products:
        if p.is_on_sale:
            break
    if not p:
        abort(403, u'产品已下线，请稍后再试')
    max_free_redeem_times = 5
    total_buy_amount = p.total_buy_amount
    min_redeem_amount = p.min_redeem_amount
    day_redeem_amount = p.day_redeem_amount
    return render_template('wallet/sxb_withdraw_rule.html', **locals())
