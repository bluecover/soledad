# coding: utf-8

from operator import itemgetter

from gb2260 import Division
from gb2260.data import data

from libs.cache import cache


__all__ = ['get_division', 'get_provinces', 'get_children']

excluded_division_codes = frozenset([
    u'810000',  # 香港特别行政区
    u'820000',  # 澳门特别行政区
    u'710000',  # 台湾省
])


def all_division(year=None):
    for code in data.get(year, []):
        if unicode(code) in excluded_division_codes:
            continue  # restricted to China Mainland
        yield Division.get(code, year)


def is_child_of(left, right):
    if right.is_province:
        prefix = unicode(right.code)[:2]
        addition = left.is_prefecture
    elif right.is_prefecture:
        prefix = unicode(right.code)[:4]
        addition = left.is_county
    else:
        raise ValueError('right should not be county')
    return all([
        unicode(left.code).startswith(prefix),
        left.code != right.code,
        addition,
    ])


def get_division(code, year=None):
    try:
        return Division.get(code, year)
    except ValueError:
        return


@cache('GB2260:provinces:{year}:v2')
def get_provinces(year):
    result = [{'code': d.code, 'name': d.name, 'revision': d.year}
              for d in all_division(year) if d.is_province]
    return sorted(result, key=itemgetter('code'))


@cache('GB2260:{parent.code}-{parent.year}:children:v2')
def get_children(parent):
    result = [{'code': d.code, 'name': d.name, 'revision': d.year}
              for d in all_division(parent.year) if is_child_of(d, parent)]
    return sorted(result, key=itemgetter('code'))
