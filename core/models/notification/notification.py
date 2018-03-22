# coding: utf-8

from datetime import datetime

from flask_mako import render_template, render_template_def
from werkzeug.utils import cached_property

from jupiter.workers.pusher import (
    notification_unicast_push as mq_notification_push)
from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.consts import Platform
from core.models.pusher import PushSupport
from core.models.user.account import Account
from core.models.mixin.props import PropsMixin, PropsItem
from .kind import NotificationKind, welfare_gift_notification


class Notification(EntityModel, PropsMixin, PushSupport):
    """消息通知"""

    table_name = 'notification'
    cache_key = 'notification:{id_}:v1'
    cache_key_by_user_id = 'notification:user:{user_id}:v1'
    cache_key_by_user_unread = 'notification:user:{user_id}:unread:v1'
    cache_key_by_user_and_kind = 'notification:user:{user_id}:kind:{kind_id}:v1'

    #: the properties to render(id of linked entity is recommended)
    properties = PropsItem('properties', {})

    def __init__(self, id_, user_id, kind_id, is_read, creation_time, read_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.kind_id = str(kind_id)
        self.is_read = bool(is_read)
        self.creation_time = creation_time
        self.read_time = read_time

    def get_uuid(self):
        return 'item:{id_}'.format(id_=self.id_)

    def get_db(self):
        return 'notification'

    @property
    def status(self):
        return self.Status(self._status)

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def kind(self):
        return NotificationKind.get(self.kind_id)

    @cached_property
    def template(self):
        return render_template(
            self.kind.common_template_location, palette=self, link=self.kind.web_target_link)

    @cached_property
    def title(self):
        # 暂要求单播通知不使用消息类型中的默认标题
        return render_template_def(
            self.kind.common_template_location, 'notification_title', palette=self).strip()

    @cached_property
    def timestamp(self):
        return render_template_def(
            self.kind.common_template_location, 'notification_timestamp', palette=self).strip()

    @cached_property
    def content(self):
        # 暂要求单播通知不使用消息类型中的默认内容
        return render_template_def(
            self.kind.common_template_location, 'notification_content', palette=self).strip()

    def mark_as_read(self):
        """标记消息为已读"""
        if self.is_read:
            return

        read_time = datetime.now()
        sql = 'update {.table_name} set is_read=%s, read_time=%s where id=%s'.format(self)
        params = (True, read_time, self.id_)
        db.execute(sql, params)
        db.commit()

        # 刷新实例属性并清除缓存
        self.is_read = True
        self.read_time = read_time
        self.clear_cache(self.id_)
        self.clear_cache_by_user(self.user_id)
        self.clear_cache_by_user_and_kind(self.user_id, self.kind_id)

    @property
    def allow_push(self):
        return self.kind.allow_push

    @property
    def is_unicast_push_only(self):
        return self.kind.is_unicast_push_only

    @property
    def push_platforms(self):
        """实际推送平台将由具体类型优先定夺，以类型定义为fallback默认值"""
        from core.models.welfare import Package

        if self.allow_push:
            if self.kind is welfare_gift_notification:
                # 礼包类型单播推送
                package = Package.get(self.properties.get('welfare_package_id'))
                return package.kind.push_platforms
            return self.kind.push_platforms

    def make_push_pack(self, audience, platform):
        """创建单播通知(面向设备)的推送"""
        from core.models.welfare import Package
        from core.models.pusher.element import Pack, Notice, SingleDeviceAudience

        assert isinstance(audience, SingleDeviceAudience)
        assert isinstance(platform, Platform)

        if self.allow_push:
            if self.kind is welfare_gift_notification:
                # 礼包类型单播推送
                package = Package.get(self.properties.get('welfare_package_id'))
                notice = Notice(
                    package.kind.description or self.content, title=self.title)
            else:
                # 其他类型单播推送
                notice = Notice(self.content, title=self.title)

            return Pack(
                audience, notice, [platform],
                target_link=self.kind.app_target_link,
                needs_following_up=True)

    @classmethod
    def create(cls, user_id, kind, properties=None):
        assert isinstance(kind, NotificationKind)
        assert properties is None or isinstance(properties, dict)

        # 校验参数
        user = Account.get(user_id)
        if not user:
            raise ValueError('invalid user id')

        if kind.is_once_only:
            id_list = cls.get_id_list_by_user_and_kind(user.id_, kind.id_)
            if id_list:
                return cls.get(id_list[0])

        sql = ('insert into {.table_name} (user_id, kind_id, is_read, '
               'creation_time) values (%s, %s, %s, %s)').format(cls)
        params = (user_id, kind.id_, False, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        instance = cls.get(id_)
        instance.properties = properties or {}

        # 单播消息则提交并加入推送队列
        cls.clear_cache_by_user(user.id_)
        cls.clear_cache_by_user_and_kind(user.id_, kind.id_)

        # 由推送控制中心来记录和完成推送
        if kind.allow_push:
            mq_notification_push.produce(str(id_))
        return instance

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, kind_id, is_read, creation_time, '
               'read_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_user_id)
    def get_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id=%s '
               'order by creation_time desc').format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_by_user_unread)
    def get_unread_id_list_by_user_id(cls, user_id):
        sql = ('select id from {.table_name} where user_id=%s '
               'and is_read=%s order by creation_time desc').format(cls)
        params = (user_id, False)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_by_user_and_kind)
    def get_id_list_by_user_and_kind(cls, user_id, kind_id):
        sql = ('select id from {.table_name} where user_id=%s '
               'and kind_id=%s order by creation_time desc').format(cls)
        params = (user_id, kind_id)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_id_list_by_user_id(user_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi_unreads_by_user(cls, user_id):
        id_list = cls.get_unread_id_list_by_user_id(user_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi_by_user_and_kind(cls, user_id, kind_id):
        id_list = cls.get_id_list_by_user_and_kind(user_id, kind_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi(cls, id_list):
        return [cls.get(id_) for id_ in id_list]

    @classmethod
    def get_merged_popout_template(cls, notifications):
        kinds = list(set([n.kind for n in notifications]))
        if len(kinds) > 1:
            raise ValueError('template merge of different notifications is not supported')
        return render_template(kinds[0].popout_template_location, palettes=notifications)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_key_by_user_id.format(**locals()))
        mc.delete(cls.cache_key_by_user_unread.format(**locals()))

    @classmethod
    def clear_cache_by_user_and_kind(cls, user_id, kind_id):
        mc.delete(cls.cache_key_by_user_and_kind.format(**locals()))
