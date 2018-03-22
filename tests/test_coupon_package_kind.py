# coding: utf-8

from pytest import raises

from core.models.welfare import CouponWrapper, PackageKind
from core.models.welfare.coupon.kind import deduction_1000_cut_5
from core.models.welfare.package.distributor import SpecialPrize
from .framework import BaseTestCase


class CouponPackageKindTest(BaseTestCase):

    def test_new_kind(self):
        coupon_wrappers = [CouponWrapper(deduction_1000_cut_5, u'呵呵哒', 3)]
        kind = PackageKind(
            id_=42,
            name='Foo is here',
            distributor=SpecialPrize(42),
            coupon_wrappers=coupon_wrappers
        )

        assert PackageKind.get(42) is kind
        assert kind.id_ == 42
        assert kind.name == 'Foo is here'
        assert kind.coupon_wrappers[0].kind == deduction_1000_cut_5
        assert kind.coupon_wrappers[0].name == u'呵呵哒'
        assert kind.coupon_wrappers[0].amount == 3

        # failed
        with raises(ValueError):
            kind1 = PackageKind(42, 'bazinga', SpecialPrize(42), None, coupon_wrappers)
            del kind1

        with raises(ValueError):
            kind2 = PackageKind(43, 'well done', SpecialPrize(44), None, coupon_wrappers)
            del kind2

        # success
        kind2 = PackageKind(43, 'well done', SpecialPrize(43), None, coupon_wrappers)

        # success
        del kind
        kind3 = PackageKind(42, 'i am back', SpecialPrize(42), None, coupon_wrappers)

        # be quiet
        del kind2
        del kind3
