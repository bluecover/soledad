# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

import hmac
import base64
import collections

from core.models.bank import Partner


_ServiceProvider = collections.namedtuple('ServiceProvider', [
    'id_',
    'name',
    'secret_key',
    'bank_partner',
    'fund_code',
    'fund_name',
    'fund_company_name',
    'fund_bank_name',
])


class ServiceProvider(_ServiceProvider):
    """The service provider of wallet."""

    storage = {}

    def __init__(self, id_, *args, **kwargs):
        self.storage[int(id_)] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(int(id_))

    @classmethod
    def get_all(cls):
        return cls.storage.values()

    def make_secret_id(self, user_id):
        """Translates the local user id into a secret string which could be
        exposed to third-party.
        """
        normalized_user_id = bytes(user_id).lower().strip()
        digest = hmac.new(self.secret_key, normalized_user_id).digest()
        return base64.urlsafe_b64encode(digest)

    def is_avalable_bankcard(self, bankcard):
        return self.bank_partner in bankcard.bank.available_in


zhongshan = ServiceProvider(
    id_=1,
    name=u'中山证券',
    secret_key=b'2fb76708be2ff92f',
    bank_partner=Partner.zs,
    fund_code='000371',
    fund_name='民生现金宝',
    fund_company_name='民生加银',
    fund_bank_name='建设银行')
