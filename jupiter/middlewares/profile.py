# coding: utf-8

"""
    在线性能调试
"""

import time
import cProfile

from flask import g, request, Blueprint


pr = cProfile.Profile()
bp = Blueprint('middlewares.profile', __name__)


def can_debug():
    return g.get('user') and request.args.get('debug', '') == 'guihua'


@bp.before_app_request
def begin():
    if can_debug():
        g._start_time = time.time()


@bp.after_app_request
def end(response):
    diff = None
    if can_debug():
        content_type = response.headers.get('content-type', '')
        if content_type == 'text/html; charset=utf-8':
            data = response.data
            g._end_time = time.time()
            diff = g._end_time - g._start_time
            data += ('<div class="debug">' + str(diff) + '</div>')
            response.data = data
            g._start_time = None
            g._end_time = None
    return response
