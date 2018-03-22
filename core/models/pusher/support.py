# coding: utf-8

from __future__ import absolute_import


class PushSupport(object):

    @property
    def allow_push(self):
        raise NotImplementedError

    @property
    def is_unicast_push_only(self):
        raise NotImplementedError

    @property
    def push_platforms(self):
        raise NotImplementedError

    def make_push_pack(self, *args, **kwargs):
        raise NotImplementedError
