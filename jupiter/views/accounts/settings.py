# coding: utf-8

from flask import redirect, g, url_for, request
from flask_mako import render_template

from core.models.profile.identity import Identity
from core.models.security.twofactor import TwoFactor, get_twofactor_apps
from ._blueprint import create_blueprint


bp = create_blueprint('settings', __name__)


@bp.before_request
def initialize_user():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))


@bp.before_request
def initialize_twofactor():
    g.twofactor_apps = get_twofactor_apps(request.user_agent)
    g.twofactor = TwoFactor.get(g.user.id_)


@bp.route('/settings')
def settings():
    mobile = g.user.display_mobile
    identity = Identity.get(g.user.id_)
    return render_template(
        'accounts/settings.html', mobile=mobile, identity=identity)
