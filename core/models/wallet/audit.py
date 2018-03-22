# coding:utf-8

from __future__ import print_function, absolute_import, unicode_literals

import uuid
import datetime

from werkzeug.utils import cached_property
from zslib.wrappers import TransactionRecord

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.wallet.transaction import WalletTransaction
from core.models.wallet.account import WalletAccount


class WalletAudit(EntityModel):
    table_name = 'wallet_audit'
    cache_key = 'wallet:audit:{id_}:v3'

    def __init__(self, id_, wallet_account_id, local_transaction_id, local_transaction_type,
                 local_transaction_amount, local_transaction_time, remote_transaction_id,
                 remote_transaction_type, remote_transaction_amount, remote_transaction_time,
                 audit_time, local_status, remote_status, is_modified, is_confirmed):
        self.id_ = str(id_)
        self.wallet_account_id = str(wallet_account_id)
        self.local_transaction_id = local_transaction_id
        self.local_transaction_type = local_transaction_type
        self.local_transaction_amount = local_transaction_amount
        self.local_transaction_time = local_transaction_time
        self.remote_transaction_id = remote_transaction_id
        self.remote_transaction_type = remote_transaction_type
        self.remote_transaction_amount = remote_transaction_amount
        self.remote_transaction_time = remote_transaction_time
        self.audit_time = audit_time
        self._local_status = local_status
        self._remote_status = remote_status
        self.is_modified = bool(is_modified)
        self.is_confirmed = bool(is_confirmed)

    @cached_property
    def wallet_account(self):
        return WalletAccount.get(self.wallet_account_id)

    @property
    def local_status(self):
        return WalletTransaction.Status(self._local_status)

    @property
    def remote_status(self):
        return TransactionRecord.TransactionStatus(self._remote_status)

    @property
    def local_type(self):
        if self.local_transaction_type:
            return WalletTransaction.Type(self.local_transaction_type)

    @property
    def remote_type(self):
        if self.remote_transaction_type:
            return TransactionRecord.TransactionType(self.remote_transaction_type)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, wallet_account_id, local_transaction_id, local_transaction_type,'
               ' local_transaction_amount, local_transaction_time, remote_transaction_id,'
               ' remote_transaction_type, remote_transaction_amount, remote_transaction_time, '
               ' audit_time, local_status, remote_status, is_modified, is_confirmed'
               ' from {.table_name} where id=%s').format(cls)
        rs = db.execute(sql, (id_,))
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_by_local_transaction_id(cls, local_transaction_id):
        sql = 'select id from {.table_name} where local_transaction_id=%s'.format(cls)
        rs = db.execute(sql, (local_transaction_id,))
        if rs:
            return cls.get(rs[0])

    @classmethod
    def get_unconfirmed_ids(cls):
        sql = 'select id from {.table_name} where is_confirmed=%s'.format(cls)
        rs = db.execute(sql, False)
        return [r[0] for r in rs]

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def add(cls, wallet_account, audit_time, is_modified, is_confirmed, local_status,
            remote_status, local_transaction_id=None, local_transaction_type=None,
            local_transaction_amount=None, local_transaction_time=None, remote_transaction_id=None,
            remote_transaction_type=None, remote_transaction_amount=None,
            remote_transaction_time=None):
        assert isinstance(wallet_account, WalletAccount)

        if not local_transaction_id and not remote_transaction_id:
            raise ValueError('specify at least one side transaction_id is necessary')

        sql = (
            'insert into {.table_name} (wallet_account_id,'
            ' local_transaction_id, local_transaction_type,'
            ' local_transaction_amount, local_transaction_time, '
            ' remote_transaction_id, remote_transaction_type,'
            ' remote_transaction_amount, remote_transaction_time, audit_time,'
            ' local_status, remote_status, is_modified,is_confirmed) '
            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'
            ' %s)').format(cls)

        local_transaction_type = (
            local_transaction_type.value if local_transaction_type else None)
        remote_transaction_type = (
            remote_transaction_type.value if remote_transaction_type else None)
        local_status = (
            local_status.value if local_status else None)
        remote_status = (
            remote_status.value if remote_status else None)

        params = (
            wallet_account.id_, local_transaction_id, local_transaction_type,
            local_transaction_amount, local_transaction_time,
            remote_transaction_id, remote_transaction_type,
            remote_transaction_amount, remote_transaction_time, audit_time,
            local_status, remote_status, is_modified, is_confirmed)

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)

        return cls.get(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def compare_and_add(cls, wallet_account, local_transaction=None, remote_transaction=None):
        is_confirmed = is_modified = False
        if not local_transaction and not remote_transaction:
            raise ValueError('specify at least one side transaction is necessary')

        if local_transaction and remote_transaction:
            if all([
                local_transaction.status in (
                    WalletTransaction.Status.failure, WalletTransaction.Status.raw),
                remote_transaction.transaction_status is
                    TransactionRecord.TransactionStatus.success,
            ]):
                local_transaction.transfer_status(WalletTransaction.Status.success)
                is_modified = True
            elif all([
                local_transaction.status in (
                    WalletTransaction.Status.failure, WalletTransaction.Status.raw),
                remote_transaction.transaction_status is
                    TransactionRecord.TransactionStatus.failure,
            ]):
                remote_transaction = None
                is_confirmed = True
            elif (remote_transaction.transaction_status is
                    TransactionRecord.TransactionStatus.failure):
                remote_transaction = None
            else:
                is_confirmed = True

        if local_transaction:
            local_transaction_id = local_transaction.id_
            local_transaction_type = local_transaction.type_
            local_transaction_amount = local_transaction.amount
            local_transaction_time = local_transaction.creation_time
            if local_transaction.status in (
                    WalletTransaction.Status.failure, WalletTransaction.Status.raw):
                local_transaction_status = WalletTransaction.Status.failure
            else:
                local_transaction_status = local_transaction.status
        else:
            local_transaction_id = None
            local_transaction_type = None
            local_transaction_amount = None
            local_transaction_time = None
            local_transaction_status = WalletTransaction.Status.failure

        if remote_transaction:
            remote_transaction_id = remote_transaction.transaction_id
            remote_transaction_type = remote_transaction.transaction_type
            remote_transaction_amount = remote_transaction.transaction_amount
            remote_transaction_time = remote_transaction.transaction_time
            remote_transaction_status = remote_transaction.transaction_status
        else:
            remote_transaction_id = None
            remote_transaction_type = None
            remote_transaction_amount = None
            remote_transaction_time = None
            remote_transaction_status = TransactionRecord.TransactionStatus.failure

        return cls.add(
            wallet_account, datetime.datetime.now(), is_modified, is_confirmed,
            local_transaction_status, remote_transaction_status,
            local_transaction_id, local_transaction_type,
            local_transaction_amount, local_transaction_time,
            remote_transaction_id, remote_transaction_type,
            remote_transaction_amount, remote_transaction_time)

    def confirm(self):
        sql = 'update {.table_name} set is_confirmed=%s where id=%s'.format(self)
        params = (True, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self.is_confirmed = True


def fetch_remote_records(client, wallet_account, date_from, date_to):
    response = client.list_transactions(
        transaction_id=uuid.uuid4().hex,
        user_id=wallet_account.secret_id,
        date_from=date_from,
        date_to=date_to,
        transaction_filter=client.TransactionFilter.all_)
    return {record.transaction_id: record for record in response.records}


def get_active_accounts_by_date(date):
    sql = ('select distinct(account_id) from wallet_transaction'
           ' where date(creation_time)=%s')
    params = (date,)
    rs = db.execute(sql, params)
    for r in rs:
        yield WalletAccount.get(r[0])


def audit_by_account(client, wallet_account, date_from, date_to):
    assert isinstance(wallet_account, WalletAccount)

    args = (wallet_account, date_from, date_to)
    remote_records = fetch_remote_records(client, *args)
    local_records = WalletTransaction._get_by_account_and_date(*args)

    for local in local_records:
        remote = remote_records.pop(local.transaction_id, None)
        WalletAudit.compare_and_add(
            wallet_account=wallet_account,
            local_transaction=local,
            remote_transaction=remote)

    # 弥补本地可能存在而没有获取到的情况
    for k, _ in remote_records.items():
        local_record = WalletTransaction.get_by_transaction_id(k)
        if local_record:
            remote_record = remote_records.pop(k)
            WalletAudit.compare_and_add(
                wallet_account=wallet_account,
                local_transaction=local_record,
                remote_transaction=remote_record)

    for remote in remote_records.values():
        WalletAudit.compare_and_add(
            wallet_account=wallet_account,
            remote_transaction=remote)
