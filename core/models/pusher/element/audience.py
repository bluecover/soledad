# coding: utf-8

from enum import Enum

from core.models.consts import CastKind


class Audience(object):

    class Kind(Enum):
        #: 单用户
        single_user = 'SU'
        #: 单设备
        single_device = 'SD'
        #: 多用户组播
        multi_users = 'MU'
        #: 并集标签
        uninon_tags = 'UT'
        #: 交集标签
        intersect_tags = 'IT'
        #: 全员广播
        all_users = 'AU'

    Kind.single_user.cast = CastKind.unicast
    Kind.single_device.cast = CastKind.unicast
    Kind.multi_users.cast = CastKind.multicast
    Kind.uninon_tags.cast = CastKind.multicast
    Kind.intersect_tags.cast = CastKind.multicast
    Kind.all_users.cast = CastKind.broadcast


class SingleUserAudience(Audience):

    kind = Audience.Kind.single_user

    def __init__(self, user_id):
        self.user_id = user_id

    @property
    def payload(self):
        return {'alias': [self.user_id]}


class SingleDeviceAudience(Audience):

    kind = Audience.Kind.single_device

    def __init__(self, device_id):
        self.device_id = device_id

    @property
    def payload(self):
        return {'registration_id': [self.device_id]}


class MultiUsersAudience(Audience):

    kind = Audience.Kind.multi_users

    def __init__(self, user_ids):
        self.user_ids = list(user_ids)

    @property
    def payload(self):
        return {'alias': self.user_ids}


class AllUsersAudience(Audience):

    kind = Audience.Kind.all_users

    @property
    def payload(self):
        return {'all': []}


class UnionTagsAudience(Audience):

    kind = Audience.Kind.uninon_tags

    def __init__(self, tags):
        self.tags = list(tags)

    @property
    def payload(self):
        return {'tag': self.tags}


class IntersectTagsAudience(Audience):

    kind = Audience.Kind.intersect_tags

    def __init__(self, tags):
        self.tags = list(tags)

    @property
    def payload(self):
        return {'tag_and': self.tags}
