# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from flask import Blueprint

from jupiter.views.profile.identity import IdentityBindingView


bp = Blueprint('profile.auth', __name__, url_prefix='/profile')


bp.add_url_rule('/auth', view_func=IdentityBindingView.as_view(
    name=b'supply',
    subtitle='由于升级了账户安全体系，请重新验证您的身份信息',
))
