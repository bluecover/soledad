from pytest import raises

from core.models.wallet.providers import ServiceProvider
from core.models.wallet._bankcard_binding import WalletBankcardBinding
from .framework import BaseTestCase


class WalletBankcardBindingTest(BaseTestCase):

    def setUp(self):
        super(WalletBankcardBindingTest, self).setUp()
        self.user = self.add_account(mobile='13800138000')
        self.bankcard = self.add_bankcard(self.user.id_)
        self.provider = ServiceProvider(
            id_=65535, name='Fake Service', secret_key=b'0' * 16,
            bank_partner=None, fund_code=None, fund_name=None,
            fund_company_name=None, fund_bank_name=None)

    def tearDown(self):
        ServiceProvider.storage.pop(65535, None)
        super(WalletBankcardBindingTest, self).tearDown()

    def _bankcard_binding(self):
        return WalletBankcardBinding.get_by_bankcard(
            self.bankcard, self.provider)

    def test_binding(self):
        assert not self._bankcard_binding()

        with WalletBankcardBinding.record_for_binding(
                self.bankcard, self.provider):
            binding = self._bankcard_binding()
            assert binding
            assert not binding.is_confirmed

        binding = self._bankcard_binding()
        assert binding
        assert binding.is_confirmed

    def test_binding_failed(self):
        assert not self._bankcard_binding()

        class TestingException(Exception):
            pass

        with raises(TestingException):
            with WalletBankcardBinding.record_for_binding(
                    self.bankcard, self.provider):
                raise TestingException

        binding = self._bankcard_binding()
        assert binding
        assert not binding.is_confirmed

        # retry
        with WalletBankcardBinding.record_for_binding(
                self.bankcard, self.provider):
            binding = self._bankcard_binding()
            assert binding
            assert not binding.is_confirmed

        binding = self._bankcard_binding()
        assert binding
        assert binding.is_confirmed
