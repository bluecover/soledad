# coding: utf-8

"""
    Two-Factor Authentication
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Give more security to our accounts.
"""

import os
import time
import datetime

from werkzeug.utils import cached_property
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.twofactor.totp import TOTP, InvalidToken

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.decorators import coerce_type
from core.models.user.account import Account
from .consts import TWOFACTOR_APPS


class TwoFactor(EntityModel):
    """The required information for Two-Factor Authentication users."""

    table_name = 'security_twofactor'
    cache_key = 'security:twofactor:user:{user_id}:v1'

    totp_length = 6
    totp_algorithm = SHA1()
    totp_time_step = 30
    totp_backend = default_backend()
    totp_issuer = '好规划'

    def __init__(self, id_, secret_key, is_enabled, creation_time):
        self.id_ = bytes(id_)
        self.secret_key = bytes(secret_key)
        self.is_enabled = bool(is_enabled)
        self.creation_time = creation_time

    @cached_property
    def totp(self):
        """The implementation of Time-based One-Time Password algorithm.

        :rtype: cryptography.hazmat.primitives.twofactor.totp.TOTP
        """
        return TOTP(
            self.secret_key, self.totp_length, self.totp_algorithm,
            self.totp_time_step, self.totp_backend)

    @cached_property
    def user(self):
        """The current account."""
        return Account.get(self.id_)

    def generate(self, timestamp=None):
        """Generates an one-time password.

        :return: A digit string.
        """
        timestamp = time.time() if timestamp is None else timestamp
        return self.totp.generate(timestamp)

    def verify(self, password, timestamp=None, silent=True):
        timestamp = time.time() if timestamp is None else timestamp
        try:
            self.totp.verify(bytes(password), timestamp)
        except InvalidToken:
            if silent:
                return False
            else:
                raise
        return True

    def get_provisioning_uri(self):
        account_name = self.user.screen_ident or str(self.user.id_)
        return self.totp.get_provisioning_uri(account_name, self.totp_issuer)

    @classmethod
    def add(cls, user_id):
        sql = ('insert into {0} (id, secret_key, is_enabled, creation_time) '
               'values (%s, %s, %s, %s)').format(cls.table_name)
        params = (user_id, cls.generate_key(), False, datetime.datetime.now())
        db.execute(sql, params)
        db.commit()
        return cls.get(user_id)

    @classmethod
    @cache(cache_key)
    def get(cls, user_id):
        sql = ('select id, secret_key, is_enabled, creation_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (user_id,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_or_add(cls, user_id):
        return cls.get(user_id) or cls.add(user_id)

    def enable(self, password, timestamp=None):
        self.verify(password, timestamp=timestamp, silent=False)
        self._toggle(True)

    def disable(self):
        self._toggle(False)

    def renew(self):
        self.disable()

        secret_key = self.generate_key()
        sql = ('update {0} set secret_key = %s '
               'where id = %s').format(self.table_name)
        params = (secret_key, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self.secret_key = bytes(secret_key)
        self.__dict__.pop('totp', None)

    def _toggle(self, is_enabled):
        sql = ('update {0} set is_enabled = %s '
               'where id = %s').format(self.table_name)
        params = (bool(is_enabled), self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self.is_enabled = bool(is_enabled)

    @classmethod
    def clear_cache(cls, user_id):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def generate_key(cls):
        return os.urandom(20)


@coerce_type(list)
def get_twofactor_apps(user_agent):
    for name, url, platform_urls in TWOFACTOR_APPS:
        if user_agent and user_agent.platform in platform_urls:
            url = platform_urls[user_agent.platform]
        yield (name, url)
