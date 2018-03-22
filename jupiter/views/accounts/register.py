# coding: utf-8

from flask import request, url_for
from flask_mako import render_template

from ._blueprint import create_blueprint


bp = create_blueprint('register', __name__)


@bp.route('/register')
def register():
    redirect_url = request.args.get('next')
    dcm = request.args.get('dcm')
    dcs = request.args.get('dcs')
    if not redirect_url:
        redirect_url = url_for('mine.mine.mine')
    return render_template(
            'accounts/login_and_register.html',
            redirect_url=redirect_url, dcm=dcm, dcs=dcs)
