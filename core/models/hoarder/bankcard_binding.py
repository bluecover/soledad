# coding: utf-8

from datetime import datetime

from libs.db.store import db
from libs.cache import mc, cache
from core.models.profile.bankcard import BankCard
from .vendor import Vendor


class BankcardBinding(object):

    table_name = 'hoarder_bankcard_binding'
    cache_key = 'hoarder:bankcard:binding:{id_}'
    cache_id_by_bankcard_vendor_key = (
        'hoarder:bankcard:binding:{bankcard_id}:{vendor_id}')

    def __init__(self, id_, user_id, bankcard_id,
                 vendor_id, is_confirmed, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.bankcard_id = str(bankcard_id)
        self.vendor_id = str(vendor_id)
        self.is_confirmed = bool(is_confirmed)
        self.creation_time = creation_time

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, user_id, bankcard_id, vendor_id, is_confirmed, creation_time'
            ' from {.table_name} where id=%s').format(cls)
        params = (id_, )
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_id_by_bankcard_vendor_key)
    def get_id_by_bankcard_vendor(cls, bankcard_id, vendor_id):
        sql = (
            'select id from {.table_name} where bankcard_id=%s'
            ' and vendor_id=%s').format(cls)
        params = (bankcard_id, vendor_id)
        rs = db.execute(sql, params)
        return rs[0] if rs else None

    @classmethod
    def get_by_bankcard_vendor(cls, bankcard_id, vendor_id):
        id_ = cls.get_id_by_bankcard_vendor(bankcard_id, vendor_id)
        return cls.get(id_)

    @classmethod
    def add_or_update(cls, user_id, bankcard_id, vendor_id):
        id_ = cls.get_id_by_bankcard_vendor(bankcard_id, vendor_id)
        if not id_:
            sql = (
                'insert into {.table_name} (user_id, bankcard_id, vendor_id,'
                ' is_confirmed, creation_time)'
                ' values(%s, %s, %s, %s, %s)').format(cls)
            params = (user_id, bankcard_id, vendor_id, True, datetime.now())
            id_ = db.execute(sql, params)
            db.commit()

            cls.clear_cache(id_)
            cls.clear_cache_id_by_bankcard_vendor(bankcard_id, vendor_id)

    @classmethod
    def freeze_available(cls, user_id):
        sql = ('update {.table_name} set is_confirmed=%s '
               ' where is_confirmed=%s and user_id=%s').format(cls)
        params = (False, True, user_id)
        db.execute(sql, params)
        db.commit()

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_id_by_bankcard_vendor(cls, bankcard_id, vendor_id):
        mc.delete(cls.cache_id_by_bankcard_vendor_key.format(
            bankcard_id=bankcard_id, vendor_id=vendor_id))


def is_bound_bankcard(bankcard, vendor):
    assert isinstance(bankcard, BankCard)
    assert isinstance(vendor, Vendor)
    binding = BankcardBinding.get_by_bankcard_vendor(bankcard.id_, vendor.id_)
    if binding:
        return binding.is_confirmed
