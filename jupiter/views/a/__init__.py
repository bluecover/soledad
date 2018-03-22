# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, abort

from libs.shorten.url import ShortenUrl
from libs.logger.rsyslog import rsyslog


bp = Blueprint('a', __name__, url_prefix='/a')


def _send_click_log(code, url):
    rsyslog.send('%s\t%s' % (code, url), tag='shorten_url')


@bp.route('/<code>')
def a(code):
    url = ShortenUrl.get(code)
    if not url:
        abort(404)
    _send_click_log(code, url)
    return redirect(url)
