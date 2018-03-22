from datetime import datetime

from core.models.wallet.account import WalletAccount
from core.models.wallet.providers import ServiceProvider
from .framework import BaseTestCase


class WalletAccountTest(BaseTestCase):

    def setUp(self):
        super(WalletAccountTest, self).setUp()
        self.user = self.add_account('foo@guihua.dev', 'foobar', 'Foo')
        self.provider = ServiceProvider(
            id_=65535, name='Fake Service', secret_key=b'0' * 16,
            bank_partner=None, fund_code=None, fund_name=None,
            fund_company_name=None, fund_bank_name=None)

    def tearDown(self):
        ServiceProvider.storage.pop(65535, None)
        super(WalletAccountTest, self).tearDown()

    def test_get_nothing(self):
        assert not WalletAccount.get(42)
        assert not WalletAccount.get_by_local_account(self.user, self.provider)

    def test_add_and_get(self):
        account = WalletAccount.add(self.user, self.provider)

        assert account.account_id == self.user.id_
        assert account.secret_id == 'e9xcSDzt_92jl5ZVyToEDQ=='
        assert len(account.secret_token) == 32
        assert account.creation_time <= datetime.now()
        assert account.service_provider == self.provider
        assert account.local_account == self.user

        assert WalletAccount.get_by_local_account(self.user, self.provider) == account

    def test_get_or_add(self):
        assert not WalletAccount.get_by_local_account(self.user, self.provider)
        assert WalletAccount.get_or_add(self.user, self.provider)
        assert (WalletAccount.get_or_add(self.user, self.provider) ==
                WalletAccount.get_or_add(self.user, self.provider))

    def test_status(self):
        account = WalletAccount.add(self.user, self.provider)
        assert account.status is WalletAccount.Status.raw

        account.transfer_status(WalletAccount.Status.success)
        assert account.status is WalletAccount.Status.success
        account = WalletAccount.get(account.id_)
        assert account.status is WalletAccount.Status.success

        account.transfer_status(WalletAccount.Status.failure)
        assert account.status is WalletAccount.Status.failure
        account = WalletAccount.get(account.id_)
        assert account.status is WalletAccount.Status.failure

    def test_all_ids(self):
        account = WalletAccount.add(self.user, self.provider)
        assert WalletAccount.get_all_ids() == [account.id_]
