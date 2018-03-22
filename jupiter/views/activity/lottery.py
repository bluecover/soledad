# coding: utf-8

from flask import Blueprint, g, redirect, url_for, request
from flask_mako import render_template

from core.models.welfare import FirewoodWorkflow
from core.models.gift import UserLottery


bp = Blueprint('activity.lottery', __name__, url_prefix='/activity')


@bp.before_request
def initialize():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))
    g.firewood_flow = FirewoodWorkflow(g.user.id_)
    if not g.firewood_flow.account_uid:
        return redirect(url_for('profile.auth.supply', next=request.path))


@bp.route('/lottery')
def index():
    user = g.user
    user_lottery = UserLottery.get(user.id_)
    return render_template('activity/lottery/index.html', remain_num=user_lottery.remain_num)
