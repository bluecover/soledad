import uuid
from decimal import Decimal

from mock import patch, Mock
from core.models.wallet.transaction import WalletTransaction
from core.models.wallet.account import WalletAccount
from .framework import BaseTestCase


class WalletTransactionTest(BaseTestCase):

    def setUp(self):
        super(WalletTransactionTest, self).setUp()
        self.bankcard_patcher = patch('core.models.wallet.transaction.BankCard')
        self.bankcard_class = self.bankcard_patcher.start()
        self.account_patcher = patch.object(WalletAccount, 'get')
        self.account_patcher.start()

        self.account = self.add_account('foo@guihua.dev', 'foobar', 'Foo')
        self.wallet_account = Mock(spec=WalletAccount)
        self.wallet_account.id_ = '1010'
        self.wallet_account.local_account = self.account
        WalletAccount.get.return_value = self.wallet_account

        self.bankcard = self.bankcard_class.get.return_value
        self.bankcard.id_ = 42
        self.bankcard.user_id = str(self.account.id_)

    def tearDown(self):
        self.bankcard_patcher.stop()
        self.account_patcher.stop()
        super(WalletTransactionTest, self).tearDown()

    def test_new_transaction(self):
        t = WalletTransaction.add(
            account=self.wallet_account,
            bankcard=self.bankcard,
            transaction_id=uuid.uuid4().hex,
            amount=Decimal('1024.12'),
            type_=WalletTransaction.Type.purchase)

        assert t.owner == self.account
        assert t.wallet_account == self.wallet_account
        assert t.type_ is WalletTransaction.Type.purchase
        assert t.status is WalletTransaction.Status.raw
        assert t.bankcard == self.bankcard

        WalletAccount.get.assert_called_once_with('1010')
        self.bankcard_class.get.assert_called_once_with(42)

        WalletTransaction.sum_amount(WalletTransaction.Type.purchase) == \
            Decimal('0')

    def test_transfer_status(self):
        t = WalletTransaction.add(
            account=self.wallet_account,
            bankcard=self.bankcard,
            transaction_id=uuid.uuid4().hex,
            amount=Decimal('1024.12'),
            type_=WalletTransaction.Type.purchase)
        assert t.status is WalletTransaction.Status.raw
        t = WalletTransaction.get(t.id_)
        assert t.status is WalletTransaction.Status.raw

        WalletTransaction.sum_amount(WalletTransaction.Type.purchase) == \
            Decimal('0')

        t.transfer_status(WalletTransaction.Status.success)
        assert t.status is WalletTransaction.Status.success
        t = WalletTransaction.get(t.id_)
        assert t.status is WalletTransaction.Status.success

        WalletTransaction.sum_amount(WalletTransaction.Type.purchase) == \
            Decimal('1024.12')

        t.transfer_status(WalletTransaction.Status.failure)
        assert t.status is WalletTransaction.Status.failure
        t = WalletTransaction.get(t.id_)
        assert t.status is WalletTransaction.Status.failure

        WalletTransaction.sum_amount(WalletTransaction.Type.purchase) == \
            Decimal('0')

    def test_get_by_bankcard_id(self):
        t = WalletTransaction.add(
            account=self.wallet_account,
            bankcard=self.bankcard,
            transaction_id=uuid.uuid4().hex,
            amount=Decimal('1024.22'),
            type_=WalletTransaction.Type.purchase)

        ids = WalletTransaction.get_ids_by_bankcard(self.bankcard.id_)
        assert ids == []

        t.transfer_status(WalletTransaction.Status.success)
        ids = WalletTransaction.get_ids_by_bankcard(self.bankcard.id_)
        assert ids == [t.id_]
