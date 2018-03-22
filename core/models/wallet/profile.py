from __future__ import print_function, absolute_import, unicode_literals

from datetime import datetime

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account


class WalletProfile(EntityModel):
    """The user profile information in "wallet"."""

    table_name = 'wallet_profile'
    cache_key = 'wallet:profile:{id_}:v1'

    def __init__(self, id_, creation_time):
        self.id_ = id_
        self.creation_time = creation_time

    @cached_property
    def user(self):
        return Account.get(self.id_)

    @classmethod
    def add(cls, user_id):
        """Adds profile entity for specific user.

        Don't use it without any user's operation. If you need to obtain an
        attribute, use :meth:`.WalletProfile.get` instead::

            wallet_profile = WalletProfile.get(g.user.id_)
            wallet_foo = wallet_profile.foo if wallet_profile else None

        The following way will cause users lost their landing page::

            wallet_foo = WalletProfile.add(g.user.id_).

        :param user_id: The id of local account.
        """
        existent = cls.get(user_id)
        if existent:
            return existent

        sql = ('insert into {0} (id, creation_time) '
               'values (%s, %s)').format(cls.table_name)
        params = (user_id, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        """Gets profile entity."""
        sql = ('select id, creation_time from {0} '
               'where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))
