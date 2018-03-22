# coding: utf-8

from __future__ import print_function, absolute_import

import datetime
import calendar

from zslib.errors import BusinessError

from core.models.bank import bank_collection, Partner
from .switch import wallet_bank_suspend, wallet_suspend
from .consts import ZSLIB_ERROR_PAIRS


__all__ = ['get_transaction_date', 'get_value_date']


_VISIBLE_REDIS_KEY = 'wallet:visible_for_users'

transaction_close_time = datetime.time(15, 0, 0)
transaction_close_weekday = frozenset([calendar.SATURDAY, calendar.SUNDAY])

# TODO (tonyseek) 这个日历也许应该被拆分成一个独立 service 并带后台编辑功能
# 所有元组都是遵守基本法的左闭右开区间
national_holiday_ranges = [
    # 元旦
    (datetime.date(2015, 1, 1), datetime.date(2015, 1, 3)),
    # 春节
    (datetime.date(2015, 2, 18), datetime.date(2015, 2, 26)),
    # 清明节
    (datetime.date(2015, 4, 4), datetime.date(2015, 4, 8)),
    # 劳动节
    (datetime.date(2015, 5, 1), datetime.date(2015, 5, 5)),
    # 端午节
    (datetime.date(2015, 6, 20), datetime.date(2015, 6, 24)),
    # 抗战胜利 70 周年
    (datetime.date(2015, 9, 3), datetime.date(2015, 9, 8)),
    # 中秋节
    (datetime.date(2015, 9, 26), datetime.date(2015, 9, 28)),
    # 国庆节
    (datetime.date(2015, 10, 1), datetime.date(2015, 10, 8)),
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


def get_transaction_date(payment_datetime):
    """从支付时间计算出有效交易日期, 包含了法定节假日等非交易日顺延规则."""
    payment_date = payment_datetime.date()
    payment_time = payment_datetime.time()

    if payment_time < transaction_close_time:
        transaction_date = payment_date
    else:
        transaction_date = payment_date + datetime.timedelta(days=1)

    if transaction_date.weekday() in transaction_close_weekday:
        transaction_date = get_next_monday(transaction_date)

    while is_national_holiday(transaction_date):
        transaction_date += datetime.timedelta(days=1)

    return transaction_date


def get_value_date(payment_datetime):
    transaction_date = get_transaction_date(payment_datetime)
    value_date = transaction_date + datetime.timedelta(days=1)

    if value_date.weekday() in transaction_close_weekday:
        value_date = get_next_monday(value_date)

    while is_national_holiday(value_date):
        value_date += datetime.timedelta(days=1)

    return value_date


def get_next_monday(date):
    return date + datetime.timedelta(days=(7 - date.weekday()))


def is_national_holiday(date):
    return any(
        start <= date < stop
        for start, stop in national_holiday_ranges)


def iter_banks(user_id):
    """列出银行限额"""
    for bank in bank_collection.banks:
        if Partner.zs in bank.available_in:
            yield (bank, bank.zslib_amount_limit)


def describe_business_error(error, sentry):
    """将 :exc:`.BusinessError` 映射为用户文案.

    :param error: 异常实例
    :param sentry: Sentry client, 用于收集未预期的异常
    """
    description, is_unexpected = ZSLIB_ERROR_PAIRS.get(
        error.kind, ZSLIB_ERROR_PAIRS[BusinessError.kinds.unknown])
    if is_unexpected:
        sentry.captureException()
    return description.format(error_code=error.code)


def describe_bank_suspend(bank, transfer_type):
    assert transfer_type in ('purchase', 'redeem')

    suspend = wallet_bank_suspend[transfer_type][bank]
    if suspend.is_enable:
        period_desc = u'{0}至{1}'.format(
            _cn_time(suspend.open_time), _cn_time(suspend.close_time))
        return u'抱歉，{0}于{1}进行升级维护，请您暂时选择其他银行卡'.format(
            bank.name, period_desc)


def describe_wallet_suspend(order_type):
    transfer_dict = {'purchase': 'deposit', 'redeem': 'withdraw'}
    if order_type in transfer_dict:
        order_type = transfer_dict[order_type]
    suspend = wallet_suspend[order_type]
    if suspend.is_enable:
        name_dict = {'deposit': u'存入', 'withdraw': u'取出'}
        period_desc = u'{0}至{1}'.format(
            _cn_time(suspend.open_time), _cn_time(suspend.close_time))
        return u'由于系统升级，零钱包的{0}服务将于{1}暂停，请您于升级成功后重新进行操作，多谢！'.format(
            name_dict[order_type], period_desc)


def _cn_time(dt):
    return unicode(dt.strftime('%Y年%m月%d日%H点%M分'), 'utf-8')
