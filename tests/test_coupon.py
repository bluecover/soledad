# coding: utf-8

from datetime import datetime, timedelta

from mock import patch, Mock
from pytest import raises

from core.models.consts import Platform
from core.models.welfare import Coupon, CouponKind, CouponRegulation, Package
from core.models.welfare.matcher import ProductMatcher, ProductMatcherKind
from core.models.welfare.coupon.errors import (
    CouponOutdatedError, InvalidCouponStatusTransferError,
    UnsupportedProductError, IneligibleOrderError)
from .framework import BaseTestCase


class CouponTest(BaseTestCase):

    def setUp(self):
        super(CouponTest, self).setUp()
        self.account = self.add_account('foo@guihua.dev', 'foobar', 'Foo')
        self.expires_in = timedelta(days=60)
        self.coupon_kind = Mock(spec=CouponKind)
        self.coupon_kind.id_ = '101'
        self.coupon_kind.regulation = Mock(spec=CouponRegulation)

        self.product_matcher_kind = Mock(spec=ProductMatcherKind)
        self.product_matcher_kind.id_ = '202'
        self.product_matcher_kind.matcher = Mock(spec=ProductMatcher)

        self.package = Mock(spec=Package)
        self.package.id_ = '303'
        self.package.user = self.account

    def tearDown(self):
        super(CouponTest, self).tearDown()

    @patch.object(Package, 'get')
    @patch.object(CouponKind, 'get')
    def test_new_coupon(self, coupon_kind_get, package_get):
        coupon_kind_get.return_value = self.coupon_kind
        package_get.return_value = self.package
        c = Coupon.create(
            name=u'呵呵哒',
            kind=self.coupon_kind,
            package=self.package,
            product_matcher_kind=self.product_matcher_kind,
            available_platforms=[Platform.web],
            expire_time=datetime.now() + self.expires_in
        )

        assert c.name == u'呵呵哒'
        assert c.user == self.account
        assert c.kind == self.coupon_kind
        assert c.status is Coupon.Status.in_wallet
        assert c.package == self.package
        assert Platform.web in c.platforms

        coupon_kind_get.assert_called_once_with('101')
        package_get.assert_called_once_with('303')

    @patch.object(Package, 'get')
    @patch.object(CouponKind, 'get')
    def test_get_coupon(self, coupon_kind_get, package_get):
        coupon_kind_get.return_value = self.coupon_kind
        package_get.return_value = self.package
        c = Coupon.create(
            name=u'呵呵哒',
            kind=self.coupon_kind,
            package=self.package,
            product_matcher_kind=self.product_matcher_kind,
            available_platforms=[Platform.web],
            expire_time=datetime.now() + self.expires_in
        )

        existence = Coupon.get(c.id_)
        assert existence == c

        id_list = Coupon.get_ids_by_user(c.user.id_)
        assert c.id_ in id_list

        id_list = Coupon.get_ids_by_package(c.package.id_)
        assert c.id_ in id_list

    @patch.object(ProductMatcherKind, 'get')
    @patch.object(Coupon, 'outdated')
    @patch.object(Coupon, 'kind')
    def test_check_usage(self, kind, outdated, product_matcher_kind_get):
        product_matcher_kind_get.return_value = self.product_matcher_kind
        coupon = Coupon.create(
            name=u'呵呵哒',
            kind=self.coupon_kind,
            package=self.package,
            product_matcher_kind=self.product_matcher_kind,
            available_platforms=[Platform.web],
            expire_time=datetime(2015, 1, 1)
        )

        with raises(CouponOutdatedError):
            coupon.check_before_use()

        Coupon.outdated = False
        coupon.product_matcher.is_available_for_product.return_value = False
        with raises(UnsupportedProductError):
            coupon.check_before_use(product='test')
        coupon.regulation.is_available_for_order.return_value = False
        with raises(IneligibleOrderError):
            coupon.check_before_use(amount=3000)

    def test_transfer_status(self):
        coupon = Coupon.create(
            name=u'呵呵哒',
            kind=self.coupon_kind,
            package=self.package,
            product_matcher_kind=self.product_matcher_kind,
            available_platforms=[Platform.web],
            expire_time=datetime.now() + self.expires_in
        )

        coupon.shell_out()
        assert coupon.status is Coupon.Status.stocktaking

        coupon.put_back_wallet()
        assert coupon.status is Coupon.Status.in_wallet

        coupon.shell_out()
        coupon.confirm_consumption()
        assert coupon.status is Coupon.Status.consumed

        with raises(InvalidCouponStatusTransferError):
            coupon.put_back_wallet()

        with raises(InvalidCouponStatusTransferError):
            coupon.confirm_consumption()
