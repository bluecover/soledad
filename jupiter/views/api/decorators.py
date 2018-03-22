# coding: utf-8

"""
    Decorators of API Views
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module controls the permission of view accessing.
"""

from __future__ import absolute_import, unicode_literals

from functools import update_wrapper

from flask import request, jsonify, current_app, abort
from werkzeug.security import safe_str_cmp

from core.models.oauth import OAuthClient, OAuthScope
from jupiter.ext import oauth_provider


def require_credentials(wrapped):
    """A decorator to restrict views to be accessible with client credentials.

    The API caller must have ``user_info`` in its scopes.

    This is usually used in anonymous API.
    """
    def wrapper(*args, **kwargs):
        client_id = request.headers.get('X-Client-ID', '')
        client_secret = request.headers.get('X-Client-Secret', '')

        if not client_id or not client_secret:
            return jsonify(error='missing_token'), 401

        client = OAuthClient.get_by_client_id(client_id)
        if not client or not safe_str_cmp(client_secret, client.client_secret):
            return jsonify(error='invalid_token'), 403

        if OAuthScope.user_info not in client.allowed_scopes:
            return jsonify(error='invalid_scope'), 403

        request.oauth_client = client
        return wrapped(*args, **kwargs)

    return update_wrapper(wrapper, wrapped)


def require_oauth(scopes):
    """A decorator to restrict views to be accessible with authorized user."""
    scopes = [OAuthScope(scope).value for scope in scopes]
    decorator = oauth_provider.require_oauth(*scopes)

    def secondary_decorator(wrapped):
        def wrapper(*args, **kwargs):
            if current_app.debug:
                # Prevents dangerous usage
                if any([
                    ('X-Client-ID' in request.headers),
                    ('X-Client-Secret' in request.headers),
                    ('token' in request.values),
                ]):
                    abort(400, u'The client credentials should be excluded '
                               u'from this kind of request')
            return decorator(wrapped)(*args, **kwargs)
        return update_wrapper(wrapper, wrapped)

    return secondary_decorator


def anonymous_oauth(scopes):
    scopes = [OAuthScope(scope).value for scope in scopes]
    decorator = oauth_provider.require_oauth(*scopes)

    def secondary_decorator(wrapped):
        def wrapper(*args, **kwargs):
            client_id = request.headers.get('X-Client-ID', '')
            client_secret = request.headers.get('X-Client-Secret', '')
            token = request.headers.get('Authorization', '')
            if not token:
                if not client_id or not client_secret:
                    return jsonify(error='missing_token'), 401

                client = OAuthClient.get_by_client_id(client_id)
                if not client or not safe_str_cmp(client_secret, client.client_secret):
                    return jsonify(error='invalid_token'), 403

                if OAuthScope.basic not in client.allowed_scopes:
                    return jsonify(error='invalid_scope'), 403

                request.oauth_client = client
                return wrapped(*args, **kwargs)
            return decorator(wrapped)(*args, **kwargs)

        return update_wrapper(wrapper, wrapped)

    return secondary_decorator
