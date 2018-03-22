# coding: utf-8

from datetime import datetime
from operator import attrgetter
from hashlib import sha1

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.utils.codec import encode, decode
from core.models.consts import Platform, CastKind, SetOperationKind
from core.models.pusher import PushSupport
from core.models.pusher.errors import DocTooShortError
from core.models.pusher.consts import PUSH_TITLE_MIN_LENGTH, PUSH_CONTENT_MIN_LENGTH
from core.models.pusher.element import (
    Pack, Notice, AllUsersAudience, UnionTagsAudience, IntersectTagsAudience)
from core.models.mixin.props import PropsMixin, PropsItem


class Bulletin(EntityModel, PropsMixin, PushSupport):
    """APP纯运营消息通知"""

    table_name = 'site_bulletin'
    cache_key = 'site_bulletin:v1:{id_}'
    cache_key_app_latest = 'site_bulletin:v2:cache_key_app_latest'

    #: The title of bulletin
    title = PropsItem('title', default=u'')

    #: The content of bulletin
    content = PropsItem('content', default=u'')

    #: The target_link of bulletin
    target_link = PropsItem('target_link', default=u'')

    #: The cast tags of bulletin
    cast_tags = PropsItem('cast_tags', default=[])

    #: The cast tags combine method of bulletin
    cast_tags_combine_method_code = PropsItem('cast_tags_combine_method_code', default=u'')

    def __init__(self, id_, platforms, cast_kind, creation_time, expire_time):
        self.id_ = str(id_)
        self._platforms = platforms.split(',')
        self._cast_kind = cast_kind
        self.creation_time = creation_time
        self.expire_time = expire_time

    def get_uuid(self):
        return 'bulletin:{.id_}'.format(self)

    def get_db(self):
        return 'site_bulletin'

    @cached_property
    def platforms(self):
        return [Platform(p) for p in self._platforms]

    @cached_property
    def cast_kind(self):
        return CastKind(self._cast_kind)

    @cached_property
    def cast_tags_combine_method(self):
        if self.cast_tags_combine_method_code:
            return SetOperationKind(self.cast_tags_combine_method_code)

    @property
    def allow_push(self):
        return True

    @property
    def is_unicast_push_only(self):
        return False

    @property
    def push_platforms(self):
        # 暂不支持样式定制
        return self.platforms

    def make_push_pack(self):
        if self.cast_kind is CastKind.broadcast:
            audience = AllUsersAudience()
        elif self.cast_kind is CastKind.multicast:
            if self.cast_tags_combine_method is SetOperationKind.union:
                audience = UnionTagsAudience(self.cast_tags)
            elif self.cast_tags_combine_method is SetOperationKind.intersection:
                audience = IntersectTagsAudience(self.cast_tags)
            else:
                raise ValueError('invalid set operation kind')
        else:
            raise ValueError('package kind does not support multicast/broadcast')

        notice = Notice(self.content, title=self.title)
        return Pack(audience, notice, self.platforms, target_link=self.target_link)

    @classmethod
    def create(cls, title, content, platforms, cast_kind, cast_tags=None,
               cast_tags_combine_method=None, target_link=None):
        assert all(isinstance(p, Platform) for p in platforms)

        if title:
            title = decode(title)
            if len(title) < PUSH_TITLE_MIN_LENGTH:
                raise DocTooShortError(title, PUSH_TITLE_MIN_LENGTH)

        content = decode(content)
        if len(content) < PUSH_CONTENT_MIN_LENGTH:
            raise DocTooShortError(content, PUSH_CONTENT_MIN_LENGTH)

        platforms = sorted(set(platforms) - set([Platform.web]), key=attrgetter('value'))
        if not platforms:
            raise ValueError('platforms should be appointed')

        cast_kind = cast_kind or CastKind.broadcast
        if cast_kind is CastKind.multicast:
            assert cast_tags_combine_method is None or isinstance(
                cast_tags_combine_method, SetOperationKind)
            cast_tags_combine_method = cast_tags_combine_method or SetOperationKind.union
            if not cast_tags:
                raise ValueError('cast_tags should be provided for multicast')
        elif cast_kind is CastKind.broadcast:
            pass
        else:
            raise ValueError('unsupported cast kind')

        # 禁止同标题同内容群体推送多次
        title_content_sha1 = sha1(encode((u'{0}{1}'.format(
            title or u'', content).strip()))).hexdigest()
        platforms = ','.join(p.value for p in platforms)

        sql = ('insert into {.table_name} (title_content_sha1, platforms, cast_kind, '
               'creation_time) values (%s, %s, %s, %s)').format(cls)
        params = (title_content_sha1, platforms, cast_kind.value, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        instance = cls.get(id_)
        instance.update_props_items({
            'title': title,
            'content': content,
            'target_link': target_link,
            'cast_tags': cast_tags,
            'cast_tags_combine_method_code': (
                cast_tags_combine_method.value if cast_tags_combine_method else None)
        })

        if platforms == ','.join([Platform.ios.value, Platform.android.value]):
            cls.clear_app_latest_cache()

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, platforms, cast_kind, creation_time '
               'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_multi(cls):
        sql = 'select id from {.table_name}'.format(cls)
        rs = db.execute(sql)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_app_latest_cache(cls):
        mc.delete(cls.cache_key_app_latest)

    @classmethod
    @cache(cache_key_app_latest)
    def get_app_latest(cls):
        sql = ('select id, platforms, cast_kind, creation_time, expire_time '
               'from {.table_name} where platforms=%s '
               'order by creation_time desc limit 1').format(cls)
        app_platforms = ','.join([Platform.ios.value, Platform.android.value])
        params = (app_platforms,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])
