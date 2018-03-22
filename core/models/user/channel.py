# coding: utf-8

from __future__ import absolute_import

import datetime
import collections

from werkzeug.utils import cached_property

from core.models.base import EntityModel
from libs.db.store import db
from libs.cache import mc, cache


class Channel(EntityModel):
    """第三方用户注册来源渠道 (用于分成)."""

    class Meta:
        repr_attr_names = ['name', 'tag', 'is_enabled', 'creation_time']

    table_name = 'user_channel'
    cache_key = 'user:channel:{id_}'
    cache_by_tag_key = 'user:channel:tag:{tag}'

    def __init__(self, id_, name, tag, is_enabled, creation_time):
        self.id_ = str(id_)
        #: 渠道名
        self.name = name
        #: 用于 URL 和 Cookie 中标识渠道的标签名
        self.tag = tag
        self.is_enabled = bool(is_enabled)
        self.creation_time = creation_time

    @classmethod
    def add(cls, name, tag):
        sql = ('insert into {0} (name, tag, is_enabled, creation_time) '
               'values (%s, %s, %s, %s)').format(cls.table_name)
        params = (name, tag, True, datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_tag(tag)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, name, tag, is_enabled, creation_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_by_tag_key)
    def get_id_by_tag(cls, tag):
        sql = 'select id from {0} where tag = %s'.format(cls.table_name)
        params = (tag,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_tag(cls, tag):
        id_ = cls.get_id_by_tag(unicode(tag))
        if id_:
            return cls.get(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_tag(cls, tag):
        mc.delete(cls.cache_by_tag_key.format(**locals()))


class ChannelRegister(collections.namedtuple('ChannelRegister', 'user_id channel_id')):
    """用户从渠道注册的记录"""

    table_name = 'user_channel_register'
    cache_key = 'user:channel_register:{user_id}'
    cache_by_channel_key = 'user:channel_register:channel:{channel_id}:ids'

    @cached_property
    def channel(self):
        return Channel.get(self.channel_id)

    @classmethod
    def add(cls, user_id, channel_id):
        sql = ('insert into {0} (user_id, channel_id) '
               'values (%s, %s)').format(cls.table_name)
        params = (user_id, channel_id)
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(user_id, channel_id)
        return cls.get(user_id)

    @classmethod
    def get(cls, user_id):
        sql = ('select user_id, channel_id from {0} '
               'where user_id = %s').format(cls.table_name)
        params = (user_id,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*map(str, rs[0]))

    @classmethod
    @cache(cache_by_channel_key)
    def get_ids_by_channel(cls, channel_id):
        sql = ('select user_id from {0} where channel_id = %s '
               'order by user_id asc').format(cls.table_name)
        params = (channel_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_channel(cls, channel_id):
        ids = cls.get_ids_by_channel(channel_id)
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, user_id, channel_id):
        mc.delete(cls.cache_key.format(**locals()))
        mc.delete(cls.cache_by_channel_key.format(**locals()))


class ChannelMixin(object):

    channel_class = Channel
    channel_register_class = ChannelRegister

    def assign_channel_via_tag(self, channel_tag):
        channel = self.channel_class.get_by_tag(channel_tag)
        if channel:
            return self.assign_channel(channel)

    def assign_channel(self, channel):
        """将用户标记为某渠道注册的, 用户产生的交易将予以分成.

        :rtype: :class:`.Channel`
        """
        if self.channel:
            raise ChannelExistedError()
        self.__dict__.pop('channel', None)
        register = self.channel_register_class.add(self.id_, channel.id_)
        return register.channel

    @cached_property
    def channel(self):
        """获取用户的注册渠道.

        :rtype: :class:`.Channel`
        """
        register = self.channel_register_class.get(self.id_)
        if register:
            return register.channel

    @classmethod
    def get_multi_by_channel(cls, channel, start=None, stop=None):
        """获取某渠道注册的全部用户.

        :rtype: :class:`list` of :class:`.Account`
        """
        register_list = \
            cls.channel_register_class.get_multi_by_channel(channel.id_)
        return [cls.get(r.user_id) for r in register_list[start:stop]]

    @classmethod
    def count_by_channel(cls, channel):
        register_list = \
            cls.channel_register_class.get_multi_by_channel(channel.id_)
        return len(register_list)


class ChannelException(Exception):
    pass


class ChannelExistedError(ChannelException):
    pass
