# coding: utf-8

from flask import Blueprint
from flask_mako import render_template


bp = Blueprint('activity.four_million', __name__, url_prefix='/activity')


@bp.route('/400m')
def index():
    return render_template('activity/400m.html')
