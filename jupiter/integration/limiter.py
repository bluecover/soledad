from __future__ import absolute_import, unicode_literals

import re

from flask import g, request
from flask_limiter.errors import RateLimitExceeded
from babel.dates import format_timedelta
from limits import parse_many as parse_many_limits

from jupiter.ext import limiter


class FlexibleLimiter(object):
    """The wrapper of "limits" which is more flexible than Flask-Limiter."""

    re_digits = re.compile(r'(\s*\d+\s*)')

    def __init__(self, expr, scope=None, limiter=None):
        self.limits = parse_many_limits(expr)
        self.scope = scope
        self.limiter = limiter

    @property
    def _limiter(self):
        return self.limiter or limiter.limiter

    def _make_args(self, limit, key):
        return (limit, key, self.scope or request.endpoint)

    def render_message(self, message, limit):
        if message is None:
            return limit
        granularity = format_timedelta(limit.granularity[0], locale='zh_CN')
        granularity = self.re_digits.sub(r' \1 ', granularity)
        amount = self.re_digits.sub(r' \1 ', unicode(limit.amount))
        return message.format(granularity=granularity, amount=amount).strip()

    def raise_for_exceeded(self, key, message=None):
        for limit in self.limits:
            args = self._make_args(limit, key)
            if self._limiter.test(*args):
                continue
            g.view_rate_limit = args
            raise RateLimitExceeded(self.render_message(message, limit))

    def hit(self, key):
        for limit in self.limits:
            self._limiter.hit(*self._make_args(limit, key))
