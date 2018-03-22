# coding: utf-8

from datetime import datetime

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel


class UniversePushRecord(EntityModel):

    table_name = 'pusher_universe_record'
    cache_key = 'pusher:universe_record:v1:{id_}'
    cache_key_by_bulletin = 'pusher:universe_record:v1:bulletin:{bulletin_id}'

    def __init__(self, id_, bulletin_id, is_pushed, jmsg_id, creation_time, push_time):
        self.id_ = str(id_)
        self.bulletin_id = str(bulletin_id)
        self.is_pushed = is_pushed
        self.jmsg_id = jmsg_id
        self.creation_time = creation_time
        self.push_time = push_time

    @cached_property
    def bulletin(self):
        from core.models.site.bulletin import Bulletin
        return Bulletin.get(self.bulletin_id)

    @classmethod
    def create(cls, bulletin):
        from core.models.site.bulletin import Bulletin
        assert isinstance(bulletin, Bulletin)

        sql = ('insert into {.table_name} (bulletin_id, is_pushed, creation_time) '
               'values (%s, %s, %s)').format(cls)
        params = (bulletin.id_, False, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_bulletin(bulletin.id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, bulletin_id, is_pushed, jmsg_id, creation_time, '
               'push_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_bulletin)
    def get_id_by_bulletin_id(cls, bulletin_id):
        sql = 'select id from {.table_name} where bulletin_id=%s'.format(cls)
        params = (bulletin_id, )
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_bulletin_id(cls, bulletin_id):
        id_ = cls.get_id_by_bulletin_id(bulletin_id)
        return cls.get(id_)

    def mark_as_pushed(self, msg_id):
        """标记推送已发出"""
        sql = ('update {.table_name} set is_pushed=%s, jmsg_id=%s, '
               'push_time=%s where id=%s').format(self)
        params = (True, msg_id, datetime.now(), self.id_)
        db.execute(sql, params)
        db.commit()

        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

        self.clear_cache(self.id_)
        self.clear_cache_by_bulletin(self.bulletin_id)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_bulletin(cls, bulletin_id):
        mc.delete(cls.cache_key_by_bulletin.format(**locals()))
