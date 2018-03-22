# -*- coding: utf-8 -*-

import time
from datetime import datetime
from enum import Enum

from libs.db.store import db
from libs.cache import mc, cache


class AppBanner(object):
    """ APP首页banner """

    table_name = 'app_banner'
    cache_key = 'app_banner:v2:{id_}'

    class Status(Enum):
        enabled = 'E'
        disabled = 'D'

    def __init__(self, id_, name, status, image_url, link_url, sequence, creation_time):
        self.id_ = str(id_)
        self.name = name
        self.status = status
        self.image_url = image_url
        self.link_url = link_url
        self.sequence = sequence
        self.creation_time = creation_time

    @classmethod
    def add(cls, name, image_url, link_url, sequence=None, enable=False):
        status = AppBanner.Status.enabled if enable else AppBanner.Status.disabled
        sequence = sequence if sequence is not None else int(time.time())
        sql = ('insert into {.table_name} '
               '(name, status, image_url, link_url, sequence, creation_time) '
               'values(%s, %s, %s, %s, %s, %s)').format(cls)
        params = (name, status.value, image_url, link_url, sequence, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, name, status, image_url, link_url, sequence, creation_time '
               'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def gets_by_status(cls, status):
        sql = ('select id from {.table_name} where status=%s'
               'order by sequence').format(cls)
        params = (status.value,)
        rs = db.execute(sql, params)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def enable_banner(cls, id_, enable=True):
        status = AppBanner.Status.enabled if enable else AppBanner.Status.disabled
        sql = ('update {.table_name} set status = %s '
               'where id = %s').format(cls)
        params = (status.value, id_)
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))
