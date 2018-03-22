# coding: utf-8

from flask import request, g, after_this_request, Blueprint

from core.models.user.account import Account
from jupiter.ext import sentry
from jupiter.views.accounts.utils.session import authenticate_user


bp = Blueprint('middlewares.authenticate_user', __name__)


@bp.before_app_request
def authenticate_account():
    """session 认证."""
    if not request.endpoint or request.endpoint.startswith('api'):
        return

    account = authenticate_user()
    if account:
        g.user = Account.get(account.id_)
        sentry.user_context({
            'id': g.user.id_,
            'email': g.user.email,
            'mobile': g.user.display_mobile,
            'via': 'cookie'})
    else:
        g.user = None

    @after_this_request
    def report_user_via_headers(response):
        if g.user:
            response.headers['X-UserID'] = '%s@guihua.com' % g.user.id_
        else:
            response.headers['X-UserID'] = request.browser_id
        return response
