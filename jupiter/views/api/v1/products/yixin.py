# coding: utf-8

from flask import abort

from jupiter.views.api.decorators import require_oauth
from jupiter.views.api.consts import VERSION_TOO_LOW
from ..savings import bp


@bp.route('/yixin/auth', methods=['POST'])
@require_oauth(['savings_w'])
def yixin_auth():
    """[已下线] 绑定宜人贷账户.

    :status 410: Gone
    """
    abort(410, VERSION_TOO_LOW)


@bp.route('/yixin/auth/verify', methods=['POST'])
@require_oauth(['savings_w'])
def yixin_auth_verify():
    """[已下线] 通过跳转宜人贷登录页面完成账户绑定.

    :status 410: Gone
    """
    abort(410, VERSION_TOO_LOW)
