# coding: utf-8

"""
    API Schema Fields
    ~~~~~~~~~~~~~~~~~

    This module includes a numbers of fields which is compatible with schema
    classes defined in :class:`marshmallow.Schema`.
"""

from __future__ import absolute_import, unicode_literals

from marshmallow import ValidationError
from marshmallow.fields import ValidatedField, DateTime
from gb2260 import Division
from dateutil.tz import tzlocal

from core.models.utils.validator import (
    validate_phone, validate_password, validate_han, validate_identity)
from core.models.errors import (
    err_ok, err_invalid_phone_number, err_password_too_short, err_invalid_validate)
from core.models.bank import bank_collection
from core.models.profile.bankcard import BankCard


class MobilePhoneField(ValidatedField):
    def __init__(self, *args, **kwargs):
        super(MobilePhoneField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        value = value.strip()
        result = validate_phone(value)
        if result == err_invalid_phone_number:
            raise ValidationError('该手机号无效，请修改后重试')
        if result != err_ok:
            raise ValueError(result)
        return value


class PasswordField(ValidatedField):
    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        value = value.strip()
        result = validate_password(value)
        if result == err_password_too_short:
            raise ValidationError('密码长度至少为6个字符，请修改后重试')
        if result == err_invalid_validate:
            raise ValidationError('密码包含非法字符！')
        if result != err_ok:
            raise ValueError(result)
        return value


class PersonNameField(ValidatedField):

    def __init__(self, *args, **kwargs):
        super(PersonNameField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        value = value.strip()
        result = validate_han(value, 2, 20)
        if result != err_ok:
            raise ValidationError('请输入正确的姓名')
        return value


class PersonRicnField(ValidatedField):

    def __init__(self, *args, **kwargs):
        super(PersonRicnField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        value = value.strip()
        result = validate_identity(value)
        if result != err_ok:
            raise ValidationError('该身份证号无效，请修改后重试')
        return value


class BankCardNumberField(ValidatedField):

    def __init__(self, *args, **kwargs):
        super(BankCardNumberField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        try:
            BankCard.validate_card_number(value)
        except ValueError:
            raise ValidationError(u'该银行卡号无效，请修改后重试')
        return value


class BankIDField(ValidatedField):

    def __init__(self, *args, **kwargs):
        super(BankIDField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        bank = bank_collection.get_bank(value)
        if not bank:
            raise ValidationError('请选择正确的开户银行')


class DivisionIDField(ValidatedField):

    def __init__(self, *args, **kwargs):
        super(DivisionIDField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        try:
            division = Division.search(value)
        except ValueError:
            raise ValidationError('请选择正确的银行卡开户城市')
        if not division.is_prefecture:
            raise ValidationError(u'请选择正确的银行卡开户城市')


class RedeemCodeField(ValidatedField):
    def __init__(self, *args, **kwargs):
        super(RedeemCodeField, self).__init__(*args, **kwargs)
        self.validators.insert(0, self._validated)

    def _validated(self, value):
        value = value.strip()
        if not value:
            raise ValidationError(u'请输入兑换码')
        return value


class LocalDateTimeField(DateTime):

    localtime = True

    def _serialize(self, value, *args, **kwargs):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=tzlocal())
        return super(LocalDateTimeField, self)._serialize(
            value, *args, **kwargs)
