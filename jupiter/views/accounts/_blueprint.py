from flask import Blueprint


def create_blueprint(name, import_name, url_prefix='', **kwargs):
    name = '.'.join(['accounts', name])
    bp = Blueprint(name, import_name, url_prefix='/accounts' + url_prefix)
    return bp
