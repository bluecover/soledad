# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask_mako import render_template


bp = Blueprint('ins.landing', __name__)


@bp.route('/ins/')
def index():
    if request.user_agent.is_mobile:
        return render_template('ins/index_mobile.html', **locals())
    else:
        return render_template('ins/index.html', **locals())


@bp.route('/ins/rules')
def rules():
    return render_template('/ins/rules.html')
