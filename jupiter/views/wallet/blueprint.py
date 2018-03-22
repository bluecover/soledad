from __future__ import print_function, absolute_import, unicode_literals

from flask import Blueprint, redirect, url_for, request, g

from core.models.wallet.account import WalletAccount
from core.models.wallet.providers import zhongshan
from core.models.profile.bankcard import BankCardManager
from core.models.wallet._bankcard_binding import is_bound_bankcard


def create_blueprint(name, package_name, url_prefix='', login_required=False,
                     **kwargs):
    url_prefix = '/wallet/{0}'.format(url_prefix.lstrip('/')).rstrip('/')
    blueprint = Blueprint(name, package_name, url_prefix=url_prefix, **kwargs)

    @blueprint.before_request
    def prepare_profile():
        if not login_required:
            return
        if not g.user:
            return redirect(url_for('accounts.login.login', next=request.path))
        g.bankcards = BankCardManager(g.user.id_)
        g.bind_cards = [card for card in g.bankcards.get_all()
                        if is_bound_bankcard(card, zhongshan)]
        g.wallet_provider = zhongshan
        g.wallet_account = WalletAccount.get_or_add(g.user, g.wallet_provider)

    return blueprint
