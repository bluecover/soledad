# -*- coding: utf-8 -*-

from flask import Blueprint, send_file, session

from libs.captcha import digits_captcha
from libs.utils.randbytes import randbytes2

bp = Blueprint('captcha', __name__, url_prefix='/captcha')


@bp.route('/get')
def get():
    if 'cap_secret' not in session:
        session['cap_secret'] = randbytes2(6)
    image_io = digits_captcha.generate(session['cap_secret'])
    image_io.seek(0)
    return send_file(image_io, mimetype='image/png')
