# coding: utf-8

from datetime import datetime, timedelta

from flask import g, request, current_app, after_this_request

from core.models.consts import SESSION_EXPIRE_DAYS
from core.models.user.account import Account
from core.models.utils import randbytes2


def login_user(account, remember=True):
    g.user = Account.get(account.id_)
    if not g.user.has_valid_session():
        g.user.create_session()

    @after_this_request
    def set_cookie(response):
        if remember:
            expires = datetime.now() + timedelta(days=SESSION_EXPIRE_DAYS)
        else:
            expires = None
        response.set_cookie(
            key=current_app.config['SITE_SESSION_KEY'],
            value='%s:%s' % (g.user.id_, g.user.session_id),
            expires=expires, httponly=True)
        return response

    return g.user


def logout_user(kick_all=False):
    if g.get('user') and kick_all:
        g.user.clear_session()

    g.user = None

    @after_this_request
    def after_request(response):
        response.set_cookie(
            key=current_app.config['SITE_SESSION_KEY'], expires=0)
        return response


def authenticate_user():
    value = request.cookies.get(current_app.config['SITE_SESSION_KEY'])
    if value is None:
        return

    try:
        uid, token = value.split(':', 1)
    except ValueError:
        logout_user(kick_all=False)
        return

    account = Account.get(uid)
    if account and account.is_valid_session(token):
        return account
    else:
        logout_user(kick_all=False)
        return


_P3P_POLICY = ('CP="IDC DSP COR ADM DEVi TAIi PSA '
               'PSD IVAi IVDi CONi HIS OUR IND CNT"')
_BROWSER_COOKIE = 'bid'


def check_browser_cookie():
    browser_cookie = request.cookies.get(_BROWSER_COOKIE)
    if not browser_cookie:
        set_account_browser_cookie()
        request.original_browser_id = ''
    else:
        # FIXME (tonyseek) side effect
        request.browser_id = request.bid = browser_cookie
        request.original_browser_id = browser_cookie


def set_account_browser_cookie(browser_id=''):
    browser_id = browser_id or randbytes2(8)

    @after_this_request
    def set_cookie_and_header(response):
        response.set_cookie(
            key=_BROWSER_COOKIE,
            value=browser_id,
            expires=datetime.now() + timedelta(days=365))
        response.headers['P3P'] = _P3P_POLICY
        return response

    request.browser_id = request.bid = browser_id
