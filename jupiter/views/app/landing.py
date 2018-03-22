# coding: utf-8

from flask import Blueprint
from flask_mako import render_template


bp = Blueprint('app.landing', __name__)


@bp.route('/app')
def index():
    return render_template('app/app_download.html')
