# coding: utf-8

import contextlib

from mock import patch
from pytest import raises
from cryptography.hazmat.primitives.twofactor.totp import InvalidToken

from core.models.security.twofactor import TwoFactor
from .framework import BaseTestCase


class TwoFactorTestCase(BaseTestCase):

    def setUp(self):
        super(TwoFactorTestCase, self).setUp()
        self.user_foo = self.add_account(email='foo@guihua.dev')
        self.user_bar = self.add_account(mobile='13800138000')

    @contextlib.contextmanager
    def nothing_is_random(self, urandom=(b'0' * 20), time=1442682280):
        with patch('os.urandom') as _urandom, patch('time.time') as _time:
            _urandom.return_value = urandom
            _time.return_value = time
            yield

    def test_create(self):
        assert TwoFactor.get(self.user_foo.id_) is None
        assert TwoFactor.add(self.user_foo.id_)
        assert not TwoFactor.get(self.user_foo.id_).is_enabled

        assert TwoFactor.get(self.user_bar.id_) is None
        assert TwoFactor.get_or_add(self.user_bar.id_)
        assert not TwoFactor.get(self.user_bar.id_).is_enabled

    def test_totp(self):
        with self.nothing_is_random():
            twofactor = TwoFactor.add(self.user_foo.id_)
            assert twofactor.totp
            assert twofactor.secret_key == b'0' * 20
            assert twofactor.generate() == '366882'
            assert twofactor.verify('366882')
            assert not twofactor.verify('123456')

    def test_enable(self):
        with self.nothing_is_random():
            twofactor = TwoFactor.add(self.user_foo.id_)
            assert not twofactor.is_enabled

            # fail
            with raises(InvalidToken):
                twofactor.enable('123456')
            assert not twofactor.is_enabled
            twofactor = TwoFactor.get(self.user_foo.id_)
            assert not twofactor.is_enabled

            # pass
            twofactor.enable('366882')
            assert twofactor.is_enabled
            twofactor = TwoFactor.get(self.user_foo.id_)
            assert twofactor.is_enabled

    def test_disable(self):
        with self.nothing_is_random():
            twofactor = TwoFactor.add(self.user_foo.id_)
            twofactor.enable('366882')
            assert twofactor.is_enabled

            twofactor.disable()
            assert not twofactor.is_enabled
            twofactor = TwoFactor.get(self.user_foo.id_)
            assert not twofactor.is_enabled

    def test_renew(self):
        with self.nothing_is_random():
            twofactor = TwoFactor.add(self.user_foo.id_)
            twofactor.enable('366882')
        with self.nothing_is_random(urandom=(b'1' * 20)):
            twofactor.renew()
            assert not twofactor.is_enabled
            assert twofactor.secret_key == b'1' * 20
            assert twofactor.generate() == '284107'

            twofactor = TwoFactor.get(self.user_foo.id_)
            assert not twofactor.is_enabled
            assert not twofactor.verify('366882')
            assert twofactor.verify('284107')

    def test_qrcode_uri(self):
        with self.nothing_is_random():
            twofactor = TwoFactor.add(self.user_foo.id_)
            assert twofactor.get_provisioning_uri() == (
                'otpauth://totp/%E5%A5%BD%E8%A7%84%E5%88%92:foo%40guihua.dev'
                '?digits=6&secret=GAYDAMBQGAYDAMBQGAYDAMBQGAYDAMBQ&algorithm'
                '=SHA1&issuer=%E5%A5%BD%E8%A7%84%E5%88%92&period=30')

        with self.nothing_is_random():
            twofactor = TwoFactor.add(self.user_bar.id_)
            assert twofactor.get_provisioning_uri() == (
                'otpauth://totp/%E5%A5%BD%E8%A7%84%E5%88%92:138%2A%2A%2A%2A8000'
                '?digits=6&secret=GAYDAMBQGAYDAMBQGAYDAMBQGAYDAMBQ&algorithm'
                '=SHA1&issuer=%E5%A5%BD%E8%A7%84%E5%88%92&period=30')
