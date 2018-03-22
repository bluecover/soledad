# coding:utf-8

import uuid
import datetime
import decimal

from mock import Mock
from zslib.wrappers import TransactionRecord

from core.models.wallet.account import WalletAccount
from core.models.wallet.audit import WalletAudit
from core.models.wallet.transaction import WalletTransaction
from .framework import BaseTestCase


class WalletAuditTest(BaseTestCase):

    def setUp(self):
        super(WalletAuditTest, self).setUp()
        self.local_type = WalletTransaction.Type
        self.local_status = WalletTransaction.Status
        self.remote_type = TransactionRecord.TransactionType

        self.local_transaction = Mock(spec=WalletTransaction)
        self.remote_transaction = Mock(spec=TransactionRecord)
        self.local_transaction.id_ = '1010'
        self.local_transaction.status = self.local_status.failure
        self.local_transaction.type_.value = self.local_type.purchase.value
        self.local_transaction.amount = decimal.Decimal('120.00')
        self.local_transaction.creation_time = datetime.datetime.now()
        self.remote_transaction.ransaction_id = uuid.uuid4().hex
        self.remote_transaction.transaction_type.value = self.remote_type.transfer_in.value
        self.remote_transaction.transaction_amount = decimal.Decimal('120.00')
        self.remote_transaction.transaction_time = datetime.datetime.now()
        self.wallet_account = Mock(spec=WalletAccount)
        self.wallet_account.id_ = '2020'

    def tearDown(self):
        super(WalletAuditTest, self).tearDown()

    def test_audit_local_remote(self):
        audit = WalletAudit.compare_and_add(
            self.wallet_account, self.local_transaction, self.remote_transaction)
        assert audit.local_type is self.local_type.purchase
        assert audit.remote_type is self.remote_type.transfer_in

    def test_audit_remote_only(self):
        audit = WalletAudit.compare_and_add(
            self.wallet_account, None, self.remote_transaction)
        assert audit.remote_type is self.remote_type.transfer_in
        assert audit.local_type is None

    def test_audit_local_only(self):
        audit = WalletAudit.compare_and_add(
            self.wallet_account, self.local_transaction)
        assert audit.local_type is self.local_type.purchase
        assert audit.remote_type is None

    def test_get_by_local_transaction_id(self):
        audit = WalletAudit.compare_and_add(
            self.wallet_account, self.local_transaction)
        audit_from_local_transaction = WalletAudit.get_by_local_transaction_id(
            audit.local_transaction_id)
        assert audit.local_type is self.local_type.purchase
        assert audit_from_local_transaction.local_type is audit.local_type
        assert audit.remote_type is None
        assert audit_from_local_transaction.remote_type is audit.remote_type
