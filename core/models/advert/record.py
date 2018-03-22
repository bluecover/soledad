# coding: utf-8

from datetime import datetime

from libs.db.store import db
from libs.cache import mc, cache

from core.models.base import EntityModel
from .kind import AdvertKind


class AdvertRecord(EntityModel):
    """好规划弹窗广告"""

    table_name = 'advert_record'
    cache_key = 'advert:record:{id_}'

    def __init__(self, user_id, kind_id, creation_time):
        self.user_id = str(user_id)
        self.kind_id = str(kind_id)
        self.creation_time = creation_time

    @property
    def kind(self):
        return AdvertKind.get(self.kind_id)

    @classmethod
    def add(cls, user_id, kind_id):
        sql = (
            'insert into {.table_name} (user_id, kind_id, creation_time) '
            'values (%s, %s, %s)').format(cls)
        params = (user_id, kind_id, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select user_id, kind_id, creation_time '
            'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_user_and_kind(cls, user_id, kind_id):
        sql = 'select id from {.table_name} where user_id=%s and kind_id=%s'.format(cls)
        params = (user_id, kind_id)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))
