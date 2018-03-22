# -*- coding: utf-8 -*-

from flask import Blueprint, g, redirect, url_for, request

from core.models.hoard.account import YixinAccount
from core.models.hoard.zhiwang.account import ZhiwangAccount
from core.models.hoard.xinmi import XMAccount
from core.models.hoard.manager import SavingsManager


def create_blueprint(name, import_name, url_prefix='', for_anonymous=False):
    name = '.'.join(['savings', name])
    bp = Blueprint(name, __name__, url_prefix='/savings' + url_prefix)

    @bp.before_request
    def init():
        if not for_anonymous and not g.user:
            return redirect(url_for('accounts.login.login', next=request.path))
        g.yx_account = YixinAccount.get_by_local(g.user.id) if g.user else None
        g.zw_account = ZhiwangAccount.get_by_local(
            g.user.id) if g.user else None
        g.xm_account = XMAccount.get_by_local(g.user.id) if g.user else None
        g.savings_manager = SavingsManager(g.user.id_) if g.user else None
        # 用户是否被邀请，并且首次攒钱
    return bp
