# -*- coding: utf-8 -*-

import re

from zhon.hanzi import characters as zh_han_chars

from core.models import errors
from core.models.consts import MIN_PASSWD_LEN


_EMAIL_RE = re.compile(
    r'^[_\.0-9a-zA-Z+-]+@([0-9a-zA-Z]+[0-9a-zA-Z-]*\.)+[a-zA-Z]{2,4}$')

_PASSWORD_RE = re.compile(
    r'^[a-zA-Z0-9\~\)\!\$\%\*\(\_\+\-\=\{\}\[\]\|\:\;\<\>\,\.\/\@\#\^\&\"\'\`\?]*$')

_INPUT_RE = re.compile(r"^[A-Za-z0-9]+$")


def not_validate(**kwargs):
    return errors.err_ok


def validate_han(value, least, most):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    if re.match(u'^[%s]{%s,%s}$' % (zh_han_chars, least, most), value):
        return errors.err_ok
    return errors.err_invalid_validate


def validate_xss_input(value, filter_chinese=True, **kwargs):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    value = str(value)
    if not value:
        return errors.err_ok
    if filter_chinese:
        if not _INPUT_RE.match(value):
            return errors.err_input_is_xss
    _spcs = '\ '.replace(' ', '')
    words = ['<', '>', 'script', 'alert', '..', '/', '../..',
             '=', ''', ''', '(', ')', '-', _spcs, '0x', 'svg',
             'object', ]
    for w in words:
        if w in value:
            return errors.err_input_is_xss
    return errors.err_ok


def validate_values_in(value, check_values, **kwargs):
    if not isinstance(check_values, list):
        raise Exception('default_values should be list')
    if value in check_values:
        return errors.err_ok
    return errors.err_invalid_default_values


def validate_values_range(value, check_values, allow_zero=False,
                          **kwargs):
    _min, _max = check_values
    try:
        value = int(value)
    except:
        return errors.err_invalid_range_values
    if allow_zero and value == 0:
        return errors.err_ok
    if value < _min or value > _max:
        return errors.err_invalid_range_values
    return errors.err_ok


def validate_values_range_allow_zero(value, check_values, **kwargs):
    return validate_values_range(value, check_values, allow_zero=True)


def validate_email(value, **kwargs):
    email = value
    if not email or not len(email) >= 6 or not _EMAIL_RE.match(email):
        return errors.err_invalid_email
    return errors.err_ok


def validate_phone(value, **kwargs):
    phone_number = value
    if not phone_number:
        return errors.err_invalid_range_values
    p = re.compile(ur'^1[3|4|5|8|7]\d{9}$')
    m = p.match(phone_number)
    if m:
        return errors.err_ok
    return errors.err_invalid_phone_number


def validate_password(value, **kwargs):
    password = value
    if not password:
        return errors.err_no_password
    elif len(password) < MIN_PASSWD_LEN:
        return errors.err_password_too_short
    elif not _PASSWORD_RE.match(password):
        return errors.err_invalid_validate
    return errors.err_ok


def validate_value_len(value, max_size):
    if not value:
        return errors.err_input_value_empty
    if len(value) > max_size:
        return errors.err_value_too_long
    return errors.err_ok


ID_RE = '(^\d{15}$)|(^\d{17}([0-9]|x)$)'


def validate_identity_bits(identity):
    s = map(int, identity[:-1])
    a = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    b = sum(map(lambda x: x[0] * x[1], zip(a, s)))
    c = b % 11
    d = ['1', '0', 'x', '9', '8', '7', '6', '5', '4', '3', '2']
    if str(identity[-1]) != d[c]:
        return errors.err_invalid_data_format
    return errors.err_ok


def validate_identity(identity):
    if not identity:
        return errors.err_input_value_empty
    if isinstance(identity, unicode):
        try:
            identity = identity.encode('ascii')
        except UnicodeEncodeError:
            return errors.err_invalid_data_format
    identity = str(identity).lower()
    if not re.match(ID_RE, identity):
        return errors.err_invalid_data_format
    return validate_identity_bits(identity)


def is_include_chinese(origin_value):
    if isinstance(origin_value, bytes):
        origin_value = origin_value.decode('utf-8')
    for o in origin_value:
        if u'\u4e00' <= o <= u'\u9fff':
            return True
    return False


class AnnotatedValidationMixin(object):
    @property
    def failure(self):
        return [{'field': k, 'message': v[0]} for k, v in self.errors.items() if v]
