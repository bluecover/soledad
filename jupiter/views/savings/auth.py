# coding: utf-8

from jupiter.views.profile.identity import IdentityBindingView
from ._blueprint import create_blueprint


bp = create_blueprint('auth', __name__, '/auth')

bp.add_url_rule('/channel/c02', view_func=IdentityBindingView.as_view(
    name='zhiwang',
    channel_endpoint='jauth.channel_zhiwang',
))

bp.add_url_rule('/channel/c03', view_func=IdentityBindingView.as_view(
    name='xinmi',
    channel_endpoint='jauth.channel_xm',
))
