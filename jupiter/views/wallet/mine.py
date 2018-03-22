from __future__ import print_function, absolute_import, unicode_literals

from flask import g
from flask_mako import render_template

from core.models.wallet import PublicDashboard, UserDashboard
from core.models.wallet.profile import WalletProfile
from core.models.wallet.transaction import WalletTransaction
from jupiter.views.profile.identity import IdentityBindingView
from .blueprint import create_blueprint


bp = create_blueprint('wallet.mine', __name__, login_required=True)
bp.add_url_rule('/auth', view_func=IdentityBindingView.as_view(name=b'auth'))


@bp.before_request
def initialize_profile():
    # disables the landing page
    g.wallet_profile = WalletProfile.add(g.user.id_)


@bp.route('/mine')
def index():
    dashboard = PublicDashboard.today()
    profile = UserDashboard.today(g.wallet_account)
    transaction_ids = WalletTransaction.get_ids_by_account(
        g.wallet_account.id_)
    transactions = WalletTransaction.get_multi(transaction_ids[:5])
    return render_template(
        'wallet/mine.html', dashboard=dashboard, profile=profile,
        transactions=transactions, total_transaction=len(transaction_ids))
