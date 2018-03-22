# coding: utf-8

from functools import partial

import arrow

unicode_type = partial(str.decode, encoding='utf-8')
arrow_type = arrow.get


def date_type(t):
    return arrow.get(t).date() if t else None
