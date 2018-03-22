# -*- coding: utf-8 -*-

from flask import Blueprint


def create_blueprint(name, import_name, **kwargs):
    kwargs.setdefault('url_prefix', '/ins/children')
    bp = Blueprint('ins.%s' % name, import_name, **kwargs)
    return bp
