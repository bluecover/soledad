from __future__ import print_function, absolute_import, unicode_literals

import datetime
import contextlib

from libs.db.store import db
from libs.logger.rsyslog import rsyslog
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.profile.bankcard import BankCard
from core.models.profile.signals import bankcard_updated
from .account import WalletAccount
from .providers import ServiceProvider
from .signals import account_status_changed


class WalletBankcardBinding(EntityModel):
    """The remote binding status of bankcard.

    This is an internal model. Please do not use it out of this package.
    """

    class Meta:
        repr_attr_names = ['bankcard_id', 'provider_id', 'creation_time']

    table_name = 'wallet_bankcard_binding'
    cache_key = 'wallet:bankcard:binding:{id_}'
    cache_by_bankcard_key = 'wallet:bankcard:{bankcard_id}:{provider_id}:id'

    def __init__(self, id_, bankcard_id, provider_id, is_confirmed,
                 creation_time):
        self.id_ = str(id_)
        self.bankcard_id = str(bankcard_id)
        self.provider_id = provider_id
        self.is_confirmed = bool(is_confirmed)
        self.creation_time = creation_time

    @classmethod
    @contextlib.contextmanager
    def record_for_binding(cls, bankcard, provider):
        """This method is a context manager for binding bankcard.

        The caller should access the remote API of third-party service provider
        with this context.

        :param bankcard: The bankcard instance.
        :param provider: The service provider instance.
        """
        assert isinstance(bankcard, BankCard)
        assert isinstance(provider, ServiceProvider)

        id_ = cls.get_id_by_bankcard(bankcard.id_, provider.id_)
        if not id_:
            sql = ('insert into {0} (bankcard_id, provider_id, is_confirmed,'
                   ' creation_time) '
                   'values (%s, %s, %s, %s)').format(cls.table_name)
            params = (bankcard.id_, provider.id_, False,
                      datetime.datetime.now())
            id_ = db.execute(sql, params)
            db.commit()

        yield

        sql = ('update {0} set is_confirmed = %s '
               'where id = %s').format(cls.table_name)
        params = (True, id_)
        db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_bankcard(bankcard.id_, provider.id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, bankcard_id, provider_id, is_confirmed,'
               ' creation_time from {0} where id = %s').format(cls.table_name)
        params = (id_,)

        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_by_bankcard_key)
    def get_id_by_bankcard(cls, bankcard_id, provider_id):
        sql = ('select id from {0} where bankcard_id = %s and'
               ' provider_id = %s').format(cls.table_name)
        params = (bankcard_id, provider_id)

        rs = db.execute(sql, params)
        return rs[0][0] if rs else None

    @classmethod
    def get_by_bankcard(cls, bankcard, provider):
        assert isinstance(bankcard, BankCard)
        assert isinstance(provider, ServiceProvider)
        id_ = cls.get_id_by_bankcard(bankcard.id_, provider.id_)
        return cls.get(id_) if id_ else None

    @classmethod
    def get_multi_by_user(cls, user_id, provider):
        bankcards = BankCard.get_multi_by_user(user_id)
        generator = (cls.get_by_bankcard(b, provider) for b in bankcards)
        return [binding for binding in generator if binding]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_bankcard(cls, bankcard_id, provider_id):
        mc.delete(cls.cache_by_bankcard_key.format(**locals()))

    def freeze(self):
        self.is_confirmed = False
        sql = ('update {0} set is_confirmed = %s '
               'where id = %s').format(self.table_name)
        params = (self.is_confirmed, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)

    def enable(self):
        self.is_confirmed = True
        sql = ('update {0} set is_confirmed = %s '
               'where id = %s').format(self.table_name)
        params = (self.is_confirmed, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)


def is_bound_bankcard(bankcard, provider):
    assert isinstance(bankcard, BankCard)
    assert isinstance(provider, ServiceProvider)
    binding = WalletBankcardBinding.get_by_bankcard(bankcard, provider)
    return binding and binding.is_confirmed


@bankcard_updated.connect
def freeze_updated_bankcard(sender, changed_fields):
    if 'mobile_phone' not in changed_fields:
        return
    for provider in ServiceProvider.get_all():
        binding = WalletBankcardBinding.get_by_bankcard(sender, provider)
        if not binding:
            continue
        binding.freeze()
        rsyslog.send('%r freezed' % binding, tag='wallet_unbind_bankcard')


@account_status_changed.connect
def freeze_failure_account(sender, previous_status, current_status):
    if (previous_status is current_status or
            current_status is WalletAccount.Status.success):
        return
    bindings = WalletBankcardBinding.get_multi_by_user(
        sender.local_account.id_, sender.service_provider)
    for binding in bindings:
        binding.freeze()
