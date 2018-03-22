# coding: utf-8

from __future__ import print_function, absolute_import

import datetime
import calendar


__all__ = ['get_effect_date']


close_weekday = frozenset([calendar.SATURDAY, calendar.SUNDAY])

# TODO 这个日历应该被拆分成一个独立 service 并带后台编辑功能
# 所有元组都是遵守基本法的左闭右开区间
national_holiday_ranges = [
    # 元旦（以下为2016年）
    (datetime.date(2016, 1, 1), datetime.date(2016, 1, 4)),
    # 春节
    (datetime.date(2016, 2, 7), datetime.date(2016, 2, 15)),
    # 清明节
    (datetime.date(2016, 4, 2), datetime.date(2016, 4, 5)),
    # 劳动节
    (datetime.date(2016, 4, 30), datetime.date(2016, 5, 3)),
    # 端午节
    (datetime.date(2016, 6, 9), datetime.date(2016, 6, 13)),
    # 中秋节
    (datetime.date(2016, 9, 15), datetime.date(2016, 9, 19)),
    # 国庆节
    (datetime.date(2016, 10, 1), datetime.date(2016, 10, 10)),
]


def get_effect_date(origin_datetime):
    """从给定时间计算出有效日期(起息日), 包含了法定节假日等非交易日顺延规则."""

    assert (origin_datetime, datetime.datetime)

    effect_date = origin_datetime.date()

    if effect_date.weekday() in close_weekday:
        effect_date = get_next_monday(effect_date)

    while is_national_holiday(effect_date):
        effect_date += datetime.timedelta(days=1)

    return effect_date


def get_next_monday(origin_date):
    return origin_date + datetime.timedelta(days=(7 - origin_date.weekday()))


def is_national_holiday(date):
    return any(
        start <= date < stop
        for start, stop in national_holiday_ranges)
