# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

import wtforms.validators

from core.models import errors
from core.models.utils.validator import validate_phone
from core.models.profile.bankcard import BankCard


class BankCardNumber(object):
    """Validates bankcard numbers with Luhn algorithm."""

    def __init__(self, message=None):
        self.message = message or '该银行卡号无效，请修改后重试'

    def __call__(self, form, field):
        message = field.gettext(self.message)
        try:
            BankCard.validate_card_number(field.data)
        except ValueError:
            raise wtforms.validators.ValidationError(message)


class MobilePhone(object):
    """Validates the mobile phone number in China."""

    def __init__(self, message=None):
        self.message = message or '该手机号无效，请修改后重试'

    def __call__(self, form, field):
        message = field.gettext(self.message)

        error = validate_phone(field.data)
        if error != errors.err_ok:
            raise wtforms.validators.ValidationError(message)
