# coding: utf-8

import datetime

from core.models.bank import Partner
from core.models.bank.banks import bank_collection
from core.models.profile.bankcard import BankCard
from .order import ZhiwangOrder
from .profile import ZhiwangProfile
from core.models.wallet.utils import (
    transaction_close_weekday, get_next_monday)


national_holiday_ranges = [
    # 国庆节
    (datetime.date(2015, 10, 1), datetime.date(2015, 10, 8)),
]


def is_national_holiday(date):
    return any(
        start <= date < stop
        for start, stop in national_holiday_ranges)


def iter_banks(user_id):
    profile = ZhiwangProfile.add(user_id)
    bankcards = profile.bankcards.get_all(Partner.zw)

    def never_used(bank):
        return all(
            not ZhiwangOrder.is_bankcard_swiped(bankcard)
            for bankcard in bankcards if bankcard.bank is bank)

    for bank in bank_collection.banks:
        if Partner.zw not in bank.available_in:
            continue
        if never_used(bank):
            amount_limit = bank.zwlib_amount_limit[0]
        else:
            amount_limit = bank.zwlib_amount_limit[1]
        yield (bank, amount_limit)


def remove_bankcard(user_id, bankcard_id):
    profile = ZhiwangProfile.add(user_id)
    bankcard = BankCard.get(bankcard_id)
    if not bankcard:
        return
    profile.bankcards.remove(bankcard.card_number, silent=True)


def get_expect_payback_date(due_date):
    """从到期日时间计算出赎回日，包含了法定节假日等非到期日顺眼规则."""
    payback_date = due_date + datetime.timedelta(days=1)
    if payback_date.weekday() in transaction_close_weekday:
        payback_date = get_next_monday(payback_date)
    while is_national_holiday(payback_date):
        payback_date += datetime.timedelta(days=1)
    return payback_date
