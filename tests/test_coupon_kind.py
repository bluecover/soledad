# coding: utf-8

import decimal
from mock import Mock
from pytest import raises

from core.models.welfare import CouponKind
from core.models.welfare.coupon.regulation import CouponRegulation, QuotaDeductionRegulation
from .framework import BaseTestCase


class CouponKindTest(BaseTestCase):

    def setUp(self):
        super(CouponKindTest, self).setUp()
        self.regulation = Mock(spec=CouponRegulation)

    def tearDown(self):
        super(CouponKindTest, self).tearDown()

    def test_new_kind(self):
        kind = CouponKind(1, self.regulation)
        assert kind.id_ == 1

        with raises(ValueError):
            kind1 = CouponKind(1, self.regulation)
            del kind1

        # success
        kind2 = CouponKind(2, self.regulation)

        # success
        del kind
        kind3 = CouponKind(1, self.regulation)

        # cleanup
        del kind2
        del kind3

    def test_get_kind(self):
        kind = CouponKind(999, self.regulation)
        kind = CouponKind.get(999)
        assert kind.id_ == 999

        kind = CouponKind.get(888)
        assert kind is None

    def test_regulation_and_matcher(self):
        regulation = QuotaDeductionRegulation(
            fulfill_quota=decimal.Decimal(2000.0), deduct_quota=decimal.Decimal(20.0)
        )

        assert regulation.fulfill_quota == 2000
        assert regulation.deduct_quota == 20
        assert regulation.is_available_for_order(3000)
