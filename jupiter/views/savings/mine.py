# coding: utf-8

from flask import g
from flask_mako import render_template

from core.models.welfare import CouponManager
from core.models.hoard import HoardProfile, SavingsManager
from core.models.hoard.common import ProfitPeriod
from core.models.hoard.zhiwang import ZhiwangAccount, ZhiwangProduct
from core.models.hoard.xinmi import XMFixedDuedayProduct, XMAccount
from core.models.profile.identity import has_real_identity
from core.models.utils.switch import zhiwang_fdb_product_on_switch
from ._blueprint import create_blueprint

bp = create_blueprint('mine', __name__, url_prefix='/mine')


@bp.before_request
def initialize_profile():
    # disables the landing page
    g.hoard_profile = HoardProfile.add(g.user.id_)


@bp.route('/')
def index():
    cur_path = 'savings'

    # 个人信息
    saving_manager = SavingsManager(g.user.id_)
    coupon_manager = CouponManager(g.user.id_)

    # 礼券
    coupons = coupon_manager.deduplicated_available_coupons

    # 指旺产品
    fdb_products, cls_products, ncm_products = [], [], []
    for p in ZhiwangProduct.get_all():
        if p.product_type is ZhiwangProduct.Type.fangdaibao:
            fdb_products.append(p)
        elif p.product_type is ZhiwangProduct.Type.classic:
            # 指旺暂不显示中长期产品
            if p.profit_period['min'] not in (
                    ProfitPeriod(90, 'day'),   # 临时决定不在Web上显示90天产品
                    ProfitPeriod(180, 'day'), ProfitPeriod(270, 'day'),
                    ProfitPeriod(365, 'day')):
                cls_products.append(p)

    # 2016年五月一日下线指旺自选到期日产品
    if not zhiwang_fdb_product_on_switch.is_enabled:
        fdb_products = []

    xm_products = XMFixedDuedayProduct.get_all()

    has_identity = has_real_identity(g.user)
    # 合作方授权(检查是否需要验证(尝试自动注册)指旺账号
    zhiwang_account = ZhiwangAccount.get_by_local(g.user.id_)
    can_quick_reg_zhiwang = has_identity and not zhiwang_account

    # 合作方授权(检查是否需要验证(尝试自动注册)新米账号
    xm_account = XMAccount.get_by_local(g.user.id_)
    can_quick_reg_xm = has_identity and not xm_account

    context = {'cur_path': cur_path,
               'coupons': coupons,
               'ncm_products': ncm_products,
               'fdb_products': fdb_products,
               'cls_products': cls_products,
               'xm_products': xm_products,
               'saving_manager': saving_manager,
               'plan_amount': g.hoard_profile.plan_amount,
               'can_quick_reg_xm': can_quick_reg_xm,
               'can_quick_reg_zhiwang': can_quick_reg_zhiwang}
    return render_template('savings/mine.html', **context)
