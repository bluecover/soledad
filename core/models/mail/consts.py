# coding:utf-8

from enum import Enum


NORMAL_PRIORITY = 1
HIGH_PRIORITY = 10


class SenderType(Enum):
    normal = '1'
    multi = '2'
