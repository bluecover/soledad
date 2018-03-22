# coding: utf-8

from functools import partial
from datetime import date, datetime

from core.models.wallet.utils import (
    get_transaction_date, get_next_monday, get_value_date)
from .framework import BaseTestCase


class WalletAlgorithmTest(BaseTestCase):

    def test_next_monday(self):
        day = partial(date, 2015, 7)
        assert get_next_monday(day(19)) == day(20)
        assert get_next_monday(day(20)) == day(27)
        assert get_next_monday(day(21)) == day(27)
        assert get_next_monday(day(22)) == day(27)
        assert get_next_monday(day(23)) == day(27)
        assert get_next_monday(day(24)) == day(27)
        assert get_next_monday(day(25)) == day(27)
        assert get_next_monday(day(26)) == day(27)
        assert get_next_monday(day(27)) == date(2015, 8, 3)

        day_at_2016 = partial(date, 2016, 1)
        assert get_next_monday(day_at_2016(1)) == day_at_2016(4)
        assert get_next_monday(day_at_2016(4)) == day_at_2016(11)
        assert get_next_monday(day_at_2016(5)) == day_at_2016(11)
        assert get_next_monday(day_at_2016(6)) == day_at_2016(11)
        assert get_next_monday(day_at_2016(7)) == day_at_2016(11)
        assert get_next_monday(day_at_2016(8)) == day_at_2016(11)
        assert get_next_monday(day_at_2016(9)) == day_at_2016(11)
        assert get_next_monday(day_at_2016(10)) == day_at_2016(11)

    def test_transaction_date(self):
        day = partial(date, 2015, 7)
        day_at_2016 = partial(date, 2016, 1)

        def before_ending(day, year=2015, month=7):
            return datetime(year, month, day, 14, 59, 59)

        def after_ending(day, year=2015, month=7):
            return datetime(year, month, day, 15, 0, 0)

        # 测试过节期间
        assert get_transaction_date(before_ending(1, 2016, 1)) == day_at_2016(4)
        assert get_transaction_date(after_ending(1, 2016, 1)) == day_at_2016(4)
        # 测试普通工作日
        assert get_transaction_date(before_ending(5, 2016, 1)) == day_at_2016(5)
        assert get_transaction_date(after_ending(5, 2016, 1)) == day_at_2016(6)
        # 测试周末
        assert get_transaction_date(before_ending(9, 2016, 1)) == day_at_2016(11)
        assert get_transaction_date(after_ending(9, 2016, 1)) == day_at_2016(11)

        assert get_transaction_date(before_ending(19)) == day(20)
        assert get_transaction_date(after_ending(19)) == day(20)

        assert get_transaction_date(before_ending(20)) == day(20)
        assert get_transaction_date(after_ending(20)) == day(21)

        assert get_transaction_date(before_ending(21)) == day(21)
        assert get_transaction_date(after_ending(21)) == day(22)

        assert get_transaction_date(before_ending(22)) == day(22)
        assert get_transaction_date(after_ending(22)) == day(23)

        assert get_transaction_date(before_ending(23)) == day(23)
        assert get_transaction_date(after_ending(23)) == day(24)

        assert get_transaction_date(before_ending(24)) == day(24)
        assert get_transaction_date(after_ending(25)) == day(27)

        assert get_transaction_date(before_ending(24)) == day(24)
        assert get_transaction_date(after_ending(24)) == day(27)

        assert get_transaction_date(before_ending(25)) == day(27)
        assert get_transaction_date(after_ending(25)) == day(27)

        assert get_transaction_date(before_ending(26)) == day(27)
        assert get_transaction_date(after_ending(26)) == day(27)

    def test_value_date(self):
        # 由报告的 Bug 补充的测试用例
        assert get_value_date(
            datetime(2015, 9, 24, 19, 21, 00)) == date(2015, 9, 28)
