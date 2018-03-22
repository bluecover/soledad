from __future__ import absolute_import

from functools import update_wrapper

from flask import session, request, g

from jupiter.ext import oauth_provider
from core.models.oauth import OAuthScope


class HybridView(object):
    """The webview-embed page for mobile apps."""

    def __init__(self, view_func, scopes):
        self.view_func = view_func
        self.scopes = [OAuthScope(scope).value for scope in scopes]
        self.require_oauth = oauth_provider.require_oauth(*self.scopes)

    def get_fresh_bearer_token(self):
        token = request.headers.get('Authorization', u'')
        if not token.startswith(u'Bearer '):
            return
        return token[7:].strip()

    def get_saved_bearer_token(self):
        token = session.get('bearer', u'').strip()
        if not token:
            return
        request.headers.environ['HTTP_AUTHORIZATION'] = u'Bearer %s' % token
        return token

    def save_bearer_token(self, token):
        session['bearer'] = token

    def authorize(self):
        token = self.get_fresh_bearer_token()
        is_fresh_token = True
        if not token:
            token = self.get_saved_bearer_token()
            is_fresh_token = False

        # empty token and invalid token will tigger 401 here
        self.require_oauth(lambda: None)()

        if is_fresh_token:
            self.save_bearer_token(token)

    def __call__(self, *args, **kwargs):
        self.authorize()
        g.user = request.oauth.user
        return self.view_func(*args, **kwargs)


def hybrid_view(scopes):
    """The decorator to turn a common view into hybrid UI of mobile apps."""
    def decorator(wrapped):
        wrapper = HybridView(wrapped, scopes)
        return update_wrapper(wrapper, wrapped)
    return decorator
