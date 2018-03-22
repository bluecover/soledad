# coding: utf-8
from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel


class Product(EntityModel):

    table_name = 'activity_realm'
    cache_key = 'activity_realm:v1:{id_}'
    cache_key_all = 'activity_realm_all:v1'
    cache_key_by_sn = 'activity_realm_by_sn:v1:{sn}'

    def __init__(self, id, name, sn):
        self.id_ = id
        self.name = name
        self.sn = sn

    @classmethod
    def add(cls, name, sn):
        """Add new product.
        """
        c = cls.get_by_sn(sn)
        if c:
            return c
        sql = ('insert ignore into {.table_name} (name, sn) '
               'values (%s, %s)').format(cls)
        params = (name, sn)
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_, sn)
        return cls.get(id_)

    @classmethod
    def get_id_by_sn(cls, sn):
        sql = ('select id from {.table_name} '
               'where sn = %s').format(cls)
        params = (sn,)
        rs = db.execute(sql, params)
        return rs[0][0] if rs else None

    @classmethod
    @cache(cache_key_by_sn)
    def get_by_sn(cls, sn):
        id_ = cls.get_id_by_sn(sn)
        return cls.get(id_) if id_ else None

    @classmethod
    @cache(cache_key_all)
    def get_ids(cls):
        sql = ('select id from {.table_name} '
               'order by id').format(cls)
        rs = db.execute(sql)
        return [r[0] for r in rs]

    @classmethod
    def get_all(cls):
        ids = cls.get_ids()
        return [cls.get(id_) for id_ in ids]

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, name, sn from {.table_name} '
               'where id = %s ').format(cls)
        param = (id_,)
        rs = db.execute(sql, param)
        return cls(*rs[0]) if rs else None

    @classmethod
    def clear_cache(cls, id_, sn):
        mc.delete(cls.cache_key.format(id_=id_))
        mc.delete(cls.cache_key_by_sn.format(sn=sn))
        mc.delete(cls.cache_key_all)
