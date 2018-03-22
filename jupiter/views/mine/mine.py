# coding: utf-8

from flask import g
from flask_mako import render_template

from core.models.plan.report import Report, cal_intermediate_data
from core.models.plan.consts import REPORT_STATUS, FORMULA_VER
from core.models.hoard.manager import SavingsManager
from core.models.hoard.zhiwang import ZhiwangProduct
from core.models.wallet import PublicDashboard, UserDashboard
from core.models.wallet.account import WalletAccount
from core.models.wallet.transaction import WalletTransaction
from core.models.wallet.providers import zhongshan
from core.models.hoard.xinmi.product import XMFixedDuedayProduct
from core.models.hoarder.product import Product
from core.models.hoarder.vendor import Vendor, Provider
from ._blueprint import create_blueprint, regen_log


bp = create_blueprint('mine', __name__)


@bp.route('/')
def mine():
    # 攒钱助手
    savings_manager = SavingsManager(g.user.id_)
    savings_products = ZhiwangProduct.get_all()

    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = Product.get_products_by_vendor_id(vendor.id_)
    xm_products = XMFixedDuedayProduct.get_all()

    # 零钱包
    wallet_dashboard = PublicDashboard.today()
    wallet_account = WalletAccount.get_by_local_account(g.user, zhongshan)
    if wallet_account:
        wallet_profile = UserDashboard.today(wallet_account)
        wallet_has_transaction = bool(WalletTransaction.get_ids_by_account(
            wallet_account.id_))
    else:
        wallet_profile = None
        wallet_has_transaction = False

    # 规划书
    report = Report.get_latest_by_plan_id(g.plan.id) if g.plan else None

    if not (report and report.status >= REPORT_STATUS.interdata):
        return render_template('/mine/center_unplanned.html', **locals())

    if int(report.formula_ver) < int(FORMULA_VER):
        regen_log(report, 'start regenerate inter data')
        cal_intermediate_data(report, force=True, log=regen_log)
        report.update_formula_ver(FORMULA_VER)
        regen_log(
            report, 'success regenerate inter data FV:%s' % report.formula_ver)

    inter_data = report.inter_data
    locals().update(inter_data)

    cur_path = 'center'
    return render_template('/mine/center.html', **locals())
