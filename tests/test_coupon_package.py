# coding: utf-8

from datetime import timedelta
from mock import patch, Mock
from pytest import raises

from core.models.welfare import CouponKind, CouponWrapper, Package, PackageKind
from core.models.welfare.package.errors import (
    WrongPackageTokenError, InvalidPackageStatusTransferError)
from .framework import BaseTestCase


class CouponPackageTest(BaseTestCase):

    def setUp(self):
        super(CouponPackageTest, self).setUp()

        self.coupon_kind = Mock(spec=CouponKind)
        self.coupon_kind.id_ = 1
        self.coupon_kind.expires_in = timedelta(days=30)

        self.kind = Mock(spec=PackageKind)
        self.kind.id_ = 11
        self.kind.firewood_wrapper = None
        self.kind.coupon_wrappers = [CouponWrapper(self.coupon_kind, u'测试券', 3)]
        self.kind.distributor = Mock()
        self.kind.distributor.can_unpack.return_value = True

        self.user = self.add_account(mobile='18500000000')

    def tearDown(self):
        del self.kind
        del self.coupon_kind
        super(CouponPackageTest, self).tearDown()

    @patch.object(PackageKind, 'get')
    def test_creation(self, package_kind_get):
        package_kind_get.return_value = self.kind

        package = Package.create(self.kind)
        assert package.user_id is None
        assert package.creation_time is not None
        assert package.unpacked_time is None
        assert package.reserved_time is None
        assert package.status is Package.Status.in_air
        assert package.reserved_sha1 is None
        assert package.kind.id_ == 11

        assert Package.get(package.id_)

    @patch.object(PackageKind, 'get')
    def test_reserved(self, package_kind_get):
        package_kind_get.return_value = self.kind
        package = Package.create(self.kind)
        assert package.status is Package.Status.in_air

        token = package.reserve()
        assert token == package.reserved_sha1

        package = Package.get(package.id_)
        assert token == package.reserved_sha1

        # reverses again
        with raises(InvalidPackageStatusTransferError):
            package.reserve()

        # nothing changed
        assert token == package.reserved_sha1
        package = Package.get(package.id_)
        assert token == package.reserved_sha1

    @patch.object(PackageKind, 'get')
    def test_unpacking(self, package_kind_get):
        package_kind_get.return_value = self.kind
        package = Package.create(self.kind)
        assert package.status is Package.Status.in_air

        # unpacks with token
        with raises(ValueError):
            package.unpack(self.user, 'token')

        # unpacks success
        package.unpack(self.user)
        assert package.user.id == self.user.id

        # unpacks again
        with raises(InvalidPackageStatusTransferError):
            package.unpack(self.user)

        # nothing changed
        assert package.user.id == self.user.id
        package = Package.get(package.id_)
        assert package.user.id == self.user.id

    @patch.object(PackageKind, 'get')
    def test_unpacking_reserved(self, package_kind_get):
        package_kind_get.return_value = self.kind
        package = Package.create(self.kind)
        token = package.reserve()
        assert package.status is Package.Status.under_foot

        # missing token
        with raises(ValueError):
            package.unpack(self.user)
        assert package.status is Package.Status.under_foot

        # wrong token
        with raises(WrongPackageTokenError):
            package.unpack(self.user, 'token')
        assert package.status is Package.Status.under_foot

        # empty token
        with raises(WrongPackageTokenError):
            package.unpack(self.user, '')
        assert package.status is Package.Status.under_foot

        # unpacks success
        package.unpack(self.user, token)
        assert package.status is Package.Status.in_pocket

        # unpacks again
        with raises(InvalidPackageStatusTransferError):
            package.unpack(self.user, token)

        # nothing changed
        assert package.user.id == self.user.id
        package = Package.get(package.id_)
        assert package.user.id == self.user.id
