# -*- coding: utf-8 -*-

import hashlib
import warnings
import decimal
import datetime
import base64

from solar.utils.randbytes import randbytes, randbytes2
from solar.db.utils import encode as _encode


__all__ = ['randbytes', 'randbytes2']


def _double_md5_pwd(password):
    # double md5 for password
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    return base64.b64encode(
        hashlib.md5(
            base64.b64encode(
                hashlib.md5(password).digest())).digest())


def pwd_hash(salt, password):
    if not password:
        return ''
    pwd = _double_md5_pwd(password)
    m = hashlib.md5(salt)
    m.update(pwd)
    return m.hexdigest()[:14]


def encode(value):
    warnings.warn(
        'Please use solar.db.utils.encode instead', DeprecationWarning)
    return _encode(value)


def escape(s, strict=False):
    '''Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.'''
    warnings.warn(
        'Please use markupsafe.escpae instead of core.models.utils.escape',
        DeprecationWarning)
    s = str(s)
    s = s.replace('&', '&amp;')  # Must be done first!
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    if strict:
        s = s.replace('`', '&#x60;')
        s = s.replace("'", '&#x27;')
        s = s.replace('/', '&#x2F;')
        s = s.replace('"', '&quot;')
    return s


def unescape(s, quote=False):
    warnings.warn(
        'Please use markupsafe.Markup("&gt;").unescape() instead of '
        'core.models.utils.unescape', DeprecationWarning)
    # safe unescape
    s = str(s)
    s = s.replace('&#x60;', '`')
    s = s.replace('&#x2F;', '/')
    if quote:
        s = s.replace('&#x27;', "'")
        s = s.replace('&quot;', '"')
    return s


def mako_escape(*args):
    '''
    mako  -> ${content}
    args  -> (u'content', )
    '''
    warnings.warn(
        'Do not use this. The mako template engine has built-in escape '
        'filter.', DeprecationWarning)
    if args:
        s = str(args[0]).encode('utf-8')
        return escape(s, strict=True)
    return ''


def dec_2_pct(dec, place=0):
    if not isinstance(dec, float):
        try:
            dec = float(dec)
        except ValueError:
            return
    if not isinstance(place, int):
        try:
            place = int(place)
        except ValueError:
            return
    _format = '%.' + str(place) + 'f%%'
    return _format % (dec * 100)


def datetime_2_str(dtime):
    return dtime.strftime('%Y%m%d %H:%M:%S')


def str_2_datetime(string):
    return datetime.datetime.strptime(string, '%Y%m%d %H:%M:%S')


def round_half_up(d, ndigits):
    exp = decimal.Decimal(str(1.0 / 10 ** ndigits))
    rounding = decimal.ROUND_HALF_UP
    return decimal.Decimal(str(d)).quantize(exp, rounding)


def datetime_range(start, stop, step=datetime.timedelta(days=1)):
    """
    >>> list(datetime_range(datetime.date(2015, 11, 1), datetime.date(2015, 11, 3)))
    [datetime.date(2015, 11, 1), datetime.date(2015, 11, 2)]
    >>> list(datetime_range(datetime.date(2015, 11, 3), datetime.date(2015, 11, 1)))
    []
    >>> list(datetime_range(datetime.date(2015, 11, 3), datetime.date(2015, 11, 1),
    ...                     datetime.timedelta(days=-1)))
    [datetime.date(2015, 11, 3), datetime.date(2015, 11, 2)]
    >>> list(datetime_range(None, None, datetime.timedelta()))
    Traceback (most recent call last):
        ...
    ValueError: step argument must not be zero
    """
    zero = datetime.timedelta()
    if step == zero:
        raise ValueError('step argument must not be zero')
    value = start
    while (value < stop and step > zero) or (value > stop and step < zero):
        yield value
        value += step


def hundred_rounding(d):
    return _num_rounding(d, digi=100)


def ten_thou_rounding(d):
    return _num_rounding(d, digi=10000)


def ten_rounding(d):
    return _num_rounding(d, digi=10)


def _num_rounding(d, digi=100):
    '''
    d    需要四舍五入的数字
    digi 需要四舍五入的位数，比如100, 10000
    '''
    d = int(d)
    h = d / digi
    l = d % digi
    if l >= (digi / 2):
        h += 1
    return h * digi


def get_sex_by_identity(identity):
    i = identity[-2]
    if int(i) % 2 == 0:
        return '女'
    return '男'


def get_age_by_identity(identity):
    born = identity[6:-4]
    born = datetime.datetime.strptime(born, '%Y%m%d')
    now = datetime.datetime.now()
    today = born.replace(year=now.year)

    birthday = born.replace(year=today.year)

    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


def calculate_age(born):
    today = datetime.date.today()
    try:
        birthday = born.replace(year=today.year)
    except ValueError:
        # raised when birth date is February 29 and the current year is not a
        # leap year
        birthday = born.replace(year=today.year, month=born.month + 1, day=1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


def coerce_to_unicode(text, encoding='utf-8'):
    if not isinstance(text, basestring):
        raise TypeError('must be string type')
    if not isinstance(text, unicode):
        text = text.decode(encoding)
    return text
