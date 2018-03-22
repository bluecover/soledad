# -*- coding: utf-8 -*-

from enum import Enum
from datetime import datetime

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.account import Account as LocalAccount
from .errors import RepeatRegisterError, NotFoundError, RemoteAccountOccupiedError
from .vendor import Vendor


class Account(object):
    table_name = 'hoarder_account'
    cache_key = 'hoarder:account:{vendor_id}:{account_id}'
    cache_all_ids_by_vendor = 'hoarder:account:all_ids:{vendor_id}'

    class Status(Enum):
        """目前考虑两个状态, 默认为启用状态。"""
        # 启用
        enabled = 'E'
        # 禁用 ，用户不可购买关联商户产品。
        disabled = 'D'

    def __init__(self, account_id, remote_id, vendor_id, bind_time, status):
        self.account_id = str(account_id)
        self.remote_id = remote_id
        self.bind_time = bind_time
        self.vendor_id = vendor_id
        self._status = status

    @cached_property
    def local_account(self):
        return LocalAccount.get(self.account_id)

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, new_status):
        assert isinstance(new_status, self.Status)
        sql = 'update {.table_name} set status=%s'.format(self)
        params = (new_status.value,)
        db.execute(sql, params)
        db.commit()
        self._status = new_status.value

        self.clear_cache(self.vendor_id, self.account_id)

    @property
    def vendor(self):
        return Vendor.get(self.vendor_id)

    @classmethod
    def bind(cls, vendor_id, account_id, remote_id):
        if not LocalAccount.get(account_id):
            raise NotFoundError(account_id, LocalAccount)

        if cls.get(vendor_id, account_id):
            raise RepeatRegisterError(account_id)

        if cls.get_by_remote(vendor_id, remote_id):
            raise RemoteAccountOccupiedError(remote_id)

        sql = ('insert into {.table_name} (account_id, remote_id, status, '
               'bind_time, vendor_id) values (%s, %s, %s, %s, %s)').format(cls)
        params = (account_id, remote_id, cls.Status.enabled.value, datetime.now(), vendor_id,)
        db.execute(sql, params)
        db.commit()

        cls.clear_cache(vendor_id, account_id)

    @classmethod
    def unbind(cls, vendor_id, account_id):
        sql = ('delete from {.table_name} where vendor_id=%s and account_id=%s').format(cls)
        params = (vendor_id, account_id,)

        db.execute(sql, params)
        db.commit()

        cls.clear_cache(vendor_id, account_id)

    @classmethod
    def get(cls, vendor_id, account_id):
        return cls.get_by_local(vendor_id=vendor_id, account_id=account_id)

    @classmethod
    @cache(cache_key)
    def get_by_local(cls, vendor_id, account_id):
        sql = ('select account_id, remote_id, bind_time, status, vendor_id from {.table_name} '
               'where vendor_id=%s and account_id=%s').format(cls)
        params = (vendor_id, account_id,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_all_ids_by_vendor)
    def get_all_ids_by_vendor_id(cls, vendor_id):
        sql = ('select account_id from {.table_name} '
               'where vendor_id=%s').format(cls)
        params = (vendor_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_by_remote(cls, vendor_id, remote_id):
        sql = ('select account_id from {.table_name} '
               'where vendor_id=%s and remote_id=%s').format(cls)
        params = (vendor_id, remote_id,)
        rs = db.execute(sql, params)
        return cls.get(vendor_id, rs[0][0]) if rs else None

    @classmethod
    def clear_cache(cls, vendor_id, account_id):
        mc.delete(cls.cache_key.format(vendor_id=vendor_id, account_id=account_id))
        mc.delete(cls.cache_all_ids_by_vendor.format(vendor_id=vendor_id))
