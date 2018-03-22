from decimal import Decimal
from datetime import date, timedelta

from zslib.wrappers import AnnualRateList
from mock import patch

from core.models.wallet.dashboard import PublicDashboard
from core.models.wallet.providers import zhongshan
from core.models.wallet.annual_rate import WalletAnnualRate
from .framework import BaseTestCase


class MockClient(object):
    """The fake zslib client."""

    def __init__(self, fund_code):
        self.fund_code = fund_code

    def list_annual_rates(self, fund_code, date_from, date_to):
        assert fund_code == self.fund_code
        assert isinstance(date_from, date)
        assert isinstance(date_to, date)
        assert date_from < date_to

        return AnnualRateList({
            u'fundCode': u'360021',
            u'infos': [
                {u'day7AnnualRate': u'1.0430',
                 u'mostIncomes': u'1.0000',
                 u'shareDate': u'20150714'},
                {u'day7AnnualRate': u'1.0430',
                 u'mostIncomes': u'1.0000',
                 u'shareDate': u'20150716'},
                {u'day7AnnualRate': u'5.2240',
                 u'mostIncomes': u'2.4363',
                 u'shareDate': u'20150713'},
            ],
            u'transactionId': u'000001437469573568'
        })


class WalletAnnualRateTest(BaseTestCase):

    def setUp(self):
        super(WalletAnnualRateTest, self).setUp()
        self.fund_code = zhongshan.fund_code
        self.client = MockClient(self.fund_code)

    def test_synchronize(self):
        rates = WalletAnnualRate.synchronize(self.client, self.fund_code)
        assert len(rates) == 3
        assert sorted([r.annual_rate for r in rates]) == [
            Decimal('1.0430'),
            Decimal('1.0430'),
            Decimal('5.2240'),
        ]

        rates = WalletAnnualRate.get_multi_by_date_range(
            date(2015, 7, 13), date(2015, 7, 17), self.fund_code)
        assert len(rates) == 3
        assert sorted([r.annual_rate for r in rates]) == [
            Decimal('1.0430'),
            Decimal('1.0430'),
            Decimal('5.2240'),
        ]

        rates = WalletAnnualRate.get_multi_by_date_range(
            date(2015, 7, 14), date(2015, 7, 16), self.fund_code)
        assert len(rates) == 1
        assert sorted([r.annual_rate for r in rates]) == [
            Decimal('1.0430'),
        ]

        rates = WalletAnnualRate.get_multi_by_date_range(
            date(2015, 7, 13), date(2015, 7, 17), self.fund_code + '-chaos')
        assert len(rates) == 0

    @patch('core.models.wallet.dashboard.datetime')
    def test_facade(self, datetime):
        datetime.date.today.return_value = date(2015, 7, 17)
        datetime.timedelta.return_value = timedelta(days=7)

        WalletAnnualRate.synchronize(self.client, self.fund_code)

        dashboard = PublicDashboard.today()
        rates = dashboard.weekly_annual_rates
        assert len(rates) == 3
        assert sorted([r.annual_rate for r in rates]) == [
            Decimal('1.0430'),
            Decimal('1.0430'),
            Decimal('5.2240'),
        ]
