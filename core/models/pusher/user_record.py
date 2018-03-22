# coding: utf-8

from datetime import datetime

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.pusher.binding import DeviceBinding


class UserPushRecord(EntityModel):

    class Status(Enum):
        created = 'C'
        pushed = 'P'
        received = 'R'
        clicked = 'K'

    Status.created.label = u'已创建'
    Status.pushed.sequence = u'已推送'
    Status.received.sequence = u'已接收'
    Status.clicked.sequence = u'已查阅'

    table_name = 'pusher_user_record'
    cache_key = 'pusher:user_record:v1:{id_}'
    cache_key_by_user = 'pusher:user_record:v1:user:{user_id}'
    cache_key_by_jmsg_id = 'pusher:user_record:v1:jmsg:{jmsg_id}'
    cache_key_by_device_and_notification = (
        'pusher:user_record:v1:device:{device_id}:notice:{notification_id}')

    def __init__(self, id_, user_id, device_id, notification_id, status, jmsg_id,
                 creation_time, push_time, received_time, clicked_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.device_id = device_id
        self.notification_id = str(notification_id)
        self._status = status
        self.jmsg_id = jmsg_id
        self.creation_time = creation_time
        self.push_time = push_time
        self.received_time = received_time
        self.clicked_time = clicked_time

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def notification(self):
        from core.models.notification import Notification
        return Notification.get(self.notification_id)

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        self._status = item.value

    @classmethod
    def create(cls, user, device_binding, notification):
        from core.models.notification import Notification

        assert isinstance(user, Account)
        assert isinstance(device_binding, DeviceBinding)
        assert isinstance(notification, Notification)

        if not (user.id_ == device_binding.user_id == notification.user_id):
            raise ValueError('invalid push tempt as user infos are unmatched')

        if cls.get_by_device_and_notification(
                device_binding.device_id, notification.id_):
            raise ValueError('notification can only be pushed once')

        sql = ('insert into {.table_name} (user_id, device_id, notification_id, '
               'status, creation_time) values (%s, %s, %s, %s, %s)').format(cls)
        params = (user.id_, device_binding.device_id, notification.id_,
                  cls.Status.created.value, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache_key_by_user(user.id_)
        cls.clear_cache_key_by_device_and_notification(
            device_binding.device_id, notification.id_)
        return cls.get(id_)

    def mark_as_pushed(self, msg_id):
        """标记推送已发出"""
        sql = ('update {.table_name} set status=%s, jmsg_id=%s, '
               'push_time=%s where id=%s').format(self)
        params = (self.Status.pushed.value, msg_id, datetime.now(), self.id_)
        self._commit_and_clear(sql, params)

    def mark_as_received(self):
        """标记推送已接收"""
        sql = ('update {.table_name} set status=%s, '
               'received_time=%s where id=%s').format(self)
        params = (self.Status.received.value, datetime.now(), self.id_)
        self._commit_and_clear(sql, params)

    def mark_as_clicked(self):
        """标记推送已被读"""
        sql = ('update {.table_name} set status=%s, '
               'clicked_time=%s where id=%s').format(self)
        params = (self.Status.clicked.value, datetime.now(), self.id_)
        self._commit_and_clear(sql, params)

    def _commit_and_clear(self, sql, params):
        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)
        self.clear_cache_key_by_user(self.user_id)
        self.clear_cache_key_by_jmsg(self.jmsg_id)
        self.clear_cache_key_by_device_and_notification(
            self.device_id, self.notification_id)

        new_state = vars(self.get(self.id_))
        vars(self).update(new_state)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        if not id_:
            return

        sql = ('select id, user_id, device_id, notification_id, status, jmsg_id, creation_time, '
               'push_time, received_time, clicked_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_user)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        params = (user_id, )
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_user_id(cls, user_id):
        id_list = cls.get_ids_by_user(user_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    @cache(cache_key_by_device_and_notification)
    def get_id_by_device_and_notification(cls, device_id, notification_id):
        sql = ('select id from {.table_name} where device_id=%s '
               'and notification_id=%s').format(cls)
        params = (device_id, notification_id)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_device_and_notification(cls, device_id, notification_id):
        id_ = cls.get_id_by_device_and_notification(device_id, notification_id)
        return cls.get(id_)

    @classmethod
    @cache(cache_key_by_jmsg_id)
    def get_id_by_jmsg_id(cls, jmsg_id):
        sql = 'select id from {.table_name} where jmsg_id=%s'.format(cls)
        params = (jmsg_id, )
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_jmsg_id(cls, jmsg_id):
        id_ = cls.get_id_by_jmsg_id(jmsg_id)
        return cls.get(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_key_by_user(cls, user_id):
        mc.delete(cls.cache_key_by_user.format(**locals()))

    @classmethod
    def clear_cache_key_by_jmsg(cls, jmsg_id):
        mc.delete(cls.cache_key_by_jmsg_id.format(**locals()))

    @classmethod
    def clear_cache_key_by_device_and_notification(cls, device_id, notification_id):
        mc.delete(cls.cache_key_by_device_and_notification.format(**locals()))
