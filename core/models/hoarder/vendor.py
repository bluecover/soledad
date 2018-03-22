# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum

from libs.db.store import db
from libs.cache import mc, cache


class Provider(Enum):
    sxb = 'sxb'
    xm = 'xm'
    zw = 'zw'
    ms = 'ms'


class Vendor(object):
    """供应商"""

    table_name = 'hoarder_vendor'
    cache_key = 'hoarder:vendor:{vendor_id}'

    class Status(Enum):
        enable = 'E'
        disabled = 'D'

    def __init__(self, id_, name, protocol, status, creation_time):
        self.id_ = str(id_)
        self.name = name
        self.protocol = protocol
        self._status = status
        self.creation_time = creation_time

    @property
    def provider(self):
        return Provider(self.name)

    @classmethod
    def add(cls, name, protocol):
        sql = ('insert into {.table_name} (name, protocol, status, creation_time) '
               'values(%s, %s, %s, %s)').format(cls)
        params = (name, protocol, cls.Status.enable.value, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        return cls.get(id_)

    @classmethod
    def get_by_name(cls, name):
        assert isinstance(name, Provider)
        sql = ('select id '
               'from {.table_name} where name=%s').format(cls)
        params = (name.value,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(cache_key)
    def get(cls, vendor_id):
        sql = ('select id, name, protocol, status, creation_time '
               'from {.table_name} where id=%s').format(cls)
        params = (vendor_id,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_all(cls):
        sql = 'SELECT id FROM {.table_name}'.format(cls)
        rs = db.execute(sql, )
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_enabled_vendors(cls):
        sql = 'select id from {.table_name} where status=%s'.format(cls)
        params = (cls.Status.enable.value,)
        rs = db.execute(sql, params, )
        return [cls.get(r[0]) for r in rs]

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, new_status):
        assert isinstance(new_status, self.Status)
        db.execute('update {.table_name} set status=%s where id=%s',
                   (new_status.value, self.id_))
        db.commit()
        self._status = new_status.value
        self.clear_cache(self.id_)

    @classmethod
    def clear_cache(cls, vendor_id):
        mc.delete(cls.cache_key.format(vendor_id=vendor_id))
