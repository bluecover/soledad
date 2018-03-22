# -*- coding: utf-8 -*-

'''
    为整个网站增加CSP安全验证
    http://www.couchbase.com/couchbase-server/overview
'''

from flask import Blueprint, current_app


bp = Blueprint('middlewares.csp', __name__)


CSP_HEADERS = ['X-Content-Security-Policy',
               'Content-Security-Policy',
               'X-Webkit-CSP']

RULES = ('default-src *; '
         'script-src *.guihua.com hm.baidu.com '
         "*.google-analytics.com 'unsafe-eval'; "
         'object-src *.guihua.com; '
         "style-src 'self' 'unsafe-inline'; "
         "img-src 'self' *.guihua.com "
         'hm.baidu.com dn-ghimg.qbox.me '
         '*.google-analytics.com data:;'
         "media-src 'none';")

HEADERS = [('X-XSS-Protection', '1'),
           ('X-Frame-Options', 'deny'),
           ('X-Content-Type-Options', 'nosniff'), ]


@bp.after_app_request
def add_csp_response(response):
    '''
    本地绕过了这个验证
    线上需要这个验证
    '''
    # add for develop mode
    for header, rule in HEADERS:
        response.headers.add(header, rule)
    return response
    if current_app.debug:
        return response
    rules = RULES
    for header in CSP_HEADERS:
        response.headers.add(header, rules)
    return response
