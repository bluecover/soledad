# coding: utf-8

"""
    Track Log
    ~~~~~~~~~

    This module includes the logging utilities for tracking user event.
"""

from __future__ import absolute_import, unicode_literals

from blinker import Namespace

from libs.logger.rsyslog import rsyslog


__all__ = ['events']

events = Namespace()

# User Events
register_success = events.signal('register_success')
savings_success = events.signal('savings_success')


class EventLogger(object):
    """The logger for recording user events."""

    refs = {}

    def __init__(self, name):
        self.name = name
        self.refs[name] = self

    def __call__(self, sender, **kwargs):
        extra = dict(kwargs)
        extra.setdefault('endpoint', sender.endpoint)
        extra.setdefault('platform', sender.user_agent.app_info.platform or u'')
        extra.setdefault('version', sender.user_agent.app_info.version or u'')
        extra.setdefault('channel', sender.headers.get('X-Channel-Name', u''))
        if hasattr(sender, 'oauth'):
            extra.setdefault('oauth_user_id', sender.oauth.user.id_)
            extra.setdefault('oauth_token_id', sender.oauth.access_token.id_)
            extra.setdefault('oauth_token_type', sender.oauth.token_type)
            extra.setdefault('oauth_client_id', sender.oauth.client.id_)
            extra.setdefault('oauth_scopes', ','.join(sender.oauth.scopes))
        if hasattr(sender, 'oauth_client'):
            extra.setdefault('oauth_client_id', sender.oauth_client.id_)
        pairs = ['%s=%s' % pair for pair in sorted(list(extra.items()))]
        rsyslog.send(
            '\t'.join([self.name] + pairs).encode('utf-8'), tag='api_events')

    @classmethod
    def subscribe_all(cls, events):
        for event in events:
            event.connect(cls(event.name))


EventLogger.subscribe_all(events.values())
