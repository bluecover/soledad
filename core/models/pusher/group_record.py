# coding: utf-8

from datetime import datetime

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel


class GroupPushRecord(EntityModel):

    table_name = 'pusher_group_record'
    cache_key = 'pusher:group_record:v1:{id_}'
    cache_key_by_bilayer_kinds = (
        'pusher:group_record:v1:notice_kind:{notification_kind_id}:sub_kind:{subdivision_kind_id}')

    def __init__(self, id_, notification_kind_id, subdivision_kind_id, is_pushed,
                 jmsg_id, creation_time, push_time):
        self.id_ = str(id_)
        self.notification_kind_id = str(notification_kind_id)
        self.subdivision_kind_id = str(subdivision_kind_id)
        self.is_pushed = is_pushed
        self.jmsg_id = jmsg_id
        self.creation_time = creation_time
        self.push_time = push_time

    @cached_property
    def notification_kind(self):
        from core.models.notification import NotificationKind
        return NotificationKind.get(self.notification_kind_id)

    @classmethod
    def create(cls, notification_kind, subdivision_kind=None):
        from core.models.notification import NotificationKind
        assert isinstance(notification_kind, NotificationKind)
        assert subdivision_kind is None or isinstance(
            subdivision_kind, notification_kind.subdivision_kind_cls)

        # 双层通知类型组播由于面向平台、标签组，可以进行单例检查
        # 对于面向多别名、多设备的组播，由于有单次组播限制，因此无法进行单例检查
        if subdivision_kind:
            if cls.get_by_bilayer_kinds(notification_kind, subdivision_kind):
                raise ValueError('the bilayer multicast/broadcast has been pushed once')

        sql = ('insert into {.table_name} (notification_kind_id, subdivision_kind_id, '
               'is_pushed, creation_time) values (%s, %s, %s, %s)').format(cls)
        params = (notification_kind.id_, subdivision_kind.id_ if subdivision_kind else None,
                  False, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_bilayer_kinds(
            notification_kind.id_, subdivision_kind.id_ if subdivision_kind else None)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, notification_kind_id, subdivision_kind_id, is_pushed, jmsg_id, '
               'creation_time, push_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_bilayer_kinds)
    def get_id_by_bilayer_kinds(cls, notification_kind_id, subdivision_kind_id=None):
        sql = ('select id from {0.table_name} where notification_kind_id=%s and '
               'subdivision_kind_id {1} %s').format(cls, '=' if subdivision_kind_id else 'is')
        params = (notification_kind_id, subdivision_kind_id or 'null')
        rs = db.execute(sql, params)
        if rs:
            return str(rs[0][0])

    @classmethod
    def get_by_bilayer_kinds(cls, notification_kind, subdivision_kind):
        id_ = cls.get_id_by_bilayer_kinds(
            notification_kind.id_, subdivision_kind.id_)
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

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_bilayer_kinds(cls, notification_kind_id, subdivision_kind_id):
        mc.delete(cls.cache_key_by_bilayer_kinds.format(**locals()))
