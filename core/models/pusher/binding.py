# coding: utf-8

from datetime import datetime

from enum import Enum
from werkzeug.utils import cached_property
from pkg_resources import SetuptoolsVersion

from jupiter.ext import sentry
from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.consts import Platform
from core.models.user.account import Account
from .consts import jpush_splitter_sub


class DeviceBinding(EntityModel):
    """极光用户与设备的绑定"""

    class Status(Enum):
        #: 登录状态
        active = 'A'
        #: 注销状态
        inactive = 'I'

    table_name = 'pusher_device_binding'
    cache_key = 'pusher:device_binding:v1:{id_}:v1'
    cache_key_by_user_id = 'pusher:device_binding:v1:user:{user_id}'
    cache_key_by_device_id = 'pusher:device_binding:v1:device:{device_id}'
    cache_key_by_user_and_status = 'pusher:device_binding:v1:user:{user_id}:status:{status}'
    cache_key_by_user_and_device = 'pusher:device_binding:v1:user:{user_id}:device:{device_id}'
    cache_key_by_user_and_platform = 'pusher:device_binding:v1:user:{user_id}:platform:{platform}'

    def __init__(self, id_, user_id, device_id, status, platform, app_version,
                 creation_time, update_time):
        self.id_ = id_
        self.user_id = str(user_id)
        self.device_id = device_id
        self._status = status
        self._platform = str(platform)
        self._app_version = app_version
        self.creation_time = creation_time
        self.update_time = update_time

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def platform(self):
        return Platform(self._platform)

    @cached_property
    def app_version(self):
        return SetuptoolsVersion(self._app_version)

    @cached_property
    def underscored_app_version(self):
        return jpush_splitter_sub(self._app_version)

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, item):
        self._status = item.value

    @classmethod
    def check_before_create(cls, user, device_id, device_platform, device_app_version):
        assert isinstance(user, Account)
        assert isinstance(device_platform, Platform)
        assert isinstance(device_app_version, SetuptoolsVersion)

        if not isinstance(device_id, (str, unicode)):
            raise TypeError('provided device id is not string')

        if device_platform not in [Platform.ios, Platform.android]:
            raise ValueError('pushing target device must be mobile')

        if cls.get_by_user_and_device(user.id_, device_id):
            raise ValueError('user device binding has existed')

    @classmethod
    def create(cls, user, device_id, device_platform, device_app_version, _validate=True):
        """创建新的用户设备（当device_id存在而user不同时需要将旧的设备冻结）"""
        if _validate:
            cls.check_before_create(user, device_id, device_platform, device_app_version)

        sql = ('insert into {.table_name} (user_id, device_id, status, platform, '
               'app_version, creation_time) values (%s, %s, %s, %s, %s, %s)').format(cls)
        params = (user.id_, device_id, cls.Status.active.value, device_platform.value,
                  str(device_app_version), datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_all_cache(id_, user.id_, device_id, device_platform)
        return cls.get(id_)

    def change_owner(self, new_user):
        """为设备调整所属登录用户"""
        if new_user.id_ == self.user_id:
            sentry.captureMessage('try to change owner to self %s' % self.user_id)
            return

        sql = ('update {.table_name} set user_id=%s, status=%s '
               'where user_id=%s and device_id=%s').format(self)
        params = (new_user.id_, self.Status.active.value, self.user_id, self.device_id)

        #: 清除原用户相关缓存
        self.clear_all_cache(self.id_, self.user_id, self.device_id, self.platform)

        #: 更新所属为新用户
        self.user_id = new_user.id_
        self.clear_cached_properties()
        self._commit_and_refresh(sql, params)

    def delete(self):
        """解除绑定关系"""
        sql = 'delete from {.table_name} where id=%s'.format(self)
        params = (self.id_, )
        self._commit_and_refresh(sql, params)

    def update_app_version(self, new_version):
        """为设备更新装载APP版本信息"""
        if not new_version or new_version == self.app_version:
            return

        sql = 'update {.table_name} set app_version=%s where id=%s'.format(self)
        params = (new_version, self.id_)

        self.clear_cached_properties()
        self._commit_and_refresh(sql, params)

    def activate(self):
        """激活（唤醒）设备已接受"""
        if self.status is self.Status.active:
            return

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.active.value, self.id_)
        self._commit_and_refresh(sql, params)

    def deactivate(self):
        """冻结（睡眠）设备以避免接受推送"""
        if self.status is self.Status.inactive:
            return

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.inactive.value, self.id_)
        self._commit_and_refresh(sql, params)

    def _commit_and_refresh(self, sql, params):
        db.execute(sql, params)
        db.commit()

        self.clear_all_cache(self.id_, self.user_id, self.device_id, self.platform)

        instance = self.get(self.id_)
        new_state = vars(instance) if instance else {}
        vars(self).update(new_state)

    def clear_cached_properties(self):
        self.__dict__.pop('user', None)
        self.__dict__.pop('app_version', None)
        self.__dict__.pop('underscored_app_version', None)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        if not id_:
            return

        sql = ('select id, user_id, device_id, status, platform, app_version, '
               'creation_time, update_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_device_id)
    def get_id_by_device_id(cls, device_id):
        sql = 'select id from {.table_name} where device_id=%s'.format(cls)
        params = (device_id,)
        rs = db.execute(sql, params)
        if rs:
            return str(rs[0][0])

    @classmethod
    @cache(cache_key_by_user_and_device)
    def get_id_by_user_and_device(cls, user_id, device_id):
        sql = 'select id from {.table_name} where user_id=%s and device_id=%s'.format(cls)
        params = (user_id, device_id)
        rs = db.execute(sql, params)
        if rs:
            return str(rs[0][0])

    @classmethod
    @cache(cache_key_by_user_id)
    def get_id_list_by_user_id(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_by_user_and_status)
    def get_id_list_by_user_and_status(cls, user_id, status=Status.active):
        sql = 'select id from {.table_name} where user_id=%s and status=%s'.format(cls)
        params = (user_id, status.value)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_by_user_and_platform)
    def get_id_list_by_user_and_platform(cls, user_id, platform):
        sql = 'select id from {.table_name} where user_id=%s and platform=%s'.format(cls)
        params = (user_id, platform.value)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_by_device(cls, device_id):
        id_ = cls.get_id_by_device_id(device_id)
        return cls.get(id_)

    @classmethod
    def get_by_user_and_device(cls, user_id, device_id):
        id_ = cls.get_id_by_user_and_device(user_id, device_id)
        return cls.get(id_)

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_id_list_by_user_id(user_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi_by_user_and_status(cls, user_id, status=Status.active):
        id_list = cls.get_id_list_by_user_and_status(user_id, status)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi_by_user_and_platform(cls, user_id, platform):
        id_list = cls.get_id_list_by_user_and_platform(user_id, platform)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi(cls, id_list):
        return [cls.get(id_) for id_ in id_list]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_device(cls, device_id):
        mc.delete(cls.cache_key_by_device_id.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_key_by_user_id.format(user_id=user_id))
        mc.delete(cls.cache_key_by_user_and_status.format(
            user_id=user_id, status=cls.Status.active))
        mc.delete(cls.cache_key_by_user_and_status.format(
            user_id=user_id, status=cls.Status.inactive))

    @classmethod
    def clear_cache_by_user_and_device(cls, user_id, device_id):
        mc.delete(cls.cache_key_by_user_and_device.format(**locals()))

    @classmethod
    def clear_cache_by_user_and_platform(cls, user_id, platform):
        mc.delete(cls.cache_key_by_user_and_platform.format(**locals()))

    @classmethod
    def clear_all_cache(cls, id_, user_id, device_id, platform):
        assert isinstance(platform, Platform)

        cls.clear_cache(id_)
        cls.clear_cache_by_device(device_id)
        cls.clear_cache_by_user(user_id)
        cls.clear_cache_by_user_and_device(user_id, device_id)
        cls.clear_cache_by_user_and_platform(user_id, platform)
