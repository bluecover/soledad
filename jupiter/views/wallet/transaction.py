from __future__ import print_function, absolute_import, unicode_literals

from datetime import datetime

from flask import g, redirect, url_for, request
from flask_mako import render_template

from core.models.wallet import UserDashboard
from core.models.wallet.utils import get_value_date
from core.models.bank import bank_collection
from core.models.profile.identity import has_real_identity
from .blueprint import create_blueprint


bp = create_blueprint('wallet.transaction', __name__, login_required=True)


@bp.before_request
def check_identity():
    if not has_real_identity(g.user):
        return redirect(url_for('wallet.mine.auth', next=request.path))


@bp.before_request
def assign_banks():
    g.banks = [b for b in bank_collection.banks
               if g.wallet_provider.bank_partner in b.available_in]


@bp.before_request
def assign_profile():
    g.wallet_profile = UserDashboard.today(g.wallet_account)


@bp.route('/deposit')
def deposit():
    value_date = get_value_date(datetime.now())
    return render_template(
        'wallet/order.html', order_type='deposit', value_date=value_date)


@bp.route('/withdraw')
def withdraw():
    return render_template('wallet/order.html', order_type='withdraw')
