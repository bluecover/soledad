# coding: utf-8

from flask import Blueprint
from flask_mako import render_template


bp = Blueprint('activity.cake', __name__, url_prefix='/activity')


@bp.route('/cake')
def index():
    return render_template('activity/cake.html')
