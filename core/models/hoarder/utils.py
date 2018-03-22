# coding: utf-8

import datetime

from core.models.bank import Partner
from core.models.bank.banks import bank_collection
from core.models.profile.bankcard import BankCardManager
from .order import HoarderOrder


national_holiday_ranges = [
    # 国庆节
    (datetime.date(2015, 10, 1), datetime.date(2015, 10, 8)),
]


def is_national_holiday(date):
    return any(
        start <= date < stop
        for start, stop in national_holiday_ranges)


def iter_banks(user_id):

    bankcards = BankCardManager(user_id).get_all(Partner.sxb)

    def never_used(bank):
        return all(
            not HoarderOrder.is_bankcard_swiped(bankcard)
            for bankcard in bankcards if bankcard.bank is bank)

    for bank in bank_collection.banks:
        if Partner.sxb not in bank.available_in:
            continue
        if never_used(bank):
            amount_limit = bank.sxblib_amount_limit[0]
        else:
            amount_limit = bank.sxblib_amount_limit[1]
        yield (bank, amount_limit)
