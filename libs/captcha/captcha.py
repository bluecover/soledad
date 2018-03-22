# -*- coding: utf-8 -*-
from __future__ import absolute_import

import cStringIO
import pkg_resources
import random
import string

from captcha.image import ImageCaptcha
from flask import current_app

from libs.cache import mc


_MC_CAPTCHA_KEY = 'captcha:%s'

FONT_PATH = pkg_resources.resource_filename(__name__, 'ae_AlArabiya.ttf')


class Captcha(object):

    def __init__(self, length=4, contain_numbers=True, contain_letters=False,
                 is_letter_upper_case=False, expire=60 * 5):
        self.caset = string.digits if contain_numbers else ''
        self.expire = expire if expire >= 60 else 60

        letter_set = ''
        if contain_letters:
            if is_letter_upper_case:
                letter_set = string.ascii_uppercase
            else:
                letter_set = string.ascii_lowercase
        self.caset += letter_set
        self.length = length

    def generate(self, secret):
        image_io, code = self._gen()
        mc.set(_MC_CAPTCHA_KEY % secret, code)
        mc.expire(_MC_CAPTCHA_KEY % secret, self.expire)
        return image_io

    def _gen(self):
        image = ImageCaptcha(fonts=[FONT_PATH])
        code = ''.join(random.choice(self.caset) for _ in range(self.length))
        output = cStringIO.StringIO()
        if current_app.testing:
            code = '6' * self.length
        image.write(code, output)
        return output, code

    @classmethod
    def get(cls, secret):
        return mc.get(_MC_CAPTCHA_KEY % secret)

    @classmethod
    def validate(cls, text, secret, delete=True):
        strs = cls.get(secret)
        if not strs:
            raise OutdatedCaptchaError()
        if text != strs:
            raise WrongCaptchaError()
        if delete:
            mc.delete(_MC_CAPTCHA_KEY % secret)


class CaptchaError(Exception):
    """The exception corresponding to captcha"""

    def __unicode__(self):
        return u'图形验证码校验错误'


class CaptchaSecretNotFoundError(CaptchaError):
    """Captcha secret is unfound"""

    def __unicode__(self):
        return u'业务会话已过期'


class WrongCaptchaError(CaptchaError):
    """The filled captcha is wrong"""

    def __unicode__(self):
        return u'图形验证码填写有误，请重新输入'


class OutdatedCaptchaError(CaptchaError):
    """The filled captcha is outdated"""

    def __unicode__(self):
        return u'图形验证码已过期'


digits_captcha = Captcha()
