# -*- coding: utf-8 -*-

from flask import Blueprint


def create_blueprint(name, import_name, url_prefix='', for_anonymous=False):
    name = '.'.join(['services', name])
    bp = Blueprint(name, __name__, url_prefix='/services' + url_prefix)
    return bp
