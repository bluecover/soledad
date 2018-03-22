# -*- coding: utf-8 -*-

import datetime

from enum import Enum

SITE_NAME = 'guihua'
SITE_NAME_CN = '好规划'
SITE_GOLIVE_DATE = datetime.date(2014, 12, 4)

MAX_PASSWD_LEN = 16
MIN_PASSWD_LEN = 6

SESSION_EXPIRE_DAYS = 30


class Platform(Enum):
    """ 请求来源（平台）枚举"""
    #: uncertained or unsupported
    unknown = '0'
    #: all browsers
    web = '1'
    #: ios app
    ios = '2'
    #: android app
    android = '3'


class CastKind(Enum):
    unicast = 'U'
    multicast = 'M'
    broadcast = 'B'


class SetOperationKind(Enum):
    union = 'U'
    intersection = 'I'
