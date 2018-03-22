from __future__ import print_function, absolute_import, unicode_literals

from flask import Blueprint, g, redirect, url_for
from flask_mako import render_template

from core.models.wallet import PublicDashboard
from core.models.wallet.profile import WalletProfile


bp = Blueprint('wallet.landing', __name__, url_prefix='/wallet')


@bp.route('/')
def index():
    if g.user and WalletProfile.get(g.user.id_):
        return redirect(url_for('wallet.mine.index'))
    else:
        dashboard = PublicDashboard.today()
        return render_template('wallet/index.html', dashboard=dashboard)


@bp.route('/agreement')
def agreement():
    return render_template('wallet/agreement.html')


@bp.route('/agreement/ms')
def agreement_ms():
    return render_template('wallet/agreement_ms.html')
