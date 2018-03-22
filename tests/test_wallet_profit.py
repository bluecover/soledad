from decimal import Decimal
from datetime import date, datetime

from pytest import raises
from mock import Mock

from core.models.wallet.profit import WalletProfit
from core.models.wallet.account import WalletAccount

from .framework import BaseTestCase


class WalletProfitTest(BaseTestCase):

    def setUp(self):
        super(WalletProfitTest, self).setUp()
        self.account = self._make_account(1000001)

    def tearDown(self):
        super(WalletProfitTest, self).tearDown()

    def _make_account(self, id_):
        account = Mock(spec=WalletAccount)
        account.id_ = str(id_)
        return account

    def test_get_nothing(self):
        records = WalletProfit.get_multi_by_date(
            self.account, date(2012, 12, 12))
        assert records == []

    def test_record_once(self):
        profit = WalletProfit.record(
            self.account, Decimal(12321), date(2012, 12, 12))
        assert profit.account_id == str(self.account.id_)
        assert profit.amount == Decimal(12321)
        assert profit.date == date(2012, 12, 12)
        assert profit.updated_time <= datetime.now()

    def test_update(self):
        profit = WalletProfit.record(
            self.account, Decimal(12321), date(2012, 12, 12))
        last_updated_time = profit.updated_time

        profit = WalletProfit.record(
            self.account, Decimal(12322), date(2012, 12, 12))
        assert profit.updated_time >= last_updated_time
        assert profit.account_id == str(self.account.id_)
        assert profit.amount == Decimal(12322)
        assert profit.date == date(2012, 12, 12)

    def test_query(self):
        p1 = WalletProfit.record(
            self.account, Decimal(12321), date(2012, 12, 12))
        p2 = WalletProfit.record(
            self.account, Decimal(20), date(2012, 12, 15))

        assert WalletProfit.get_multi_by_date(
            self._make_account(123), date(2012, 12, 12)) == []
        assert WalletProfit.get_multi_by_date(
            self._make_account(123), date(2012, 12, 15)) == []
        assert WalletProfit.get_multi_by_date(
            self.account, date(2012, 12, 16)) == []
        assert WalletProfit.get_multi_by_date(
            self.account, date(2012, 12, 12)) == [p1]
        assert WalletProfit.get_multi_by_date(
            self.account, date(2012, 12, 15)) == [p2]
        assert WalletProfit.get_multi_by_date(
            self.account, (date(2012, 12, 12), date(2012, 12, 15))) == [p1, p2]
        assert WalletProfit.get_multi_by_date(
            self.account, (date(2012, 12, 11), date(2012, 12, 16))) == [p1, p2]
        assert WalletProfit.get_multi_by_date(
            self.account, (date(2012, 12, 12), date(2012, 12, 14))) == [p1]

    def test_query_with_invalid_argument(self):
        with raises(ValueError) as einfo:
            WalletProfit.get_multi_by_date(self.account, None)
        assert 'datetime.date or tuple' in einfo.value.args[0]

        with raises(ValueError) as einfo:
            WalletProfit.get_multi_by_date(
                self.account, (date(2012, 1, 1), date(2010, 1, 1)))
        assert 'must less or equal' in einfo.value.args[0]
