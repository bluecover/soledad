# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

import decimal
import itertools

from enum import Enum
from werkzeug.utils import cached_property

from jupiter.ext import sentry
from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.bank.errors import UnavailableBankError
from core.models.profile.bankcard import BankCard
from core.models.profile.signals import before_deleting_bankcard
from .account import WalletAccount
from .signals import transaction_status_changed, account_status_changed
from .utils import get_value_date


class WalletTransaction(EntityModel):
    """The transaction record for purchase and redeeming."""

    table_name = 'wallet_transaction'
    cache_key = 'wallet:transaction:{id_}:v2'
    cache_key_by_bankcard = 'wallet:transaction:bankcard:{bankcard_id}:v2'
    cache_key_by_account = 'wallet:transaction:account:{wallet_account_id}:{status.value}:v3'
    cache_key_for_balance = 'wallet:transaction:balance:{wallet_account_id}:v2'
    cache_key_for_sum_amount = 'wallet:transaction:sum_amount:{type_.value}:{status.value}'
    cache_key_by_transaction_id = 'wallet:transaction:transaction_id:{transaction_id}:v2'

    class Meta:
        repr_attr_names = ['amount', 'type', 'status', 'creation']

    class Type(Enum):
        purchase = 'P'
        redeeming = 'R'

    class Status(Enum):
        raw = 'R'
        success = 'S'
        failure = 'F'

    def __init__(self, id_, account_id, amount, type_code, bankcard_id,
                 status_code, creation_time, transaction_id):
        self.id_ = str(id_)
        self.account_id = str(account_id)
        self.amount = amount
        self._type = type_code
        self._status = status_code
        self.bankcard_id = bankcard_id
        self.transaction_id = transaction_id
        self.creation_time = creation_time

    @property
    def owner(self):
        return self.wallet_account.local_account

    @cached_property
    def wallet_account(self):
        return WalletAccount.get(self.account_id)

    @cached_property
    def type_(self):
        return self.Type(self._type)

    @property
    def status(self):
        return self.Status(self._status)

    @cached_property
    def bankcard(self):
        return BankCard.get(self.bankcard_id)

    @cached_property
    def creation_date(self):
        return self.creation_time.date()

    @cached_property
    def value_date(self):
        if self.type_ is self.Type.purchase:
            return get_value_date(self.creation_time)

    @cached_property
    def end_date(self):
        if self.type_ is self.Type.redeeming:
            return self.creation_time.date()

    @cached_property
    def balance_amount(self):
        """The signed amount for calculating balance."""
        if self.type_ is self.Type.purchase:
            return self.amount
        if self.type_ is self.Type.redeeming:
            return -self.amount

    @classmethod
    def add(cls, account, bankcard, amount, type_, transaction_id,
            status=Status.raw):
        """Creates a raw transaction."""
        assert isinstance(account, WalletAccount)
        assert isinstance(amount, decimal.Decimal)
        assert isinstance(type_, cls.Type)
        assert isinstance(status, cls.Status)

        if not account.service_provider.is_avalable_bankcard(bankcard):
            raise UnavailableBankError(bankcard, account.service_provider)
        if str(account.local_account.id_) != str(bankcard.user_id):
            raise ValueError('mismatched user id')

        sql = (
            'insert into {0} (account_id, amount, type, bankcard_id, status,'
            ' transaction_id) '
            'values (%s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (
            account.id_, amount, type_.value, bankcard.id_, status.value,
            transaction_id)

        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_bankcard(bankcard.id_)
        cls.clear_cache_by_account(account.id_)
        cls.clear_cache_for_sum_amount()

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, account_id, amount, type, bankcard_id, status,'
            ' creation_time, transaction_id '
            'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_transaction_id)
    def get_id_by_transaction(cls, transaction_id):
        sql = 'select id from {.table_name} where transaction_id = %s'.format(cls)
        params = (transaction_id,)
        rs = db.execute(sql, params)
        if rs:
            return str(rs[0][0])

    @classmethod
    def get_by_transaction_id(cls, transaction_id):
        id_ = cls.get_id_by_transaction(transaction_id)
        return cls.get(id_)

    @classmethod
    @cache(cache_key_by_bankcard)
    def get_ids_by_bankcard(cls, bankcard_id):
        sql = ('select id from {0} where bankcard_id = %s and status = %s'
               'order by id desc').format(cls.table_name)
        params = (bankcard_id, cls.Status.success.value)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    @cache(cache_key_by_account)
    def get_ids_by_account(cls, wallet_account_id, status=Status.success):
        sql = ('select id from {0} where account_id = %s and status = %s'
               'order by id desc').format(cls.table_name)
        params = (wallet_account_id, status.value)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_account(cls, wallet_account, status=Status.success):
        assert isinstance(wallet_account, WalletAccount)
        ids = cls.get_ids_by_account(wallet_account.id_, status=status)
        return cls.get_multi(ids)

    @classmethod
    def _get_by_account_and_date(cls, wallet_account, from_date, to_date):
        assert isinstance(wallet_account, WalletAccount)
        sql = ('select id from {0} where account_id = %s '
               'and creation_time between %s and %s'
               'order by id desc').format(cls.table_name)
        params = (wallet_account.id_, from_date, to_date)
        rs = db.execute(sql, params)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    @cache(cache_key_for_balance)
    def get_balance_by_account(cls, wallet_account_id):
        wallet_account = WalletAccount.get(wallet_account_id)
        transactions = cls.get_multi_by_account(wallet_account)
        return sum(t.balance_amount for t in transactions
                   if t.status is WalletTransaction.Status.success)

    @classmethod
    @cache(cache_key_for_sum_amount)
    def sum_amount(cls, type_, status=Status.success):
        assert isinstance(type_, cls.Type)
        assert isinstance(status, cls.Status)
        sql = ('select sum(amount) from {0} where status = %s and'
               ' type = %s').format(cls.table_name)
        params = (status.value, type_.value)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0] or decimal.Decimal(0)
        else:
            return decimal.Decimal(0)

    @classmethod
    def get_user_ids_by_transaction(cls):
        sql = 'select distinct(account_id) from {.table_name}'.format(cls)
        rs = db.execute(sql)
        return [str(r[0]) for r in rs]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_bankcard(cls, bankcard_id):
        mc.delete(cls.cache_key_by_bankcard.format(**locals()))

    @classmethod
    def clear_cache_by_account(cls, wallet_account_id):
        for status in cls.Status:
            mc.delete(cls.cache_key_by_account.format(**locals()))

    @classmethod
    def clear_cache_for_balance(cls, wallet_account_id):
        mc.delete(cls.cache_key_for_balance.format(**locals()))

    @classmethod
    def clear_cache_for_sum_amount(cls):
        for type_, status in itertools.product(cls.Type, cls.Status):
            mc.delete(cls.cache_key_for_sum_amount.format(**locals()))

    @classmethod
    def clear_cache_by_transaction_id(cls, transaction_id):
        mc.delete(cls.cache_key_by_transaction_id.format(**locals()))

    def transfer_status(self, status):
        assert isinstance(status, self.Status)

        sql = 'update {0} set status = %s where id = %s'.format(self.table_name)
        params = (status.value, self.id_)
        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)
        self.clear_cache_by_bankcard(self.bankcard_id)
        self.clear_cache_by_account(self.account_id)
        self.clear_cache_for_balance(self.account_id)
        self.clear_cache_for_sum_amount()
        self.clear_cache_by_transaction_id(self.transaction_id)

        old_status = self.status
        self._status = status.value

        transaction_status_changed.send(
            self, old_status=old_status, new_status=status)

        return self.status


@before_deleting_bankcard.connect
def check_bankcard_usage(sender, bankcard_id, user_id):
    ids = WalletTransaction.get_ids_by_bankcard(bankcard_id)
    transactions = (WalletTransaction.get(id_) for id_ in ids)
    return not any(
        transaction.status is WalletTransaction.Status.success
        for transaction in transactions)


@account_status_changed.connect
def warn_for_broken_account(sender, previous_status, current_status):
    if current_status is not WalletAccount.Status.broken:
        return
    ids = WalletTransaction.get_ids_by_account(sender.id_)
    if ids:
        sentry.captureMessage(u'有交易的零钱包帐号被报异常', extra={
            'previous_status': previous_status,
            'current_status': current_status,
            'wallet_account_id': sentry.id_,
            'transaction_ids': ids,
        })
