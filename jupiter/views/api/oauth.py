# coding: utf-8

"""
    Flask-OAuthlib Integration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module integrates those models with Flask-OAuthlib:

    =============================================== ==========================
     :class:`core.models.oauth.client.OAuthClient`   OAuth 2.0 Client
     :class:`core.models.oauth.scopes.OAuthScope`    OAuth 2.0 Scope
     :class:`core.models.oauth.grant.OAuthGrant`     OAuth 2.0 Grant Token
     :class:`core.models.oauth.token.OAuthToken`     OAuth 2.0 Bearer Token
    =============================================== ==========================
"""

from __future__ import absolute_import, unicode_literals

from flask import Blueprint, g, url_for, redirect, request, flash
from flask_mako import render_template

from jupiter.ext import oauth_provider
from libs.logger.rsyslog import rsyslog
from core.models.oauth import OAuthClient, OAuthGrant, OAuthToken, OAuthScope
from core.models.user.account import Account
from core.models.utils.validator import validate_phone, validate_email, errors


bp = Blueprint('api.oauth', __name__, url_prefix='/oauth')


@oauth_provider.clientgetter
def load_client(client_id):
    return OAuthClient.get_by_client_id(client_id)


@oauth_provider.grantgetter
def load_grant(client_id, code):
    return OAuthGrant.get_by_code(client_id, code)


@oauth_provider.grantsetter
def save_grant(client_id, code_response, request, *args, **kwargs):
    OAuthGrant.add(
        client_pk=request.client.id_,
        code=code_response['code'],
        redirect_uri=request.redirect_uri,
        scopes=request.scopes,
        user_id=g.user.id_)


@oauth_provider.tokengetter
def load_token(access_token=None, refresh_token=None):
    token = None
    if access_token:
        token = OAuthToken.get_by_access_token(access_token)
    if refresh_token:
        token = OAuthToken.get_by_refresh_token(refresh_token)
    if token and not token.is_frozen:
        return token


@oauth_provider.tokensetter
def save_token(token, request, *args, **kwargs):
    OAuthToken.add(
        client_pk=request.client.id_,
        user_id=request.user.id_,
        scopes=token['scope'].split(),
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        expires_in=token['expires_in'])


@oauth_provider.usergetter
def get_user(username, password, *args, **kwargs):
    rsyslog.send(u'login request, user id:%s, pass:%s' % (username, password), tag='apiv1')
    if errors.err_ok not in [
            validate_email(username), validate_phone(username)]:
        rsyslog.send(u'login validation error, user id:%s, pass:%s' % (username, password),
                     tag='apiv1')
        return
    account = Account.get_by_alias(username)
    account_id = account.id_ if account else 0
    rsyslog.send(u'login account info, user id:%s, account id:%s' % (username, account_id),
                 tag='apiv1')
    if not account:
        return
    if not account.is_normal_account():
        return
    if not account.verify_password(password):
        return
    return account


@bp.route('/authorize', methods=['GET', 'POST'])
@oauth_provider.authorize_handler
def authorize(**kwargs):
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.url))
    if request.method == 'GET':
        context = {
            'client': OAuthClient.get_by_client_id(kwargs['client_id']),
            'scopes': {OAuthScope(scope) for scope in kwargs['scopes']},
            'response_type': kwargs['response_type'],
            'redirect_uri': kwargs['redirect_uri'],
            'state': kwargs['state'],
        }
        return render_template('oauth/authorize.html', **context)
    return request.form.get('confirm') == 'yes'


@bp.route('/errors', methods=['GET'])
def authorize_errors():
    error_name = request.args['error']
    flash(error_name, 'error')
    return redirect(url_for('home.home'))


@bp.route('/token', methods=['POST'])
@oauth_provider.token_handler
def access_token(*args, **kwargs):
    return {}


@bp.route('/revoke', methods=['POST'])
@oauth_provider.revoke_handler
def revoke_token():
    return {}
