# -*- coding: utf-8 -*-
from flask import session

from libs.captcha import Captcha
from libs.captcha.captcha import CaptchaSecretNotFoundError


def validate_captcha_text(captcha, delete=True):
    secret = session.get('cap_secret')
    if not secret:
        raise CaptchaSecretNotFoundError()
    Captcha.validate(captcha, secret, delete)
