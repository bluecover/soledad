# coding: utf-8

from flask import Blueprint
from werkzeug.wrappers import Response

from libs.cache import mc

bp = Blueprint('webtest', __name__, url_prefix='/webtests')


@bp.route('/images/<key>')
def images(key):
    v = mc.get(key)
    r = Response(v, mimetype='image/jpeg')
    return r
