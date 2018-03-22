# -*- coding: utf-8 -*-

import time

from libs.cache import mc
from libs.logger.rsyslog import rsyslog

from solar.utils.storify import storify

LIMIT = storify(dict(
    REGISTER='register:%s',  # ip
    FORGOT_PASSWORD='forgot_password:%s',  # ip
    POST='post:%s',  # ip
    MOBILE_REG='mobile_reg:%s',  # mobile
    IP_MOBILE_REG='ip_mobile_reg:%s',  # ip mobile
    BACKEND_MOBILE_SERVICE='backend_mobile_service:%s',
    MOBILE_BIND='mobile_bind:%s',  # mobile binding
    IP_MOBILE_BIND='ip_mobile_bind:%s',  # ip mobile binding
    MOBILE_WITHDRAW='mobile_withdraw:%s',
    IP_MOBILE_WITHDRAW='ip_mobile_withdraw:%s',
    USER_FETCH_ZW_LOANS='user_fetch_zw_loans:%s'
))


def _log(msg):
    rsyslog.send(msg, tag='limit')


class Limit(object):

    def __init__(self, key, timeout, limit):
        self.key = key
        self._limit_key = 'guihua_limit_%s' % key
        self.timeout = timeout
        self.limit = limit

    def __repr__(self):
        return '<Limit key=%s, timeout=%s>' % (
            self.key, self.timeout)

    @classmethod
    def get(cls, key, timeout=3600, limit=20):
        return cls(key, timeout, limit)

    @property
    def num(self):
        _n = mc.llen(self._limit_key)
        if not _n:
            now = int(time.time())
            mc.lpush(self._limit_key, now)
            mc.expire(self._limit_key, self.timeout)
        return mc.llen(self._limit_key) - 1

    def touch(self):
        now = int(time.time())
        if self.is_limited():
            return self.num
        mc.lpush(self._limit_key, now)
        return self.num

    def is_limited(self):
        if self.num > self.limit:
            _log('\t'.join([self.key, str(self.limit), str(self.timeout),
                            str(self.num)]))
            return True
        return False

    def clear(self):
        mc.delete(self._limit_key)
