from __future__ import print_function, absolute_import, unicode_literals

import os
import hashlib
import datetime
import contextlib

from enum import Enum
from werkzeug.utils import cached_property
from zslib.errors import BusinessError

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.user.signals import before_freezing_user
from .providers import ServiceProvider, zhongshan
from .signals import account_status_changed


class WalletAccount(EntityModel):
    """The third-party account for integrating with service providers."""

    table_name = 'wallet_account'
    cache_key = 'wallet:account:{id_}:v2'
    cache_by_local_account_key = 'wallet:account:{account_id}:{provider_id}'
    cache_for_all_ids_key = 'wallet:account:all_ids'

    class Status(Enum):
        raw = 'R'
        success = 'S'
        failure = 'F'
        broken = 'B'

    def __init__(self, id_, account_id, provider_id, secret_token, status_code,
                 creation_time, updated_time):
        self.id_ = str(id_)
        self.account_id = str(account_id)
        self.provider_id = provider_id
        self.secret_token = secret_token
        self.creation_time = creation_time
        self.updated_time = updated_time
        self._status = status_code

    @cached_property
    def secret_id(self):
        """The secret user id.

        It is used for communicating with specific service provider.
        """
        return self.service_provider.make_secret_id(self.account_id)

    @cached_property
    def local_account(self):
        return Account.get(self.account_id)

    @cached_property
    def service_provider(self):
        return ServiceProvider.get(self.provider_id)

    @property
    def status(self):
        return self.Status(self._status)

    @classmethod
    def gen_token(cls):
        """Generates a random token."""
        return hashlib.md5(os.urandom(64)).hexdigest()

    @classmethod
    def add(cls, account, provider):
        """Creates a wallet account.

        The account information should be bound with the service provider.

        :param account: The local account.
        :type account: :class:`core.models.user.account.Account`
        :param provider: The service provider.
        :type provider: :class:`core.models.wallet.providers.ServiceProvider`
        :return: An instance of :class:`WalletAccount`
        :raises MySQLdb.IntegrityError: if account id exists
        """
        assert isinstance(provider, ServiceProvider)
        now = datetime.datetime.now()

        sql = ('insert into {0} (account_id, provider_id, secret_token,'
               ' status_code, creation_time, updated_time) '
               'values (%s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (account.id_, provider.id_, cls.gen_token(),
                  cls.Status.raw.value, now, now)

        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_local_account(account.id_, provider.id_)
        cls.clear_cache_for_all_ids()

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        """Gets a wallet account.

        :param id_: The id of wallet account. It is different to id of local
                    account.
        :return: An instance of :class:`WalletAccount`, or ``None``.
        """
        sql = ('select id, account_id, provider_id, secret_token,'
               ' status_code, creation_time, updated_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_for_all_ids_key)
    def get_all_ids(cls):
        """Gets all id of wallet accounts."""
        sql = 'select id from {0}'.format(cls.table_name)
        rs = db.execute(sql)
        return [str(r[0]) for r in rs]

    @classmethod
    @cache(cache_by_local_account_key)
    def get_id_by_local_account(cls, account_id, provider_id):
        """Gets the id of wallet account by the id of local account and the
        id of service provider.

        :param account_id: The id of local account.
        :param provider_id: The id of service provider.
        """
        sql = ('select id from {0} where account_id = %s and'
               ' provider_id = %s').format(cls.table_name)
        params = (account_id, provider_id)
        rs = db.execute(sql, params)
        if rs:
            return str(rs[0][0])

    @classmethod
    def get_by_local_account(cls, account, provider):
        """Gets wallet account by a local account and a specific service
        provider.
        """
        assert isinstance(provider, ServiceProvider)

        id_ = cls.get_id_by_local_account(account.id_, provider.id_)
        if id_ is not None:
            return cls.get(id_)

    @classmethod
    def get_or_add(cls, account, provider):
        """Finds account and creates new one if nothing found.

        :type account: :class:`core.models.user.account.Account`
        :type provider: :class:`core.models.wallet.providers.ServiceProvider`
        """
        return (cls.get_by_local_account(account, provider) or
                cls.add(account, provider))

    def transfer_status(self, status):
        assert isinstance(status, self.Status)
        previous_status = self.status
        self._status = status.value
        sql = ('update {0} set status_code = %s, updated_time = %s '
               'where id = %s').format(self.table_name)
        db.execute(sql, (self._status, datetime.datetime.now(), self.id_))
        db.commit()
        self.clear_cache(id_=self.id_)
        account_status_changed.send(
            self, previous_status=previous_status, current_status=self.status)
        return self.status

    @contextlib.contextmanager
    def track_broken_account(self):
        try:
            yield
        except BusinessError as e:
            if e.kind is BusinessError.kinds.account_broken:
                self.transfer_status(self.Status.broken)
            raise

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_local_account(cls, account_id, provider_id):
        mc.delete(cls.cache_by_local_account_key.format(**locals()))

    @classmethod
    def clear_cache_for_all_ids(cls):
        mc.delete(cls.cache_for_all_ids_key)


@before_freezing_user.connect
def check_wallet_account_existence(user):
    wallet_account = WalletAccount.get_by_local_account(user, zhongshan)
    return bool(wallet_account and wallet_account.status is WalletAccount.Status.success)

check_wallet_account_existence.product_name = 'wallet'
