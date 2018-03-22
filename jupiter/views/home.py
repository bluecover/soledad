# coding: utf-8
from flask import Blueprint, g, redirect
from flask_mako import render_template

from core.models.hoard.stats import get_savings_amount
from core.models.plan.report import get_user_count
from core.models.wallet.transaction import WalletTransaction

bp = Blueprint('home', __name__)


@bp.route('/')
def home():
    user_count = get_user_count()
    investment_sum_amount = get_savings_amount() + \
        WalletTransaction.sum_amount(WalletTransaction.Type.purchase)

    if g.user:
        return redirect('/mine/')

    return render_template('index/index.html', user_count=user_count,
                           investment_sum_amount=investment_sum_amount)


@bp.route('/colors')
def colors():
    return render_template('colors.html', **locals())


@bp.route('/ui')
def ui():
    return render_template('ui.html', **locals())
