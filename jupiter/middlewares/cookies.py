# coding: utf-8

from datetime import datetime, timedelta

from flask import request, Blueprint


bp = Blueprint('middlewares.cookies', __name__)
cookie_version = '3'


@bp.after_app_request
def invalidate_old_cookies(response):
    """废弃写在 .guihua.com 根域下的所有 cookie.

    历史上我们曾用共享 cookie 的方式来做后台鉴权, 废弃这种做法后, 我们需要清理
    用户浏览器中剩下的 cookie garbage.
    """
    if not request.endpoint or request.endpoint.startswith('api'):
        return response

    if request.cookies.get('v') == cookie_version:
        return response

    if request.host.startswith('www.'):
        bare_domain = '.' + request.host[4:].lstrip('.')
    else:
        return response

    for key in request.cookies:
        if key.lower().startswith('hm'):
            continue  # skips baidu tracked cookies
        response.set_cookie(key, expires=0, domain=bare_domain)
        response.set_cookie(key, expires=0, domain='.' + request.host)

    next_year = datetime.now() + timedelta(days=365)
    response.set_cookie('v', cookie_version, expires=next_year, httponly=True)
    return response
